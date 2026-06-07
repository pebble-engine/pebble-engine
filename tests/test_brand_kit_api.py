"""P3 T3 — GET/POST /api/account/brand-kit."""
from __future__ import annotations

import json
from io import BytesIO

import pytest

from pebble.server import brand_kit_api as bka


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
    monkeypatch.setattr(bka, "_output_dir", lambda: out)
    monkeypatch.setattr(bka, "resolve_user_id", lambda h: "u1")
    return out


def test_get_empty_kit(env):
    h = FakeHandler()
    bka.run_get_brand_kit(h)
    assert h.status == 200
    assert h.json_body["brand_kit"] == {}


def test_post_then_get_round_trips_and_sanitizes(env):
    put = FakeHandler({"brand_kit": {"primary_color": "#1F6FEB", "font": "Inter", "evil": "x"}})
    bka.run_put_brand_kit(put)
    assert put.status == 200
    assert put.json_body["brand_kit"]["primary_color"] == "#1F6FEB"
    assert "evil" not in put.json_body["brand_kit"]
    get = FakeHandler()
    bka.run_get_brand_kit(get)
    assert get.json_body["brand_kit"]["font"] == "Inter"


def test_requires_auth(env, monkeypatch):
    monkeypatch.setattr(bka, "resolve_user_id", lambda h: None)
    h = FakeHandler()
    bka.run_get_brand_kit(h)
    assert h.status == 401
