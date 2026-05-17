"""Tests for POST /api/checkout/create-session — creates a Stripe Checkout
Session in subscription mode and returns its hosted-payment URL.

The Stripe SDK is patched on the module under test so no test ever talks
to Stripe over the wire — we assert on what the engine WOULD call.
"""
from __future__ import annotations

import json
from io import BytesIO
from typing import Any
from unittest.mock import MagicMock

import pytest
import stripe  # real SDK — only used for exception classes; the SDK
# reference inside the endpoint module is monkeypatched per test.


# ---------- handler + stripe stub fixtures --------------------------------

class FakeHandler:
    """Minimal handler shape — body + auth header + captured response."""

    def __init__(
        self,
        body: dict | str | None = None,
        authorization: str | None = None,
    ):
        if isinstance(body, dict):
            raw = json.dumps(body).encode("utf-8")
        elif isinstance(body, str):
            raw = body.encode("utf-8")
        else:
            raw = b""
        self.rfile = BytesIO(raw)
        self.headers: dict[str, str] = {"Content-Length": str(len(raw))}
        if authorization is not None:
            self.headers["Authorization"] = authorization
        self.client_address = ("127.0.0.1", 12345)
        self.status: int | None = None
        self.body: dict | None = None

    def _json(self, status: int, payload: dict, extra_headers=None) -> None:  # noqa: ARG002
        self.status = status
        self.body = payload


@pytest.fixture
def signed_in_user(monkeypatch):
    """Patch require_user to always return a fixed user dict so endpoint
    tests focus on the Checkout logic, not the auth gate (which has its
    own unit tests in test_security.py)."""
    user = {"id": "uuid-marc-abc", "email": "marc@example.com"}

    # Patch require_user where the endpoint module looks it up — that's
    # pebble.server.stripe_checkout, not pebble.security, because the
    # endpoint does `from pebble.security import require_user` once and
    # then calls the local name.
    monkeypatch.setattr(
        "pebble.server.stripe_checkout.require_user",
        lambda h: user,
    )
    return user


@pytest.fixture
def stripe_env(monkeypatch):
    """Provide the env vars the endpoint expects so we exercise the
    happy path rather than the 503-not-configured branch."""
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_unit-test-key")
    monkeypatch.setenv("PEBBLE_STRIPE_STARTER_PRICE_ID", "price_starter_unit")
    monkeypatch.setenv("PEBBLE_STRIPE_PRO_PRICE_ID", "price_pro_unit")
    monkeypatch.setenv("PEBBLE_PUBLIC_URL", "https://app.test.pebble")


@pytest.fixture
def fake_stripe(monkeypatch):
    """Replace the stripe SDK reference inside pebble.server.stripe_checkout
    with a MagicMock that records calls. Tests can then assert on the
    parameters the endpoint sends."""
    fake = MagicMock()
    fake.checkout.Session.create.return_value = MagicMock(
        id="cs_test_session_id",
        url="https://checkout.stripe.com/c/pay/cs_test_session_id",
    )
    monkeypatch.setattr("pebble.server.stripe_checkout.stripe", fake)
    return fake


# ---------- auth gate ------------------------------------------------------

def test_returns_401_when_require_user_says_no(monkeypatch, stripe_env):
    """When require_user writes its own 401 + returns None, the endpoint
    must bail without writing a second response or touching Stripe."""
    from pebble.server import stripe_checkout

    def stub_require_user(h):
        h._json(401, {"error": "sign in required"})
        return None

    monkeypatch.setattr(stripe_checkout, "require_user", stub_require_user)
    h = FakeHandler({"plan": "starter"})
    stripe_checkout.run_create_session(h)
    assert h.status == 401


# ---------- body parsing ---------------------------------------------------

def test_returns_400_when_body_missing_plan(signed_in_user, stripe_env, fake_stripe):
    """No plan key in the body → 400; Stripe SDK never called."""
    from pebble.server import stripe_checkout

    h = FakeHandler({})
    stripe_checkout.run_create_session(h)
    assert h.status == 400
    fake_stripe.checkout.Session.create.assert_not_called()


def test_returns_400_when_plan_not_whitelisted(signed_in_user, stripe_env, fake_stripe):
    """Any plan other than starter / pro is rejected — never let the
    caller pick a price by free-text (or worse, supply a price ID)."""
    from pebble.server import stripe_checkout

    h = FakeHandler({"plan": "enterprise"})
    stripe_checkout.run_create_session(h)
    assert h.status == 400
    fake_stripe.checkout.Session.create.assert_not_called()


def test_returns_400_on_invalid_json_body(signed_in_user, stripe_env, fake_stripe):
    from pebble.server import stripe_checkout

    h = FakeHandler("{this is not json")
    stripe_checkout.run_create_session(h)
    assert h.status == 400
    fake_stripe.checkout.Session.create.assert_not_called()


# ---------- env config gates -----------------------------------------------

def test_returns_503_when_stripe_secret_key_missing(signed_in_user, monkeypatch, fake_stripe):
    """No STRIPE_SECRET_KEY in env → 503. We don't want to silently use
    whatever stripe.api_key happens to be set to (could be stale state
    from a prior test run, or empty)."""
    from pebble.server import stripe_checkout

    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.setenv("PEBBLE_STRIPE_STARTER_PRICE_ID", "price_starter_unit")
    monkeypatch.setenv("PEBBLE_PUBLIC_URL", "https://app.test.pebble")
    h = FakeHandler({"plan": "starter"})
    stripe_checkout.run_create_session(h)
    assert h.status == 503
    fake_stripe.checkout.Session.create.assert_not_called()


def test_returns_503_when_starter_price_id_missing(signed_in_user, monkeypatch, fake_stripe):
    """Bootstrap not run yet → the price-ID env var is missing for the
    requested plan. 503 is correct ('not configured on this instance')."""
    from pebble.server import stripe_checkout

    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    monkeypatch.delenv("PEBBLE_STRIPE_STARTER_PRICE_ID", raising=False)
    monkeypatch.setenv("PEBBLE_PUBLIC_URL", "https://app.test.pebble")
    h = FakeHandler({"plan": "starter"})
    stripe_checkout.run_create_session(h)
    assert h.status == 503
    fake_stripe.checkout.Session.create.assert_not_called()


def test_returns_503_when_pro_price_id_missing(signed_in_user, monkeypatch, fake_stripe):
    from pebble.server import stripe_checkout

    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    monkeypatch.delenv("PEBBLE_STRIPE_PRO_PRICE_ID", raising=False)
    monkeypatch.setenv("PEBBLE_PUBLIC_URL", "https://app.test.pebble")
    h = FakeHandler({"plan": "pro"})
    stripe_checkout.run_create_session(h)
    assert h.status == 503


# ---------- happy path -----------------------------------------------------

def test_starter_creates_session_with_starter_price(signed_in_user, stripe_env, fake_stripe):
    """plan=starter → SDK called with the starter price ID + subscription
    mode + user's email."""
    from pebble.server import stripe_checkout

    h = FakeHandler({"plan": "starter"})
    stripe_checkout.run_create_session(h)

    assert h.status == 200
    assert h.body == {
        "url": "https://checkout.stripe.com/c/pay/cs_test_session_id",
        "session_id": "cs_test_session_id",
    }

    fake_stripe.checkout.Session.create.assert_called_once()
    kwargs = fake_stripe.checkout.Session.create.call_args.kwargs
    assert kwargs["mode"] == "subscription"
    assert kwargs["line_items"] == [{"price": "price_starter_unit", "quantity": 1}]
    assert kwargs["customer_email"] == "marc@example.com"


def test_pro_creates_session_with_pro_price(signed_in_user, stripe_env, fake_stripe):
    from pebble.server import stripe_checkout

    h = FakeHandler({"plan": "pro"})
    stripe_checkout.run_create_session(h)

    assert h.status == 200
    kwargs = fake_stripe.checkout.Session.create.call_args.kwargs
    assert kwargs["line_items"] == [{"price": "price_pro_unit", "quantity": 1}]


def test_does_not_pass_payment_method_types(signed_in_user, stripe_env, fake_stripe):
    """Stripe best practices: NEVER include payment_method_types. Omitting
    it lets Stripe pick the optimal methods per region/device dynamically
    via Dashboard config. Hardcoding ['card'] tanks conversion."""
    from pebble.server import stripe_checkout

    h = FakeHandler({"plan": "starter"})
    stripe_checkout.run_create_session(h)
    kwargs = fake_stripe.checkout.Session.create.call_args.kwargs
    assert "payment_method_types" not in kwargs


def test_success_url_has_session_id_placeholder(signed_in_user, stripe_env, fake_stripe):
    """The {CHECKOUT_SESSION_ID} placeholder is mandatory — Stripe replaces
    it server-side with the real session id so v3's success page can
    look up the subscription."""
    from pebble.server import stripe_checkout

    h = FakeHandler({"plan": "starter"})
    stripe_checkout.run_create_session(h)
    kwargs = fake_stripe.checkout.Session.create.call_args.kwargs
    assert "{CHECKOUT_SESSION_ID}" in kwargs["success_url"]
    assert kwargs["success_url"].startswith("https://app.test.pebble/")
    assert kwargs["cancel_url"].startswith("https://app.test.pebble/")


def test_no_trial_days_when_env_unset(signed_in_user, stripe_env, fake_stripe, monkeypatch):
    """Chapter 9.5 — when PEBBLE_TRIAL_DAYS is not set, the Checkout
    Session must NOT include subscription_data.trial_period_days. Default
    behavior is immediate-charge."""
    monkeypatch.delenv("PEBBLE_TRIAL_DAYS", raising=False)
    from pebble.server import stripe_checkout

    h = FakeHandler({"plan": "starter"})
    stripe_checkout.run_create_session(h)
    sub_data = fake_stripe.checkout.Session.create.call_args.kwargs.get("subscription_data") or {}
    assert "trial_period_days" not in sub_data


def test_trial_days_passed_when_env_set_to_positive_int(
    signed_in_user, stripe_env, fake_stripe, monkeypatch,
):
    """When PEBBLE_TRIAL_DAYS=7, the Checkout Session gets a 7-day
    trial before the first charge."""
    monkeypatch.setenv("PEBBLE_TRIAL_DAYS", "7")
    from pebble.server import stripe_checkout

    h = FakeHandler({"plan": "starter"})
    stripe_checkout.run_create_session(h)
    sub_data = fake_stripe.checkout.Session.create.call_args.kwargs["subscription_data"]
    assert sub_data["trial_period_days"] == 7


def test_trial_days_zero_means_no_trial(signed_in_user, stripe_env, fake_stripe, monkeypatch):
    """PEBBLE_TRIAL_DAYS=0 is the explicit 'no trial' value — must NOT
    pass trial_period_days=0 to Stripe (Stripe's API treats 0 as a
    1-day trial)."""
    monkeypatch.setenv("PEBBLE_TRIAL_DAYS", "0")
    from pebble.server import stripe_checkout

    h = FakeHandler({"plan": "starter"})
    stripe_checkout.run_create_session(h)
    sub_data = fake_stripe.checkout.Session.create.call_args.kwargs.get("subscription_data") or {}
    assert "trial_period_days" not in sub_data


def test_trial_days_invalid_value_is_ignored(signed_in_user, stripe_env, fake_stripe, monkeypatch):
    """Non-int values (whitespace, 'abc', negatives) must be silently
    ignored — the endpoint stays functional rather than 500'ing on a
    misconfigured env."""
    from pebble.server import stripe_checkout

    for bad_value in ["abc", "-1", "7.5", "  ", "true"]:
        monkeypatch.setenv("PEBBLE_TRIAL_DAYS", bad_value)
        fake_stripe.checkout.Session.create.reset_mock()
        h = FakeHandler({"plan": "starter"})
        stripe_checkout.run_create_session(h)
        sub_data = fake_stripe.checkout.Session.create.call_args.kwargs.get("subscription_data") or {}
        assert "trial_period_days" not in sub_data, f"bad value {bad_value!r} leaked into Checkout"


def test_passes_pebble_user_id_in_metadata(signed_in_user, stripe_env, fake_stripe):
    """Stamp the Supabase user id on the Checkout Session as metadata so
    the webhook can look up which Pebble user a subscription belongs to
    (the customer_email could change later; the uuid is stable)."""
    from pebble.server import stripe_checkout

    h = FakeHandler({"plan": "starter"})
    stripe_checkout.run_create_session(h)
    kwargs = fake_stripe.checkout.Session.create.call_args.kwargs
    md = kwargs.get("metadata") or {}
    assert md.get("pebble_user_id") == "uuid-marc-abc"
    # The same id also needs to propagate to the subscription itself so
    # renewals/cancellations carry it without us joining on email.
    sub_md = (kwargs.get("subscription_data") or {}).get("metadata") or {}
    assert sub_md.get("pebble_user_id") == "uuid-marc-abc"


# ---------- error handling -------------------------------------------------

def test_returns_502_when_stripe_raises(signed_in_user, stripe_env, fake_stripe):
    """Stripe network/auth errors → 502 (upstream problem), NOT 500. v3
    can show 'try again' rather than 'something went wrong on our end'."""
    from pebble.server import stripe_checkout

    fake_stripe.error = stripe.error  # propagate real error classes
    fake_stripe.checkout.Session.create.side_effect = stripe.error.APIConnectionError(
        "boom"
    )
    h = FakeHandler({"plan": "starter"})
    stripe_checkout.run_create_session(h)
    assert h.status == 502


def test_does_not_log_stripe_secret_or_user_email(signed_in_user, stripe_env, fake_stripe, caplog):
    """Privacy regression — even on the happy path, neither the secret
    key nor the user's email may appear in engine logs at INFO+."""
    import logging
    from pebble.server import stripe_checkout

    caplog.set_level(logging.INFO, logger="pebble")
    h = FakeHandler({"plan": "starter"})
    stripe_checkout.run_create_session(h)
    blob = caplog.text
    assert "sk_test_unit-test-key" not in blob
    assert "marc@example.com" not in blob
