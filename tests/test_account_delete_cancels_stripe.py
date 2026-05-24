"""E2E test: account deletion cancels active Stripe subscription
BEFORE the 14-day cooling-off period starts. Otherwise users keep
getting billed for the period between clicking delete and the actual
data scrub. Audit log captures the cancellation event."""
from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

import pebble.server.account as account_mod
from pebble.server import account as account_server


# ── shared fixtures ────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _supabase_env(monkeypatch):
    monkeypatch.setenv("PEBBLE_SUPABASE_URL", "https://proj.supabase.co")
    monkeypatch.setenv("PEBBLE_SUPABASE_SERVICE_ROLE_KEY", "service-role-jwt-fake")
    monkeypatch.setenv("PEBBLE_SUPABASE_ANON_KEY", "anon-key-fake")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    monkeypatch.delenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", raising=False)


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    account_mod._reset_delete_rate_limiter_for_tests()
    yield


@pytest.fixture()
def output_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("pebble.server.account._output_dir", lambda: tmp_path)
    return tmp_path


# ── fake handler (mirrors test_account_endpoint.py) ───────────────────────────

_FAKE_USER = {"id": "u-test-001", "email": "test@example.com"}

_DELETE_BODY = json.dumps({"email_confirmation": "test@example.com"}).encode()


class _FakeHandler:
    def __init__(self, body: bytes = _DELETE_BODY, client_ip: str = "127.0.0.1"):
        self.headers: dict = {
            "Authorization": "Bearer ey.fake.jwt",
            "Content-Length": str(len(body)),
            "Content-Type": "application/json",
        }
        self.client_address = (client_ip, 12345)
        self.rfile = io.BytesIO(body)
        self.status: int | None = None
        self.json_body: dict | None = None

    def _json(self, status: int, payload: dict, extra_headers=None):
        self.status = status
        self.json_body = payload


# ── helpers ────────────────────────────────────────────────────────────────────

def _make_sub_file(output_dir: Path, status: str, sub_id: str = "sub_test456") -> None:
    """Write a subscription.json for the test user."""
    user_dir = output_dir / ".users" / _FAKE_USER["id"]
    user_dir.mkdir(parents=True, exist_ok=True)
    (user_dir / "subscription.json").write_text(json.dumps({
        "status": status,
        "plan": "pro",
        "stripe_customer_id": "cus_test123",
        "stripe_subscription_id": sub_id,
    }), encoding="utf-8")


# ── tests ──────────────────────────────────────────────────────────────────────

def test_delete_cancels_active_stripe_subscription(monkeypatch, output_dir):
    """active subscription → _cancel_stripe_subscription called with the sub id."""
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda token: _FAKE_USER)

    _make_sub_file(output_dir, "active", "sub_test456")

    cancel_calls = []
    monkeypatch.setattr(account_mod, "_cancel_stripe_subscription",
                        lambda sub_id: cancel_calls.append(sub_id) or True)

    audit_calls = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_calls.append(kw))

    email_calls = []
    monkeypatch.setattr("pebble.email.send_account_deletion_scheduled",
                        lambda email, cooling_off_ends: email_calls.append((email, cooling_off_ends)))

    h = _FakeHandler()
    account_server.run_delete_account(h)

    assert h.status == 200, f"got {h.status}: {h.json_body}"
    assert cancel_calls == ["sub_test456"]
    assert any(c.get("event_type") == "stripe_subscription_canceled" for c in audit_calls)
    assert any(c.get("event_type") == "account_delete_requested" for c in audit_calls)
    assert len(email_calls) == 1
    assert email_calls[0][0] == "test@example.com"


def test_delete_skips_cancel_when_no_subscription(monkeypatch, output_dir):
    """Free-tier user (no subscription.json) → cancel not called, still scheduled."""
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda token: _FAKE_USER)

    cancel_calls = []
    monkeypatch.setattr(account_mod, "_cancel_stripe_subscription",
                        lambda sub_id: cancel_calls.append(sub_id) or True)

    audit_calls = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_calls.append(kw))

    monkeypatch.setattr("pebble.email.send_account_deletion_scheduled",
                        lambda email, cooling_off_ends: None)

    h = _FakeHandler()
    account_server.run_delete_account(h)

    assert h.status == 200
    assert cancel_calls == []
    # account_delete_requested still logged even without a subscription
    assert any(c.get("event_type") == "account_delete_requested" for c in audit_calls)


def test_delete_skips_cancel_when_subscription_already_canceled(monkeypatch, output_dir):
    """status=canceled in subscription.json → don't double-cancel."""
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda token: _FAKE_USER)

    _make_sub_file(output_dir, "canceled", "sub_old")

    cancel_calls = []
    monkeypatch.setattr(account_mod, "_cancel_stripe_subscription",
                        lambda sub_id: cancel_calls.append(sub_id) or True)

    monkeypatch.setattr("pebble.audit_log.log_event_for_handler", lambda **kw: None)
    monkeypatch.setattr("pebble.email.send_account_deletion_scheduled",
                        lambda email, cooling_off_ends: None)

    h = _FakeHandler()
    account_server.run_delete_account(h)

    assert h.status == 200
    assert cancel_calls == []  # not in (active, trialing, past_due) — skipped


def test_delete_still_proceeds_when_stripe_cancel_fails(monkeypatch, output_dir):
    """Stripe down or sub already gone → log the failure but proceed with delete."""
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda token: _FAKE_USER)

    _make_sub_file(output_dir, "active", "sub_active")

    monkeypatch.setattr(account_mod, "_cancel_stripe_subscription",
                        lambda sub_id: False)  # cancel fails

    audit_calls = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_calls.append(kw))

    monkeypatch.setattr("pebble.email.send_account_deletion_scheduled",
                        lambda email, cooling_off_ends: None)

    h = _FakeHandler()
    account_server.run_delete_account(h)

    assert h.status == 200
    # Deletion proceeds even on Stripe failure — log the failed cancel for
    # operator follow-up.
    assert any(c.get("event_type") == "stripe_subscription_cancel_failed" for c in audit_calls)
    assert any(c.get("event_type") == "account_delete_requested" for c in audit_calls)
