"""POST /api/brief-compose — hidden merge after user confirms (not shown in UI)."""
from __future__ import annotations

import json

from pebble.brief_compose import compose_brief
from pebble.security import client_ip, plan_limiter


_MAX_BODY = 16384


def run_brief_compose(handler) -> None:
    ip = client_ip(handler)
    if not plan_limiter.allow(ip or ""):
        handler._json(429, {"error": "too many requests — try again in a moment"})
        return

    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"})
        return
    if length <= 0 or length > _MAX_BODY:
        handler._json(400, {"error": "missing or oversized body"})
        return

    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"})
        return

    if not isinstance(body, dict):
        handler._json(400, {"error": "body must be a json object"})
        return

    result = compose_brief(body)
    if not result.get("ok"):
        handler._json(400, {"error": result.get("error", "compose failed")})
        return

    # Client merges brief_patch silently — never display extra_context in UI.
    handler._json(200, {
        "ok": True,
        "fields_ready": True,
        "compose_source": result.get("compose_source", "template"),
        "brief_patch": result.get("brief_patch", {}),
    })
