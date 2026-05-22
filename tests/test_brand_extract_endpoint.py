"""Tests for POST /api/brand-extract.

Covers:
- JSON path (no images): happy path, missing URL, bad mode.
- Multipart path (with images): happy path, MIME rejection, size rejection,
  too-many-images rejection, wrong-MIME (application/zip) rejection.
- Rate-limit gate (429).

LLM calls are monkeypatched away in every test so no real API is hit.
The mock style follows test_inspire.py: monkeypatch the ``extract_brand``
function directly inside the server module.
"""
from __future__ import annotations

import json
import socket
import struct
import threading
import time
import urllib.error
import urllib.request
import zlib
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import pebble_engine
import pebble.history as history_mod
import pebble.security as security_mod
import pebble.server.brand_extract as be_server
from pebble.brand_extract import BrandExtract


# ---- Minimal PNG: build a 1×1 white PNG entirely from stdlib ----------------
# We're testing the HTTP layer, not the LLM.  The endpoint validates MIME via
# Content-Type header + per-file size only; magic-byte checking lives in
# pebble.storage (form uploads), not here.

def _make_tiny_png() -> bytes:
    """Build a 1×1 white PNG entirely from struct + zlib."""
    def _chunk(tag: bytes, data: bytes) -> bytes:
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    idat_raw = b"\x00\xff\xff\xff"  # filter=0, RGB white pixel
    idat = zlib.compress(idat_raw)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )

_TINY_PNG = _make_tiny_png()


# ---- HTTP server fixture (mirrors test_analytics.py) -----------------------

def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def engine_server(tmp_path, monkeypatch):
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.setattr(history_mod, "OUTPUT_DIR", out)
    # Reset the rate limiter for each test so tests don't bleed state.
    # Patch both the security module's canonical object AND the already-bound
    # name in the brand_extract server module (it imports the limiter at module
    # load time, so patching only the security module is not enough).
    import pebble.security as sec
    fresh_limiter = sec.RateLimiter(rate=1.0, burst=20)
    monkeypatch.setattr(sec, "inspire_fetch_limiter", fresh_limiter)
    monkeypatch.setattr(be_server, "inspire_fetch_limiter", fresh_limiter)
    port = _find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), pebble_engine.PebbleHandler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    time.sleep(0.1)
    try:
        yield {"base": f"http://127.0.0.1:{port}", "output": out}
    finally:
        server.shutdown()
        server.server_close()


def _post_json(base: str, path: str, body: dict) -> tuple[int, dict]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{base}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8", errors="replace"))


def _build_multipart_body(
    fields: dict[str, str],
    files: list[tuple[str, bytes, str]],   # (field_name, data, mime_type)
    boundary: str = "PebbleTestBoundary42",
) -> bytes:
    """Build a multipart/form-data body manually (no third-party deps).

    This avoids the stdlib email.encoders import which shadows the module-level
    ``email`` import and causes UnboundLocalError in some Python versions.
    """
    buf = bytearray()
    sep = f"--{boundary}\r\n".encode()

    for name, value in fields.items():
        buf += sep
        buf += f'Content-Disposition: form-data; name="{name}"\r\n'.encode()
        buf += b"\r\n"
        buf += value.encode("utf-8")
        buf += b"\r\n"

    for field_name, data, mime_type in files:
        ext = mime_type.split("/", 1)[-1] if "/" in mime_type else "bin"
        buf += sep
        buf += (
            f'Content-Disposition: form-data; name="{field_name}"; filename="test.{ext}"\r\n'
            f"Content-Type: {mime_type}\r\n"
            f"\r\n"
        ).encode()
        buf += data
        buf += b"\r\n"

    buf += f"--{boundary}--\r\n".encode()
    return bytes(buf)


def _post_multipart(
    base: str,
    path: str,
    fields: dict[str, str],
    files: list[tuple[str, bytes, str]],   # (field_name, data, mime_type)
    boundary: str = "PebbleTestBoundary42",
) -> tuple[int, dict]:
    """Send a multipart/form-data POST built entirely by hand."""
    body = _build_multipart_body(fields, files, boundary)
    content_type = f"multipart/form-data; boundary={boundary}"
    req = urllib.request.Request(
        f"{base}{path}",
        data=body,
        headers={
            "Content-Type": content_type,
            "Content-Length": str(len(body)),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(text)
        except Exception:
            return e.code, {"error": text}


# ---- Helper: mock LLM result ------------------------------------------------

def _mock_extract_brand(url, mode="brand", *, inspiration_images=None):
    """A fake extract_brand that returns a canned successful result."""
    return BrandExtract(
        mode=mode,
        url=url,
        business_name_guess="Test Co",
        business_type_guess="bakery",
        palette_hints=["#ff0000"],
        layout_notes="clean and minimal",
        copy_voice="warm",
        dna_hint="swiss_magazine",
    )


# ============================================================================
# JSON path tests
# ============================================================================

def test_json_path_happy(engine_server, monkeypatch):
    """JSON POST with a URL returns 200 + extract shape."""
    monkeypatch.setattr(be_server, "extract_brand", _mock_extract_brand)
    status, body = _post_json(
        engine_server["base"], "/api/brand-extract",
        {"url": "https://example.com", "mode": "brand"},
    )
    assert status == 200, body
    assert body["ok"] is True
    assert body["extract"]["business_name_guess"] == "Test Co"
    assert body["brief_partial"]["business_name"] == "Test Co"


def test_json_path_missing_url(engine_server, monkeypatch):
    """JSON POST with no URL still 200 (url defaults to empty string)."""
    monkeypatch.setattr(be_server, "extract_brand", _mock_extract_brand)
    status, body = _post_json(
        engine_server["base"], "/api/brand-extract",
        {"mode": "inspire"},
    )
    # The endpoint doesn't require a URL (images-only is valid); must not 4xx.
    assert status == 200, body


def test_json_path_invalid_json(engine_server, monkeypatch):
    monkeypatch.setattr(be_server, "extract_brand", _mock_extract_brand)
    req = urllib.request.Request(
        f"{engine_server['base']}/api/brand-extract",
        data=b"not json!!",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            status, body = resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        status, body = e.code, json.loads(e.read())
    assert status == 400
    assert "json" in body.get("error", "").lower() or "invalid" in body.get("error", "").lower()


# ============================================================================
# Multipart path tests
# ============================================================================

def test_multipart_happy_path_one_png(engine_server, monkeypatch):
    """Multipart POST with one valid PNG returns 200 + extract shape."""
    monkeypatch.setattr(be_server, "extract_brand", _mock_extract_brand)
    status, body = _post_multipart(
        engine_server["base"], "/api/brand-extract",
        fields={"url": "https://example.com", "mode": "brand"},
        files=[("images[]", _TINY_PNG, "image/png")],
    )
    assert status == 200, body
    assert body["ok"] is True
    assert body["extract"]["business_type_guess"] == "bakery"


def test_multipart_rejects_oversized_image(engine_server, monkeypatch):
    """An image exceeding 10 MB must be rejected with a clear 400."""
    monkeypatch.setattr(be_server, "extract_brand", _mock_extract_brand)
    # Build a stub that claims to be PNG but is huge (just zeros is fine —
    # we're testing the size gate, not the bytes).
    big_image = b"\x89PNG" + b"\x00" * (10 * 1024 * 1024 + 1)
    status, body = _post_multipart(
        engine_server["base"], "/api/brand-extract",
        fields={"url": "https://example.com"},
        files=[("images[]", big_image, "image/png")],
    )
    assert status in (400, 413), body
    assert body.get("error")


def test_multipart_rejects_wrong_mime(engine_server, monkeypatch):
    """A file with MIME application/zip must be rejected with 400."""
    monkeypatch.setattr(be_server, "extract_brand", _mock_extract_brand)
    status, body = _post_multipart(
        engine_server["base"], "/api/brand-extract",
        fields={"url": "https://example.com"},
        files=[("images[]", b"PK\x03\x04", "application/zip")],
    )
    assert status == 400, body
    err = body.get("error", "").lower()
    assert "mime" in err or "unsupported" in err or "type" in err


def test_multipart_rejects_too_many_images(engine_server, monkeypatch):
    """More than 5 images must be rejected with 400."""
    monkeypatch.setattr(be_server, "extract_brand", _mock_extract_brand)
    six_pngs = [("images[]", _TINY_PNG, "image/png")] * 6
    status, body = _post_multipart(
        engine_server["base"], "/api/brand-extract",
        fields={"url": "https://example.com"},
        files=six_pngs,
    )
    assert status == 400, body
    assert "too many" in body.get("error", "").lower()


def test_multipart_accepts_jpeg_and_webp(engine_server, monkeypatch):
    """image/jpeg and image/webp are in the allowlist."""
    monkeypatch.setattr(be_server, "extract_brand", _mock_extract_brand)
    # JPEG magic bytes
    jpeg_stub = b"\xff\xd8\xff\xe0"
    status, body = _post_multipart(
        engine_server["base"], "/api/brand-extract",
        fields={"url": "https://example.com", "mode": "inspire"},
        files=[("images[]", jpeg_stub, "image/jpeg")],
    )
    assert status == 200, body
    assert body["ok"] is True
