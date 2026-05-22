"""POST /api/brand-extract — brand / inspiration extraction with optional images.

Accepts two content types:

- ``application/json`` — ``{ url, mode, use_cache? }`` — existing JSON path,
  no images.  Behaviour identical to the old /api/inspire endpoint for callers
  that don't need vision.

- ``multipart/form-data`` — fields: ``url``, ``mode``, ``use_cache`` (opt),
  plus up to **5** ``images[]`` file parts.  Each image is validated for MIME
  type and size before being forwarded to :func:`pebble.brand_extract.extract_brand`.

Limits (multipart path):
    - Per-file:  10 MB decoded
    - Total payload: 60 MB (Content-Length gate)
    - Image count: max 5
    - Allowed MIME: image/png, image/jpeg, image/webp, image/gif, image/svg+xml

Rate-limited — same 6-burst / 1-per-minute-per-IP limiter as /api/inspire.
"""
from __future__ import annotations

import email.parser
import email.policy
import io
import json
from typing import Optional

from pebble.brand_extract import extract_brand
from pebble.security import client_ip, inspire_fetch_limiter


# ---- Constants ---------------------------------------------------------------

_IMAGE_MIME_ALLOWLIST = frozenset({
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
    "image/svg+xml",
})

_MAX_IMAGE_BYTES = 10 * 1024 * 1024   # 10 MB per file
_MAX_TOTAL_BYTES = 60 * 1024 * 1024   # 60 MB total payload
_MAX_IMAGES = 5


# ---- Multipart parsing -------------------------------------------------------

def _parse_multipart(
    raw_body: bytes,
    content_type_header: str,
) -> tuple[dict, list[tuple[str, bytes]], Optional[str]]:
    """Parse a multipart/form-data body.

    Returns ``(fields, images, error)`` where:
    - ``fields`` is a dict of non-file form fields (str → str).
    - ``images`` is a list of ``(mime_type, bytes)`` pairs.
    - ``error`` is set on validation failure; caller sends 400.

    Uses the stdlib ``email`` package which understands MIME multipart —
    the same toolkit used for email attachments.  We prepend a synthetic
    Content-Type header so the library can locate the boundary.
    """
    # email.parser expects a full MIME message with headers. We synthesise
    # one by prepending the Content-Type and a blank line before the body.
    synthetic = (
        f"Content-Type: {content_type_header}\r\n"
        f"MIME-Version: 1.0\r\n"
        f"\r\n"
    ).encode("latin-1") + raw_body

    parser = email.parser.BytesParser(policy=email.policy.compat32)
    msg = parser.parsebytes(synthetic)

    if not msg.is_multipart():
        return {}, [], "expected multipart/form-data body"

    fields: dict[str, str] = {}
    images: list[tuple[str, bytes]] = []

    for part in msg.get_payload():  # type: ignore[union-attr]
        content_disp = part.get("Content-Disposition", "")
        # Parse name= from Content-Disposition
        name = _parse_param(content_disp, "name")
        if name is None:
            continue

        filename = _parse_param(content_disp, "filename")
        raw = part.get_payload(decode=True) or b""

        if filename is not None or name == "images[]":
            # Treat as file upload.
            if len(images) >= _MAX_IMAGES:
                return {}, [], f"too many images; max {_MAX_IMAGES}"

            mime = (part.get_content_type() or "").lower().strip()
            if mime not in _IMAGE_MIME_ALLOWLIST:
                return {}, [], (
                    f"unsupported image MIME type: {mime!r}. "
                    f"Allowed: {sorted(_IMAGE_MIME_ALLOWLIST)}"
                )

            if len(raw) > _MAX_IMAGE_BYTES:
                return {}, [], (
                    f"image too large; max {_MAX_IMAGE_BYTES // (1024 * 1024)} MB per file"
                )

            images.append((mime, raw))
        else:
            # Plain text field.
            try:
                val = raw.decode("utf-8", errors="replace") if raw else ""
            except Exception:
                val = ""
            fields[name] = val

    return fields, images, None


def _parse_param(header_value: str, param: str) -> Optional[str]:
    """Extract ``param="value"`` from a header like Content-Disposition.

    Returns the value (without quotes) or None if not present.
    Handles both quoted and unquoted forms.
    """
    lower = header_value.lower()
    key = param + "="
    idx = lower.find(key)
    if idx == -1:
        return None
    after = header_value[idx + len(key):]
    if after.startswith('"'):
        end = after.find('"', 1)
        return after[1:end] if end != -1 else after[1:]
    # Unquoted — up to the next semicolon or whitespace.
    end = 0
    while end < len(after) and after[end] not in (' ', '\t', ';', '\r', '\n'):
        end += 1
    return after[:end] or None


# ---- Request handler ---------------------------------------------------------

def run_brand_extract(handler) -> None:
    """POST /api/brand-extract.

    Accepts JSON or multipart/form-data.  Delegates to
    :func:`pebble.brand_extract.extract_brand`.
    """
    ip = client_ip(handler)
    if not inspire_fetch_limiter.allow(ip or ""):
        handler._json(429, {"error": "too many requests; try again in a minute"})
        return

    content_type = (handler.headers.get("Content-Type") or "").lower().strip()
    is_multipart = content_type.startswith("multipart/form-data")

    # ---- Read raw body -------------------------------------------------------
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return

    if length > _MAX_TOTAL_BYTES:
        handler._json(413, {
            "error": f"payload too large; max {_MAX_TOTAL_BYTES // (1024 * 1024)} MB"
        }); return

    if length <= 0 and not is_multipart:
        handler._json(400, {"error": "empty request body"}); return

    raw_body = handler.rfile.read(length) if length > 0 else b""

    # ---- Parse ---------------------------------------------------------------
    url: str = ""
    mode: str = "brand"
    images: list[tuple[str, bytes]] = []

    if is_multipart:
        # Strip the leading "content-type: " text — we need just the header value.
        ct_header = handler.headers.get("Content-Type") or ""
        fields, images, err = _parse_multipart(raw_body, ct_header)
        if err:
            handler._json(400, {"error": err}); return
        url = fields.get("url", "")
        mode = fields.get("mode", "brand")
    else:
        # JSON path — keep existing behaviour.
        try:
            body = json.loads(raw_body.decode("utf-8"))
        except Exception:
            handler._json(400, {"error": "invalid JSON"}); return
        if not isinstance(body, dict):
            handler._json(400, {"error": "body must be a JSON object"}); return
        url = str(body.get("url") or "")
        mode = str(body.get("mode") or "brand")

    # mode validation
    if mode not in ("brand", "inspire"):
        mode = "brand"

    # ---- Run extraction ------------------------------------------------------
    result = extract_brand(url, mode, inspiration_images=images or None)

    handler._json(200, {
        "url":           result.url,
        "mode":          result.mode,
        "extract":       result.to_dict(),
        "brief_partial": result.to_brief_partial(),
        "ok":            result.error is None,
        "error":         result.error,
    })
