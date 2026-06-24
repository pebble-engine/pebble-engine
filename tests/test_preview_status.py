"""Tests for GET /api/projects/<slug>/preview-status."""
from __future__ import annotations

import json

import pebble_engine
from pebble.server import preview_status as ps


def test_build_preview_status_no_source(tmp_path, monkeypatch):
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.setattr(ps, "_output_dir", lambda: out)
    monkeypatch.setenv("PEBBLE_PREVIEW_BACKEND", "vercel")

    st = ps.build_preview_status("bakery", kick=False)
    assert st["has_source"] is False
    assert st["ready"] is False


def test_build_preview_status_ready(tmp_path, monkeypatch):
    out = tmp_path / "output"
    site = out / "bakery" / "site"
    site.mkdir(parents=True)
    (site / "package.json").write_text("{}", encoding="utf-8")
    (out / "bakery" / ".vercel-preview.json").write_text(
        json.dumps({"url": "https://bakery.vercel.app", "deployed_at": "2026-01-01T00:00:00Z"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.setattr(ps, "_output_dir", lambda: out)
    monkeypatch.setenv("PEBBLE_PREVIEW_BACKEND", "vercel")

    st = ps.build_preview_status("bakery", kick=False)
    assert st["ready"] is True
    assert st["vercel_url"] == "https://bakery.vercel.app"
    assert st["preview_url"] == "/preview/bakery/"


def test_deployment_error_message():
    from pebble.vercel_deploy import _deployment_error_message

    msg = _deployment_error_message({"readyState": "ERROR", "errorMessage": "Build failed"})
    assert "ERROR" in msg
    assert "Build failed" in msg
