"""Tests for pebble.beta_credits — the one-shot admin CLI that tops up
invited beta testers so a Free account can run a few real engine builds.

The Supabase-touching functions (resolve_email_to_uid, _set_hard_cap,
grant_beta_builds) are integration-shaped; here we cover the PURE logic:
builds→credits conversion, the top-up cap/delta math, and arg parsing.
Those are where the bugs that would silently over/under-grant live.
"""
import pytest

from pebble import beta_credits as bc
from pebble import credits


def test_builds_to_credits_uses_full_build_cost():
    # One build must cost exactly COST_FULL_ENGINE_BUILD credits.
    assert bc.builds_to_credits(1) == credits.COST_FULL_ENGINE_BUILD
    assert bc.builds_to_credits(3) == 3 * credits.COST_FULL_ENGINE_BUILD


def test_builds_to_credits_rejects_non_positive():
    with pytest.raises(ValueError):
        bc.builds_to_credits(0)
    with pytest.raises(ValueError):
        bc.builds_to_credits(-2)


def test_default_beta_builds_is_three():
    # Marc's ask: "small allotment (2-3 builds)". Default to 3.
    assert bc.DEFAULT_BETA_BUILDS == 3


def test_plan_topup_below_target_raises_cap_and_tops_up():
    # Fresh free user: balance 5, cap 20, wants 30 credits (3 builds).
    new_cap, delta = bc.plan_topup(current_balance=5, current_cap=20, target=30)
    assert new_cap == 30          # cap must rise to fit the grant
    assert delta == 25            # top up 5 -> 30


def test_plan_topup_already_at_or_above_target_is_noop():
    # Already has 40 credits / cap 40 — granting 30 must NOT remove any.
    new_cap, delta = bc.plan_topup(current_balance=40, current_cap=40, target=30)
    assert delta == 0
    assert new_cap == 40          # never lower an existing cap


def test_plan_topup_exact_target_is_noop():
    new_cap, delta = bc.plan_topup(current_balance=30, current_cap=30, target=30)
    assert delta == 0
    assert new_cap == 30


def test_plan_topup_keeps_higher_existing_cap():
    # Pre-existing cap above target stays; only balance tops up.
    new_cap, delta = bc.plan_topup(current_balance=5, current_cap=400, target=30)
    assert new_cap == 400
    assert delta == 25


def test_parse_args_collects_recipients_and_builds():
    ns = bc.parse_args(["a@b.com", "c@d.com", "--builds", "2"])
    assert ns.recipients == ["a@b.com", "c@d.com"]
    assert ns.builds == 2
    assert ns.dry_run is False


def test_parse_args_defaults_builds_and_supports_dry_run():
    ns = bc.parse_args(["someone@example.com", "--dry-run"])
    assert ns.recipients == ["someone@example.com"]
    assert ns.builds == bc.DEFAULT_BETA_BUILDS
    assert ns.dry_run is True


def test_looks_like_email_vs_uuid():
    assert bc.looks_like_email("marc@pebble.com") is True
    assert bc.looks_like_email("f19c0cb6-5b75-4968-97b7-e2dcf3dae431") is False
    assert bc.looks_like_email("not-an-email") is False


def test_grant_returns_skipped_when_supabase_unconfigured(monkeypatch):
    monkeypatch.setattr(bc.credits, "is_configured", lambda: False)
    res = bc.grant_beta_builds("f19c0cb6-5b75-4968-97b7-e2dcf3dae431", builds=3)
    assert res.ok is False
    assert "supabase" in res.message.lower()
