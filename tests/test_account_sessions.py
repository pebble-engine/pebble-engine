"""E2E tests for the sessions list / revoke endpoints.

Phase D.2 (2026-05-24). Three endpoints:
  GET    /api/account/sessions               — list active sessions
  DELETE /api/account/sessions/<id>          — revoke one session
  POST   /api/account/sessions/revoke-others — sign out everywhere ELSE
                                                (keeps current session alive)

Backed by the public.list_user_sessions / public.revoke_user_session
SECURITY DEFINER functions in migration 008.

Pattern mirrors tests/test_mfa_flow.py — boots PebbleHandler on a
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
import pebble.server.account_sessions as sessions_mod


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


_FAKE_USER = {"id": "u-sessions-1234", "email": "sessuser@example.com"}


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

    sessions_mod._reset_sessions_limiter_for_tests()

    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()


def _request(method: str, base: str, path: str, body: dict | None = None,
             *, with_auth: bool = True) -> tuple[int, dict | str]:
    headers = {"Content-Type": "application/json"}
    if with_auth:
        headers["Authorization"] = "Bearer fake-test-token"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{base}{path}", data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read().decode() if resp.length != 0 else ""
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw


# ── GET /api/account/sessions ────────────────────────────────────────────────

_FAKE_SESSIONS = [
    {
        "id": "sess-uuid-1",
        "created_at": "2026-05-20T10:00:00+00:00",
        "updated_at": "2026-05-24T12:00:00+00:00",
        "refreshed_at": "2026-05-24T11:30:00",
        "not_after": "2026-06-24T10:00:00+00:00",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
        "ip": "203.0.113.1",
        "aal": "aal1",
        "factor_id": None,
    },
    {
        "id": "sess-uuid-2",
        "created_at": "2026-05-21T08:00:00+00:00",
        "updated_at": "2026-05-24T08:00:00+00:00",
        "refreshed_at": "2026-05-24T07:30:00",
        "not_after": "2026-06-25T08:00:00+00:00",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) Mobile/15E148",
        "ip": "203.0.113.2",
        "aal": "aal1",
        "factor_id": None,
    },
]


def test_list_unauthenticated_401(engine_base):
    status, _ = _request("GET", engine_base, "/api/account/sessions", with_auth=False)
    assert status == 401


def test_list_returns_sanitized_session_rows(engine_base, monkeypatch):
    """Happy path: returns sessions sanitized + this-device flag set."""
    monkeypatch.setattr(sessions_mod, "_fetch_user_sessions",
                        lambda user_id: _FAKE_SESSIONS)

    status, body = _request("GET", engine_base, "/api/account/sessions")
    assert status == 200, f"Expected 200, got {status}: {body}"
    assert "sessions" in body
    sessions = body["sessions"]
    assert len(sessions) == 2
    # Each row has the expected fields
    for s in sessions:
        assert "id" in s
        assert "created_at" in s
        assert "user_agent_summary" in s, "Expected parsed user agent summary"
        assert "ip" in s
        assert "is_current" in s, "Expected this-device flag"
    # Sensitive fields should NOT be surfaced
    for s in sessions:
        assert "refresh_token_hmac_key" not in s
        assert "refresh_token_counter" not in s


def test_list_returns_empty_when_no_sessions(engine_base, monkeypatch):
    monkeypatch.setattr(sessions_mod, "_fetch_user_sessions", lambda user_id: [])
    status, body = _request("GET", engine_base, "/api/account/sessions")
    assert status == 200
    assert body.get("sessions") == []


def test_list_user_agent_parsed_for_browser_and_os(engine_base, monkeypatch):
    """user_agent_summary should be a human-readable string like
    'Safari on macOS' or 'Safari on iPhone'."""
    monkeypatch.setattr(sessions_mod, "_fetch_user_sessions",
                        lambda user_id: _FAKE_SESSIONS)
    status, body = _request("GET", engine_base, "/api/account/sessions")
    sessions = body["sessions"]
    summaries = [s["user_agent_summary"] for s in sessions]
    # We don't assert exact wording — just that it's non-empty and human-ish
    for s in summaries:
        assert isinstance(s, str) and s, f"Expected non-empty summary, got: {s!r}"


def test_list_supabase_failure_returns_502(engine_base, monkeypatch):
    def boom(user_id):
        raise RuntimeError("Supabase down")

    monkeypatch.setattr(sessions_mod, "_fetch_user_sessions", boom)
    status, body = _request("GET", engine_base, "/api/account/sessions")
    assert status == 502, f"Expected 502 on Supabase failure, got {status}"


# ── DELETE /api/account/sessions/<id> ────────────────────────────────────────

def test_revoke_one_unauthenticated_401(engine_base):
    status, _ = _request("DELETE", engine_base,
                         "/api/account/sessions/sess-uuid-1", with_auth=False)
    assert status == 401


def test_revoke_one_success(engine_base, monkeypatch):
    """Successfully revokes a session by id, writes audit log."""
    revoke_calls: list[tuple] = []
    monkeypatch.setattr(sessions_mod, "_supabase_revoke_session",
                        lambda uid, sid: revoke_calls.append((uid, sid)) or True)
    audit_calls: list[dict] = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_calls.append(kw))

    status, body = _request("DELETE", engine_base,
                            "/api/account/sessions/12345678-1234-1234-1234-123456789abc")
    assert status == 200, f"Expected 200, got {status}: {body}"
    assert body.get("ok") is True
    # Backend got the right user/session pair
    assert revoke_calls == [(_FAKE_USER["id"], "12345678-1234-1234-1234-123456789abc")], \
        f"Expected revoke call, got: {revoke_calls}"
    # Audit log written
    assert any(c.get("event_type") == "session_revoked" for c in audit_calls), \
        f"Expected session_revoked in audit log, got: {audit_calls}"


def test_revoke_one_invalid_id_400(engine_base):
    """Reject obviously bad session ids (path traversal, SQL injection
    shape) before forwarding to Supabase."""
    status, _ = _request("DELETE", engine_base,
                         "/api/account/sessions/../../etc/passwd")
    assert status == 400 or status == 404, f"Expected 400/404, got {status}"


def test_revoke_one_not_found_returns_404(engine_base, monkeypatch):
    """Supabase returns False → session didn't exist for this user → 404."""
    monkeypatch.setattr(sessions_mod, "_supabase_revoke_session",
                        lambda uid, sid: False)
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler", lambda **kw: None)

    status, body = _request("DELETE", engine_base,
                            "/api/account/sessions/12345678-1234-1234-1234-123456789abc")
    assert status == 404, f"Expected 404, got {status}: {body}"


# ── Rate-limit ───────────────────────────────────────────────────────────────

def test_list_rate_limited(engine_base, monkeypatch):
    """Per-user 30/minute on the LIST endpoint — generous for a healthy
    user reloading their settings page but tight enough to thwart scraping."""
    monkeypatch.setattr(sessions_mod, "_fetch_user_sessions", lambda uid: [])
    sessions_mod._reset_sessions_limiter_for_tests()

    # 30 should succeed
    for i in range(30):
        status, _ = _request("GET", engine_base, "/api/account/sessions")
        assert status == 200, f"Attempt {i+1}: expected 200, got {status}"

    # 31st rate-limited
    status, body = _request("GET", engine_base, "/api/account/sessions")
    assert status == 429, f"Expected 429 on 31st attempt, got {status}"
