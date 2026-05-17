"""Tests for POST /api/billing/portal — mints a Stripe Customer Portal
session so users can self-serve plan changes, cancellation, and payment
method updates.
"""
from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import MagicMock

import pytest
import stripe

import pebble_engine


class FakeHandler:
    """Mirror of the stripe_checkout FakeHandler — no body needed for
    the portal endpoint but we keep the same shape for consistency."""

    def __init__(self, body: dict | None = None, authorization: str | None = "Bearer t"):
        raw = json.dumps(body or {}).encode("utf-8")
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
    user = {"id": "uuid-marc-abc", "email": "marc@example.com"}
    monkeypatch.setattr(
        "pebble.server.billing_portal.require_user",
        lambda h: user,
    )
    return user


@pytest.fixture
def output_root(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    return tmp_path


@pytest.fixture
def stripe_env(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_unit-test-key")
    monkeypatch.setenv("PEBBLE_PUBLIC_URL", "https://app.test.pebble")


@pytest.fixture
def fake_stripe(monkeypatch):
    fake = MagicMock()
    fake.billing_portal.Session.create.return_value = MagicMock(
        id="bps_test_session",
        url="https://billing.stripe.com/session/test-link",
    )
    # Propagate the real exception classes through the mock so the
    # endpoint's `except stripe.error.StripeError:` works against
    # MagicMock'd stripe. Without this, attribute access resolves to a
    # new MagicMock which isn't catchable.
    fake.error = stripe.error
    monkeypatch.setattr("pebble.server.billing_portal.stripe", fake)
    return fake


def _write_subscription_sentinel(output_root, user_id: str,
                                 *, customer_id: str = "cus_marc_real"):
    p = output_root / ".users" / user_id
    p.mkdir(parents=True, exist_ok=True)
    (p / "subscription.json").write_text(json.dumps({
        "status": "active",
        "plan": "starter",
        "stripe_subscription_id": "sub_test",
        "stripe_customer_id": customer_id,
        "current_period_end": 1893456000,
        "updated_at": "2026-05-17T00:00:00+00:00",
    }), encoding="utf-8")


# ---------- auth gate ------------------------------------------------------

def test_returns_401_when_require_user_says_no(monkeypatch, output_root, stripe_env):
    from pebble.server import billing_portal

    def stub(h):
        h._json(401, {"error": "sign in required"})
        return None

    monkeypatch.setattr(billing_portal, "require_user", stub)
    h = FakeHandler()
    billing_portal.run_billing_portal(h)
    assert h.status == 401


# ---------- env gate -------------------------------------------------------

def test_returns_503_when_stripe_secret_key_missing(
    signed_in_user, output_root, monkeypatch, fake_stripe,
):
    from pebble.server import billing_portal

    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.setenv("PEBBLE_PUBLIC_URL", "https://app.test.pebble")
    _write_subscription_sentinel(output_root, "uuid-marc-abc")
    h = FakeHandler()
    billing_portal.run_billing_portal(h)
    assert h.status == 503
    fake_stripe.billing_portal.Session.create.assert_not_called()


# ---------- no-subscription cases ------------------------------------------

def test_returns_404_when_user_has_no_subscription(
    signed_in_user, output_root, stripe_env, fake_stripe,
):
    """User has never subscribed → no sentinel. Surface a friendly 404
    so v3 can prompt 'choose a plan first'."""
    from pebble.server import billing_portal

    h = FakeHandler()
    billing_portal.run_billing_portal(h)
    assert h.status == 404
    fake_stripe.billing_portal.Session.create.assert_not_called()


def test_returns_404_when_sentinel_lacks_customer_id(
    signed_in_user, output_root, stripe_env, fake_stripe,
):
    """Defensive — sentinel exists but somehow has no customer_id. Don't
    try to call Stripe with empty customer; treat as no subscription."""
    from pebble.server import billing_portal

    _write_subscription_sentinel(output_root, "uuid-marc-abc", customer_id="")
    h = FakeHandler()
    billing_portal.run_billing_portal(h)
    assert h.status == 404


def test_returns_404_when_sentinel_is_corrupt(
    signed_in_user, output_root, stripe_env, fake_stripe,
):
    """Malformed JSON in subscription.json → treat as no subscription
    rather than 500. Webhook will overwrite it on the next event."""
    from pebble.server import billing_portal

    p = output_root / ".users" / "uuid-marc-abc"
    p.mkdir(parents=True)
    (p / "subscription.json").write_text("not-json{")
    h = FakeHandler()
    billing_portal.run_billing_portal(h)
    assert h.status == 404


# ---------- happy path -----------------------------------------------------

def test_creates_portal_session_with_customer_id(
    signed_in_user, output_root, stripe_env, fake_stripe,
):
    """Sentinel has customer_id → SDK called with that customer + return
    URL, response body has the portal URL."""
    from pebble.server import billing_portal

    _write_subscription_sentinel(output_root, "uuid-marc-abc",
                                 customer_id="cus_real_marc")
    h = FakeHandler()
    billing_portal.run_billing_portal(h)

    assert h.status == 200
    assert h.body == {"url": "https://billing.stripe.com/session/test-link"}
    kwargs = fake_stripe.billing_portal.Session.create.call_args.kwargs
    assert kwargs["customer"] == "cus_real_marc"
    assert kwargs["return_url"].startswith("https://app.test.pebble/")


def test_return_url_points_to_settings(
    signed_in_user, output_root, stripe_env, fake_stripe,
):
    """User finishes in the Stripe portal → bounces back to v3's settings
    page (so they immediately see their updated plan)."""
    from pebble.server import billing_portal

    _write_subscription_sentinel(output_root, "uuid-marc-abc")
    h = FakeHandler()
    billing_portal.run_billing_portal(h)
    kwargs = fake_stripe.billing_portal.Session.create.call_args.kwargs
    assert "settings" in kwargs["return_url"]


# ---------- error handling -------------------------------------------------

def test_returns_502_when_stripe_raises(
    signed_in_user, output_root, stripe_env, fake_stripe,
):
    from pebble.server import billing_portal

    _write_subscription_sentinel(output_root, "uuid-marc-abc")
    fake_stripe.billing_portal.Session.create.side_effect = (
        stripe.error.APIConnectionError("boom")
    )
    h = FakeHandler()
    billing_portal.run_billing_portal(h)
    assert h.status == 502


# ---------- privacy regression --------------------------------------------

def test_does_not_log_customer_id_or_email(
    signed_in_user, output_root, stripe_env, fake_stripe, caplog,
):
    """Customer IDs and emails are PII — never INFO-log them."""
    import logging
    from pebble.server import billing_portal

    _write_subscription_sentinel(output_root, "uuid-marc-abc",
                                 customer_id="cus_sensitive_id")
    caplog.set_level(logging.INFO, logger="pebble")
    h = FakeHandler()
    billing_portal.run_billing_portal(h)
    assert "cus_sensitive_id" not in caplog.text
    assert "marc@example.com" not in caplog.text
