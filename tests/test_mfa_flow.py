"""E2E tests for the MFA flow.

The MFA enrollment is client-driven (the v3 SecurityTab calls Supabase's
mfa.enroll/verify SDK directly). After verify succeeds, the frontend POSTs
to /api/account/mfa-event so the engine can:
  - write the audit_log row (mfa_enabled / mfa_disabled)
  - send the notification email

Mirrors tests/test_account_password_change.py — boots PebbleHandler on a
random port, hits the real route, asserts on the response.
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
import pebble.server.account_mfa as account_mfa_mod


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


_FAKE_USER = {"id": "u-mfa-test-1234", "email": "mfauser@example.com"}


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
    monkeypatch.setattr("pebble.auth_admin.is_configured", lambda: True)

    # Reset rate limiter for hermetic tests.
    account_mfa_mod._reset_mfa_event_limiter_for_tests()

    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()


def _post(base: str, path: str, body: dict, *, with_auth: bool = True) -> tuple[int, dict | str]:
    headers = {
        "Content-Type": "application/json",
    }
    if with_auth:
        headers["Authorization"] = "Bearer fake-test-token"
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{base}{path}", data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw


# ── /api/account/mfa-event ───────────────────────────────────────────────────

def test_mfa_event_unauthenticated_401(engine_base):
    """Without bearer JWT → 401."""
    status, _ = _post(engine_base, "/api/account/mfa-event",
                      {"event_type": "mfa_enabled"}, with_auth=False)
    assert status == 401, f"Expected 401, got {status}"


def test_mfa_event_invalid_event_type_400(engine_base, monkeypatch):
    """event_type must be in the allow-list."""
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler", lambda **kw: None)
    status, body = _post(engine_base, "/api/account/mfa-event",
                         {"event_type": "arbitrary_spam"})
    assert status == 400, f"Expected 400, got {status}: {body}"


def test_mfa_event_missing_event_type_400(engine_base):
    status, body = _post(engine_base, "/api/account/mfa-event", {})
    assert status == 400, f"Expected 400, got {status}: {body}"


def test_mfa_enabled_writes_audit_log_and_sends_email(engine_base, monkeypatch):
    """mfa_enabled event → 200 + audit_log entry + notification email."""
    audit_calls: list[dict] = []
    monkeypatch.setattr(
        "pebble.audit_log.log_event_for_handler",
        lambda **kw: audit_calls.append(kw),
    )
    email_calls: list[str] = []
    monkeypatch.setattr(
        "pebble.email.send_mfa_enabled_notification",
        lambda email: email_calls.append(email),
    )
    # Also stub the disabled one so import works
    monkeypatch.setattr(
        "pebble.email.send_mfa_disabled_notification",
        lambda email: None,
    )

    status, body = _post(engine_base, "/api/account/mfa-event",
                         {"event_type": "mfa_enabled"})
    assert status == 200, f"Expected 200, got {status}: {body}"
    assert body.get("ok") is True
    # Audit logged
    assert any(c.get("event_type") == "mfa_enabled" for c in audit_calls), \
        f"Expected mfa_enabled in audit log, got: {audit_calls}"
    # Notification email sent
    assert email_calls == [_FAKE_USER["email"]], \
        f"Expected notification email sent, got: {email_calls}"


def test_mfa_disabled_writes_audit_log_and_sends_email(engine_base, monkeypatch):
    """mfa_disabled event → 200 + audit_log entry + notification email."""
    audit_calls: list[dict] = []
    monkeypatch.setattr(
        "pebble.audit_log.log_event_for_handler",
        lambda **kw: audit_calls.append(kw),
    )
    email_calls: list[str] = []
    monkeypatch.setattr(
        "pebble.email.send_mfa_disabled_notification",
        lambda email: email_calls.append(email),
    )
    monkeypatch.setattr(
        "pebble.email.send_mfa_enabled_notification",
        lambda email: None,
    )

    status, body = _post(engine_base, "/api/account/mfa-event",
                         {"event_type": "mfa_disabled"})
    assert status == 200, f"Expected 200, got {status}: {body}"
    assert any(c.get("event_type") == "mfa_disabled" for c in audit_calls)
    assert email_calls == [_FAKE_USER["email"]]


def test_mfa_event_email_failure_does_not_break_response(engine_base, monkeypatch):
    """Email failure must NOT crash the endpoint — fire-and-forget audit."""
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler", lambda **kw: None)

    def boom(email):
        raise RuntimeError("email is down")

    monkeypatch.setattr("pebble.email.send_mfa_enabled_notification", boom)
    monkeypatch.setattr("pebble.email.send_mfa_disabled_notification", lambda email: None)

    status, body = _post(engine_base, "/api/account/mfa-event",
                         {"event_type": "mfa_enabled"})
    assert status == 200, f"Expected 200 even when email fails, got {status}: {body}"


def test_mfa_event_rate_limited_after_5_per_minute(engine_base, monkeypatch):
    """Per-user 5/minute rate limit prevents audit-log spam."""
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler", lambda **kw: None)
    monkeypatch.setattr("pebble.email.send_mfa_enabled_notification", lambda email: None)
    monkeypatch.setattr("pebble.email.send_mfa_disabled_notification", lambda email: None)

    account_mfa_mod._reset_mfa_event_limiter_for_tests()

    # 5 attempts allowed
    for i in range(5):
        status, _ = _post(engine_base, "/api/account/mfa-event",
                          {"event_type": "mfa_enabled"})
        assert status == 200, f"Attempt {i+1}: expected 200, got {status}"

    # 6th rate-limited
    status, body = _post(engine_base, "/api/account/mfa-event",
                         {"event_type": "mfa_enabled"})
    assert status == 429, f"Expected 429 on 6th attempt, got {status}: {body}"
