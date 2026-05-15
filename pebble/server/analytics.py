"""HTTP endpoints for first-party privacy analytics.

- POST /api/track/<slug>                         — record a page view (public)
- GET  /api/projects/<slug>/analytics            — owner-facing summary
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from pebble.analytics import record_page_view, summarize


def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


def _safe_slug(slug: str) -> bool:
    return bool(slug) and "/" not in slug and "\\" not in slug and ".." not in slug


def _read_body(handler, max_bytes: int = 2048) -> Optional[dict]:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length"}); return None
    if length <= 0:
        return {}
    if length > max_bytes:
        handler._json(413, {"error": "too large"}); return None
    try:
        return json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return None


def _client_ip(handler) -> Optional[str]:
    fwd = handler.headers.get("X-Forwarded-For")
    if fwd:
        return fwd.split(",", 1)[0].strip() or None
    try:
        return handler.client_address[0]
    except Exception:
        return None


def run_track(handler, slug: str) -> None:
    """Record a page view. Body: ``{ path?: "/about", referrer?: "..." }``.
    Always returns 200 (even on cap-hit) so analytics never breaks the
    user's site if Pebble is down or rate-limiting."""
    if not _safe_slug(slug):
        handler._json(200, {"ok": True, "recorded": False}); return
    if not (_output_dir() / slug).exists():
        handler._json(200, {"ok": True, "recorded": False}); return

    body = _read_body(handler) or {}
    path = body.get("path") or "/"
    referrer = body.get("referrer") or handler.headers.get("Referer")
    ua = handler.headers.get("User-Agent")
    ip = _client_ip(handler)
    ok = record_page_view(slug, path=path, ip=ip, user_agent=ua, referrer=referrer)
    handler._json(200, {"ok": True, "recorded": bool(ok)})


def run_get_summary(handler, slug: str) -> None:
    """Owner-facing analytics summary for the last 7 days."""
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    if not (_output_dir() / slug).exists():
        handler._json(404, {"error": "project not found"}); return
    handler._json(200, summarize(slug, days=7))
