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


# ---- Fix 5 (2026-05-24): cancel-deletion warns when Stripe was lost -------

_CANCEL_BODY = json.dumps({}).encode()


def test_cancel_deletion_warns_when_stripe_sub_was_cancelled(monkeypatch, output_dir):
    """User schedules delete (Stripe sub cancelled), then changes their mind
    inside the cooling-off period. The response MUST surface that they lost
    their Pro plan as a side-effect — losing Pro silently is bad UX."""
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda token: _FAKE_USER)

    # Step 1: schedule deletion (Stripe sub gets cancelled).
    _make_sub_file(output_dir, "active", "sub_active123")
    monkeypatch.setattr(account_mod, "_cancel_stripe_subscription",
                        lambda sub_id: True)
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: None)
    monkeypatch.setattr("pebble.email.send_account_deletion_scheduled",
                        lambda email, cooling_off_ends: None)

    delete_h = _FakeHandler()
    account_server.run_delete_account(delete_h)
    assert delete_h.status == 200, f"setup: scheduling failed: {delete_h.json_body}"

    # Confirm the marker was written to subscription.json
    sub_path = output_dir / ".users" / _FAKE_USER["id"] / "subscription.json"
    sub_data = json.loads(sub_path.read_text(encoding="utf-8"))
    assert sub_data.get("cancelled_by_delete_at"), \
        "delete handler must stamp cancelled_by_delete_at when it cancels a Stripe sub"

    # Step 2: cancel deletion. Response MUST include the warning.
    audit_after: list[dict] = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_after.append(kw))

    cancel_h = _FakeHandler(body=_CANCEL_BODY)
    account_server.run_cancel_deletion(cancel_h)

    assert cancel_h.status == 200
    body = cancel_h.json_body or {}
    assert body.get("ok") is True
    assert body.get("cancelled") is True
    warning = body.get("subscription_warning") or ""
    assert "Pro" in warning or "plan" in warning.lower(), \
        f"missing subscription_warning in cancel response: {body}"
    assert "/pricing" in warning, \
        f"warning must point at /pricing to resume: {body}"

    # Audit event: account_delete_cancelled with had_stripe_sub_cancelled=True
    delete_cancelled = [c for c in audit_after
                        if c.get("event_type") == "account_delete_cancelled"]
    assert delete_cancelled, \
        f"missing account_delete_cancelled audit event: {[c.get('event_type') for c in audit_after]}"
    assert delete_cancelled[0].get("metadata", {}).get("had_stripe_sub_cancelled") is True


# ---- Fix 1 (2026-05-24): AdminError on hard-delete emits audit event ------

def test_execute_deletion_admin_error_emits_audit_event(monkeypatch, output_dir):
    """When delete_user(user_id) raises AdminError, the failure MUST be
    surfaced via audit_log.log_event with event_type='account_delete_failed'.
    Before this fix the failure was log.error-only — a user whose hard-delete
    kept failing silently had no audit trail to investigate."""
    from datetime import datetime, timedelta, timezone
    from pebble.auth_admin import AdminError

    # Seed a past-due pending deletion.
    user_id = _FAKE_USER["id"]
    user_dir = output_dir / ".users" / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    scheduled = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    (user_dir / "pending_deletion.json").write_text(
        json.dumps({
            "user_id": user_id,
            "email": _FAKE_USER["email"],
            "requested_at": scheduled,
            "scheduled_for": scheduled,
        }),
        encoding="utf-8",
    )

    # Make delete_user raise AdminError.
    def fake_delete_user(uid):
        raise AdminError("boom")
    monkeypatch.setattr("pebble.server.account.delete_user", fake_delete_user)

    # Capture audit_log.log_event calls (NOT log_event_for_handler — the
    # background path uses the bare log_event since there is no handler).
    audit_calls: list[dict] = []
    monkeypatch.setattr("pebble.audit_log.log_event",
                        lambda **kw: audit_calls.append(kw))

    # Call _execute_deletion_if_due directly.
    result = account_mod._execute_deletion_if_due(user_id, _FAKE_USER["email"])

    # Must return False (delete didn't pretend to succeed).
    assert result is False, "AdminError path must return False"

    # Must emit account_delete_failed audit event with reason.
    failed = [c for c in audit_calls if c.get("event_type") == "account_delete_failed"]
    assert failed, (
        f"missing account_delete_failed audit event. "
        f"Got events: {[c.get('event_type') for c in audit_calls]}"
    )
    assert failed[0].get("user_id") == user_id
    assert failed[0].get("metadata", {}).get("reason") == "boom", (
        f"audit metadata must include reason. Got: {failed[0].get('metadata')}"
    )


def test_cancel_deletion_no_warning_for_free_tier_user(monkeypatch, output_dir):
    """User on Free (no subscription.json) → cancel-deletion response has
    no subscription_warning. Don't crowd the UI with irrelevant text."""
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda token: _FAKE_USER)

    # No subscription file at all.
    monkeypatch.setattr(account_mod, "_cancel_stripe_subscription",
                        lambda sub_id: True)
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: None)
    monkeypatch.setattr("pebble.email.send_account_deletion_scheduled",
                        lambda email, cooling_off_ends: None)

    # Schedule deletion (no Stripe sub to cancel).
    delete_h = _FakeHandler()
    account_server.run_delete_account(delete_h)
    assert delete_h.status == 200

    audit_after: list[dict] = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_after.append(kw))

    cancel_h = _FakeHandler(body=_CANCEL_BODY)
    account_server.run_cancel_deletion(cancel_h)

    assert cancel_h.status == 200
    body = cancel_h.json_body or {}
    assert body.get("ok") is True
    assert body.get("cancelled") is True
    assert "subscription_warning" not in body, \
        f"free-tier cancel must NOT include subscription_warning: {body}"

    # Audit event present with had_stripe_sub_cancelled=False
    delete_cancelled = [c for c in audit_after
                        if c.get("event_type") == "account_delete_cancelled"]
    assert delete_cancelled, \
        f"missing account_delete_cancelled audit event: {[c.get('event_type') for c in audit_after]}"
    assert delete_cancelled[0].get("metadata", {}).get("had_stripe_sub_cancelled") is False
