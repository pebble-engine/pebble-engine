"""Tier-aware model selection tests (Phase 13c, 2026-05-19).

Pins the resolve_user_plan + model_for_plan helpers so the free/paid
boundary stays predictable. Marc's pricing thesis depends on Free tier
users always landing on Qwen Flash; if this regresses silently, free
builds start costing 7x more.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pebble.server.model_for_plan import (
    MODEL_FOR_FREE_TIER,
    MODEL_FOR_PAID_TIER,
    model_for_plan,
    resolve_user_plan,
)


# ------------------------------------------------------------------ #
# Constants are the IDs we expect on OpenRouter                        #
# ------------------------------------------------------------------ #

def test_free_tier_model_is_flash():
    assert MODEL_FOR_FREE_TIER == "qwen/qwen3.6-flash"


def test_paid_tier_model_is_plus():
    assert MODEL_FOR_PAID_TIER == "qwen/qwen3.6-plus-04-02"


def test_paid_model_is_not_same_as_free():
    """If these ever collapse to one model, tier-shifting becomes a no-op
    and Marc's pricing thesis quietly breaks."""
    assert MODEL_FOR_FREE_TIER != MODEL_FOR_PAID_TIER


# ------------------------------------------------------------------ #
# model_for_plan — pure mapping                                        #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("plan,expected", [
    ("free",     MODEL_FOR_FREE_TIER),
    ("starter",  MODEL_FOR_PAID_TIER),
    ("pro",      MODEL_FOR_PAID_TIER),
    ("unknown",  MODEL_FOR_PAID_TIER),  # unknown plan name → paid floor (don't downgrade real customers)
    ("",         MODEL_FOR_PAID_TIER),  # empty plan name → paid floor too
])
def test_model_for_plan_mapping(plan, expected):
    assert model_for_plan(plan) == expected


# ------------------------------------------------------------------ #
# resolve_user_plan — sentinel reading + edge cases                    #
# ------------------------------------------------------------------ #

def _write_sentinel(tmp_path: Path, uid: str, data: dict) -> None:
    d = tmp_path / ".users" / uid
    d.mkdir(parents=True, exist_ok=True)
    (d / "subscription.json").write_text(json.dumps(data), encoding="utf-8")


def test_no_user_id_returns_free(tmp_path):
    assert resolve_user_plan(None, output_root=tmp_path) == "free"
    assert resolve_user_plan("", output_root=tmp_path) == "free"


def test_invalid_uid_returns_free(tmp_path):
    """A traversal-y uid should fail safe_user_id and route to free."""
    assert resolve_user_plan("../victim", output_root=tmp_path) == "free"


def test_missing_sentinel_returns_free(tmp_path):
    assert resolve_user_plan("user-abc-123", output_root=tmp_path) == "free"


def test_active_starter_returns_starter(tmp_path):
    _write_sentinel(tmp_path, "user-abc-123", {"status": "active", "plan": "starter"})
    assert resolve_user_plan("user-abc-123", output_root=tmp_path) == "starter"


def test_active_pro_returns_pro(tmp_path):
    _write_sentinel(tmp_path, "user-abc-123", {"status": "active", "plan": "pro"})
    assert resolve_user_plan("user-abc-123", output_root=tmp_path) == "pro"


def test_trialing_is_treated_as_paid(tmp_path):
    """Stripe trials are real billing intent — count them as paid for
    model-selection purposes so trial users get the Plus quality they're
    evaluating."""
    _write_sentinel(tmp_path, "user-abc-123", {"status": "trialing", "plan": "starter"})
    assert resolve_user_plan("user-abc-123", output_root=tmp_path) == "starter"


def test_canceled_subscription_returns_free(tmp_path):
    """Lapsed subscription → free behavior. User keeps building, on the
    cheap model, until they re-subscribe."""
    _write_sentinel(tmp_path, "user-abc-123", {"status": "canceled", "plan": "pro"})
    assert resolve_user_plan("user-abc-123", output_root=tmp_path) == "free"


def test_past_due_returns_free(tmp_path):
    _write_sentinel(tmp_path, "user-abc-123", {"status": "past_due", "plan": "pro"})
    assert resolve_user_plan("user-abc-123", output_root=tmp_path) == "free"


def test_incomplete_returns_free(tmp_path):
    """Subscription started but payment never completed."""
    _write_sentinel(tmp_path, "user-abc-123", {"status": "incomplete", "plan": "starter"})
    assert resolve_user_plan("user-abc-123", output_root=tmp_path) == "free"


def test_corrupt_sentinel_returns_free(tmp_path):
    """Malformed JSON must not crash the build — fall back to free."""
    d = tmp_path / ".users" / "user-abc-123"
    d.mkdir(parents=True)
    (d / "subscription.json").write_text("{not valid json", encoding="utf-8")
    assert resolve_user_plan("user-abc-123", output_root=tmp_path) == "free"


def test_non_dict_json_returns_free(tmp_path):
    """An array or string in the sentinel file — still must not crash."""
    d = tmp_path / ".users" / "user-abc-123"
    d.mkdir(parents=True)
    (d / "subscription.json").write_text("[]", encoding="utf-8")
    assert resolve_user_plan("user-abc-123", output_root=tmp_path) == "free"


def test_active_with_unknown_plan_name_returns_starter(tmp_path):
    """Active subscription with an unrecognised plan string should NOT
    downgrade the user to free over a typo / new plan we haven't taught
    the code about. Route to the paid floor (starter)."""
    _write_sentinel(tmp_path, "user-abc-123", {"status": "active", "plan": "agency"})
    assert resolve_user_plan("user-abc-123", output_root=tmp_path) == "starter"


# ------------------------------------------------------------------ #
# Composed: end-to-end (uid → plan → model)                            #
# ------------------------------------------------------------------ #

def test_pro_user_gets_plus_model(tmp_path):
    _write_sentinel(tmp_path, "u1", {"status": "active", "plan": "pro"})
    plan = resolve_user_plan("u1", output_root=tmp_path)
    assert model_for_plan(plan) == MODEL_FOR_PAID_TIER


def test_anonymous_user_gets_flash_model(tmp_path):
    plan = resolve_user_plan(None, output_root=tmp_path)
    assert model_for_plan(plan) == MODEL_FOR_FREE_TIER


def test_lapsed_pro_gets_flash_model(tmp_path):
    """A pro user whose subscription canceled gets free-tier model on
    their next build. Marc's policy from billing memory: keep them
    building, just on the cheaper model."""
    _write_sentinel(tmp_path, "u1", {"status": "canceled", "plan": "pro"})
    plan = resolve_user_plan("u1", output_root=tmp_path)
    assert model_for_plan(plan) == MODEL_FOR_FREE_TIER
