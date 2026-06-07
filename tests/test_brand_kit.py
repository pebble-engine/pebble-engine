"""P3 — per-account brand kit (colors, font, voice)."""
from __future__ import annotations

from pathlib import Path

from pebble import brand_kit as bk


def test_empty_kit_renders_blank():
    assert bk.render_brand_kit_block({}) == ""
    assert bk.render_brand_kit_block({"primary_color": "", "voice": ""}) == ""


def test_render_includes_colors_font_voice():
    out = bk.render_brand_kit_block({
        "primary_color": "#1F6FEB", "accent_color": "#F59E0B",
        "font": "Inter", "voice": "warm, plain",
    })
    assert "BRAND KIT" in out
    assert "#1F6FEB" in out and "#F59E0B" in out
    assert "Inter" in out and "warm, plain" in out


def test_render_is_strformat_safe():
    out = bk.render_brand_kit_block({"voice": "a {b} c"})
    assert "{" not in out and "}" not in out


def test_sanitize_validates_hex_and_caps_lengths():
    k = bk.sanitize_kit({
        "primary_color": "not-a-color",
        "accent_color": "#abc",
        "font": "x" * 200,
        "voice": "y" * 5000,
    })
    assert k["primary_color"] == ""        # invalid hex dropped
    assert k["accent_color"] == "#abc"      # valid short hex kept
    assert len(k["font"]) <= bk.MAX_FONT
    assert len(k["voice"]) <= bk.MAX_VOICE


def test_sanitize_drops_unknown_keys():
    k = bk.sanitize_kit({"primary_color": "#000000", "evil": "rm -rf"})
    assert "evil" not in k
    assert k["primary_color"] == "#000000"


def test_account_round_trip(tmp_path: Path):
    assert bk.load_account_brand_kit(tmp_path, "u1") == {}
    bk.save_account_brand_kit(tmp_path, "u1", {"primary_color": "#000000", "font": "Inter"})
    loaded = bk.load_account_brand_kit(tmp_path, "u1")
    assert loaded["primary_color"] == "#000000" and loaded["font"] == "Inter"


def test_load_blank_uid_safe(tmp_path: Path):
    assert bk.load_account_brand_kit(tmp_path, "") == {}
