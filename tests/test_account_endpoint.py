"""HTTP-level tests for `POST /api/account/delete`.

Uses a tiny FakeHandler that mimics the BaseHTTPRequestHandler-shaped
interface the endpoint expects. Network calls to Supabase are mocked
via `pebble.auth_admin.{validate_access_token,delete_user}` patches.
"""
from __future__ import annotations

import pytest

from pebble.server import account as account_server


# ---- Fixture: configured Supabase env (so is_configured() is True) ------

@pytest.fixture(autouse=True)
def _supabase_env(monkeypatch):
    monkeypatch.setenv("PEBBLE_SUPABASE_URL", "https://proj.supabase.co")
    monkeypatch.setenv("PEBBLE_SUPABASE_SERVICE_ROLE_KEY", "service-role-jwt-fake")
    monkeypatch.setenv("PEBBLE_SUPABASE_ANON_KEY", "anon-key-fake")
    yield


class _FakeHandler:
    """Minimum surface the endpoint touches: headers (Authorization)
    and _json (status + payload + extra_headers)."""
    def __init__(self, auth_header: str | None = None):
        self.headers = {}
        if auth_header is not None:
            self.headers["Authorization"] = auth_header
        self.status: int | None = None
        self.json_body: dict | None = None
        self.extra_headers: list = []

    def _json(self, status: int, payload: dict, extra_headers=None):
        self.status = status
        self.json_body = payload
        self.extra_headers = list(extra_headers or [])


# ---- Auth gate: no token / wrong shape ---------------------------------

def test_returns_401_when_no_auth_header():
    h = _FakeHandler()
    account_server.run_delete_account(h)
    assert h.status == 401
    assert "missing" in h.json_body["error"].lower() or "token" in h.json_body["error"].lower()


def test_returns_401_when_auth_header_is_not_bearer():
    h = _FakeHandler(auth_header="Basic xyz")
    account_server.run_delete_account(h)
    assert h.status == 401


def test_returns_401_when_bearer_token_is_empty():
    h = _FakeHandler(auth_header="Bearer ")
    account_server.run_delete_account(h)
    assert h.status == 401


# ---- Config gate ---------------------------------------------------------

def test_returns_503_when_env_not_configured(monkeypatch):
    monkeypatch.delenv("PEBBLE_SUPABASE_URL")
    h = _FakeHandler(auth_header="Bearer ey.fake.jwt")
    account_server.run_delete_account(h)
    assert h.status == 503
    assert "configured" in h.json_body["error"].lower()


# ---- Validate fails ------------------------------------------------------

def test_returns_401_when_token_validates_as_none(monkeypatch):
    """validate_access_token returning None means the token is bad
    (expired, wrong signature). 401 to the caller."""
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda token, **kw: None)
    h = _FakeHandler(auth_header="Bearer ey.expired.jwt")
    account_server.run_delete_account(h)
    assert h.status == 401
    assert "invalid" in h.json_body["error"].lower() or "expired" in h.json_body["error"].lower()


def test_returns_502_when_validate_raises_admin_error(monkeypatch):
    """validate_access_token raising AdminError means Supabase is
    unreachable or returned a 500. Vendor problem, surface as 502."""
    from pebble.auth_admin import AdminError
    def boom(*_a, **_kw):
        raise AdminError("Supabase unreachable: DNS failure")
    monkeypatch.setattr("pebble.server.account.validate_access_token", boom)
    h = _FakeHandler(auth_header="Bearer ey.fake.jwt")
    account_server.run_delete_account(h)
    assert h.status == 502
    assert "validate" in h.json_body["error"].lower() or "session" in h.json_body["error"].lower()


# ---- Delete fails --------------------------------------------------------

def test_returns_502_when_delete_raises(monkeypatch):
    """validate_access_token succeeds but delete_user fails. Surface
    as 502 (vendor problem). The user is still logged in — they can
    retry."""
    from pebble.auth_admin import AdminError
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda token, **kw: {"id": "11111111-2222-3333-4444-555555555555",
                                             "email": "marc@example.com"})
    monkeypatch.setattr("pebble.server.account.delete_user",
                        lambda uid, **kw: (_ for _ in ()).throw(AdminError("rate limited")))
    h = _FakeHandler(auth_header="Bearer ey.fake.jwt")
    account_server.run_delete_account(h)
    assert h.status == 502
    assert "delete" in h.json_body["error"].lower() or "rate" in h.json_body["error"].lower()


# ---- Happy path ----------------------------------------------------------

def test_returns_200_and_next_url_on_success(monkeypatch):
    """Validate returns a user, delete succeeds, response is 200 +
    {ok, deleted, user_id, next}."""
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda token, **kw: {"id": "11111111-2222-3333-4444-555555555555",
                                             "email": "marc@example.com"})
    calls = []
    monkeypatch.setattr("pebble.server.account.delete_user",
                        lambda uid, **kw: calls.append(uid))
    h = _FakeHandler(auth_header="Bearer ey.fake.jwt")
    account_server.run_delete_account(h)
    assert h.status == 200
    assert h.json_body["ok"] is True
    assert h.json_body["deleted"] is True
    assert h.json_body["user_id"] == "11111111-2222-3333-4444-555555555555"
    # Client uses `next` to know where to redirect after Supabase
    # client-side signOut clears the session.
    assert h.json_body["next"] == "/landing"
    # delete_user was actually called with the validated user's id
    assert calls == ["11111111-2222-3333-4444-555555555555"]


def test_validate_called_with_extracted_token(monkeypatch):
    """The bearer prefix is stripped before validating."""
    captured = {}
    def fake_validate(token, **kw):
        captured["token"] = token
        return {"id": "u-1234-5678-9012-3456-7890-1234", "email": "x@y"}
    monkeypatch.setattr("pebble.server.account.validate_access_token", fake_validate)
    monkeypatch.setattr("pebble.server.account.delete_user", lambda *_a, **_kw: None)
    h = _FakeHandler(auth_header="Bearer ey.real.token.value")
    account_server.run_delete_account(h)
    assert captured["token"] == "ey.real.token.value"
