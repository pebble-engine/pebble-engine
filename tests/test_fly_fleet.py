"""Fly Machines fleet client — pure-Python, mocked HTTP.

Live verification (booting a real machine, HMR timing, per-machine public
routing) requires a Fly token and is done separately — these tests pin the
request shapes + the registry/lifecycle logic.
"""
from __future__ import annotations

import json

import pytest

from pebble import fly_fleet as ff


@pytest.fixture
def cfg(monkeypatch, tmp_path):
    monkeypatch.setenv("FLY_API_TOKEN", "fly_tok")
    monkeypatch.setenv("FLY_APP", "pebble-preview-fleet")
    monkeypatch.setenv("FLY_PREVIEW_IMAGE", "registry.fly.io/pebble-preview-fleet:pebble-preview")
    monkeypatch.setenv("PEBBLE_FLEET_SECRET", "s3cr3t")
    monkeypatch.setattr(ff, "_fleet_dir", lambda: tmp_path / ".fleet")
    return tmp_path


def test_not_configured_without_env(monkeypatch):
    for k in ("FLY_API_TOKEN", "FLY_APP", "FLY_PREVIEW_IMAGE", "PEBBLE_FLEET_SECRET"):
        monkeypatch.delenv(k, raising=False)
    assert ff.fleet_configured() is False


def test_configured(cfg):
    assert ff.fleet_configured() is True


def test_create_machine_request_shape(cfg, monkeypatch):
    seen = {}

    class _R:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return {"id": "m_123", "state": "started"}

    def fake_post(url, **kw):
        seen["url"] = url; seen["json"] = kw.get("json"); seen["headers"] = kw.get("headers")
        return _R()

    monkeypatch.setattr(ff.httpx, "post", fake_post)
    m = ff.create_machine("my-slug")
    assert m["id"] == "m_123"
    assert seen["url"].endswith("/v1/apps/pebble-preview-fleet/machines")
    assert seen["headers"]["Authorization"] == "Bearer fly_tok"
    cfgj = seen["json"]["config"]
    assert cfgj["image"] == "registry.fly.io/pebble-preview-fleet:pebble-preview"
    # exposes the receiver's 8080 publicly on 443 tls+http
    svc = cfgj["services"][0]
    assert svc["internal_port"] == 8080
    assert any(p["port"] == 443 and "tls" in p["handlers"] for p in svc["ports"])
    # the shared secret is passed to the machine env
    assert cfgj["env"]["PEBBLE_FLEET_SECRET"] == "s3cr3t"


def test_ensure_machine_reuses_registered_started(cfg, monkeypatch):
    calls = {"create": 0}
    monkeypatch.setattr(ff, "create_machine", lambda slug: (calls.__setitem__("create", calls["create"] + 1) or {"id": "m_1", "state": "started"}))
    monkeypatch.setattr(ff, "get_machine", lambda mid: {"id": mid, "state": "started"})
    monkeypatch.setattr(ff, "start_machine", lambda mid: None)
    u1 = ff.ensure_machine("slugA")
    u2 = ff.ensure_machine("slugA")
    assert u1 == u2
    assert calls["create"] == 1  # second call reused the registry entry


def test_ensure_machine_restarts_stopped(cfg, monkeypatch):
    monkeypatch.setattr(ff, "create_machine", lambda slug: {"id": "m_1", "state": "started"})
    monkeypatch.setattr(ff, "get_machine", lambda mid: {"id": mid, "state": "stopped"})
    started = {"n": 0}
    monkeypatch.setattr(ff, "start_machine", lambda mid: started.__setitem__("n", started["n"] + 1))
    ff.ensure_machine("slugB")  # create + register
    ff.ensure_machine("slugB")  # registered but stopped -> start
    assert started["n"] >= 1


def test_sync_files_posts_to_receiver(cfg, monkeypatch):
    seen = {}

    class _R:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return {"ok": True, "written": 2}

    def fake_post(url, **kw):
        seen["url"] = url; seen["json"] = kw.get("json"); seen["headers"] = kw.get("headers")
        return _R()

    monkeypatch.setattr(ff.httpx, "post", fake_post)
    monkeypatch.setattr(ff, "machine_public_url", lambda slug, machine=None: "https://pebble-preview-slugc.fly.dev")
    res = ff.sync_files("slugc", [{"path": "app/page.tsx", "data": "x"}], deleted=["old.tsx"])
    assert res["ok"] is True
    assert seen["url"] == "https://pebble-preview-slugc.fly.dev/__pebble/sync"
    assert seen["headers"]["x-pebble-secret"] == "s3cr3t"
    assert seen["json"]["files"][0]["path"] == "app/page.tsx"
    assert seen["json"]["deleted"] == ["old.tsx"]


def test_reap_idle_stops_old_machines(cfg, monkeypatch):
    # Two registry entries; one idle past the cutoff.
    reg = {
        "fresh": {"machine_id": "m_fresh", "last_seen": 10_000.0},
        "stale": {"machine_id": "m_stale", "last_seen": 1.0},
    }
    ff._save_registry(reg)
    stopped = []
    monkeypatch.setattr(ff, "stop_machine", lambda mid: stopped.append(mid))
    monkeypatch.setattr(ff.time, "time", lambda: 10_000.0)
    ff.reap_idle(max_idle_s=100)
    assert stopped == ["m_stale"]


def test_concurrency_cap_blocks_new(cfg, monkeypatch):
    monkeypatch.setenv("PEBBLE_FLEET_MAX", "1")
    monkeypatch.setattr(ff, "create_machine", lambda slug: {"id": "m_" + slug, "state": "started"})
    monkeypatch.setattr(ff, "get_machine", lambda mid: {"id": mid, "state": "started"})
    monkeypatch.setattr(ff, "start_machine", lambda mid: None)
    ff.ensure_machine("one")  # fills the single slot
    res = ff.ensure_machine("two")  # over cap
    assert res is None or (isinstance(res, dict) and res.get("error"))
