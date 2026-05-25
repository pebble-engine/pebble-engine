"""Regression pin for /api/enrich-content auth gate (Phase 58e, 2026-05-22).

The handler mutates files inside ``<output>/<slug>/site/`` (phone, location,
services rewrite). The 2026-05-22 overnight bug-hunt sweep caught that it
had no auth gate at all — an anon caller could substitute their own phone
number, address, or services blurb into any project by guessing the slug.

These tests pin the auth gate so a future refactor can't silently
re-open the hole. They don't exercise the rewrite logic itself; that
belongs in a separate fixture if/when we add coverage for it.
"""
from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import pytest

import pebble_engine
import pebble.security as security_mod
import pebble.server.enrich as enrich_mod


class _FakeHandler:
    def __init__(self, body: dict):
        raw = json.dumps(body).encode("utf-8")
        self.rfile = BytesIO(raw)
        self.headers = {"Content-Length": str(len(raw))}
        self.status = None
        self.json_body = None
    def _json(self, status, payload):
        self.status = status
        self.json_body = payload


@pytest.fixture
def fake_output(tmp_path, monkeypatch):
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.setattr(security_mod, "_output_dir", lambda: out)
    return out


def _seed_project(output: Path, slug: str, owner_uid: str | None = None) -> Path:
    project = output / slug
    site = project / "site"
    site.mkdir(parents=True)
    (site / "app").mkdir()
    (site / "app" / "page.tsx").write_text("<p>Hi</p>", encoding="utf-8")
    brief = {}
    if owner_uid:
        brief["_user_id"] = owner_uid
    (project / "brief.json").write_text(json.dumps(brief), encoding="utf-8")
    return project


def test_enrich_content_401_when_signed_out(fake_output):
    """The leak: previously rewrote files for any anon caller. Must 401."""
    _seed_project(fake_output, "victim-co")
    h = _FakeHandler({
        "slug":  "victim-co",
        "facts": [{"key": "phone", "value": "+15551234567"}],
    })
    enrich_mod.run_enrich_content(h)
    assert h.status == 401


def test_enrich_content_403_when_signed_in_as_other_user(fake_output, monkeypatch):
    """Signed-in but not the owner — must 403, not 200."""
    _seed_project(fake_output, "alice-co", owner_uid="ALICE_UID")
    monkeypatch.setattr(security_mod, "resolve_user_id", lambda h: "BOB_UID")
    h = _FakeHandler({
        "slug":  "alice-co",
        "facts": [{"key": "phone", "value": "+15551234567"}],
    })
    enrich_mod.run_enrich_content(h)
    assert h.status == 403


def test_enrich_content_400_validation_still_runs_before_auth(fake_output):
    """Belt-and-suspenders: malformed payloads should keep returning 400
    so we don't lose the existing validation contract (empty body, missing
    slug, non-list facts) just because we added an auth gate. The gate
    runs AFTER the body validation."""
    # Missing slug — should 400 (the gate never runs because slug is "").
    h = _FakeHandler({"slug": "", "facts": []})
    enrich_mod.run_enrich_content(h)
    assert h.status == 400


def test_enrich_content_200_when_owner_with_no_facts(fake_output, monkeypatch):
    """Owner with empty facts list — 200 with a no-op response (existing
    behavior). Pin so we don't accidentally over-gate."""
    _seed_project(fake_output, "alice-co", owner_uid="ALICE_UID")
    monkeypatch.setattr(security_mod, "resolve_user_id", lambda h: "ALICE_UID")
    h = _FakeHandler({"slug": "alice-co", "facts": []})
    enrich_mod.run_enrich_content(h)
    assert h.status == 200
    assert h.json_body["facts_applied"] == 0
