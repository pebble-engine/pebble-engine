"""Tests for POST /api/internal/stripe-webhook — receives Stripe events,
verifies the HMAC signature, and updates the user's subscription sentinel.

The Stripe SDK's signature verifier is patched per-test so no test ever
attempts real cryptographic verification — we assert on the side effects
of receiving a verified event.
"""
from __future__ import annotations

import json
from io import BytesIO
from typing import Any
from unittest.mock import MagicMock

import pytest
import stripe

import pebble_engine


WEBHOOK_SECRET = "whsec_test_unit_secret"


# ---------- handler + fixtures --------------------------------------------

class FakeHandler:
    def __init__(self, body: dict | bytes | str | None = None,
                 sig_header: str | None = "t=1,v1=fakefakefake"):
        if isinstance(body, dict):
            raw = json.dumps(body).encode("utf-8")
        elif isinstance(body, str):
            raw = body.encode("utf-8")
        elif isinstance(body, bytes):
            raw = body
        else:
            raw = b""
        self.rfile = BytesIO(raw)
        self.headers: dict[str, str] = {"Content-Length": str(len(raw))}
        if sig_header is not None:
            self.headers["Stripe-Signature"] = sig_header
        self.client_address = ("127.0.0.1", 12345)
        self.status: int | None = None
        self.body: dict | None = None

    def _json(self, status: int, payload: dict, extra_headers=None) -> None:  # noqa: ARG002
        self.status = status
        self.body = payload


@pytest.fixture
def with_secret(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", WEBHOOK_SECRET)


@pytest.fixture
def output_root(tmp_path, monkeypatch):
    """Redirect output/.users/... writes into a tmp dir so tests don't
    touch the developer's real output/ directory."""
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    return tmp_path


def _subscription_event(
    event_type: str = "customer.subscription.created",
    *,
    pebble_user_id: str | None = "uuid-marc-abc",
    plan: str | None = "starter",
    status: str = "active",
    period_end: int = 1893456000,  # 2030-01-01
    subscription_id: str = "sub_test_abc",
    customer_id: str | None = "cus_test_abc",
    extra_meta: dict | None = None,
) -> dict:
    """Build a Stripe event dict shaped like the real `customer.subscription.*`
    payloads, with the metadata we stamp in checkout."""
    metadata: dict[str, Any] = {}
    if pebble_user_id is not None:
        metadata["pebble_user_id"] = pebble_user_id
    if plan is not None:
        metadata["pebble_plan"] = plan
    if extra_meta:
        metadata.update(extra_meta)
    obj: dict[str, Any] = {
        "id":                  subscription_id,
        "object":              "subscription",
        "status":              status,
        "current_period_end":  period_end,
        "metadata":            metadata,
        "items": {"data": [{"price": {"id": "price_test"}}]},
    }
    if customer_id is not None:
        obj["customer"] = customer_id
    return {
        "id": "evt_test",
        "type": event_type,
        "data": {"object": obj},
    }


@pytest.fixture
def verified_event(monkeypatch):
    """Patch stripe.Webhook.construct_event to return whatever event the
    test asks for. The patcher is a function so tests can supply different
    event shapes."""

    def _patch(event_dict: dict) -> MagicMock:
        m = MagicMock(return_value=event_dict)
        monkeypatch.setattr(stripe.Webhook, "construct_event", m)
        return m
    return _patch


@pytest.fixture
def rejecting_signature(monkeypatch):
    """Patch construct_event to ALWAYS raise SignatureVerificationError —
    simulates a spoofed/tampered request."""
    def boom(*args, **kwargs):
        raise stripe.error.SignatureVerificationError("bad sig", "raw")
    monkeypatch.setattr(stripe.Webhook, "construct_event", boom)


# ---------- config / auth gates --------------------------------------------

def test_returns_503_when_webhook_secret_not_configured(monkeypatch):
    """No STRIPE_WEBHOOK_SECRET set → 503 — visible misconfiguration, not
    a silent accept-everything."""
    from pebble.server import stripe_webhook

    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
    h = FakeHandler({"id": "evt"})
    stripe_webhook.run_stripe_webhook(h)
    assert h.status == 503


def test_returns_400_when_signature_header_missing(with_secret):
    """No Stripe-Signature header → 400. Not 401 — Stripe's docs are clear
    this is a malformed request, not an auth challenge."""
    from pebble.server import stripe_webhook

    h = FakeHandler({"id": "evt"}, sig_header=None)
    stripe_webhook.run_stripe_webhook(h)
    assert h.status == 400


def test_returns_400_when_signature_invalid(with_secret, rejecting_signature):
    """SignatureVerificationError → 400. Critical defense: never act on
    an event whose HMAC didn't verify, even if the payload 'looks' valid."""
    from pebble.server import stripe_webhook

    h = FakeHandler({"id": "evt"})
    stripe_webhook.run_stripe_webhook(h)
    assert h.status == 400


# ---------- body parsing ---------------------------------------------------

def test_returns_400_on_huge_body(with_secret):
    """Stripe webhook payloads are small (~few KB). 1 MB is abuse."""
    from pebble.server import stripe_webhook

    huge = b"x" * (1024 * 1024)
    h = FakeHandler(huge)
    stripe_webhook.run_stripe_webhook(h)
    assert h.status == 400


# ---------- subscription side-effects --------------------------------------

def test_subscription_created_writes_sentinel(
    with_secret, output_root, verified_event,
):
    """Verified subscription.created event → output/.users/<uid>/subscription.json
    populated with status, plan, period_end, subscription_id."""
    from pebble.server import stripe_webhook

    verified_event(_subscription_event(
        event_type="customer.subscription.created",
        pebble_user_id="uuid-marc-abc",
        plan="starter",
        status="active",
        period_end=1893456000,
        subscription_id="sub_starter_one",
    ))

    h = FakeHandler({"placeholder": "real-body-is-bytes"})
    stripe_webhook.run_stripe_webhook(h)

    assert h.status == 200
    sentinel = output_root / ".users" / "uuid-marc-abc" / "subscription.json"
    assert sentinel.exists()
    data = json.loads(sentinel.read_text(encoding="utf-8"))
    assert data["status"] == "active"
    assert data["plan"] == "starter"
    assert data["stripe_subscription_id"] == "sub_starter_one"
    assert data["current_period_end"] == 1893456000


def test_subscription_created_stamps_customer_id(
    with_secret, output_root, verified_event,
):
    """The Stripe customer_id MUST land in the sentinel — the billing
    portal endpoint reads it to mint a customer-portal session, and we
    don't want to call Stripe to resolve the customer per portal hit."""
    from pebble.server import stripe_webhook

    verified_event(_subscription_event(
        event_type="customer.subscription.created",
        customer_id="cus_marc_real",
    ))
    stripe_webhook.run_stripe_webhook(FakeHandler({}))

    sentinel = output_root / ".users" / "uuid-marc-abc" / "subscription.json"
    data = json.loads(sentinel.read_text(encoding="utf-8"))
    assert data["stripe_customer_id"] == "cus_marc_real"


def test_subscription_updated_overwrites_sentinel(
    with_secret, output_root, verified_event,
):
    """Same user, second event → file overwritten with latest state."""
    from pebble.server import stripe_webhook

    # First event: status active
    verified_event(_subscription_event(
        event_type="customer.subscription.created",
        plan="starter", status="active", subscription_id="sub_one",
    ))
    stripe_webhook.run_stripe_webhook(FakeHandler({}))

    # Second event: same user, plan upgraded to pro
    verified_event(_subscription_event(
        event_type="customer.subscription.updated",
        plan="pro", status="active", subscription_id="sub_one",
    ))
    stripe_webhook.run_stripe_webhook(FakeHandler({}))

    sentinel = output_root / ".users" / "uuid-marc-abc" / "subscription.json"
    data = json.loads(sentinel.read_text(encoding="utf-8"))
    assert data["plan"] == "pro"


def test_subscription_deleted_marks_canceled(
    with_secret, output_root, verified_event,
):
    """customer.subscription.deleted → status: canceled."""
    from pebble.server import stripe_webhook

    verified_event(_subscription_event(
        event_type="customer.subscription.deleted",
        status="canceled",
        subscription_id="sub_one",
    ))
    h = FakeHandler({})
    stripe_webhook.run_stripe_webhook(h)

    sentinel = output_root / ".users" / "uuid-marc-abc" / "subscription.json"
    data = json.loads(sentinel.read_text(encoding="utf-8"))
    assert data["status"] == "canceled"


def test_event_without_pebble_user_id_is_200_and_skipped(
    with_secret, output_root, verified_event,
):
    """Older subscriptions (or test-mode noise) without our metadata
    must NOT crash — return 200 so Stripe stops retrying, no write."""
    from pebble.server import stripe_webhook

    verified_event(_subscription_event(pebble_user_id=None))
    h = FakeHandler({})
    stripe_webhook.run_stripe_webhook(h)
    assert h.status == 200
    # No file created anywhere — there's no user to attribute it to.
    assert list(output_root.glob(".users/*/subscription.json")) == []


def test_unknown_event_type_is_200_and_skipped(
    with_secret, output_root, verified_event,
):
    """Stripe sends many event types; we only care about the four we
    subscribed to. Anything else → 200 + skip so we don't get retried."""
    from pebble.server import stripe_webhook

    verified_event({"id": "evt", "type": "charge.dispute.created", "data": {"object": {}}})
    h = FakeHandler({})
    stripe_webhook.run_stripe_webhook(h)
    assert h.status == 200
    assert list(output_root.glob(".users/*/subscription.json")) == []


# ---------- privacy regressions --------------------------------------------

def test_sentinel_never_contains_card_data(
    with_secret, output_root, verified_event,
):
    """Even if Stripe attaches a payment_method object with last4/etc to
    the event payload (real-world events do), our sentinel file must NOT
    contain it — we only persist the subscription state we need."""
    from pebble.server import stripe_webhook

    event = _subscription_event()
    event["data"]["object"]["default_payment_method"] = {
        "id": "pm_test",
        "card": {"last4": "4242", "brand": "visa", "exp_year": 2030, "exp_month": 12},
    }
    verified_event(event)
    stripe_webhook.run_stripe_webhook(FakeHandler({}))

    sentinel = output_root / ".users" / "uuid-marc-abc" / "subscription.json"
    text = sentinel.read_text(encoding="utf-8")
    assert "4242" not in text
    assert "last4" not in text
    assert "pm_test" not in text
    assert "visa" not in text


def test_does_not_log_card_data(with_secret, output_root, verified_event, caplog):
    """Card data must NOT appear in engine logs at INFO+ either."""
    import logging
    from pebble.server import stripe_webhook

    event = _subscription_event()
    event["data"]["object"]["default_payment_method"] = {
        "card": {"last4": "4242", "brand": "visa"},
    }
    verified_event(event)
    caplog.set_level(logging.INFO, logger="pebble")
    stripe_webhook.run_stripe_webhook(FakeHandler({}))
    assert "4242" not in caplog.text
