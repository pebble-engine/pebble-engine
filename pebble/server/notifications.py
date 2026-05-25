"""Notifications endpoint — bell badge feed (2026-05-24).

  GET  /api/notifications              → recent events for the user
  POST /api/notifications/<id>/read    → mark one event as read
  POST /api/notifications/read-all     → mark every unread as read

Auth-gated. Reads from pebble.events which is backed by Supabase.
When Supabase isn't configured (local dev with no creds) every list
returns []; the bell renders its hardcoded seed instead so the UI
never goes blank.
"""
from __future__ import annotations

import json

from pebble import events
from pebble.log import log
from pebble.security import client_ip, plan_limiter, resolve_user_id, validate_slug


def run_list_notifications(handler) -> None:
    """GET /api/notifications

    Returns: { notifications: [...], unread_count: int }
    """
    uid = resolve_user_id(handler)
    if not uid:
        handler._json(401, {"error": "sign in required"}); return

    ip = client_ip(handler)
    if not plan_limiter.allow(ip or ""):
        handler._json(429, {"error": "slow down"}); return

    items = events.list_user_all(uid, limit=20)
    unread = sum(1 for i in items if not i.get("is_read"))
    handler._json(200, {
        "notifications": items,
        "unread_count":  unread,
    })


def run_mark_read(handler, event_id: str) -> None:
    """POST /api/notifications/<event_id>/read"""
    uid = resolve_user_id(handler)
    if not uid:
        handler._json(401, {"error": "sign in required"}); return

    # UUID shape check — drops obvious garbage before the round-trip.
    if not _looks_like_uuid(event_id):
        handler._json(400, {"error": "invalid event_id"}); return

    ok = events.mark_read(uid, event_id)
    handler._json(200 if ok else 500, {"ok": ok})


def run_mark_all_read(handler) -> None:
    """POST /api/notifications/read-all"""
    uid = resolve_user_id(handler)
    if not uid:
        handler._json(401, {"error": "sign in required"}); return

    count = events.mark_all_read(uid)
    handler._json(200, {"ok": True, "marked": count})


def _looks_like_uuid(s: str) -> bool:
    """36 chars, 4 dashes, hex elsewhere. Cheap pre-validation so we
    don't pass a SQL injection attempt to PostgREST (which would
    reject it but still bills the round-trip)."""
    if not isinstance(s, str) or len(s) != 36:
        return False
    if s.count("-") != 4:
        return False
    return all(c in "0123456789abcdef-" for c in s.lower())


__all__ = ["run_list_notifications", "run_mark_read", "run_mark_all_read"]
