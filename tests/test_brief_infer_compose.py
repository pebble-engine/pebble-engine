"""Tests for pebble.brief_infer and pebble.brief_compose."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from pebble.brief_compose import compose_brief
from pebble.brief_infer import infer_brief
from pebble.onboarding import completed_build_count, onboarding_status


def test_infer_bakery_in_brooklyn():
    r = infer_brief("I own a bakery in Brooklyn")
    assert r["ok"] is True
    assert "bakery" in r["business_type"].lower() or r["business_type"] == "bakery"
    assert "Brooklyn" in r["location"]
    assert r["audience"]
    assert r["site_functions"]


def test_infer_empty_rejected():
    r = infer_brief("")
    assert r.get("ok") is False


def test_compose_template_includes_facts():
    r = compose_brief({
        "_raw_prompt": "I own a bakery in Brooklyn",
        "business_name": "Brooklyn Bakery",
        "business_type": "bakery",
        "location": "Brooklyn",
        "audience": ["locals"],
        "site_functions": ["presence", "leads"],
        "brand_tone": "warm",
    })
    assert r["ok"] is True
    patch = r["brief_patch"]
    assert "Brooklyn Bakery" in patch["extra_context"]
    assert "Brooklyn" in patch["extra_context"]
    assert patch.get("_composed") is True
    assert patch.get("_composed_at")


def test_compose_insufficient_input():
    r = compose_brief({})
    assert r.get("ok") is False


def test_onboarding_status_plan_required(tmp_path, monkeypatch):
    import pebble_engine as pe
    monkeypatch.setattr(pe, "OUTPUT_DIR", tmp_path)
    # One completed build for user u1
    p = tmp_path / "proj-a"
    p.mkdir()
    (p / "brief.json").write_text('{"_user_id": "u1", "business_name": "A"}', encoding="utf-8")
    (p / "build_meta.json").write_text('{"built_at": "2026-01-01"}', encoding="utf-8")
    assert completed_build_count("u1") == 1
    st = onboarding_status("u1")
    assert st["builds_completed"] == 1
    assert st["plan_required"] is True


def test_onboarding_status_plan_not_required_after_two(tmp_path, monkeypatch):
    import pebble_engine as pe
    monkeypatch.setattr(pe, "OUTPUT_DIR", tmp_path)
    for slug in ("a", "b"):
        p = tmp_path / slug
        p.mkdir()
        (p / "brief.json").write_text('{"_user_id": "u1"}', encoding="utf-8")
        (p / "build_meta.json").write_text("{}", encoding="utf-8")
    st = onboarding_status("u1")
    assert st["builds_completed"] == 2
    assert st["plan_required"] is False
