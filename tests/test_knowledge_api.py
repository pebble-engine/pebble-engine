"""P1 T5 — GET/PUT project + account knowledge endpoints."""
from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import pytest

from pebble.server import knowledge_api as kapi


class FakeHandler:
    def __init__(self, body=None):
        raw = json.dumps(body).encode("utf-8") if body is not None else b""
        self.rfile = BytesIO(raw)
        self.headers = {"Content-Length": str(len(raw))}
        self.status = None
        self.json_body = None

    def _json(self, status, payload):
        self.status = status
        self.json_body = payload


@pytest.fixture
def env(tmp_path, monkeypatch):
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(kapi, "_output_dir", lambda: out)
    monkeypatch.setattr(kapi, "snapshot_site", lambda *a, **k: None)
    # auth bypass: owner + account resolve to a fixed uid
    monkeypatch.setattr(kapi, "require_project_owner", lambda h, slug: "user-1")
    monkeypatch.setattr(kapi, "resolve_user_id", lambda h: "user-1")
    return out


def _seed_project(out: Path, slug: str, brief: dict):
    d = out / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "brief.json").write_text(json.dumps(brief), encoding="utf-8")


def test_get_project_knowledge_returns_field(env):
    _seed_project(env, "p1", {"business_knowledge": "Closed Sundays."})
    h = FakeHandler()
    kapi.run_get_project_knowledge(h, "p1")
    assert h.status == 200
    assert h.json_body == {"slug": "p1", "knowledge": "Closed Sundays."}


def test_get_project_knowledge_blank_when_absent(env):
    _seed_project(env, "p1", {})
    h = FakeHandler()
    kapi.run_get_project_knowledge(h, "p1")
    assert h.status == 200
    assert h.json_body["knowledge"] == ""


def test_put_project_knowledge_writes_brief(env):
    _seed_project(env, "p1", {"business_name": "Acme"})
    h = FakeHandler({"knowledge": "We never work weekends."})
    kapi.run_put_project_knowledge(h, "p1")
    assert h.status == 200
    brief = json.loads((env / "p1" / "brief.json").read_text(encoding="utf-8"))
    assert brief["business_knowledge"] == "We never work weekends."
    assert brief["business_name"] == "Acme"  # preserved other fields


def test_put_project_knowledge_404_when_missing(env):
    h = FakeHandler({"knowledge": "x"})
    kapi.run_put_project_knowledge(h, "nope")
    assert h.status == 404


def test_put_project_knowledge_owner_gated(env, monkeypatch):
    monkeypatch.setattr(kapi, "require_project_owner", lambda h, slug: None)
    _seed_project(env, "p1", {})
    h = FakeHandler({"knowledge": "x"})
    kapi.run_put_project_knowledge(h, "p1")
    assert h.status != 200  # gate returned before write


def test_account_knowledge_round_trip(env):
    put = FakeHandler({"knowledge": "Always mention financing."})
    kapi.run_put_account_knowledge(put)
    assert put.status == 200
    get = FakeHandler()
    kapi.run_get_account_knowledge(get)
    assert get.status == 200
    assert get.json_body["knowledge"] == "Always mention financing."


def test_account_knowledge_requires_auth(env, monkeypatch):
    monkeypatch.setattr(kapi, "resolve_user_id", lambda h: None)
    h = FakeHandler()
    kapi.run_get_account_knowledge(h)
    assert h.status == 401
