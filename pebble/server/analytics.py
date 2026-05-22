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
from pebble.security import (
    client_ip as _client_ip,
    require_project_owner,
    track_view_limiter,
)


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


def run_track(handler, slug: str) -> None:
    """Record a page view. Body: ``{ path?: "/about", referrer?: "..." }``.
    Always returns 200 (even on cap-hit or rate-limit) so analytics
    never breaks the user's site if Pebble is down or rate-limiting.
    """
    if not _safe_slug(slug):
        handler._json(200, {"ok": True, "recorded": False}); return
    if not (_output_dir() / slug).exists():
        handler._json(200, {"ok": True, "recorded": False}); return

    ip = _client_ip(handler)
    if ip and not track_view_limiter.allow(f"track:{ip}:{slug}"):
        # Rate-limited — still a 200 so the page load stays clean.
        handler._json(200, {"ok": True, "recorded": False}); return

    body = _read_body(handler) or {}
    path = body.get("path") or "/"
    referrer = body.get("referrer") or handler.headers.get("Referer")
    ua = handler.headers.get("User-Agent")
    ok = record_page_view(slug, path=path, ip=ip, user_agent=ua, referrer=referrer)
    handler._json(200, {"ok": True, "recorded": bool(ok)})


def run_get_summary(handler, slug: str) -> None:
    """Owner-facing analytics summary for the last 7 days. Requires the
    caller to own the project AND be on a plan that includes analytics
    (Phase 54a: Pro+ only)."""
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    caller_uid = require_project_owner(handler, slug)
    if caller_uid is None:
        return

    # Phase 54a — site analytics is a Pro-tier feature. Free / Starter
    # see the v3 nav item but get a 402 + upgrade prompt instead of the
    # summary payload. Tracking endpoints (POST /api/track/<slug>) stay
    # OPEN so generated sites keep recording — the gate is on READING
    # the summary, not collecting the data.
    from pebble.user_plan import gate_response, get_user_plan, has_feature
    if not has_feature(caller_uid, "site_analytics"):
        handler._json(402, gate_response(
            feature_label="Site analytics",
            required_plan="pro",
            current_plan=get_user_plan(caller_uid),
        ))
        return

    handler._json(200, summarize(slug, days=7))
