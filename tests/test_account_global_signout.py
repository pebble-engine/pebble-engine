"""E2E tests for POST /api/account/global-signout.

Phase D.3 (2026-05-24). Endpoint signs out every session for the calling
user via Supabase's POST /auth/v1/logout?scope=global, then writes an
audit_log row + sends defensive-notify email.

Mirrors test_account_password_change.py — boots PebbleHandler on a random
port, hits the real route, asserts on the response.
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
import pebble.server.account_signout as signout_mod


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


_FAKE_USER = {"id": "u-signout-1234", "email": "signout@example.com"}


@pytest.fixture
def engine_base(monkeypatch):
    port = _find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), pebble_engine.PebbleHandler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)

    monkeypatch.setattr(
        "pebble.auth_admin.validate_access_token",
        lambda token, **kw: _FAKE_USER,
    )
    monkeypatch.setattr("pebble.auth_admin.is_configured", lambda: True)

    signout_mod._reset_global_signout_limiter_for_tests()

    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()


def _post(base: str, path: str, body: dict | None = None, *, with_auth: bool = True
          ) -> tuple[int, dict | str]:
    headers = {"Content-Type": "application/json"}
    if with_auth:
        headers["Authorization"] = "Bearer fake-test-token"
    data = json.dumps(body or {}).encode()
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


def test_unauthenticated_401(engine_base):
    """Without bearer JWT → 401."""
    status, _ = _post(engine_base, "/api/account/global-signout", with_auth=False)
    assert status == 401, f"Expected 401, got {status}"


def test_success_calls_supabase_logout_audits_emails(engine_base, monkeypatch):
    """Happy path: Supabase logout called, audit log written, email sent."""
    logout_calls: list[str] = []
    monkeypatch.setattr(signout_mod, "_supabase_global_signout",
                        lambda jwt: logout_calls.append(jwt) or True)
    audit_calls: list[dict] = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_calls.append(kw))
    email_calls: list[tuple] = []
    monkeypatch.setattr("pebble.email.send_global_signout_notification",
                        lambda email, **kw: email_calls.append((email, kw)))

    status, body = _post(engine_base, "/api/account/global-signout")
    assert status == 200, f"Expected 200, got {status}: {body}"
    assert body.get("ok") is True
    # JWT was forwarded to Supabase
    assert logout_calls == ["fake-test-token"], \
        f"Expected Supabase logout call with JWT, got: {logout_calls}"
    # Audit logged
    assert any(c.get("event_type") == "global_signout" for c in audit_calls), \
        f"Expected global_signout in audit log, got: {audit_calls}"
    # Email sent
    assert any(call[0] == _FAKE_USER["email"] for call in email_calls), \
        f"Expected notification email sent, got: {email_calls}"


def test_supabase_failure_returns_502_and_no_audit(engine_base, monkeypatch):
    """When Supabase logout fails, return 502 — DON'T write audit row
    (we didn't actually sign anyone out)."""
    monkeypatch.setattr(signout_mod, "_supabase_global_signout",
                        lambda jwt: False)
    audit_calls: list[dict] = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_calls.append(kw))
    email_calls: list = []
    monkeypatch.setattr("pebble.email.send_global_signout_notification",
                        lambda email, **kw: email_calls.append(email))

    status, body = _post(engine_base, "/api/account/global-signout")
    assert status == 502, f"Expected 502 on Supabase failure, got {status}: {body}"
    assert audit_calls == [], \
        f"Expected NO audit log when sign-out failed (would be misleading), got: {audit_calls}"
    assert email_calls == [], \
        f"Expected NO email when sign-out failed, got: {email_calls}"


def test_email_failure_does_not_break_response(engine_base, monkeypatch):
    """Email failure → 200 still returned (sign-out already succeeded)."""
    monkeypatch.setattr(signout_mod, "_supabase_global_signout",
                        lambda jwt: True)
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler", lambda **kw: None)

    def boom(email, **kw):
        raise RuntimeError("email is down")

    monkeypatch.setattr("pebble.email.send_global_signout_notification", boom)

    status, body = _post(engine_base, "/api/account/global-signout")
    assert status == 200, f"Expected 200 even when email fails, got {status}: {body}"


def test_rate_limited_after_3_per_hour(engine_base, monkeypatch):
    """3 global-signouts/hour per user — tight because each fires an email."""
    monkeypatch.setattr(signout_mod, "_supabase_global_signout", lambda jwt: True)
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler", lambda **kw: None)
    monkeypatch.setattr("pebble.email.send_global_signout_notification",
                        lambda email, **kw: None)

    signout_mod._reset_global_signout_limiter_for_tests()

    for i in range(3):
        status, _ = _post(engine_base, "/api/account/global-signout")
        assert status == 200, f"Attempt {i+1}: expected 200, got {status}"

    status, body = _post(engine_base, "/api/account/global-signout")
    assert status == 429, f"Expected 429 on 4th attempt, got {status}: {body}"
