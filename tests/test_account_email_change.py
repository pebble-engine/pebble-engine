"""E2E test for the email-change flow.

POST /api/account/change-email-request:
- Requires bearer JWT.
- Re-authenticates with current_password.
- Validates new_email format.
- Writes pending file + sends confirmation email to NEW address.
- Writes audit_log email_change_requested.
- Per-user rate limit: 3/day.

GET /api/account/change-email-confirm?token=...:
- Looks up the pending file by token.
- Rejects expired tokens.
- Calls Supabase admin updateUser to change email.
- Writes audit_log email_change_confirmed.
- Sends notification to OLD address.
- Deletes the pending file.
"""
from __future__ import annotations

import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

import pebble.server.account as account_mod
from pebble.server import account as account_server

# ── fixtures ──────────────────────────────────────────────────────────────────

_FAKE_USER = {"id": "u-email-test-001", "email": "old@example.com"}


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
def _reset_email_change_limiter():
    account_mod._reset_email_change_limiter_for_tests()
    yield


@pytest.fixture()
def output_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("pebble.server.account._output_dir", lambda: tmp_path)
    return tmp_path


# ── fake handler ──────────────────────────────────────────────────────────────

def _make_handler(body: dict | None = None, path: str = "/api/account/change-email-request"):
    raw = json.dumps(body or {}).encode()
    h = _FakeHandler(raw, path=path)
    return h


class _FakeHandler:
    def __init__(self, body: bytes = b"{}", path: str = "/api/account/change-email-request",
                 client_ip: str = "127.0.0.1"):
        self.path = path
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


# ── request tests ─────────────────────────────────────────────────────────────

def test_request_rejects_wrong_current_password(tmp_path, monkeypatch, output_dir):
    """Wrong current_password → 401, no pending file written, no email."""
    monkeypatch.setattr("pebble.security.require_user", lambda h: _FAKE_USER)
    monkeypatch.setattr(account_mod, "_reauth_user", lambda email, pw: (False, "wrong password"))

    email_calls = []
    monkeypatch.setattr(account_mod, "_send_email_change_confirmation_safe",
                        lambda **kw: email_calls.append(kw))

    audit_calls = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_calls.append(kw))

    body = {"current_password": "wrongpass", "new_email": "new@example.com"}
    h = _make_handler(body)
    account_server.run_request_email_change(h)

    assert h.status == 401
    assert "incorrect" in (h.json_body or {}).get("error", "")

    pending = output_dir / ".users" / _FAKE_USER["id"] / "email_change_pending.json"
    assert not pending.exists(), "pending file must NOT be written on auth failure"
    assert len(email_calls) == 0, "no email should be sent on auth failure"
    assert any(c.get("event_type") == "email_change_request_failed" for c in audit_calls)


def test_request_writes_pending_file_and_sends_confirm_email(tmp_path, monkeypatch, output_dir):
    """Happy path: pending token stored in Supabase (mocked), confirmation
    email sent to NEW address, audit log entry made.

    Migration 006: pending state now lives in Supabase, not a local file.
    The test mocks pebble.pending_state.create_email_change_pending to stay
    offline and verify the new storage layer is wired in correctly.
    """
    monkeypatch.setattr("pebble.security.require_user", lambda h: _FAKE_USER)
    monkeypatch.setattr(account_mod, "_reauth_user", lambda email, pw: (True, None))

    import pebble.pending_state as pending_state_mod
    fake_token = "fake-supabase-token-abc123"
    create_calls = []

    def fake_create(user_id, new_email, ttl_hours=24):
        create_calls.append({"user_id": user_id, "new_email": new_email, "ttl_hours": ttl_hours})
        return {"token": fake_token, "expires_at": "2099-01-01T00:00:00+00:00"}

    monkeypatch.setattr(pending_state_mod, "create_email_change_pending", fake_create)

    email_calls = []
    monkeypatch.setattr(account_mod, "_send_email_change_confirmation_safe",
                        lambda **kw: email_calls.append(kw))

    audit_calls = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_calls.append(kw))

    body = {"current_password": "correctpass", "new_email": "new@example.com"}
    h = _make_handler(body)
    account_server.run_request_email_change(h)

    assert h.status == 200, f"expected 200, got {h.status}: {h.json_body}"
    assert h.json_body.get("ok") is True

    # create_email_change_pending called with the right args
    assert len(create_calls) == 1
    assert create_calls[0]["user_id"] == _FAKE_USER["id"]
    assert create_calls[0]["new_email"] == "new@example.com"

    # Confirmation email sent to NEW address with the Supabase-generated token
    assert len(email_calls) == 1
    assert email_calls[0]["new_email"] == "new@example.com"
    assert email_calls[0]["token"] == fake_token

    # Audit log
    assert any(c.get("event_type") == "email_change_requested" for c in audit_calls)


def test_request_rejects_invalid_email_format(tmp_path, monkeypatch, output_dir):
    """new_email lacking @ → 400."""
    monkeypatch.setattr("pebble.security.require_user", lambda h: _FAKE_USER)
    monkeypatch.setattr(account_mod, "_reauth_user", lambda email, pw: (True, None))

    body = {"current_password": "correctpass", "new_email": "notanemail"}
    h = _make_handler(body)
    account_server.run_request_email_change(h)

    assert h.status == 400
    assert "valid" in (h.json_body or {}).get("error", "").lower()


def test_request_rate_limited_after_3_per_day(tmp_path, monkeypatch, output_dir):
    """4th request from same user → 429."""
    monkeypatch.setattr("pebble.security.require_user", lambda h: _FAKE_USER)
    monkeypatch.setattr(account_mod, "_reauth_user", lambda email, pw: (True, None))
    monkeypatch.setattr(account_mod, "_send_email_change_confirmation_safe", lambda **kw: None)
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler", lambda **kw: None)

    body = {"current_password": "correctpass", "new_email": "new@example.com"}

    # 3 requests succeed
    for _ in range(3):
        h = _make_handler(body)
        account_server.run_request_email_change(h)
        # Each call overwrites the pending file — that's fine

    # 4th request should be rate-limited
    h = _make_handler(body)
    account_server.run_request_email_change(h)
    assert h.status == 429, f"expected 429, got {h.status}: {h.json_body}"


# ── confirm tests ─────────────────────────────────────────────────────────────

def _seed_pending(output_dir: Path, token: str, new_email: str, user_id: str,
                  expired: bool = False) -> Path:
    """Write a pending file for confirm-flow tests."""
    now = datetime.now(timezone.utc)
    if expired:
        expires = now - timedelta(hours=25)
    else:
        expires = now + timedelta(hours=24)
    data = {
        "token": token,
        "new_email": new_email,
        "user_id": user_id,
        "requested_at": now.isoformat(),
        "expires_at": expires.isoformat(),
    }
    user_dir = output_dir / ".users" / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    p = user_dir / "email_change_pending.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_confirm_with_valid_token_updates_email(tmp_path, monkeypatch, output_dir):
    """Token in pending file → Supabase admin called, audit logged,
    notification sent to OLD email, pending file deleted."""
    token = "valid-token-abc123"
    pending = _seed_pending(output_dir, token, "new@example.com", _FAKE_USER["id"])

    monkeypatch.setattr(account_mod, "_update_user_email",
                        lambda user_id, new_email: True)

    get_email_calls = []
    monkeypatch.setattr(account_mod, "_get_user_email_from_supabase",
                        lambda uid: get_email_calls.append(uid) or "old@example.com")

    audit_calls = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_calls.append(kw))

    notify_calls = []
    monkeypatch.setattr(account_mod, "_send_email_change_completed_safe",
                        lambda **kw: notify_calls.append(kw))

    h = _FakeHandler(path=f"/api/account/change-email-confirm?token={token}")
    account_server.run_confirm_email_change(h)

    assert h.status == 200, f"expected 200, got {h.status}: {h.json_body}"
    assert h.json_body.get("ok") is True

    # Pending file deleted
    assert not pending.exists(), "pending file must be deleted after successful confirm"

    # Audit log
    assert any(c.get("event_type") == "email_change_confirmed" for c in audit_calls)

    # Notification sent to OLD email
    assert len(notify_calls) == 1
    assert notify_calls[0]["old_email"] == "old@example.com"
    assert notify_calls[0]["new_email"] == "new@example.com"


def test_confirm_with_expired_token_rejected(tmp_path, monkeypatch, output_dir):
    """Token > 24h old → 400, pending file deleted (cleanup), no Supabase call."""
    token = "expired-token-xyz"
    pending = _seed_pending(output_dir, token, "new@example.com", _FAKE_USER["id"], expired=True)

    update_calls = []
    monkeypatch.setattr(account_mod, "_update_user_email",
                        lambda uid, email: update_calls.append((uid, email)) or True)

    audit_calls = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_calls.append(kw))

    h = _FakeHandler(path=f"/api/account/change-email-confirm?token={token}")
    account_server.run_confirm_email_change(h)

    assert h.status == 400
    assert "expired" in (h.json_body or {}).get("error", "").lower()

    # Pending file cleaned up even on expiry
    assert not pending.exists(), "expired pending file must be deleted (cleanup)"

    # Supabase NOT called
    assert len(update_calls) == 0


def test_confirm_with_unknown_token_rejected(tmp_path, monkeypatch, output_dir):
    """Token not in any pending file → 404."""
    # No pending file seeded
    h = _FakeHandler(path="/api/account/change-email-confirm?token=nonexistent-token")
    account_server.run_confirm_email_change(h)

    assert h.status == 404


def test_confirm_token_is_single_use(tmp_path, monkeypatch, output_dir):
    """After successful confirm, re-using the same token → 404 (file deleted)."""
    token = "single-use-token-456"
    _seed_pending(output_dir, token, "new@example.com", _FAKE_USER["id"])

    monkeypatch.setattr(account_mod, "_update_user_email",
                        lambda uid, email: True)
    monkeypatch.setattr(account_mod, "_get_user_email_from_supabase",
                        lambda uid: "old@example.com")
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler", lambda **kw: None)
    monkeypatch.setattr(account_mod, "_send_email_change_completed_safe", lambda **kw: None)

    # First use succeeds
    h1 = _FakeHandler(path=f"/api/account/change-email-confirm?token={token}")
    account_server.run_confirm_email_change(h1)
    assert h1.status == 200

    # Second use: file is gone → 404
    h2 = _FakeHandler(path=f"/api/account/change-email-confirm?token={token}")
    account_server.run_confirm_email_change(h2)
    assert h2.status == 404


# ---- Fix 4 (2026-05-24): file-fallback hard-kill date --------------------

def test_confirm_file_fallback_skipped_after_hard_kill_date(
    tmp_path, monkeypatch, output_dir,
):
    """After _FILE_FALLBACK_HARD_KILL (2026-05-29T00:00:00Z), the local-file
    fallback for email_change_pending.json is silently dropped. Any token
    only present in the legacy file location returns 410 (link expired,
    re-request) — so an attacker who can write a forged file under
    output/.users/<uid>/email_change_pending.json can't use it to confirm
    an email change.

    Pre-kill-date the file fallback still works (existing tests above).
    """
    import datetime as _dt
    from pathlib import Path as _Path

    token = "legacy-file-only-token"
    seeded = _seed_pending(output_dir, token, "new@example.com", _FAKE_USER["id"])

    # Force "now" past the hard-kill date.
    class _PastKillDatetime(_dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return _dt.datetime(2026, 6, 1, tzinfo=tz or _dt.timezone.utc)

    monkeypatch.setattr(account_mod, "datetime", _PastKillDatetime)

    # Spy on Path.iterdir to prove the file-scan code path NEVER runs.
    # If the fallback short-circuited correctly, _output_dir / ".users"
    # is never enumerated.
    iterdir_calls: list[str] = []
    real_iterdir = _Path.iterdir

    def spy_iterdir(self):
        iterdir_calls.append(str(self))
        return real_iterdir(self)

    monkeypatch.setattr(_Path, "iterdir", spy_iterdir)

    # Supabase lookup also returns None (no row) so we know any successful
    # confirm would have to have come from the file fallback.
    monkeypatch.setattr(
        "pebble.pending_state.lookup_email_change_pending",
        lambda token: None,
    )

    monkeypatch.setattr(account_mod, "_update_user_email",
                        lambda uid, email: True)
    monkeypatch.setattr(account_mod, "_get_user_email_from_supabase",
                        lambda uid: "old@example.com")
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler", lambda **kw: None)
    monkeypatch.setattr(account_mod, "_send_email_change_completed_safe", lambda **kw: None)

    h = _FakeHandler(path=f"/api/account/change-email-confirm?token={token}")
    account_server.run_confirm_email_change(h)

    # 410 Gone: the token is no longer accepted via the legacy path.
    assert h.status == 410, \
        f"expected 410 (link expired, re-request) after kill date, got {h.status}: {h.json_body}"
    # The file was NOT consumed (the test seed is still there) — proves
    # the legacy path didn't even try to read it.
    assert seeded.exists(), \
        "file must NOT be consumed when the fallback is dead-killed"
    # The .users dir must NOT have been iterated.
    users_root_iter = [c for c in iterdir_calls
                       if c.endswith(".users") or ".users" + str(_Path("/"))[-1] in c]
    assert not users_root_iter, \
        f"file-scan code path ran after hard-kill date: {users_root_iter}"
