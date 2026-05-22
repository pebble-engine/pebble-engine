"""Brand-extract endpoint tests (Phase 33b, 2026-05-21).

Covers request validation + the contract between the HTTP layer and
pebble.brand_extract. Doesn't boot a real server — uses a stub handler
that captures the response (same pattern as the bot_message tests).

The deep extraction behavior lives in pebble.brand_extract and is
covered by test_brand_extract.py — these tests pin the HTTP surface.
"""
from __future__ import annotations

import io
import json
from unittest.mock import patch

import pytest

from pebble.server import brand_extract as endpoint_module


class _StubHandler:
    """Minimal handler stub that mimics the bits run_brand_extract uses.

    Captures the JSON response into .response so tests can assert on
    status code + body.
    """

    def __init__(self, body: bytes, content_length: int | None = None):
        self.headers = {"Content-Length": str(content_length if content_length is not None else len(body))}
        self.rfile = io.BytesIO(body)
        self.client_address = ("127.0.0.1", 12345)
        self.response: tuple[int, dict] | None = None
        # PebbleHandler interface
        self.path = "/api/brand-extract"
        self.command = "POST"

    def _json(self, status: int, payload: dict) -> None:
        self.response = (status, payload)


@pytest.fixture(autouse=True)
def _reset_rate_limit():
    """Reset the plan_limiter bucket between tests so 429s don't bleed across."""
    from pebble.security import plan_limiter
    # Try the public reset() method first; fall back to clearing internal state.
    try:
        plan_limiter.reset()
    except Exception:
        pass
    try:
        plan_limiter._calls.clear()  # type: ignore[attr-defined]
    except Exception:
        pass
    try:
        plan_limiter._buckets.clear()  # type: ignore[attr-defined]
    except Exception:
        pass
    yield
    # Also reset after each test to be safe
    try:
        plan_limiter.reset()
    except Exception:
        pass
    try:
        plan_limiter._buckets.clear()  # type: ignore[attr-defined]
    except Exception:
        pass


# ------------------------------------------------------------------ #
# Request validation                                                   #
# ------------------------------------------------------------------ #


def test_missing_body_returns_400():
    h = _StubHandler(b"", content_length=0)
    endpoint_module.run_brand_extract(h)
    status, payload = h.response
    assert status == 400
    assert "error" in payload


def test_oversized_body_returns_400():
    huge = b'{"url":"' + (b"x" * 5000) + b'"}'
    h = _StubHandler(huge)
    endpoint_module.run_brand_extract(h)
    status, _ = h.response
    assert status == 400


def test_invalid_json_returns_400():
    h = _StubHandler(b"{not valid json")
    endpoint_module.run_brand_extract(h)
    status, payload = h.response
    assert status == 400
    assert "json" in payload["error"].lower()


def test_non_object_body_returns_400():
    h = _StubHandler(b'"just a string"')
    endpoint_module.run_brand_extract(h)
    status, payload = h.response
    assert status == 400


def test_missing_url_returns_400():
    h = _StubHandler(b'{"foo": "bar"}')
    endpoint_module.run_brand_extract(h)
    status, payload = h.response
    assert status == 400
    assert "url" in payload["error"].lower()


def test_empty_url_returns_400():
    h = _StubHandler(b'{"url": ""}')
    endpoint_module.run_brand_extract(h)
    status, payload = h.response
    assert status == 400


def test_url_not_a_string_returns_400():
    h = _StubHandler(b'{"url": 123}')
    endpoint_module.run_brand_extract(h)
    status, _ = h.response
    assert status == 400


def test_invalid_content_length_returns_400():
    h = _StubHandler(b'{"url": "https://example.com"}', content_length=0)
    h.headers["Content-Length"] = "not-a-number"
    endpoint_module.run_brand_extract(h)
    status, _ = h.response
    assert status == 400


# ------------------------------------------------------------------ #
# Happy path                                                          #
# ------------------------------------------------------------------ #


def test_valid_url_calls_extract_brand_and_returns_200():
    fake_result = {
        "url": "https://acme.co",
        "ok": True,
        "error": None,
        "business_name": "Acme",
        "tagline": None,
        "industry": "tech",
        "tone": "professional",
        "palette": ["#3054ff"],
        "logo_url": None,
        "favicon_url": "https://acme.co/favicon.ico",
        "hero_copy": "Hello world",
        "raw_text_sample": "Acme is a company.",
        "source": "fresh",
    }
    h = _StubHandler(b'{"url": "https://acme.co"}')
    with patch.object(endpoint_module, "extract_brand", return_value=fake_result) as mock_ext:
        endpoint_module.run_brand_extract(h)
    status, payload = h.response
    assert status == 200
    assert payload == fake_result
    mock_ext.assert_called_once_with("https://acme.co", mode="brand", use_cache=True)


def test_use_cache_false_is_honored():
    fake_result = {"ok": False, "url": "https://x.com", "error": "fail",
                   "business_name": None, "tagline": None, "industry": None,
                   "tone": None, "palette": [], "logo_url": None,
                   "favicon_url": None, "hero_copy": None, "raw_text_sample": "",
                   "source": "fresh"}
    h = _StubHandler(b'{"url": "https://x.com", "use_cache": false}')
    with patch.object(endpoint_module, "extract_brand", return_value=fake_result) as mock_ext:
        endpoint_module.run_brand_extract(h)
    mock_ext.assert_called_once_with("https://x.com", mode="brand", use_cache=False)


def test_extraction_failure_returns_200_with_ok_false():
    """The endpoint returns 200 even for unreachable URLs — the frontend
    needs the structured `error` field to render a fallback."""
    fail_result = {
        "url": "https://invalid-domain-xyz.test",
        "ok": False,
        "error": "DNS lookup failed",
        "business_name": None, "tagline": None, "industry": None,
        "tone": None, "palette": [], "logo_url": None, "favicon_url": None,
        "hero_copy": None, "raw_text_sample": "", "source": "fresh",
    }
    h = _StubHandler(b'{"url": "https://invalid-domain-xyz.test"}')
    with patch.object(endpoint_module, "extract_brand", return_value=fail_result):
        endpoint_module.run_brand_extract(h)
    status, payload = h.response
    assert status == 200
    assert payload["ok"] is False
    assert payload["error"] == "DNS lookup failed"


def test_unexpected_exception_returns_500():
    h = _StubHandler(b'{"url": "https://acme.co"}')
    with patch.object(endpoint_module, "extract_brand", side_effect=RuntimeError("kaboom")):
        endpoint_module.run_brand_extract(h)
    status, payload = h.response
    assert status == 500
    assert "error" in payload


# ------------------------------------------------------------------ #
# Mode parameter plumbing (Phase 38a)                                 #
# ------------------------------------------------------------------ #


def _make_stub(body_dict: dict) -> "_StubHandler":
    body = json.dumps(body_dict).encode()
    return _StubHandler(body)


def test_endpoint_passes_mode_to_extract_brand():
    """mode="inspire" in body must be forwarded to extract_brand."""
    fake_result = {
        "url": "https://ref-site.com", "ok": True, "error": None,
        "mode": "inspire", "business_name": None, "tagline": None,
        "industry": None, "tone": None, "palette": [], "logo_url": None,
        "favicon_url": None, "hero_copy": None,
        "vibe_keywords": ["dark cinematic"], "font_hints": [],
        "motion_intensity": "high", "layout_density": "spacious",
        "matched_dna": None, "raw_text_sample": "", "source": "fresh",
    }
    h = _make_stub({"url": "https://ref-site.com", "mode": "inspire"})
    with patch.object(endpoint_module, "extract_brand", return_value=fake_result) as mock_ext:
        endpoint_module.run_brand_extract(h)
    mock_ext.assert_called_once_with("https://ref-site.com", mode="inspire", use_cache=True)


def test_endpoint_defaults_to_brand_mode_when_mode_omitted():
    """Body without a mode key → extract_brand called with mode="brand"."""
    fake_result = {
        "url": "https://acme.co", "ok": True, "error": None,
        "mode": "brand", "business_name": "Acme", "tagline": None,
        "industry": "tech", "tone": "professional", "palette": [],
        "logo_url": None, "favicon_url": None, "hero_copy": None,
        "vibe_keywords": [], "font_hints": [], "motion_intensity": None,
        "layout_density": None, "matched_dna": None,
        "raw_text_sample": "", "source": "fresh",
    }
    h = _make_stub({"url": "https://acme.co"})
    with patch.object(endpoint_module, "extract_brand", return_value=fake_result) as mock_ext:
        endpoint_module.run_brand_extract(h)
    mock_ext.assert_called_once_with("https://acme.co", mode="brand", use_cache=True)


def test_endpoint_invalid_mode_falls_back_to_brand():
    """Unrecognised mode string → silently becomes brand."""
    fake_result = {
        "url": "https://acme.co", "ok": True, "error": None,
        "mode": "brand", "business_name": None, "tagline": None,
        "industry": None, "tone": None, "palette": [], "logo_url": None,
        "favicon_url": None, "hero_copy": None,
        "vibe_keywords": [], "font_hints": [], "motion_intensity": None,
        "layout_density": None, "matched_dna": None,
        "raw_text_sample": "", "source": "fresh",
    }
    h = _make_stub({"url": "https://acme.co", "mode": "something_random"})
    with patch.object(endpoint_module, "extract_brand", return_value=fake_result) as mock_ext:
        endpoint_module.run_brand_extract(h)
    mock_ext.assert_called_once_with("https://acme.co", mode="brand", use_cache=True)


def test_endpoint_non_string_mode_falls_back_to_brand():
    """Non-string mode (int, null) → silently becomes brand."""
    fake_result = {
        "url": "https://acme.co", "ok": True, "error": None,
        "mode": "brand", "business_name": None, "tagline": None,
        "industry": None, "tone": None, "palette": [], "logo_url": None,
        "favicon_url": None, "hero_copy": None,
        "vibe_keywords": [], "font_hints": [], "motion_intensity": None,
        "layout_density": None, "matched_dna": None,
        "raw_text_sample": "", "source": "fresh",
    }
    # mode=42
    h = _make_stub({"url": "https://acme.co", "mode": 42})
    with patch.object(endpoint_module, "extract_brand", return_value=fake_result) as mock_ext:
        endpoint_module.run_brand_extract(h)
    mock_ext.assert_called_once_with("https://acme.co", mode="brand", use_cache=True)

    # mode=null (None in Python / null in JSON)
    h2 = _make_stub({"url": "https://acme.co", "mode": None})
    with patch.object(endpoint_module, "extract_brand", return_value=fake_result) as mock_ext2:
        endpoint_module.run_brand_extract(h2)
    mock_ext2.assert_called_once_with("https://acme.co", mode="brand", use_cache=True)


def test_endpoint_returns_inspire_mode_payload_through():
    """The endpoint must pass the inspire result dict through to _json unchanged."""
    inspire_result = {
        "url": "https://ref-site.com", "ok": True, "error": None,
        "mode": "inspire", "business_name": None, "tagline": None,
        "industry": None, "tone": None, "palette": ["#1a1a2e"],
        "logo_url": None, "favicon_url": "https://ref-site.com/favicon.ico",
        "hero_copy": None,
        "vibe_keywords": ["dark cinematic", "editorial"],
        "font_hints": ["serif display"],
        "motion_intensity": "high", "layout_density": "spacious",
        "matched_dna": {"id": "cinematic_imax", "label": "Cinematic IMAX",
                        "feel": "Widescreen drama", "confidence": 0.87},
        "raw_text_sample": "Welcome.", "source": "fresh",
    }
    h = _make_stub({"url": "https://ref-site.com", "mode": "inspire"})
    with patch.object(endpoint_module, "extract_brand", return_value=inspire_result):
        endpoint_module.run_brand_extract(h)
    status, payload = h.response
    assert status == 200
    assert payload == inspire_result
    assert payload["matched_dna"]["id"] == "cinematic_imax"


# ------------------------------------------------------------------ #
# Multipart / image-attachment path                                   #
# ------------------------------------------------------------------ #

# Minimal valid 8-byte PNG stub (correct magic: \x89PNG\r\n\x1a\n)
_FAKE_PNG = b"\x89PNG\r\n\x1a\n"


def _build_multipart(
    fields: dict[str, str],
    images: list[tuple[str, bytes, str]],  # (field_name, data, mime)
    boundary: str = "testboundary123",
) -> tuple[bytes, str]:
    """Build a raw multipart/form-data body.

    Returns (body_bytes, content_type_header_value).
    """
    parts: list[bytes] = []
    crlf = b"\r\n"

    for name, value in fields.items():
        parts.append(
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="{name}"\r\n'
            f'\r\n'
            f'{value}\r\n'.encode()
        )

    for field_name, data, mime in images:
        header = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="{field_name}"; filename="test.img"\r\n'
            f'Content-Type: {mime}\r\n'
            f'\r\n'
        ).encode()
        parts.append(header + data + crlf)

    parts.append(f'--{boundary}--\r\n'.encode())
    body = b"".join(parts)
    ct = f"multipart/form-data; boundary={boundary}"
    return body, ct


class _MultipartStubHandler:
    """Stub handler that carries a multipart Content-Type header."""

    def __init__(self, body: bytes, content_type: str):
        self.headers = {
            "Content-Type": content_type,
            "Content-Length": str(len(body)),
        }
        self.rfile = io.BytesIO(body)
        self.client_address = ("127.0.0.1", 12345)
        self.response: tuple[int, dict] | None = None
        self.path = "/api/brand-extract"
        self.command = "POST"

    def _json(self, status: int, payload: dict) -> None:
        self.response = (status, payload)


_FAKE_RESULT_OK = {
    "url": "https://acme.co", "ok": True, "error": None,
    "mode": "brand", "business_name": "Acme", "tagline": None,
    "industry": "tech", "tone": "professional", "palette": [],
    "logo_url": None, "favicon_url": None, "hero_copy": None,
    "vibe_keywords": [], "font_hints": [], "motion_intensity": None,
    "layout_density": None, "matched_dna": None,
    "raw_text_sample": "", "source": "fresh",
}


def test_multipart_happy_path_one_png_returns_200():
    """One valid PNG → 200; extract_brand called with inspiration_images=[bytes]."""
    body, ct = _build_multipart(
        fields={"url": "https://acme.co", "mode": "brand"},
        images=[("images[]", _FAKE_PNG, "image/png")],
    )
    h = _MultipartStubHandler(body, ct)
    with patch.object(endpoint_module, "extract_brand", return_value=_FAKE_RESULT_OK) as mock_ext:
        endpoint_module.run_brand_extract(h)
    status, payload = h.response
    assert status == 200
    assert payload["ok"] is True
    # Verify the raw bytes were forwarded
    args, kwargs = mock_ext.call_args
    assert kwargs.get("inspiration_images") == [_FAKE_PNG]


def test_multipart_oversized_image_returns_4xx():
    """An image > 10 MB → 400 or 413."""
    big_png = _FAKE_PNG + b"\x00" * (10 * 1024 * 1024 + 1)
    body, ct = _build_multipart(
        fields={"url": "https://acme.co"},
        images=[("images[]", big_png, "image/png")],
    )
    h = _MultipartStubHandler(body, ct)
    with patch.object(endpoint_module, "extract_brand", return_value=_FAKE_RESULT_OK):
        endpoint_module.run_brand_extract(h)
    status, payload = h.response
    assert status in (400, 413)
    assert "error" in payload


def test_multipart_wrong_mime_returns_400():
    """application/zip → 400."""
    body, ct = _build_multipart(
        fields={"url": "https://acme.co"},
        images=[("images[]", b"PK\x03\x04fakearchive", "application/zip")],
    )
    h = _MultipartStubHandler(body, ct)
    endpoint_module.run_brand_extract(h)
    status, payload = h.response
    assert status == 400
    assert "unsupported" in payload["error"].lower()


def test_multipart_too_many_images_returns_400():
    """Six images → 400."""
    images = [("images[]", _FAKE_PNG, "image/png")] * 6
    body, ct = _build_multipart(
        fields={"url": "https://acme.co"},
        images=images,
    )
    h = _MultipartStubHandler(body, ct)
    endpoint_module.run_brand_extract(h)
    status, payload = h.response
    assert status == 400
    assert "error" in payload
