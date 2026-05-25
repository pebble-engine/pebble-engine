"""Tests for /api/account/invoices — returns last N Stripe invoices."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import pebble.server.billing_api as billing_api


class _FakeHandler:
    def __init__(self, *, path="/api/account/invoices"):
        self.path = path
        self.headers = {"Authorization": "Bearer test"}
        self.client_address = ("127.0.0.1", 0)
        self.responses: list[tuple[int, dict]] = []

    def _json(self, status, body):
        self.responses.append((status, body))


def test_invoices_returns_empty_for_free_user(tmp_path, monkeypatch):
    """No subscription.json → returns {invoices: []}."""
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(billing_api, "OUTPUT_DIR", out)
    monkeypatch.setattr(billing_api, "require_user",
        lambda h: {"id": "u-1", "email": "test@example.com"})

    h = _FakeHandler()
    billing_api.run_get_invoice_history(h)
    assert h.responses[-1][0] == 200
    assert h.responses[-1][1]["invoices"] == []


def test_invoices_lists_stripe_invoices(tmp_path, monkeypatch):
    """Subscribed user → calls Stripe + returns formatted invoice rows."""
    out = tmp_path / "output"
    out.mkdir()
    sub_dir = out / ".users" / "u-1"
    sub_dir.mkdir(parents=True)
    (sub_dir / "subscription.json").write_text(json.dumps({
        "stripe_customer_id": "cus_test",
        "stripe_subscription_id": "sub_test",
        "status": "active", "plan": "pro",
    }))
    monkeypatch.setattr(billing_api, "OUTPUT_DIR", out)
    monkeypatch.setattr(billing_api, "require_user",
        lambda h: {"id": "u-1", "email": "test@example.com"})

    # Mock Stripe SDK call
    fake_invoices = [
        MagicMock(id="in_1", number="0001",
                  amount_paid=4900, currency="usd",
                  status="paid", created=1716000000,
                  invoice_pdf="https://stripe.com/inv1.pdf",
                  hosted_invoice_url="https://stripe.com/inv1"),
        MagicMock(id="in_2", number="0002",
                  amount_paid=4900, currency="usd",
                  status="paid", created=1718000000,
                  invoice_pdf="https://stripe.com/inv2.pdf",
                  hosted_invoice_url="https://stripe.com/inv2"),
    ]
    monkeypatch.setattr(billing_api, "_list_stripe_invoices",
        lambda customer_id, limit: fake_invoices)

    h = _FakeHandler()
    billing_api.run_get_invoice_history(h)
    assert h.responses[-1][0] == 200
    invs = h.responses[-1][1]["invoices"]
    assert len(invs) == 2
    assert invs[0]["number"] == "0001"
    assert invs[0]["amount_cents"] == 4900
    assert invs[0]["currency"] == "usd"
    assert invs[0]["status"] == "paid"
    assert invs[0]["pdf_url"]    == "https://stripe.com/inv1.pdf"
    assert invs[0]["hosted_url"] == "https://stripe.com/inv1"


def test_invoices_500_on_stripe_failure(tmp_path, monkeypatch):
    """Stripe API down → 500 with friendly message (no stack)."""
    out = tmp_path / "output"
    out.mkdir()
    sub_dir = out / ".users" / "u-1"
    sub_dir.mkdir(parents=True)
    (sub_dir / "subscription.json").write_text(json.dumps({
        "stripe_customer_id": "cus_test", "status": "active", "plan": "pro",
    }))
    monkeypatch.setattr(billing_api, "OUTPUT_DIR", out)
    monkeypatch.setattr(billing_api, "require_user",
        lambda h: {"id": "u-1", "email": "test@example.com"})
    monkeypatch.setattr(billing_api, "_list_stripe_invoices",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("stripe down")))

    h = _FakeHandler()
    billing_api.run_get_invoice_history(h)
    assert h.responses[-1][0] == 500


def test_invoices_401_without_user(monkeypatch):
    """No bearer → 401 (require_user handles it)."""
    monkeypatch.setattr(billing_api, "require_user", lambda h: None)
    h = _FakeHandler()
    billing_api.run_get_invoice_history(h)
    assert h.responses == []  # require_user already responded
