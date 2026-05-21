"""Brand-extract endpoint — Phase 33b (2026-05-21).

POST /api/brand-extract
Body: { url: str }
Returns: see pebble/brand_extract.extract_brand() for the full shape.

Public endpoint (no auth) because it runs BEFORE signup — it's how a
prospect's first interaction with Pebble starts. The user pastes a URL,
gets a pre-filled questionnaire, then maybe signs up.

Rate limiting: shares the cheap "plan_limiter" bucket with /api/plan.
Brand extraction does at most one outbound HTTP fetch + one cheap LLM
call (~$0.0001). Cache TTL is 1 hour so a refresh of the same URL is
near-free.

Failure mode: the endpoint NEVER 500s on a bad input URL. extract_brand()
returns an `ok: False` payload with `error` populated; we surface that
to the frontend as a 200 (so the v3 form can decide whether to fall
back to free-text). True server errors (rate limit, malformed body) get
4xx as usual.
"""
from __future__ import annotations

import json

from pebble.brand_extract import extract_brand
from pebble.log import log
from pebble.security import client_ip, plan_limiter


# Tight body cap — we only need {url: str}. 4 KB is generous.
_MAX_BODY_BYTES = 4096


def run_brand_extract(handler) -> None:
    """POST /api/brand-extract"""
    ip = client_ip(handler)
    if not plan_limiter.allow(ip or ""):
        handler._json(429, {"error": "too many requests — try again in a moment"})
        return

    # Read + parse body
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"})
        return
    if length <= 0 or length > _MAX_BODY_BYTES:
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

    url = body.get("url")
    if not isinstance(url, str) or not url.strip():
        handler._json(400, {"error": "url is required"})
        return

    # Phase 38a — mode flag. "brand" (default) extracts business facts;
    # "inspire" extracts style vocabulary + matches a DNA card. Any other
    # value silently falls back to "brand" so a stale client can't 400 us.
    mode_raw = body.get("mode", "brand")
    mode = mode_raw if isinstance(mode_raw, str) and mode_raw in ("brand", "inspire") else "brand"

    # Optional flag — power users can force a refresh
    use_cache = bool(body.get("use_cache", True))

    try:
        result = extract_brand(url, mode=mode, use_cache=use_cache)
    except Exception as e:  # extract_brand promises never to raise, but belt-and-suspenders
        log.error("[brand-extract] unexpected exception: %s", e)
        handler._json(500, {"error": "extraction failed unexpectedly"})
        return

    handler._json(200, result)
