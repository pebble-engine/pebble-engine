"""Example gallery — "clone this example" (2026-05-31).

The 15 industry example sites (built by the v2 motion engine — see
`TEMPLATE_GALLERY_RESULTS.md`) are offered as FREE pick-from starting points.
Unlike `/api/instantiate-template` (which copies a curated skeleton + runs an
LLM content-swap), an example is already a complete, real site. "Cloning" one
is a pure filesystem copy — no LLM call, instant, billable: false — that drops
a fully-built v2 site (motion + click-to-edit ids intact) into the user's
account as their starting project. They then edit it like any other build.

Manifest: `pebble/example_gallery.json` (committed). Each entry's `source_dir`
points at the built site to copy from.

Endpoints
---------
- GET  /api/examples           → list the gallery (public)
- POST /api/examples/clone      → clone one example into output/<new-slug>/
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pebble.log import log
from pebble.text import sanitize_business_name
from pebble.next_config_patch import ensure_allowed_dev_origins
from pebble.security import client_ip, generate_limiter


_REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = _REPO_ROOT / "pebble" / "example_gallery.json"

# Build artifacts we never copy when cloning (npm install happens at edit time).
_SKIP_NAMES = frozenset({"node_modules", ".next", ".turbo", "dist", "build"})


def load_examples() -> dict[str, Any]:
    """Read example_gallery.json. Degrade to an empty gallery on any error so a
    bad manifest never 500s the engine."""
    if not MANIFEST_PATH.exists():
        return {"schema_version": "1.0", "examples": []}
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        log.warning("[examples] manifest parse failed: %s", e)
        return {"schema_version": "1.0", "examples": []}


def get_example(slug: str) -> dict[str, Any] | None:
    for e in load_examples().get("examples", []):
        if isinstance(e, dict) and e.get("slug") == slug:
            return e
    return None


# ---------------------------------------------------------------------------
# GET /api/examples
# ---------------------------------------------------------------------------

def run_list_examples(handler) -> None:
    """Public gallery list. Strips the engine-internal `source_dir`."""
    reg = load_examples()
    public = [
        {k: v for k, v in e.items() if k != "source_dir"}
        for e in reg.get("examples", [])
        if isinstance(e, dict)
    ]
    handler._json(200, {"examples": public, "count": len(public)})


# ---------------------------------------------------------------------------
# POST /api/examples/clone
# ---------------------------------------------------------------------------

def _copy_site(src_dir: Path, dst_dir: Path) -> int:
    written = 0
    for src_path in src_dir.rglob("*"):
        if any(part in _SKIP_NAMES for part in src_path.parts):
            continue
        if src_path.is_dir():
            continue
        rel = src_path.relative_to(src_dir)
        dst_path = dst_dir / rel
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        written += 1
    return written


def run_clone_example(handler) -> None:
    """POST /api/examples/clone
    Body: {example_slug, business_name?}

    Copies the example's built site/ into output/<new-slug>/site/ verbatim
    (no LLM), stamps brief.json + build_meta.json, returns the new slug. The
    user edits it like any other project. billable: false.
    """
    from pebble.server.build import _engine
    pe = _engine()
    OUTPUT_DIR = pe.OUTPUT_DIR
    _slugify = pe._slugify
    MAX_REQUEST_BYTES = pe.MAX_REQUEST_BYTES

    ip = client_ip(handler)
    if not generate_limiter.allow(ip or ""):
        handler._json(429, {"error": "too many build requests — max 5 per 10 min per IP"})
        return

    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return
    if length <= 0 or length > MAX_REQUEST_BYTES:
        handler._json(400, {"error": "missing or oversized body"}); return
    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return

    example_slug = (body.get("example_slug") or "").strip()
    example = get_example(example_slug)
    if not example:
        handler._json(404, {"error": f"unknown example_slug {example_slug!r}"}); return

    src_dir = (_REPO_ROOT / example["source_dir"]).resolve()
    src_site = src_dir / "site"
    # Defense-in-depth: the resolved source must stay under the repo root and
    # actually be one of the manifest's example dirs.
    if not str(src_dir).startswith(str(_REPO_ROOT)) or not src_site.is_dir():
        log.warning("[examples] source site missing for %s: %s", example_slug, src_site)
        handler._json(500, {"error": "example source not available on this server"}); return

    # New slug: from a provided business_name, else "<example>-copy". Auto-suffix
    # on collision (matches the AI-build + instantiate convention).
    raw_name = (body.get("business_name") or "").strip()
    new_name = sanitize_business_name(raw_name) if raw_name else (example.get("name") or example_slug)
    base = _slugify(new_name) if raw_name else f"{example_slug}-copy"
    slug = base
    n = 2
    while (OUTPUT_DIR / slug).exists():
        slug = f"{base}-{n}"; n += 1

    out_dir = OUTPUT_DIR / slug
    site_dir = out_dir / "site"
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        file_count = _copy_site(src_site, site_dir)
    except Exception as e:
        log.exception("[examples] copy failed %s -> %s", src_site, site_dir)
        handler._json(500, {"error": f"clone failed: {e}"}); return

    # Patch next.config.mjs for cross-origin dev preview (Phase 20c).
    try:
        ensure_allowed_dev_origins(site_dir / "next.config.mjs")
    except Exception:
        pass

    # Carry the example's brief forward; override name if the user supplied one.
    try:
        brief = json.loads((src_dir / "brief.json").read_text(encoding="utf-8"))
    except Exception:
        brief = {}
    if raw_name:
        brief["business_name"] = new_name
    brief["_slug"] = slug
    brief["_cloned_from"] = example_slug
    brief["_created_at"] = datetime.now(timezone.utc).isoformat()
    # Stamp ownership if a session resolves (best-effort; anon clones are
    # claimable later via /api/projects/<slug>/claim).
    try:
        uid = pe._resolve_user_id(handler) if hasattr(pe, "_resolve_user_id") else None
        if uid:
            brief["_user_id"] = uid
    except Exception:
        pass
    (out_dir / "brief.json").write_text(json.dumps(brief, indent=2), encoding="utf-8")

    (out_dir / "build_meta.json").write_text(json.dumps({
        "engine_version": "v2",
        "provider": "example-clone",
        "model": "clone",
        "cloned_from": example_slug,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "file_count": file_count,
        "billable": False,
    }, indent=2), encoding="utf-8")

    handler._json(200, {
        "ok": True,
        "slug": slug,
        "cloned_from": example_slug,
        "file_count": file_count,
        "preview_url": f"/preview/{slug}/",
        "billable": False,
    })


__all__ = ["load_examples", "get_example", "run_list_examples", "run_clone_example"]
