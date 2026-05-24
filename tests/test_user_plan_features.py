"""Phase A1 — extended PLAN_LIMITS with new feature flags.

Pebble pricing restructure 2026-05-24: drop the `published_sites`
cap as the headline metric, add integration / stripe_checkout /
white_label / api_access / money_back_days flags.
"""
from pebble import user_plan


def test_free_has_no_integrations_allowed():
    assert user_plan.PLAN_LIMITS["free"]["integrations_allowed"] == []


def test_starter_has_basic_integrations():
    assert "whatsapp"     in user_plan.PLAN_LIMITS["starter"]["integrations_allowed"]
    assert "booking"      in user_plan.PLAN_LIMITS["starter"]["integrations_allowed"]
    assert "google-maps"  in user_plan.PLAN_LIMITS["starter"]["integrations_allowed"]
    assert "cookie-consent" in user_plan.PLAN_LIMITS["starter"]["integrations_allowed"]
    # Stripe + custom-code are Pro-only
    assert "stripe"      not in user_plan.PLAN_LIMITS["starter"]["integrations_allowed"]
    assert "custom-code" not in user_plan.PLAN_LIMITS["starter"]["integrations_allowed"]


def test_pro_has_all_integrations():
    pro = user_plan.PLAN_LIMITS["pro"]["integrations_allowed"]
    for iid in ("whatsapp", "booking", "google-maps", "cookie-consent",
                "stripe", "custom-code", "social"):
        assert iid in pro, f"{iid} missing from pro integrations"


def test_money_back_days_progression():
    assert user_plan.PLAN_LIMITS["free"]["money_back_days"]    == 0
    assert user_plan.PLAN_LIMITS["starter"]["money_back_days"] == 7
    assert user_plan.PLAN_LIMITS["pro"]["money_back_days"]     == 14


def test_white_label_pro_only():
    assert user_plan.PLAN_LIMITS["free"]["white_label"]    is False
    assert user_plan.PLAN_LIMITS["starter"]["white_label"] is False
    assert user_plan.PLAN_LIMITS["pro"]["white_label"]     is True


def test_api_access_pro_only():
    assert user_plan.PLAN_LIMITS["free"]["api_access"]    is False
    assert user_plan.PLAN_LIMITS["starter"]["api_access"] is False
    assert user_plan.PLAN_LIMITS["pro"]["api_access"]     is True


def test_published_sites_cap_removed():
    # 2026-05-24: published_sites cap deprecated in favor of credit-based
    # pricing. The key still exists for backwards compat but is now -1
    # (unlimited) across every tier — sites are gated by credit cost,
    # not by a sites-count cap.
    for tier in ("free", "starter", "pro", "enterprise"):
        assert user_plan.PLAN_LIMITS[tier]["published_sites"] == -1


def test_get_feature_helper_exists():
    """get_feature(user_id, key) → typed lookup, fail-soft default."""
    assert user_plan.get_feature("free",    "integrations_allowed") == []
    assert user_plan.get_feature("starter", "white_label") is False
    assert user_plan.get_feature("pro",     "api_access")  is True
    # Unknown feature → safe default
    assert user_plan.get_feature("pro", "made_up_key") is False
