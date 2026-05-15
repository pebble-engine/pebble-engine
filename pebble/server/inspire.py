"""POST /api/inspire — extract design DNA from a user-pasted URL.

Mirrors :mod:`pebble.server.migrate` in shape: the handler validates
the URL, calls :func:`pebble.inspire.extract_inspiration`, and returns
both the raw extraction and a partial-brief shape the v3 questionnaire
can use to seed the style direction.

This endpoint fetches arbitrary user-supplied URLs, so it's behind the
same kind of in-memory rate limiter as ``/api/forms`` and
``/api/auth/forgot``: 6 burst, 1/min/IP under sustained pressure.
Without this, an attacker could use the engine as a one-hop SSRF
fetcher for any URL on the public internet (the SSRF-defense in
inspire._fetch_url_safe blocks PRIVATE addresses, but unlimited
public-URL fetches would still let someone abuse the engine's
network/CPU).
"""
from __future__ import annotations

import json
from urllib.parse import urlparse

from pebble.inspire import extract_inspiration
from pebble.security import client_ip, inspire_fetch_limiter


def _is_plausible_http_url(value: str) -> bool:
    """Cheap sanity check — true if the input looks like a URL we can
    reasonably try to fetch. Permissive on missing scheme; the deeper
    SSRF gating happens in inspire._fetch_url_safe."""
    if not value or not isinstance(value, str):
        return False
    value = value.strip()
    if not value or " " in value:
        return False
    parsed = urlparse(value if "://" in value else f"https://{value}")
    return bool(parsed.netloc)


def run_inspire(handler) -> None:
    """POST /api/inspire. Body: ``{ url }``.

    Response 200:
        {
          "url":             "<input>",
          "extract":         { ...InspirationExtract.to_dict() },
          "brief_partial":   { extra_context, _inspired_by, _inspire_dna_hint },
          "ok":              true | false,
          "error":           "..." | null
        }
    Errors: 400 on validation, 429 on rate-limit, 500 on unexpected.
    """
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return
    if length <= 0:
        handler._json(400, {"error": "empty request body"}); return
    if length > 4096:
        # /api/inspire body is just { url } — anything bigger is suspicious
        handler._json(400, {"error": "request body too large"}); return
    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return

    url = (body or {}).get("url")
    if not _is_plausible_http_url(url):
        handler._json(400, {"error": "url is required"}); return

    ip = client_ip(handler)
    if not inspire_fetch_limiter.allow(ip or ""):
        handler._json(429, {"error": "too many inspire requests; try again in a minute"})
        return

    extract = extract_inspiration(url)
    handler._json(200, {
        "url":           url,
        "extract":       extract.to_dict(),
        "brief_partial": extract.to_brief_partial(),
        "ok":            extract.error is None,
        "error":         extract.error,
    })
