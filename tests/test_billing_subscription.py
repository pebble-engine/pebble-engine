"""Tests for GET /api/billing/subscription — returns the current user's
subscription state for v3's 'current plan' badge.

Pure read endpoint: takes a Bearer JWT, reads the same sentinel the
webhook wrote, returns a curated subset of fields (never the customer_id
or any internal metadata).
"""
from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import MagicMock

import pytest

import pebble_engine


class FakeHandler:
    def __init__(self, authorization: str | None = "Bearer t"):
        self.rfile = BytesIO(b"")
        self.headers: dict[str, str] = {"Content-Length": "0"}
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
        "pebble.server.billing_subscription.require_user",
        lambda h: user,
    )
    return user


@pytest.fixture
def output_root(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    return tmp_path


def _write_sentinel(output_root, user_id: str, **fields):
    """Write a subscription.json sentinel matching what the webhook would
    produce. Defaults to an active starter for happy-path tests; tests can
    override fields for edge cases."""
    p = output_root / ".users" / user_id
    p.mkdir(parents=True, exist_ok=True)
    payload = {
        "status":                 "active",
        "plan":                   "starter",
        "stripe_subscription_id": "sub_marc",
        "stripe_customer_id":     "cus_marc",
        "current_period_end":     1893456000,
        "updated_at":             "2026-05-17T00:00:00+00:00",
        "last_event_id":          "evt_pinned",
        "last_event_created":     1893456000,
    }
    payload.update(fields)
    (p / "subscription.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8",
    )


# ---- auth gate ------------------------------------------------------------

def test_returns_401_when_require_user_says_no(monkeypatch, output_root):
    from pebble.server import billing_subscription

    def stub(h):
        h._json(401, {"error": "sign in required"})
        return None

    monkeypatch.setattr(billing_subscription, "require_user", stub)
    h = FakeHandler()
    billing_subscription.run_get_subscription(h)
    assert h.status == 401


# ---- no-subscription ------------------------------------------------------

def test_returns_200_with_null_plan_when_no_sentinel(signed_in_user, output_root):
    """No sentinel == user has never subscribed. Return 200 + {plan: null}
    rather than 404 so v3 can branch on the field instead of try/catch."""
    from pebble.server import billing_subscription

    h = FakeHandler()
    billing_subscription.run_get_subscription(h)
    assert h.status == 200
    assert h.body == {"plan": None, "status": None, "current_period_end": None}


def test_returns_200_with_null_plan_when_sentinel_is_corrupt(signed_in_user, output_root):
    """A truncated/malformed sentinel must not 500 — treat as 'no sub.'"""
    from pebble.server import billing_subscription

    p = output_root / ".users" / "uuid-marc-abc"
    p.mkdir(parents=True)
    (p / "subscription.json").write_text("not-json{")
    h = FakeHandler()
    billing_subscription.run_get_subscription(h)
    assert h.status == 200
    assert h.body["plan"] is None


# ---- happy path -----------------------------------------------------------

def test_returns_active_subscription(signed_in_user, output_root):
    from pebble.server import billing_subscription

    _write_sentinel(output_root, "uuid-marc-abc",
                    plan="starter", status="active",
                    current_period_end=1893456000)
    h = FakeHandler()
    billing_subscription.run_get_subscription(h)
    assert h.status == 200
    assert h.body == {
        "plan":               "starter",
        "status":             "active",
        "current_period_end": 1893456000,
    }


def test_returns_canceled_subscription(signed_in_user, output_root):
    from pebble.server import billing_subscription

    _write_sentinel(output_root, "uuid-marc-abc",
                    plan="pro", status="canceled")
    h = FakeHandler()
    billing_subscription.run_get_subscription(h)
    assert h.status == 200
    assert h.body["plan"] == "pro"
    assert h.body["status"] == "canceled"


# ---- privacy --------------------------------------------------------------

def test_never_exposes_customer_id_or_subscription_id(signed_in_user, output_root):
    """The sentinel HAS stripe_customer_id + stripe_subscription_id, but
    this endpoint must NOT echo them back to the client. v3 doesn't need
    them — the portal endpoint resolves the customer server-side."""
    from pebble.server import billing_subscription

    _write_sentinel(output_root, "uuid-marc-abc",
                    stripe_customer_id="cus_marc_real",
                    stripe_subscription_id="sub_marc_real")
    h = FakeHandler()
    billing_subscription.run_get_subscription(h)
    body_text = json.dumps(h.body or {})
    assert "cus_marc_real" not in body_text
    assert "sub_marc_real" not in body_text
    # Internal dedup fields should also not leak.
    assert "last_event_id" not in (h.body or {})
    assert "last_event_created" not in (h.body or {})


def test_lowercases_user_id_for_path_lookup(monkeypatch, output_root):
    """Mirror the billing_portal NLM Finding #2 fix here too — same
    sentinel location, same case-normalization requirement."""
    from pebble.server import billing_subscription

    monkeypatch.setattr(
        "pebble.server.billing_subscription.require_user",
        lambda h: {"id": "UUID-MARC-ABC", "email": "marc@example.com"},
    )
    _write_sentinel(output_root, "uuid-marc-abc",
                    plan="pro", status="active")
    h = FakeHandler()
    billing_subscription.run_get_subscription(h)
    assert h.status == 200
    assert h.body["plan"] == "pro"
