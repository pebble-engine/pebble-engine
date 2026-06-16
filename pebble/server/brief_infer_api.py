"""POST /api/brief-infer — fast heuristic pre-fill for confirm screen."""
from __future__ import annotations

import json

from pebble.brief_infer import infer_brief
from pebble.security import client_ip, plan_limiter


_MAX_BODY = 4096


def run_brief_infer(handler) -> None:
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

    raw = body.get("raw_prompt") or body.get("prompt") or ""
    if not isinstance(raw, str) or not raw.strip():
        handler._json(400, {"error": "raw_prompt required"})
        return

    intent = body.get("intent", "business")
    result = infer_brief(raw.strip(), intent=str(intent))
    if not result.get("ok"):
        handler._json(400, {"error": result.get("error", "infer failed")})
        return
    handler._json(200, result)
