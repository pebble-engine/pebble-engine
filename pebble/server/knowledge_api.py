"""P1 — GET/PUT endpoints for durable "about your business" knowledge.

- /api/projects/<slug>/knowledge  (GET/PUT, owner-gated)  → brief.business_knowledge
- /api/account/knowledge          (GET/PUT, auth-gated)   → per-account default

Project PUT snapshots first (version history). All fail-soft + bounded.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from pebble.security import require_project_owner, resolve_user_id
from pebble.history import snapshot_site
from pebble import knowledge as _knowledge

MAX = _knowledge.MAX_BLOCK_CHARS


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


def _safe_slug(slug: str) -> bool:
    return bool(slug) and "/" not in slug and "\\" not in slug and ".." not in slug


# --------- /api/projects/<slug>/knowledge ---------

def run_get_project_knowledge(handler, slug: str) -> None:
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    if require_project_owner(handler, slug) is None:
        return
    brief_path = _output_dir() / slug / "brief.json"
    brief = {}
    try:
        if brief_path.exists():
            brief = json.loads(brief_path.read_text(encoding="utf-8"))
    except Exception:
        brief = {}
    handler._json(200, {"slug": slug, "knowledge": _knowledge.project_knowledge(brief)})


def run_put_project_knowledge(handler, slug: str) -> None:
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    if require_project_owner(handler, slug) is None:
        return
    body = _read_body(handler)
    if body is None:
        return
    text = (body.get("knowledge") or "").strip()[:MAX]
    project_dir = _output_dir() / slug
    brief_path = project_dir / "brief.json"
    if not project_dir.exists():
        handler._json(404, {"error": f"project not found: {slug}"}); return
    # Snapshot before mutating so the edit is in version history / undoable.
    try:
        snapshot_site(slug, reason="edit-knowledge", source="PUT /api/projects/<slug>/knowledge")
    except Exception:
        pass
    brief = {}
    try:
        if brief_path.exists():
            brief = json.loads(brief_path.read_text(encoding="utf-8"))
    except Exception:
        brief = {}
    brief["business_knowledge"] = text
    try:
        brief_path.write_text(json.dumps(brief, indent=2), encoding="utf-8")
    except Exception as e:
        handler._json(500, {"error": f"could not save: {e}"}); return
    handler._json(200, {"slug": slug, "knowledge": text, "ok": True})


# --------- /api/account/knowledge ---------

def run_get_account_knowledge(handler) -> None:
    uid = resolve_user_id(handler)
    if not uid:
        handler._json(401, {"error": "authentication required"}); return
    handler._json(200, {"knowledge": _knowledge.load_account_knowledge(_output_dir(), uid)})


def run_put_account_knowledge(handler) -> None:
    uid = resolve_user_id(handler)
    if not uid:
        handler._json(401, {"error": "authentication required"}); return
    body = _read_body(handler)
    if body is None:
        return
    text = (body.get("knowledge") or "").strip()[:MAX]
    try:
        _knowledge.save_account_knowledge(_output_dir(), uid, text)
    except Exception as e:
        handler._json(500, {"error": f"could not save: {e}"}); return
    handler._json(200, {"knowledge": text, "ok": True})
