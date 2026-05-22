"""Brand-extract endpoint — Phase 33b (2026-05-21).

POST /api/brand-extract
Body: { url: str }  — JSON path (no images)
  OR multipart/form-data with fields:
    url           str
    mode          str ("brand" | "inspire", default "brand")
    use_cache     str ("true" | "false", default "true")
    images[]      up to 5 image files (PNG/JPEG/WebP/GIF/SVG), each ≤ 10 MB,
                  total payload ≤ 60 MB

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

import email.parser
import io
import json

from pebble.brand_extract import extract_brand
from pebble.log import log
from pebble.security import client_ip, plan_limiter


# Tight body cap — JSON path: {url: str}. 4 KB is generous.
_MAX_JSON_BODY_BYTES = 4096

# Multipart limits
_MAX_IMAGES           = 5
_MAX_IMAGE_BYTES      = 10 * 1024 * 1024   # 10 MB per image
_MAX_MULTIPART_BYTES  = 60 * 1024 * 1024   # 60 MB total payload

# MIME types accepted as inspiration images
_ALLOWED_MIME = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
    "image/svg+xml",
}

# Magic-byte signatures for the binary image types (SVG is text — no magic)
_MAGIC_BYTES: dict[bytes, str] = {
    b"\x89PNG":       "image/png",
    b"\xff\xd8\xff":  "image/jpeg",
    b"RIFF":          "image/webp",   # RIFF....WEBP — checked below
    b"GIF8":          "image/gif",
}


def _check_magic(data: bytes, claimed_mime: str) -> bool:
    """Return True if the magic bytes are consistent with the claimed MIME type.

    SVG is plain text and has no magic bytes — we skip the check and trust
    the MIME declaration (Content-Type from the multipart part header).
    WebP has RIFF at offset 0 and WEBP at offset 8.
    """
    if claimed_mime == "image/svg+xml":
        return True  # text format; no magic to check

    for magic, mime in _MAGIC_BYTES.items():
        if data.startswith(magic):
            if mime == "image/webp":
                return data[8:12] == b"WEBP"
            return mime == claimed_mime

    return False


def _parse_multipart(handler) -> tuple[dict | None, list[bytes], str | None]:
    """Parse a multipart/form-data request from the handler.

    Returns (fields_dict, image_bytes_list, error_msg_or_None).
    On error, returns (None, [], error_message).

    The handler is a stdlib BaseHTTPRequestHandler instance.
    We use email.parser to decode the MIME parts — same stdlib approach
    the codebase uses elsewhere, no extra deps.
    """
    content_type_header = handler.headers.get("Content-Type", "")
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        return None, [], "invalid Content-Length header"

    if length <= 0:
        return None, [], "missing or empty body"
    if length > _MAX_MULTIPART_BYTES:
        mb = _MAX_MULTIPART_BYTES // (1024 * 1024)
        return None, [], f"total payload exceeds {mb} MB limit"

    raw = handler.rfile.read(length)

    # email.parser expects a complete MIME message. We synthesise the
    # top-level MIME headers so BytesParser can navigate the parts.
    # content_type_header is something like:
    #   multipart/form-data; boundary=----WebKitFormBoundary...
    mime_message = (
        f"MIME-Version: 1.0\r\n"
        f"Content-Type: {content_type_header}\r\n"
        f"\r\n"
    ).encode() + raw

    parser = email.parser.BytesParser()
    msg = parser.parsebytes(mime_message)

    if not msg.is_multipart():
        return None, [], "body is not multipart — missing boundary?"

    fields: dict[str, str] = {}
    images: list[bytes] = []

    for part in msg.get_payload():  # type: ignore[union-attr]
        disposition = part.get("Content-Disposition", "")
        if not disposition:
            continue

        # Extract name= and filename= from the part's Content-Disposition
        name: str | None = None
        filename: str | None = None
        for token in disposition.split(";"):
            token = token.strip()
            if token.lower().startswith("name="):
                name = token[5:].strip().strip('"')
            elif token.lower().startswith("filename="):
                filename = token[9:].strip().strip('"')

        if name is None:
            continue

        part_bytes: bytes = part.get_payload(decode=True) or b""

        if name == "images[]":
            # Validate count before reading bytes
            if len(images) >= _MAX_IMAGES:
                return None, [], f"too many images — maximum is {_MAX_IMAGES}"

            # Size check per image
            if len(part_bytes) > _MAX_IMAGE_BYTES:
                mb = _MAX_IMAGE_BYTES // (1024 * 1024)
                return None, [], f"image exceeds {mb} MB limit"

            # MIME check — Content-Type from the part header
            part_mime = part.get_content_type() or ""
            if part_mime not in _ALLOWED_MIME:
                return None, [], (
                    f"unsupported image type '{part_mime}'. "
                    f"Allowed: png, jpeg, webp, gif, svg+xml"
                )

            # Magic-byte validation (skip for SVG)
            if part_bytes and not _check_magic(part_bytes, part_mime):
                return None, [], (
                    f"image magic bytes don't match declared type '{part_mime}'"
                )

            images.append(part_bytes)
        else:
            # Regular text field (url, mode, use_cache)
            try:
                fields[name] = part_bytes.decode("utf-8", errors="replace").strip()
            except Exception:
                pass

    return fields, images, None


def run_brand_extract(handler) -> None:
    """POST /api/brand-extract"""
    ip = client_ip(handler)
    if not plan_limiter.allow(ip or ""):
        handler._json(429, {"error": "too many requests — try again in a moment"})
        return

    content_type = handler.headers.get("Content-Type", "")
    is_multipart = "multipart/form-data" in content_type

    if is_multipart:
        # ---- Multipart path (with images) ----------------------------------
        fields, images, err = _parse_multipart(handler)
        if err is not None:
            # Distinguish oversized payload (413) from other parse errors (400).
            # "too many images" is a count violation → 400, not 413.
            status = 413 if "exceeds" in err.lower() else 400
            handler._json(status, {"error": err})
            return

        url = (fields or {}).get("url", "").strip()
        if not url:
            handler._json(400, {"error": "url is required"})
            return

        mode_raw = (fields or {}).get("mode", "brand")
        mode = mode_raw if isinstance(mode_raw, str) and mode_raw in ("brand", "inspire") else "brand"
        use_cache = (fields or {}).get("use_cache", "true").lower() != "false"

        try:
            result = extract_brand(url, mode=mode, use_cache=use_cache,
                                   inspiration_images=images or None)
        except Exception as e:
            log.error("[brand-extract] unexpected exception (multipart): %s", e)
            handler._json(500, {"error": "extraction failed unexpectedly"})
            return

        handler._json(200, result)
        return

    # ---- JSON path (no images) ---------------------------------------------
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"})
        return
    if length <= 0 or length > _MAX_JSON_BODY_BYTES:
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
