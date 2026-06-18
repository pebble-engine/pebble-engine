"""Tests for lazy Vercel preview deploy kick."""
from __future__ import annotations

import json

from pebble.server import preview_vercel_kick as pvk


def test_kick_starts_deploy_when_no_state(tmp_path, monkeypatch):
    out = tmp_path / "output"
    site = out / "bakery" / "site"
    site.mkdir(parents=True)
    (site / "package.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(pvk, "_output_dir", lambda: out)
    monkeypatch.setattr(pvk, "_run_deploy", lambda slug: None)

    status = pvk.kick_if_needed("bakery")
    assert status == "deploying"
    assert "bakery" in pvk._THREADS


def test_kick_skips_when_url_present(tmp_path, monkeypatch):
    out = tmp_path / "output"
    (out / "bakery").mkdir(parents=True)
    (out / "bakery" / ".vercel-preview.json").write_text(
        json.dumps({"url": "https://bakery.vercel.app"}), encoding="utf-8"
    )
    monkeypatch.setattr(pvk, "_output_dir", lambda: out)
    assert pvk.kick_if_needed("bakery") == "ready"


def test_kick_fails_without_site(tmp_path, monkeypatch):
    out = tmp_path / "output"
    monkeypatch.setattr(pvk, "_output_dir", lambda: out)
    assert pvk.kick_if_needed("bakery") == "failed"
    assert pvk.last_deploy_error("bakery")


def test_render_vercel_splash_deploying():
    html = pvk.render_vercel_splash_html("bakery", "deploying")
    assert "Building your preview" in html
    assert 'http-equiv="refresh"' in html
