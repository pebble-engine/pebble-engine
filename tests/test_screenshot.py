"""Card thumbnail via Cloudflare Browser Rendering screenshot API (mocked)."""
from __future__ import annotations

import pytest

from pebble import screenshot as ss


def test_not_configured_without_creds(monkeypatch):
    monkeypatch.delenv("CLOUDFLARE_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)
    assert ss.configured() is False


def test_capture_posts_to_cf(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "acc")
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    seen = {}

    class _R:
        status_code = 200
        content = b"\x89PNG\r\n\x1a\n rest"
        def raise_for_status(self): pass

    def fake_post(url, **kw):
        seen["url"] = url
        seen["json"] = kw.get("json")
        seen["headers"] = kw.get("headers")
        return _R()

    monkeypatch.setattr(ss.httpx, "post", fake_post)
    png = ss.capture_to_png("https://x.vercel.app")
    assert png.startswith(b"\x89PNG")
    assert "/browser-rendering/screenshot" in seen["url"] and "acc" in seen["url"]
    assert seen["json"]["url"] == "https://x.vercel.app"
    assert seen["headers"]["Authorization"] == "Bearer tok"


def test_screenshot_project_writes_hero_png(tmp_path, monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "acc")
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    monkeypatch.setattr(ss, "capture_to_png", lambda url, **k: b"\x89PNGdata")
    dest = ss.screenshot_project(tmp_path, "s1", "https://x.vercel.app")
    assert dest == tmp_path / "s1" / "screenshots" / "01-hero.png"
    assert dest.read_bytes() == b"\x89PNGdata"


def test_screenshot_project_noop_without_creds(tmp_path, monkeypatch):
    monkeypatch.delenv("CLOUDFLARE_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)
    assert ss.screenshot_project(tmp_path, "s1", "https://x.vercel.app") is None


def test_screenshot_project_swallows_errors(tmp_path, monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "acc")
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    def boom(url, **k): raise RuntimeError("cf down")
    monkeypatch.setattr(ss, "capture_to_png", boom)
    # Thumbnail is best-effort — never raise into the build pipeline.
    assert ss.screenshot_project(tmp_path, "s1", "https://x.vercel.app") is None
