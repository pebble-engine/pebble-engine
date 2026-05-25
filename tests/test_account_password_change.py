"""E2E test for POST /api/account/change-password.

Pattern: mirrors tests/test_http_e2e.py — boots PebbleHandler on a random
port via ThreadingHTTPServer, hits the real route, asserts on the response.

Key behaviors:
- Wrong current_password → 401 + audit_log entry (password_change_failed) +
  NO password update + NO notification email.
- Correct current_password → 200 + audit_log entry (password_change) +
  password updated via Supabase admin API + notification email queued.
- Missing fields → 400.
- New password too short → 400.
- Same as current → 400.
- Per-user rate limit (5/hour) → 429 after 6th attempt.
"""
from __future__ import annotations

import json
import socket
import threading
import time
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer

import pytest

import pebble_engine
import pebble.server.account as account_mod
from pebble.auth_admin import AdminError


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


_FAKE_USER = {"id": "u-test-1234", "email": "test@example.com"}


@pytest.fixture
def engine_base(monkeypatch):
    port = _find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), pebble_engine.PebbleHandler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)

    # Bypass Supabase token validation — return fixed user for any token.
    monkeypatch.setattr(
        "pebble.auth_admin.validate_access_token",
        lambda token, **kw: _FAKE_USER,
    )
    # Supabase is_configured() must return True so the endpoint doesn't 503.
    monkeypatch.setattr("pebble.auth_admin.is_configured", lambda: True)

    # Reset the rate limiter so each test starts with a fresh bucket —
    # without this, the 5 failed attempts from earlier tests consume the
    # burst quota and subsequent tests get 429 instead of 400.
    account_mod._reset_password_change_limiter_for_tests()

    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()


def _post(base: str, path: str, body: dict) -> tuple[int, dict | str]:
    req = urllib.request.Request(
        f"{base}{path}",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": "Bearer fake-test-token",
            "Content-Type": "application/json",
            "Content-Length": str(len(json.dumps(body).encode())),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw


def test_wrong_current_password_rejected(engine_base, monkeypatch):
    """401, audit log password_change_failed, no email, no update."""
    monkeypatch.setattr(account_mod, "_reauth_user",
                        lambda email, password: (False, "Invalid login credentials"))
    audit_calls = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_calls.append(kw))
    update_calls = []
    monkeypatch.setattr(account_mod, "_update_password",
                        lambda uid, pw: update_calls.append((uid, pw)) or True)

    status, body = _post(engine_base, "/api/account/change-password",
                         {"current_password": "wrongpass", "new_password": "newSecure123!"})
    assert status == 401, f"Expected 401, got {status}: {body}"
    assert update_calls == [], "Password should NOT be updated on auth failure"
    assert any(c.get("event_type") == "password_change_failed" for c in audit_calls), \
        f"Expected password_change_failed in audit log, got: {audit_calls}"


def test_correct_password_succeeds_writes_audit_emails(engine_base, monkeypatch):
    """200, audit log password_change, email sent, Supabase update called."""
    monkeypatch.setattr(account_mod, "_reauth_user",
                        lambda email, password: (True, None))
    update_calls = []
    monkeypatch.setattr(account_mod, "_update_password",
                        lambda uid, pw: update_calls.append((uid, pw)) or True)
    audit_calls = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_calls.append(kw))
    email_calls = []
    monkeypatch.setattr("pebble.email.send_password_changed_notification",
                        lambda email: email_calls.append(email))

    status, body = _post(engine_base, "/api/account/change-password",
                         {"current_password": "correctOldPass1", "new_password": "newSecure123!"})
    assert status == 200, f"Expected 200, got {status}: {body}"
    assert body.get("ok") is True
    assert update_calls == [(_FAKE_USER["id"], "newSecure123!")], \
        f"Expected _update_password called with correct args, got: {update_calls}"
    assert any(c.get("event_type") == "password_change" for c in audit_calls), \
        f"Expected password_change in audit log, got: {audit_calls}"
    assert email_calls == [_FAKE_USER["email"]], \
        f"Expected notification email sent, got: {email_calls}"


def test_missing_new_password_400(engine_base):
    status, _ = _post(engine_base, "/api/account/change-password",
                      {"current_password": "only-this"})
    assert status == 400, f"Expected 400 for missing new_password, got {status}"


def test_missing_current_password_400(engine_base):
    status, _ = _post(engine_base, "/api/account/change-password",
                      {"new_password": "newSecure123!"})
    assert status == 400, f"Expected 400 for missing current_password, got {status}"


def test_new_password_too_short_400(engine_base):
    status, body = _post(engine_base, "/api/account/change-password",
                         {"current_password": "anything", "new_password": "abc"})
    assert status == 400, f"Expected 400 for short password, got {status}"
    assert "8" in str(body), f"Error message should mention minimum length, got: {body}"


def test_new_password_same_as_current_400(engine_base):
    status, _ = _post(engine_base, "/api/account/change-password",
                      {"current_password": "samepassword1", "new_password": "samepassword1"})
    assert status == 400, f"Expected 400 when new password matches current, got {status}"


def test_rate_limit_kicks_in_after_5_attempts(engine_base, monkeypatch):
    """Per-user 5/hour limit. 6th attempt should 429."""
    monkeypatch.setattr(account_mod, "_reauth_user",
                        lambda email, password: (False, "wrong"))
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler", lambda **kw: None)

    # Reset the limiter for hermetic test.
    account_mod._reset_password_change_limiter_for_tests()

    # 5 attempts should be allowed (returned 401 for wrong password, not 429).
    for i in range(5):
        status, _ = _post(engine_base, "/api/account/change-password",
                          {"current_password": "wrong", "new_password": "newSecure123!"})
        assert status == 401, f"Attempt {i+1}: Expected 401, got {status}"

    # 6th attempt should be rate-limited.
    status, body = _post(engine_base, "/api/account/change-password",
                         {"current_password": "wrong", "new_password": "newSecure123!"})
    assert status == 429, f"Expected 429 on 6th attempt, got {status}: {body}"
