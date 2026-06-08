"""Vercel Deployments API preview — pure-Python, mocked HTTP."""
from __future__ import annotations

import json

import pytest

from pebble import vercel_deploy as vd


# ---- Task 1: config + file collection ------------------------------------

def test_not_configured_without_token(monkeypatch):
    monkeypatch.delenv("VERCEL_TOKEN", raising=False)
    assert vd.vercel_configured() is False


def test_configured_with_token(monkeypatch):
    monkeypatch.setenv("VERCEL_TOKEN", "tok")
    assert vd.vercel_configured() is True


def test_collect_files_skips_artifacts(tmp_path):
    site = tmp_path / "site"
    (site / "app").mkdir(parents=True)
    (site / "node_modules" / "x").mkdir(parents=True)
    (site / ".next").mkdir()
    (site / "app" / "page.tsx").write_text("export default ()=>null", encoding="utf-8")
    (site / "package.json").write_text('{"name":"x"}', encoding="utf-8")
    (site / "node_modules" / "x" / "y.js").write_text("//dep", encoding="utf-8")
    files = vd.collect_files(site)
    paths = {f["file"] for f in files}
    assert "app/page.tsx" in paths and "package.json" in paths
    assert not any("node_modules" in p or ".next" in p for p in paths)
    assert all("data" in f for f in files)  # inline {file, data}


def test_apply_preview_config_replaces_next_config(tmp_path):
    files = [
        {"file": "app/page.tsx", "data": "x"},
        {"file": "next.config.mjs", "data": "export default { reactStrictMode: true }"},
        {"file": "next.config.ts", "data": "// stray"},
    ]
    out = vd.apply_preview_config(files)
    cfg = [f for f in out if f["file"] == "next.config.mjs"][0]
    assert "ignoreBuildErrors: true" in cfg["data"]  # tolerant build
    assert "output:" not in cfg["data"]  # SSR preserved (no static export)
    assert not any(f["file"] == "next.config.ts" for f in out)  # stray dropped


def test_apply_preview_config_adds_when_missing(tmp_path):
    files = [{"file": "app/page.tsx", "data": "x"}]
    out = vd.apply_preview_config(files)
    assert any(f["file"] == "next.config.mjs" and "ignoreBuildErrors" in f["data"] for f in out)


# ---- Task 2: create deployment -------------------------------------------

def test_create_deployment_posts_files_and_returns_id_url(monkeypatch):
    monkeypatch.setenv("VERCEL_TOKEN", "tok")
    monkeypatch.setenv("VERCEL_TEAM_ID", "team_1")
    captured = {}

    class _Resp:
        status_code = 200
        def json(self): return {"id": "dpl_1", "url": "gen-abc.vercel.app"}
        def raise_for_status(self): pass

    def fake_post(url, **kw):
        captured["url"] = url
        captured["json"] = kw.get("json")
        captured["headers"] = kw.get("headers")
        return _Resp()

    monkeypatch.setattr(vd.httpx, "post", fake_post)
    res = vd.create_deployment([{"file": "package.json", "data": "{}"}], name="mysite")
    assert res["id"] == "dpl_1"
    assert res["url"] == "https://gen-abc.vercel.app"
    assert "/v13/deployments" in captured["url"]
    assert "teamId=team_1" in captured["url"]
    assert captured["headers"]["Authorization"] == "Bearer tok"
    assert captured["json"]["name"] == "mysite"
    assert captured["json"]["files"][0]["file"] == "package.json"
    assert captured["json"]["projectSettings"]["framework"] == "nextjs"


# ---- Task 3: poll ---------------------------------------------------------

def test_poll_returns_ready(monkeypatch):
    monkeypatch.setenv("VERCEL_TOKEN", "tok")
    states = iter(["BUILDING", "READY"])

    class _Resp:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return {"readyState": next(states), "url": "gen-abc.vercel.app"}

    monkeypatch.setattr(vd.httpx, "get", lambda url, **kw: _Resp())
    monkeypatch.setattr(vd.time, "sleep", lambda *_a, **_k: None)
    final = vd.poll_deployment("dpl_1", interval=0, timeout=10)
    assert final["readyState"] == "READY"


# ---- Task 4: orchestrate --------------------------------------------------

def test_deploy_preview_writes_state(tmp_path, monkeypatch):
    monkeypatch.setenv("VERCEL_TOKEN", "tok")
    out = tmp_path / "output"
    (out / "s1" / "site" / "app").mkdir(parents=True)
    (out / "s1" / "site" / "app" / "page.tsx").write_text("export default ()=>null", encoding="utf-8")
    (out / "s1" / "build_meta.json").write_text(json.dumps({"broken_files": []}), encoding="utf-8")
    monkeypatch.setattr(vd, "_output_dir", lambda: out)
    monkeypatch.setattr(vd, "create_deployment", lambda files, **k: {"id": "dpl_1", "url": "https://x.vercel.app"})
    monkeypatch.setattr(vd, "poll_deployment", lambda i, **k: {"readyState": "READY", "url": "x.vercel.app"})
    res = vd.deploy_preview("s1")
    assert res["url"] == "https://x.vercel.app"
    saved = json.loads((out / "s1" / ".vercel-preview.json").read_text(encoding="utf-8"))
    assert saved["url"] == "https://x.vercel.app"


def test_deploy_preview_refuses_broken_build(tmp_path, monkeypatch):
    monkeypatch.setenv("VERCEL_TOKEN", "tok")
    out = tmp_path / "output"
    (out / "s1" / "site").mkdir(parents=True)
    (out / "s1" / "build_meta.json").write_text(json.dumps({"broken_files": [{"file": "a.tsx"}]}), encoding="utf-8")
    monkeypatch.setattr(vd, "_output_dir", lambda: out)
    res = vd.deploy_preview("s1")
    assert res.get("error")


def test_deploy_preview_needs_token(tmp_path, monkeypatch):
    monkeypatch.delenv("VERCEL_TOKEN", raising=False)
    res = vd.deploy_preview("s1")
    assert res.get("error")
