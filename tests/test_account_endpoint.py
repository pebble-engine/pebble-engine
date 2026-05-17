"""HTTP-level tests for account endpoints (profile, delete, cancel-deletion).

Uses a tiny FakeHandler that mimics the BaseHTTPRequestHandler-shaped
interface the endpoint expects. Network calls to Supabase are mocked
via `pebble.auth_admin.{validate_access_token,delete_user}` patches.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from pebble.server import account as account_server


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _supabase_env(monkeypatch):
    monkeypatch.setenv("PEBBLE_SUPABASE_URL", "https://proj.supabase.co")
    monkeypatch.setenv("PEBBLE_SUPABASE_SERVICE_ROLE_KEY", "service-role-jwt-fake")
    monkeypatch.setenv("PEBBLE_SUPABASE_ANON_KEY", "anon-key-fake")
    # Banish un-prefixed fallbacks so individual tests that delenv
    # PEBBLE_SUPABASE_URL actually see is_configured() return False —
    # even when the dev machine has SUPABASE_URL in its real environment.
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    monkeypatch.delenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", raising=False)
    yield


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    from pebble.server import account
    account._reset_delete_rate_limiter_for_tests()
    yield


@pytest.fixture()
def output_dir(tmp_path, monkeypatch):
    """Redirect account._output_dir() to a temp directory."""
    monkeypatch.setattr("pebble.server.account._output_dir", lambda: tmp_path)
    return tmp_path


class _FakeHandler:
    def __init__(self, auth_header: str | None = None,
                 client_ip: str = "203.0.113.7",
                 body: bytes = b"{}"):
        self.headers: dict = {}
        if auth_header is not None:
            self.headers["Authorization"] = auth_header
        if body:
            self.headers["Content-Length"] = str(len(body))
        self.client_address = (client_ip, 12345)
        self.rfile = io.BytesIO(body)
        self.status: int | None = None
        self.json_body: dict | None = None
        self.extra_headers: list = []

    def _json(self, status: int, payload: dict, extra_headers=None):
        self.status = status
        self.json_body = payload
        self.extra_headers = list(extra_headers or [])


_FAKE_USER = {"id": "11111111-2222-3333-4444-555555555555", "email": "marc@example.com"}


# ── POST /api/account/delete — auth gates ─────────────────────────────────────

def test_returns_401_when_no_auth_header():
    h = _FakeHandler()
    account_server.run_delete_account(h)
    assert h.status == 401


def test_returns_401_when_auth_header_is_not_bearer():
    h = _FakeHandler(auth_header="Basic xyz")
    account_server.run_delete_account(h)
    assert h.status == 401


def test_returns_401_when_bearer_token_is_empty():
    h = _FakeHandler(auth_header="Bearer ")
    account_server.run_delete_account(h)
    assert h.status == 401


def test_returns_503_when_env_not_configured(monkeypatch):
    monkeypatch.delenv("PEBBLE_SUPABASE_URL")
    h = _FakeHandler(auth_header="Bearer ey.fake.jwt")
    account_server.run_delete_account(h)
    assert h.status == 503


def test_returns_401_when_token_validates_as_none(monkeypatch):
    monkeypatch.setattr("pebble.server.account.validate_access_token", lambda token, **kw: None)
    h = _FakeHandler(auth_header="Bearer ey.expired.jwt")
    account_server.run_delete_account(h)
    assert h.status == 401


def test_returns_502_when_validate_raises_admin_error(monkeypatch):
    from pebble.auth_admin import AdminError
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda *a, **kw: (_ for _ in ()).throw(AdminError("DNS failure")))
    h = _FakeHandler(auth_header="Bearer ey.fake.jwt")
    account_server.run_delete_account(h)
    assert h.status == 502


# ── POST /api/account/delete — soft-delete happy path ────────────────────────

def test_schedules_soft_delete_on_first_request(monkeypatch, output_dir):
    """First delete request schedules deletion; no immediate hard delete."""
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda *a, **kw: dict(_FAKE_USER))
    delete_calls: list = []
    monkeypatch.setattr("pebble.server.account.delete_user", lambda uid, **kw: delete_calls.append(uid))

    h = _FakeHandler(auth_header="Bearer ey.real.token")
    account_server.run_delete_account(h)

    assert h.status == 200
    assert h.json_body["ok"] is True
    assert h.json_body["scheduled"] is True
    assert "scheduled_for" in h.json_body
    # Hard delete must NOT have been called yet.
    assert delete_calls == [], "delete_user should not be called on first soft-delete request"
    # File should exist.
    pd_file = output_dir / ".users" / _FAKE_USER["id"] / "pending_deletion.json"
    assert pd_file.exists()
    pd = json.loads(pd_file.read_text())
    assert pd["user_id"] == _FAKE_USER["id"]


def test_second_request_returns_existing_schedule(monkeypatch, output_dir):
    """Second POST while in cooling-off returns the existing scheduled_for."""
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda *a, **kw: dict(_FAKE_USER))
    monkeypatch.setattr("pebble.server.account.delete_user", lambda *a, **kw: None)

    h1 = _FakeHandler(auth_header="Bearer ey.t")
    account_server.run_delete_account(h1)
    first_scheduled = h1.json_body["scheduled_for"]

    h2 = _FakeHandler(auth_header="Bearer ey.t")
    account_server.run_delete_account(h2)
    assert h2.status == 200
    assert h2.json_body["scheduled"] is True
    assert h2.json_body["scheduled_for"] == first_scheduled


def test_validate_called_with_extracted_token(monkeypatch, output_dir):
    """The bearer prefix is stripped before validating."""
    captured: dict = {}
    def fake_validate(token, **kw):
        captured["token"] = token
        return dict(_FAKE_USER)
    monkeypatch.setattr("pebble.server.account.validate_access_token", fake_validate)
    monkeypatch.setattr("pebble.server.account.delete_user", lambda *_a, **_kw: None)
    h = _FakeHandler(auth_header="Bearer ey.real.token.value")
    account_server.run_delete_account(h)
    assert captured["token"] == "ey.real.token.value"


# ── POST /api/account/cancel-deletion ────────────────────────────────────────

def test_cancel_deletion_removes_file(monkeypatch, output_dir):
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda *a, **kw: dict(_FAKE_USER))
    monkeypatch.setattr("pebble.server.account.delete_user", lambda *a, **kw: None)

    # Schedule first.
    account_server.run_delete_account(_FakeHandler(auth_header="Bearer ey.t"))
    pd_file = output_dir / ".users" / _FAKE_USER["id"] / "pending_deletion.json"
    assert pd_file.exists()

    # Now cancel.
    h = _FakeHandler(auth_header="Bearer ey.t")
    account_server.run_cancel_deletion(h)
    assert h.status == 200
    assert h.json_body["ok"] is True
    assert h.json_body["cancelled"] is True
    assert not pd_file.exists()


def test_cancel_when_nothing_pending_returns_ok(monkeypatch, output_dir):
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda *a, **kw: dict(_FAKE_USER))
    h = _FakeHandler(auth_header="Bearer ey.t")
    account_server.run_cancel_deletion(h)
    assert h.status == 200
    assert h.json_body["cancelled"] is False


# ── GET /api/account/profile ──────────────────────────────────────────────────

def test_get_profile_returns_profile_data(monkeypatch, output_dir):
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda *a, **kw: dict(_FAKE_USER))
    monkeypatch.setattr("pebble.server.account.get_profile",
                        lambda uid, **kw: {"first_name": "Marc", "timezone": "America/New_York",
                                           "display_name": None, "plan_tier": "free"})
    h = _FakeHandler(auth_header="Bearer ey.t")
    account_server.run_get_profile(h)
    assert h.status == 200
    assert h.json_body["email"] == "marc@example.com"
    assert h.json_body["first_name"] == "Marc"
    assert h.json_body["timezone"] == "America/New_York"
    assert h.json_body["deletion_scheduled_for"] is None


def test_get_profile_includes_deletion_date_when_scheduled(monkeypatch, output_dir):
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda *a, **kw: dict(_FAKE_USER))
    monkeypatch.setattr("pebble.server.account.get_profile",
                        lambda uid, **kw: {"timezone": "UTC"})
    monkeypatch.setattr("pebble.server.account.delete_user", lambda *a, **kw: None)

    # Write a pending deletion with a far-future date.
    pd_path = output_dir / ".users" / _FAKE_USER["id"] / "pending_deletion.json"
    pd_path.parent.mkdir(parents=True, exist_ok=True)
    pd_path.write_text(json.dumps({
        "user_id": _FAKE_USER["id"],
        "email": _FAKE_USER["email"],
        "requested_at": "2026-05-17T00:00:00+00:00",
        "scheduled_for": "2099-01-01T00:00:00+00:00",
    }))

    h = _FakeHandler(auth_header="Bearer ey.t")
    account_server.run_get_profile(h)
    assert h.status == 200
    assert h.json_body["deletion_scheduled_for"] == "2099-01-01T00:00:00+00:00"


# ── PATCH /api/account/profile ────────────────────────────────────────────────

def test_patch_profile_updates_name(monkeypatch, output_dir):
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda *a, **kw: dict(_FAKE_USER))
    monkeypatch.setattr("pebble.server.account.update_profile",
                        lambda uid, updates, **kw: {"first_name": updates.get("first_name"),
                                                     "display_name": None, "timezone": "UTC"})
    body = json.dumps({"first_name": "Marc"}).encode()
    h = _FakeHandler(auth_header="Bearer ey.t", body=body)
    account_server.run_patch_profile(h)
    assert h.status == 200
    assert h.json_body["first_name"] == "Marc"


def test_patch_profile_rejects_unknown_timezone(monkeypatch, output_dir):
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda *a, **kw: dict(_FAKE_USER))
    # Force zoneinfo available so validation runs properly.
    monkeypatch.setattr("pebble.server.account._is_valid_timezone",
                        lambda tz: tz in {"America/New_York", "UTC"})
    body = json.dumps({"timezone": "Mars/Olympus_Mons"}).encode()
    h = _FakeHandler(auth_header="Bearer ey.t", body=body)
    account_server.run_patch_profile(h)
    assert h.status == 400


def test_patch_profile_rejects_empty_body(monkeypatch, output_dir):
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda *a, **kw: dict(_FAKE_USER))
    body = json.dumps({}).encode()
    h = _FakeHandler(auth_header="Bearer ey.t", body=body)
    account_server.run_patch_profile(h)
    assert h.status == 400


# ── per-IP rate limit ─────────────────────────────────────────────────────────

def test_returns_429_after_burst_per_ip(monkeypatch, output_dir):
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda token, **kw: None)
    statuses = []
    for i in range(10):
        h = _FakeHandler(auth_header=f"Bearer ey.t{i}", client_ip="198.51.100.42")
        account_server.run_delete_account(h)
        statuses.append(h.status)
    assert 429 in statuses
    pre_throttle = [s for s in statuses if s != 429]
    assert len(pre_throttle) <= 3


def test_rate_limit_is_per_ip_not_global(monkeypatch, output_dir):
    monkeypatch.setattr("pebble.server.account.validate_access_token",
                        lambda token, **kw: None)
    for i in range(5):
        h = _FakeHandler(auth_header=f"Bearer ey.{i}", client_ip="198.51.100.1")
        account_server.run_delete_account(h)
    h = _FakeHandler(auth_header="Bearer ey.different", client_ip="198.51.100.2")
    account_server.run_delete_account(h)
    assert h.status == 401
