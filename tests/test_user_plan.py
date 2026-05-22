"""Tests for pebble.user_plan — plan resolution + monthly usage counters.

Covers the core gate logic: which plan a user reads as, what limits
apply, the read-only quota check, and the atomic increment helpers.
HTTP-level enforcement (the 402 response shape on /api/refine etc.) is
covered by the per-endpoint integration tests; this file pins the pure
logic.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import pebble_engine
from pebble import user_plan


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Point OUTPUT_DIR at the tmp dir so each test has a fresh sentinel/usage dir."""
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    return tmp_path


def _write_sub(out: Path, uid: str, plan: str, status: str = "active") -> None:
    p = out / ".users" / uid
    p.mkdir(parents=True, exist_ok=True)
    (p / "subscription.json").write_text(
        json.dumps({"status": status, "plan": plan}), encoding="utf-8",
    )


# ---------- get_user_plan -------------------------------------------------

def test_get_user_plan_returns_free_for_no_sentinel(_isolate):
    assert user_plan.get_user_plan("noone") == "free"


def test_get_user_plan_returns_free_for_invalid_uid(_isolate):
    assert user_plan.get_user_plan("") == "free"
    assert user_plan.get_user_plan("../escape") == "free"
    assert user_plan.get_user_plan(None) == "free"  # type: ignore[arg-type]


def test_get_user_plan_reads_starter(_isolate):
    _write_sub(_isolate, "u1", "starter")
    assert user_plan.get_user_plan("u1") == "starter"


def test_get_user_plan_reads_pro(_isolate):
    _write_sub(_isolate, "u1", "pro")
    assert user_plan.get_user_plan("u1") == "pro"


def test_get_user_plan_reads_enterprise(_isolate):
    _write_sub(_isolate, "u1", "enterprise")
    assert user_plan.get_user_plan("u1") == "enterprise"


def test_get_user_plan_downgrades_lapsed_subscription(_isolate):
    """Status canceled / past_due / unpaid all read as Free."""
    for status in ("canceled", "past_due", "unpaid", "paused", "incomplete"):
        _write_sub(_isolate, f"u-{status}", "pro", status=status)
        assert user_plan.get_user_plan(f"u-{status}") == "free", status


def test_get_user_plan_downgrades_unknown_plan(_isolate):
    """A typo'd plan name in the sentinel falls back to Free, not crashes."""
    _write_sub(_isolate, "u1", "ultra-mega")
    assert user_plan.get_user_plan("u1") == "free"


def test_get_user_plan_handles_corrupt_json(_isolate):
    p = _isolate / ".users" / "u1"
    p.mkdir(parents=True)
    (p / "subscription.json").write_text("not-json{")
    assert user_plan.get_user_plan("u1") == "free"


# ---------- get_limit / has_feature ---------------------------------------

def test_limits_free_matches_pricing_page(_isolate):
    assert user_plan.get_limit("freebie", "published_sites") == 1
    assert user_plan.get_limit("freebie", "ai_refinements_per_month") == 30
    assert user_plan.get_limit("freebie", "custom_domains") == 0
    assert user_plan.get_limit("freebie", "drop_in_sections_allowed") is False
    assert user_plan.get_limit("freebie", "resend_email_forms") is False
    assert user_plan.get_limit("freebie", "site_analytics") is False
    assert user_plan.get_limit("freebie", "multi_page_sites") is True  # kept free per Marc


def test_limits_starter(_isolate):
    _write_sub(_isolate, "u1", "starter")
    assert user_plan.get_limit("u1", "published_sites") == 5
    assert user_plan.get_limit("u1", "ai_refinements_per_month") == 150
    assert user_plan.get_limit("u1", "custom_domains") == 1
    assert user_plan.get_limit("u1", "resend_email_forms") is True
    assert user_plan.get_limit("u1", "drop_in_sections_allowed") is False  # Pro only
    assert user_plan.get_limit("u1", "site_analytics") is False           # Pro only


def test_limits_pro(_isolate):
    _write_sub(_isolate, "u1", "pro")
    # Pro's published_sites=-1 (unlimited) clamps DOWN to the
    # HARD_CEILINGS value of 100. Real Pro customers shouldn't hit
    # this; if they do, ops adds a ceiling_override.json.
    assert user_plan.get_limit("u1", "published_sites") == 100
    assert user_plan.get_limit("u1", "custom_domains") == 5
    assert user_plan.get_limit("u1", "drop_in_sections_allowed") is True
    assert user_plan.get_limit("u1", "site_analytics") is True


def test_has_feature_true_for_pro_only_features(_isolate):
    _write_sub(_isolate, "u1", "pro")
    assert user_plan.has_feature("u1", "drop_in_sections_allowed") is True
    assert user_plan.has_feature("u1", "site_analytics") is True


def test_has_feature_false_for_free(_isolate):
    assert user_plan.has_feature("freebie", "drop_in_sections_allowed") is False
    assert user_plan.has_feature("freebie", "site_analytics") is False
    assert user_plan.has_feature("freebie", "custom_domains") is False  # limit=0 → False


# ---------- get_project_plan ---------------------------------------------

def test_project_plan_via_brief(_isolate):
    _write_sub(_isolate, "owner1", "pro")
    proj = _isolate / "good-co"
    proj.mkdir()
    (proj / "brief.json").write_text(json.dumps({"_user_id": "owner1"}))
    assert user_plan.get_project_plan("good-co") == "pro"


def test_project_plan_free_for_unclaimed(_isolate):
    proj = _isolate / "ghost"
    proj.mkdir()
    (proj / "brief.json").write_text(json.dumps({"business_name": "x"}))  # no _user_id
    assert user_plan.get_project_plan("ghost") == "free"


def test_project_plan_free_for_missing_brief(_isolate):
    assert user_plan.get_project_plan("nonexistent") == "free"


def test_project_has_feature_uses_owner_plan(_isolate):
    _write_sub(_isolate, "owner1", "starter")
    proj = _isolate / "good-co"
    proj.mkdir()
    (proj / "brief.json").write_text(json.dumps({"_user_id": "owner1"}))
    assert user_plan.project_has_feature("good-co", "resend_email_forms") is True
    assert user_plan.project_has_feature("good-co", "drop_in_sections_allowed") is False


# ---------- would_exceed_quota / increment_usage --------------------------

def test_would_exceed_quota_free_under_limit(_isolate):
    exceeds, current, limit = user_plan.would_exceed_quota(
        "u1", "ai_refinements", "ai_refinements_per_month",
    )
    assert exceeds is False
    assert current == 0
    assert limit == 30


def test_increment_then_check(_isolate):
    """Increment 30 times; the 31st check should report exceeds."""
    for _ in range(30):
        user_plan.increment_usage("u1", "ai_refinements")
    exceeds, current, limit = user_plan.would_exceed_quota(
        "u1", "ai_refinements", "ai_refinements_per_month",
    )
    assert exceeds is True
    assert current == 30
    assert limit == 30


def test_unlimited_plan_clamps_to_hard_ceiling(_isolate):
    """Enterprise's nominally-unlimited ai_refinements_per_month gets
    clamped to HARD_CEILINGS[ai_refinements_per_month] = 1000.
    Defense-in-depth: even if subscription.json is spoofed to Enterprise,
    the user can't burn more than 1000 refinements/month worth of LLM
    cost. Real Enterprise customers get a per-user override file."""
    _write_sub(_isolate, "u1", "enterprise")
    for _ in range(500):
        user_plan.increment_usage("u1", "ai_refinements")
    exceeds, current, limit = user_plan.would_exceed_quota(
        "u1", "ai_refinements", "ai_refinements_per_month",
    )
    assert exceeds is False           # 500 < 1000 ceiling
    assert current == 500
    assert limit == 1000              # clamped from -1


def test_ceiling_override_lifts_cap(_isolate, monkeypatch):
    """Per-user override at ceiling_override.json bypasses HARD_CEILINGS.
    Used by ops staff to honor real Enterprise contracts above the
    default ceiling. Manual filesystem write — no API path."""
    _write_sub(_isolate, "u1", "enterprise")
    override_dir = _isolate / ".users" / "u1"
    override_dir.mkdir(parents=True, exist_ok=True)
    (override_dir / "ceiling_override.json").write_text(
        json.dumps({"ai_refinements_per_month": 10000}),
        encoding="utf-8",
    )
    assert user_plan.get_limit("u1", "ai_refinements_per_month") == 10000


def test_ceiling_clamps_published_sites_for_pro(_isolate):
    """Pro's -1 published_sites clamps to 100, the HARD_CEILINGS value."""
    _write_sub(_isolate, "u1", "pro")
    assert user_plan.get_limit("u1", "published_sites") == 100


def test_ceiling_ignored_for_boolean_features(_isolate):
    """Boolean features (drop_in_sections_allowed, etc.) are feature
    flags, not counters — the ceiling doesn't apply."""
    _write_sub(_isolate, "u1", "pro")
    # No KeyError on a feature without a HARD_CEILINGS entry.
    assert user_plan.get_limit("u1", "drop_in_sections_allowed") is True


def test_increment_creates_user_dir_on_demand(_isolate):
    """No pre-existing .users/<uid>/ directory — increment_usage should mkdir."""
    user_dir = _isolate / ".users" / "u1"
    assert not user_dir.exists()
    new = user_plan.increment_usage("u1", "ai_refinements")
    assert new == 1
    assert user_dir.exists()


def test_increment_ignores_invalid_uid(_isolate):
    """Invalid uid → no-op write, returns 0."""
    assert user_plan.increment_usage("", "ai_refinements") == 0
    assert user_plan.increment_usage("../escape", "ai_refinements") == 0


def test_monthly_counter_isolated_by_month(_isolate, monkeypatch):
    """Manually swap the current_month helper to verify counters don't bleed."""
    monkeypatch.setattr(user_plan, "_current_month", lambda: "2026-05")
    user_plan.increment_usage("u1", "ai_refinements")
    user_plan.increment_usage("u1", "ai_refinements")
    assert user_plan.get_usage_count("u1", "ai_refinements") == 2

    monkeypatch.setattr(user_plan, "_current_month", lambda: "2026-06")
    assert user_plan.get_usage_count("u1", "ai_refinements") == 0


# ---------- gate_response shape ------------------------------------------

def test_gate_response_minimal_shape():
    r = user_plan.gate_response(
        feature_label="Custom domain",
        required_plan="starter",
        current_plan="free",
    )
    assert r["feature"] == "Custom domain"
    assert r["required_plan"] == "starter"
    assert r["current_plan"] == "free"
    assert r["upgrade_url"] == "/pricing"
    assert "Starter" in r["error"]  # title-cased plan name in the error string


def test_gate_response_includes_quota_when_provided():
    r = user_plan.gate_response(
        feature_label="AI refinement",
        required_plan="starter",
        current_plan="free",
        current=30,
        limit=30,
    )
    assert r["current_usage"] == 30
    assert r["limit"] == 30
