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
    # Internal state is keyed by IP — reset_ip if available, else just clear all
    try:
        plan_limiter._calls.clear()  # type: ignore[attr-defined]
    except Exception:
        pass
    yield


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
    mock_ext.assert_called_once_with("https://acme.co", use_cache=True)


def test_use_cache_false_is_honored():
    fake_result = {"ok": False, "url": "https://x.com", "error": "fail",
                   "business_name": None, "tagline": None, "industry": None,
                   "tone": None, "palette": [], "logo_url": None,
                   "favicon_url": None, "hero_copy": None, "raw_text_sample": "",
                   "source": "fresh"}
    h = _StubHandler(b'{"url": "https://x.com", "use_cache": false}')
    with patch.object(endpoint_module, "extract_brand", return_value=fake_result) as mock_ext:
        endpoint_module.run_brand_extract(h)
    mock_ext.assert_called_once_with("https://x.com", use_cache=False)


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
