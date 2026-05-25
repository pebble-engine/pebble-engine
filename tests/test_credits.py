"""Tests for the credits module.

Pure-function tests — no Supabase calls. The validation layer is what
protects users from billing accidents (Marc's 2026-05-24 brief: "how
can we make sure they don't end up buying more by accident"). The
actual Supabase round-trip is verified via the live engine smoke test.
"""
from __future__ import annotations

import pytest

from pebble import credits


# ── Plan defaults ─────────────────────────────────────────────── #


def test_plan_grants_have_all_three_tiers():
    assert "free"    in credits.PLAN_GRANTS
    assert "starter" in credits.PLAN_GRANTS
    assert "pro"     in credits.PLAN_GRANTS


def test_plan_caps_match_plan_grants_keys():
    """Caps and grants must be defined for the same plan keys so an
    init() with a plan name can't half-look-up (grant present but cap
    missing or vice versa)."""
    assert set(credits.PLAN_GRANTS.keys()) == set(credits.PLAN_CAPS.keys())


def test_pro_grant_equals_cap():
    """Pro plan refills to the cap each month — verifies the 400/400
    relationship Marc described."""
    assert credits.PLAN_GRANTS["pro"] == credits.PLAN_CAPS["pro"]


def test_grants_never_exceed_caps():
    """Every plan's monthly grant must fit under its own cap, or the
    first-month refill would already overflow."""
    for plan in credits.PLAN_GRANTS:
        assert credits.PLAN_GRANTS[plan] <= credits.PLAN_CAPS[plan], plan


def test_default_hard_cap_is_400():
    """Marc's brief: 400 credit max. Pinning so a stray edit doesn't
    silently move the ceiling."""
    assert credits.DEFAULT_HARD_CAP == 400


def test_free_grant_cannot_afford_full_build():
    """2026-05-24 free tier: a free signup should NOT have enough
    credits to run a full engine build. This is the structural gate
    that pushes free users toward templates."""
    free_grant = credits.PLAN_GRANTS["free"]
    full_build_cost = credits.COST_FULL_ENGINE_BUILD
    assert free_grant < full_build_cost, (
        f"Free grant ({free_grant}) shouldn't cover a full build ({full_build_cost})"
    )


def test_starter_grant_covers_at_least_one_full_build():
    """Starter buyers should be able to run at least one engine build
    on their monthly grant, or the tier feels useless."""
    assert credits.PLAN_GRANTS["starter"] >= credits.COST_FULL_ENGINE_BUILD


def test_cost_for_known_actions():
    """The cost_for() lookup should resolve every action the engine
    references — typos here cause silent under-billing."""
    assert credits.cost_for("template_instantiate") == credits.COST_TEMPLATE_INSTANTIATE
    assert credits.cost_for("refinement")           == credits.COST_REFINEMENT
    assert credits.cost_for("brand_extract")        == credits.COST_BRAND_EXTRACT
    assert credits.cost_for("full_engine_build")    == credits.COST_FULL_ENGINE_BUILD


def test_cost_for_unknown_action_defaults_to_one():
    """Defensive default for forward compatibility — a new action
    added in the engine before the costs table catches up should
    bill 1 credit rather than 0 (which would let it slip free)."""
    assert credits.cost_for("brand_new_action_xyz") == 1


# ── Reason constant allowlists ─────────────────────────────────── #


def test_spend_reason_allowlist_doesnt_include_refill_reasons():
    """A typo (REASON_PACK_PURCHASED passed to spend()) should fail
    rather than silently subtract."""
    for r in credits.VALID_REFILL_REASONS:
        assert r not in credits.VALID_SPEND_REASONS


def test_refill_reason_allowlist_doesnt_include_spend_reasons():
    """Symmetric — REASON_REFINEMENT must not be a valid refill reason."""
    for r in credits.VALID_SPEND_REASONS:
        assert r not in credits.VALID_REFILL_REASONS


def test_all_reason_constants_are_in_one_allowlist():
    """Every REASON_* exported constant must be reachable by spend()
    or refill() — otherwise it's dead code."""
    spend_or_refill = credits.VALID_SPEND_REASONS | credits.VALID_REFILL_REASONS
    for attr in dir(credits):
        if attr.startswith("REASON_"):
            assert getattr(credits, attr) in spend_or_refill, attr


# ── spend() validation gates ───────────────────────────────────── #


def test_spend_rejects_zero_or_negative_amount():
    assert credits.spend("uid", 0, credits.REASON_REFINEMENT) is False
    assert credits.spend("uid", -5, credits.REASON_REFINEMENT) is False


def test_spend_rejects_unknown_reason():
    assert credits.spend("uid", 1, "made_up_reason") is False


def test_spend_rejects_refill_reason():
    """Passing a refill-only reason to spend() must be refused —
    otherwise a typo could subtract under a confusing label."""
    assert credits.spend("uid", 1, credits.REASON_PACK_PURCHASED) is False


def test_spend_returns_false_without_supabase(monkeypatch):
    """No env, no spend — but no crash either. Force is_configured
    to False so the test doesn't drift to actually-touching Supabase
    if the dev's .env happens to be loaded."""
    monkeypatch.setattr(credits, "is_configured", lambda: False)
    assert credits.spend("uid", 1, credits.REASON_REFINEMENT) is False


# ── refill() validation gates ──────────────────────────────────── #


def test_refill_rejects_zero_or_negative_amount():
    assert credits.refill("uid", 0, credits.REASON_MONTHLY_REFILL) is False
    assert credits.refill("uid", -5, credits.REASON_MONTHLY_REFILL) is False


def test_refill_rejects_unknown_reason():
    assert credits.refill("uid", 10, "made_up_reason") is False


def test_refill_rejects_spend_reason():
    """Symmetric to spend(): a spend reason can't refill."""
    assert credits.refill("uid", 10, credits.REASON_REFINEMENT) is False


def test_refill_returns_false_without_supabase(monkeypatch):
    monkeypatch.setattr(credits, "is_configured", lambda: False)
    assert credits.refill("uid", 10, credits.REASON_MONTHLY_REFILL) is False


# ── can_purchase() pre-checkout validation ─────────────────────── #
# This is THE function Marc cares about. It runs BEFORE Stripe
# Checkout opens — if it returns (False, msg), the user never pays.


def test_can_purchase_rejects_zero_or_negative_pack():
    ok, msg = credits.can_purchase("uid", 0)
    assert ok is False
    assert "invalid" in msg.lower() or "pack" in msg.lower()


def test_can_purchase_returns_false_without_supabase(monkeypatch):
    """When we can't read the balance we MUST refuse — the alternative
    is creating a Stripe session for a user whose state we don't know."""
    monkeypatch.setattr(credits, "is_configured", lambda: False)
    ok, msg = credits.can_purchase("uid", 50)
    assert ok is False
    assert msg  # non-empty reason
