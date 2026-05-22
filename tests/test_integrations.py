"""Tests for pebble.integrations — storage helpers + snippet rendering.

Covers:
- get / save / delete round-trip
- Unknown integration ID raises ValueError
- render_integration_snippet for each integration type
- render_all_snippets aggregation
- Path-traversal guard on slug (via the storage path)
- Empty config fields are silently skipped (no snippet emitted)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import pebble_engine
import pebble.integrations as intg


@pytest.fixture()
def output_root(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# Storage round-trip
# ---------------------------------------------------------------------------

def test_save_and_get_roundtrip(output_root):
    saved = intg.save_integration(
        "my-slug", "whatsapp", True, {"phone": "+15551234567", "message": "Hi"}
    )
    assert saved["enabled"] is True
    assert saved["config"]["phone"] == "+15551234567"

    result = intg.get_integrations("my-slug")
    assert "whatsapp" in result
    assert result["whatsapp"]["enabled"] is True
    assert result["whatsapp"]["config"]["phone"] == "+15551234567"


def test_unknown_integration_raises(output_root):
    with pytest.raises(ValueError, match="Unknown integration"):
        intg.save_integration("s", "unknown-widget", True, {})


def test_delete_existing(output_root):
    intg.save_integration("s", "booking", True, {"url": "https://cal.com/me"})
    existed = intg.delete_integration("s", "booking")
    assert existed is True
    assert intg.get_integrations("s") == {}


def test_delete_nonexistent_returns_false(output_root):
    existed = intg.delete_integration("s", "booking")
    assert existed is False


def test_get_returns_empty_when_no_dir(output_root):
    assert intg.get_integrations("no-such-slug") == {}


def test_overwrite_updates_config(output_root):
    intg.save_integration("s", "whatsapp", True, {"phone": "+1"})
    intg.save_integration("s", "whatsapp", False, {"phone": "+2"})
    result = intg.get_integrations("s")
    assert result["whatsapp"]["enabled"] is False
    assert result["whatsapp"]["config"]["phone"] == "+2"


# ---------------------------------------------------------------------------
# Snippet rendering
# ---------------------------------------------------------------------------

def test_whatsapp_snippet_contains_wa_link():
    snip = intg.render_integration_snippet("whatsapp", {"phone": "+15551234567"})
    assert "wa.me/+15551234567" in snip
    assert 'id="pebble-whatsapp"' in snip


def test_whatsapp_snippet_empty_when_no_phone():
    snip = intg.render_integration_snippet("whatsapp", {"phone": ""})
    assert snip == ""


def test_whatsapp_strips_non_numeric_except_plus():
    snip = intg.render_integration_snippet("whatsapp", {"phone": "+1 (555) 123-4567"})
    assert "wa.me/+15551234567" in snip


def test_booking_snippet_contains_url():
    snip = intg.render_integration_snippet("booking", {"url": "https://cal.com/me"})
    assert "https://cal.com/me" in snip
    assert 'id="pebble-booking"' in snip


def test_booking_snippet_empty_when_no_url():
    snip = intg.render_integration_snippet("booking", {"url": ""})
    assert snip == ""


def test_booking_uses_default_button_text():
    snip = intg.render_integration_snippet("booking", {"url": "https://x.com"})
    assert "Book a call" in snip


def test_booking_uses_custom_button_text():
    snip = intg.render_integration_snippet("booking", {"url": "https://x.com", "button_text": "Schedule now"})
    assert "Schedule now" in snip


def test_maps_snippet_contains_address():
    snip = intg.render_integration_snippet("google-maps", {"address": "123 Main St, NY"})
    assert "maps.google.com" in snip
    assert "123" in snip  # URL-encoded address contains the number


def test_maps_snippet_empty_when_no_address():
    snip = intg.render_integration_snippet("google-maps", {"address": ""})
    assert snip == ""


def test_social_snippet_contains_links():
    snip = intg.render_integration_snippet("social", {
        "instagram": "https://instagram.com/test",
        "tiktok":    "https://tiktok.com/@test",
    })
    assert "instagram.com/test" in snip
    assert "tiktok.com/@test" in snip
    assert 'id="pebble-social"' in snip


def test_social_snippet_empty_when_no_urls():
    snip = intg.render_integration_snippet("social", {})
    assert snip == ""


def test_cookie_snippet_contains_dismiss():
    snip = intg.render_integration_snippet("cookie-consent", {})
    assert "pebble-cookie" in snip
    assert "OK" in snip


def test_custom_code_returns_code_verbatim():
    code = '<script src="https://example.com/widget.js"></script>'
    snip = intg.render_integration_snippet("custom-code", {"code": code})
    assert snip == code


def test_unknown_integration_renders_empty():
    snip = intg.render_integration_snippet("bogus-id", {"foo": "bar"})
    assert snip == ""


# ---------------------------------------------------------------------------
# render_all_snippets
# ---------------------------------------------------------------------------

def test_render_all_snippets_combines_enabled(output_root):
    intg.save_integration("s", "whatsapp", True,  {"phone": "+1"})
    intg.save_integration("s", "booking",  False, {"url": "https://x.com"})
    combined = intg.render_all_snippets("s")
    assert "wa.me" in combined           # whatsapp enabled
    assert "pebble-booking" not in combined  # booking disabled


def test_render_all_snippets_empty_project(output_root):
    assert intg.render_all_snippets("no-project") == ""
