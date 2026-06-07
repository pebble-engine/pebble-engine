"""P4 — /api/account/templates: owner-saved personal templates.

- GET    /api/account/templates              → list the caller's templates
- POST   /api/account/templates              → save {slug,label} as a template
- POST   /api/account/templates/<id>/use     → spin up a new project from it
- DELETE /api/account/templates/<id>         → remove one

"Use" copies the snapshot into a fresh output/<slug>/site/. If the snapshot
contains content/site.ts (template-instantiated source) it runs the same cheap
content-swap LLM call as /api/instantiate-template; otherwise it's a plain
structural clone the owner customises via refine / visual-edit.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from pebble.log import log
from pebble.security import resolve_user_id, require_project_owner
from pebble import personal_templates as pt


def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


def _read_body(handler) -> Optional[dict]:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return None
    if length <= 0:
        return {}
    try:
        return json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return None


# --------------------------------------------------------------------------- #
# GET /api/account/templates
# --------------------------------------------------------------------------- #

def run_list_personal_templates(handler) -> None:
    uid = resolve_user_id(handler)
    if not uid:
        handler._json(401, {"error": "authentication required"}); return
    handler._json(200, {"templates": pt.list_personal_templates(_output_dir(), uid)})


# --------------------------------------------------------------------------- #
# POST /api/account/templates  body: {slug, label}
# --------------------------------------------------------------------------- #

def run_save_personal_template(handler) -> None:
    body = _read_body(handler)
    if body is None:
        return
    slug = (body.get("slug") or "").strip()
    label = (body.get("label") or "").strip()
    if not slug:
        handler._json(400, {"error": "missing slug"}); return
    # Ownership gate (writes its own 400/401/403/404 then returns None).
    uid = require_project_owner(handler, slug)
    if not uid:
        return
    site_dir = _output_dir() / slug / "site"
    if not site_dir.exists() or not site_dir.is_dir():
        handler._json(404, {"error": f"no site found for project {slug!r}"}); return
    try:
        entry = pt.save_personal_template(_output_dir(), uid, site_dir, label, source_slug=slug)
    except ValueError as e:
        handler._json(400, {"error": str(e)}); return
    except Exception as e:
        log.exception("[personal-templates] save failed for %s", slug)
        handler._json(500, {"error": f"save failed: {e}"}); return
    handler._json(200, {"template": entry, "ok": True})


# --------------------------------------------------------------------------- #
# POST /api/account/templates/<id>/use  body: {brief}
# --------------------------------------------------------------------------- #

def run_use_personal_template(handler, template_id: str) -> None:
    uid = resolve_user_id(handler)
    if not uid:
        handler._json(401, {"error": "authentication required"}); return
    body = _read_body(handler)
    if body is None:
        return
    brief = body.get("brief") if isinstance(body.get("brief"), dict) else (body or {})
    if not isinstance(brief, dict):
        brief = {}

    out_root = _output_dir()
    entry = pt.get_personal_template(out_root, uid, template_id)
    if not entry:
        handler._json(404, {"error": f"unknown template {template_id!r}"}); return
    src_site = pt.template_site_dir(out_root, uid, template_id)
    if not src_site.exists():
        handler._json(500, {"error": "template files missing on disk"}); return

    pe = _engine()
    _slugify = pe._slugify
    from pebble.text import sanitize_business_name

    raw_name = brief.get("business_name", "")
    cleaned = sanitize_business_name(raw_name) or "untitled"
    if cleaned != raw_name and cleaned:
        brief["business_name"] = cleaned
    slug = _slugify(cleaned)
    try:
        from pebble.server.dev_registry import get_url as _get_dev_url
        if _get_dev_url(slug) or (out_root / slug).exists():
            base, n = slug, 2
            while _get_dev_url(f"{base}-{n}") or (out_root / f"{base}-{n}").exists():
                n += 1
            slug = f"{base}-{n}"
    except Exception:
        pass

    out_dir = out_root / slug
    site_dir = out_dir / "site"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy the snapshot into the new project.
    try:
        file_count = pt._copy_site(src_site, site_dir)
    except Exception as e:
        log.exception("[personal-templates] clone failed %s -> %s", src_site, site_dir)
        handler._json(500, {"error": f"clone failed: {e}"}); return

    # Optional content-swap (only when the snapshot isolates content/site.ts).
    swap_ok, swap_msg, llm_cost_usd = False, "skipped (no content/site.ts)", 0.0
    content_path = site_dir / pt.TOKENIZED_FILE
    if content_path.exists():
        try:
            from pebble.server.templates_api import (
                _build_content_swap_prompt,
                _extract_typescript_block,
                _validate_swapped_site_ts,
            )
            from pebble.knowledge import load_account_knowledge
            brief["_account_knowledge"] = load_account_knowledge(out_root, uid)
            original_ts = content_path.read_text(encoding="utf-8")
            swap_prompt = _build_content_swap_prompt(template_id, original_ts, brief)
            from pebble.llm import get_llm_client
            client, reason = get_llm_client()
            if client is None or reason != "ok":
                swap_msg = f"llm unavailable: {reason}"
            else:
                system = "You are a careful TypeScript editor. You preserve file structure and only rewrite literal values."
                response = client.generate(system=system, user=swap_prompt, max_tokens=8000)
                llm_text = response if isinstance(response, str) else getattr(response, "text", "")
                extracted = _extract_typescript_block(llm_text)
                if extracted:
                    ok, msg = _validate_swapped_site_ts(extracted, original_ts)
                    if ok:
                        content_path.write_text(extracted, encoding="utf-8")
                        swap_ok, swap_msg = True, "ok"
                    else:
                        swap_msg = f"validation failed: {msg}"
                else:
                    swap_msg = "could not extract typescript block"
                try:
                    from pebble.cost import estimate_cost
                    llm_cost_usd = round(estimate_cost(swap_prompt, llm_text, client.model).estimated_cost_usd, 6)
                except Exception:
                    llm_cost_usd = 0.0
        except Exception as e:
            log.exception("[personal-templates] content-swap failed")
            swap_msg = f"llm error: {e}"

    # Patch next.config for cross-origin dev.
    try:
        from pebble.next_config_patch import ensure_allowed_dev_origins
        ensure_allowed_dev_origins(site_dir / "next.config.mjs")
    except Exception:
        pass

    # Stamp brief + build_meta so the workspace/dashboard pick it up. Mark the
    # new project owned by the caller (so it shows on their dashboard).
    saved = dict(brief)
    saved["_slug"] = slug
    saved["_user_id"] = uid
    saved["_created_at"] = datetime.now().isoformat()
    saved["_personal_template_id"] = template_id
    saved.pop("_account_knowledge", None)
    (out_dir / "brief.json").write_text(json.dumps(saved, indent=2), encoding="utf-8")
    (out_dir / "build_meta.json").write_text(json.dumps({
        "model": "personal-template",
        "provider": "personal-template",
        "personal_template_id": template_id,
        "file_count": file_count,
        "built_at": datetime.now().isoformat(),
        "billable": False,
        "swap_ok": swap_ok,
        "swap_message": swap_msg,
        "estimated_cost_usd": llm_cost_usd,
    }, indent=2), encoding="utf-8")

    handler._json(200, {
        "ok": True,
        "slug": slug,
        "template_id": template_id,
        "file_count": file_count,
        "swap_ok": swap_ok,
        "swap_message": swap_msg,
        "estimated_cost_usd": llm_cost_usd,
    })


# --------------------------------------------------------------------------- #
# DELETE /api/account/templates/<id>
# --------------------------------------------------------------------------- #

def run_delete_personal_template(handler, template_id: str) -> None:
    uid = resolve_user_id(handler)
    if not uid:
        handler._json(401, {"error": "authentication required"}); return
    removed = pt.delete_personal_template(_output_dir(), uid, template_id)
    if not removed:
        handler._json(404, {"error": f"unknown template {template_id!r}"}); return
    handler._json(200, {"ok": True})


__all__ = [
    "run_list_personal_templates",
    "run_save_personal_template",
    "run_use_personal_template",
    "run_delete_personal_template",
]
