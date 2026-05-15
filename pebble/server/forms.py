"""HTTP endpoints for the form-inbox flow.

Public (form submitter facing):

- POST /api/forms/<slug>                          — accept a submission

User-scoped (dashboard inbox):

- GET    /api/projects/<slug>/inbox               — list submissions
- GET    /api/projects/<slug>/inbox/<id>          — read one submission
- PATCH  /api/projects/<slug>/inbox/<id>          — mark read/unread
- DELETE /api/projects/<slug>/inbox/<id>          — delete a submission
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from pebble.forms import (
    HONEYPOT_FIELD,
    MAX_PAYLOAD_BYTES,
    FormError,
    delete_submission,
    get_submission,
    is_honeypot_trip,
    list_submissions,
    save_submission,
    update_submission,
)
from pebble.log import log


def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


def _safe_slug(slug: str) -> bool:
    return bool(slug) and "/" not in slug and "\\" not in slug and ".." not in slug


def _read_body(handler, *, max_bytes: int) -> Optional[dict]:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return None
    if length <= 0:
        return {}
    if length > max_bytes:
        handler._json(413, {"error": "request too large"}); return None
    try:
        return json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return None


def _client_ip(handler) -> Optional[str]:
    """Best-effort client IP. Honors X-Forwarded-For when present (single
    hop only; multi-hop chains are not unwrapped — that needs a trust
    config we don't have yet)."""
    fwd = handler.headers.get("X-Forwarded-For")
    if fwd:
        return fwd.split(",", 1)[0].strip() or None
    try:
        return handler.client_address[0]
    except Exception:
        return None


# --------- POST /api/forms/<slug> (public) -------------------------------

def run_submit(handler, slug: str) -> None:
    """Accept a form submission for ``slug``. Honeypot trips return 200
    so bots don't learn the trick."""
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    project_dir = _output_dir() / slug
    if not project_dir.exists():
        handler._json(404, {"error": "project not found"}); return

    body = _read_body(handler, max_bytes=MAX_PAYLOAD_BYTES)
    if body is None:
        return

    # Honeypot — silently accept (200 ok, but nothing recorded)
    if is_honeypot_trip(body):
        handler._json(200, {"ok": True}); return

    ip = _client_ip(handler)
    ua = handler.headers.get("User-Agent")
    ref = handler.headers.get("Referer")
    try:
        rec = save_submission(slug, body, ip=ip, user_agent=ua, referrer=ref)
    except FormError as e:
        handler._json(400, {"error": str(e)}); return
    except Exception as e:
        log.warning("form submit failed for %s: %s", slug, e)
        handler._json(500, {"error": "submit failed"}); return

    # Always echo a stable shape — the form template doesn't care about
    # the inbox id but knowing the submission was accepted is enough.
    handler._json(200, {"ok": True, "id": rec.id})


# --------- GET /api/projects/<slug>/inbox -------------------------------

def run_list_inbox(handler, slug: str) -> None:
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    if not (_output_dir() / slug).exists():
        handler._json(404, {"error": "project not found"}); return
    items = list_submissions(slug)
    unread = sum(1 for r in items if not r.get("read"))
    handler._json(200, {
        "slug":         slug,
        "submissions":  items,
        "count":        len(items),
        "unread":       unread,
    })


# --------- GET /api/projects/<slug>/inbox/<id> --------------------------

def run_get_inbox_item(handler, slug: str, sub_id: str) -> None:
    if not _safe_slug(slug) or not _safe_slug(sub_id):
        handler._json(400, {"error": "invalid"}); return
    rec = get_submission(slug, sub_id)
    if not rec:
        handler._json(404, {"error": "submission not found"}); return
    handler._json(200, rec)


# --------- POST /api/projects/<slug>/inbox/<id>/read -------------------

def run_mark_read(handler, slug: str, sub_id: str) -> None:
    """Idempotent mark-as-read. Body: `{ read: bool }` (default true)."""
    if not _safe_slug(slug) or not _safe_slug(sub_id):
        handler._json(400, {"error": "invalid"}); return
    body = _read_body(handler, max_bytes=1024) or {}
    requested = body.get("read")
    flag = bool(requested) if isinstance(requested, bool) else True
    rec = update_submission(slug, sub_id, {"read": flag})
    if not rec:
        handler._json(404, {"error": "submission not found"}); return
    handler._json(200, rec)


# --------- DELETE /api/projects/<slug>/inbox/<id> ----------------------

def run_delete_inbox_item(handler, slug: str, sub_id: str) -> None:
    if not _safe_slug(slug) or not _safe_slug(sub_id):
        handler._json(400, {"error": "invalid"}); return
    if not delete_submission(slug, sub_id):
        handler._json(404, {"error": "submission not found"}); return
    handler._json(200, {"slug": slug, "id": sub_id, "deleted": True})
