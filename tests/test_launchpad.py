"""Launchpad v1 — Supabase showcase + HTTP contract tests."""
from __future__ import annotations

import pytest

import pebble.launchpad as launchpad_mod


def test_list_approved_empty_when_unconfigured(monkeypatch):
    monkeypatch.setattr(launchpad_mod, "is_configured", lambda: False)
    assert launchpad_mod.list_approved() == []


def test_submit_returns_none_when_unconfigured(monkeypatch):
    monkeypatch.setattr(launchpad_mod, "is_configured", lambda: False)
    assert launchpad_mod.submit("uid", "bakery", business_name="Bakery") is None


def test_list_showcase_filters_unpublished(monkeypatch, tmp_path):
    rows = [
        {"slug": "live", "business_name": "Live Co", "status": "approved", "submitted_at": "2026-01-01T00:00:00Z"},
        {"slug": "gone", "business_name": "Gone Co", "status": "approved", "submitted_at": "2026-01-02T00:00:00Z"},
    ]
    monkeypatch.setattr(launchpad_mod, "list_approved", lambda **kw: rows)

    out = tmp_path / "output"
    (out / "live").mkdir(parents=True)
    (out / "live" / "published.json").write_text('{"slug":"live","subdomain":"live"}', encoding="utf-8")

    import pebble_engine
    import pebble.security as security_mod
    import pebble.server.launchpad_api as api_mod

    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.setattr(security_mod, "_output_dir", lambda: out)

    def fake_published(slug: str) -> bool:
        return slug == "live"

    monkeypatch.setattr(api_mod, "is_published", fake_published)

    live = api_mod._live_approved_rows(limit=10)
    assert len(live) == 1
    assert live[0]["slug"] == "live"


def test_public_entry_includes_screenshot_url_when_file_exists(monkeypatch, tmp_path):
    out = tmp_path / "output"
    slug_dir = out / "bakery"
    (slug_dir / "screenshots").mkdir(parents=True)
    (slug_dir / "screenshots" / "01-hero.png").write_bytes(b"png")

    import pebble_engine
    import pebble.security as security_mod
    import pebble.server.launchpad_api as api_mod

    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.setattr(security_mod, "_output_dir", lambda: out)

    entry = api_mod._public_entry({
        "slug": "bakery",
        "business_name": "Bakery",
        "industry": "Food",
    })
    assert entry["screenshot_url"] == "/api/launchpad/screenshot/bakery"
    assert entry["preview_url"] == "/preview/bakery/"
