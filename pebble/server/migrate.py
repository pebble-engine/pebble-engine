"""POST /api/migrate — pull facts from an existing public URL.

The handler is intentionally thin: it validates the URL, calls
:func:`pebble.migrate.extract_from_url`, and returns both the raw
extraction and a partial-brief shape the v3 UI can use to pre-fill the
intake form.

Errors that come back from extract_from_url are reported as 200 with
``error`` set — the UI can still render whatever we got. We only return
4xx on input validation failures (missing URL, malformed JSON).
"""
from __future__ import annotations

import json
from urllib.parse import urlparse

from pebble.migrate import extract_from_url


def _is_plausible_http_url(value: str) -> bool:
    """Cheap sanity check — true if the input looks like a URL we can
    reasonably try to fetch. We're permissive on missing scheme."""
    if not value or not isinstance(value, str):
        return False
    value = value.strip()
    if not value:
        return False
    if " " in value:
        return False
    parsed = urlparse(value if "://" in value else f"https://{value}")
    return bool(parsed.netloc)


def run_migrate(handler) -> None:
    """POST /api/migrate. Body: ``{ url }``.

    Response:
        {
          "url":             "<input>",
          "extract":         { ...MigrationExtract.to_dict() },
          "brief_partial":   { business_name, business_type, extra_context, _migrated_from },
          "ok":              true | false,
          "error":           "..." | null
        }
    """
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return
    if length <= 0:
        handler._json(400, {"error": "empty request body"}); return
    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return

    url = (body or {}).get("url")
    if not _is_plausible_http_url(url):
        handler._json(400, {"error": "url is required"}); return

    extract = extract_from_url(url)
    handler._json(200, {
        "url":           url,
        "extract":       extract.to_dict(),
        "brief_partial": extract.to_brief_partial(),
        "ok":            extract.error is None,
        "error":         extract.error,
    })
