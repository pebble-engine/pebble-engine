"""Tests for `pebble.auth_admin` — Supabase Auth admin operations.

No real network calls. All Supabase REST calls are mocked at the
`urllib.request.urlopen` layer.
"""
from __future__ import annotations

import io
import json
from typing import Any

import pytest

from pebble import auth_admin


# ---- Fixture: act as if Supabase env is configured ----------------------

@pytest.fixture(autouse=True)
def _supabase_env(monkeypatch):
    monkeypatch.setenv("PEBBLE_SUPABASE_URL", "https://proj.supabase.co")
    monkeypatch.setenv("PEBBLE_SUPABASE_SERVICE_ROLE_KEY", "service-role-jwt-fake")
    monkeypatch.setenv("PEBBLE_SUPABASE_ANON_KEY", "anon-key-fake")
    # Belt + suspenders — also drop the unprefixed names so dual-fallback
    # tests don't accidentally pick stale values from the dev shell.
    for name in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_ANON_KEY"):
        monkeypatch.delenv(name, raising=False)
    yield


# ---- is_configured -------------------------------------------------------

def test_is_configured_true_when_all_three_set():
    assert auth_admin.is_configured() is True


def test_is_configured_false_when_url_missing(monkeypatch):
    monkeypatch.delenv("PEBBLE_SUPABASE_URL")
    assert auth_admin.is_configured() is False


def test_is_configured_false_when_service_role_missing(monkeypatch):
    monkeypatch.delenv("PEBBLE_SUPABASE_SERVICE_ROLE_KEY")
    assert auth_admin.is_configured() is False


def test_is_configured_false_when_anon_missing(monkeypatch):
    monkeypatch.delenv("PEBBLE_SUPABASE_ANON_KEY")
    assert auth_admin.is_configured() is False


def test_is_configured_accepts_unprefixed_fallback_names(monkeypatch):
    """Same dual-name fallback as pebble.storage — accept Supabase's
    standard SUPABASE_* names when PEBBLE_* aren't set."""
    monkeypatch.delenv("PEBBLE_SUPABASE_URL")
    monkeypatch.delenv("PEBBLE_SUPABASE_SERVICE_ROLE_KEY")
    monkeypatch.delenv("PEBBLE_SUPABASE_ANON_KEY")
    monkeypatch.setenv("SUPABASE_URL", "https://proj.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "x")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "y")
    assert auth_admin.is_configured() is True


# ---- validate_access_token ----------------------------------------------

class _FakeResp:
    def __init__(self, status: int = 200, body: bytes = b"{}"):
        self.status = status
        self._body = body

    def read(self, _n: int = -1) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def test_validate_rejects_empty_token():
    assert auth_admin.validate_access_token("") is None
    assert auth_admin.validate_access_token(None) is None  # type: ignore[arg-type]


def test_validate_rejects_tokens_with_whitespace():
    assert auth_admin.validate_access_token("ey token with space") is None
    assert auth_admin.validate_access_token("ey\ntoken") is None


def test_validate_raises_when_not_configured(monkeypatch):
    monkeypatch.delenv("PEBBLE_SUPABASE_URL")
    with pytest.raises(auth_admin.AdminError, match="not configured"):
        auth_admin.validate_access_token("eyJhbGciOiJIUzI1NiJ9.abc")


def test_validate_returns_user_on_success(monkeypatch):
    user_body = json.dumps({
        "id":    "11111111-2222-3333-4444-555555555555",
        "email": "marc@example.com",
        "role":  "authenticated",
    }).encode("utf-8")
    captured = {}
    def fake_urlopen(req, *args, **kwargs):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.headers)
        return _FakeResp(200, user_body)
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    user = auth_admin.validate_access_token("eyJhbGciOiJIUzI1NiJ9.fake-jwt")
    assert user is not None
    assert user["id"] == "11111111-2222-3333-4444-555555555555"
    assert user["email"] == "marc@example.com"
    # Hits GoTrue's /auth/v1/user
    assert captured["url"].endswith("/auth/v1/user")
    # Sends both apikey + Authorization headers
    headers_lower = {k.lower(): v for k, v in captured["headers"].items()}
    assert headers_lower["apikey"] == "anon-key-fake"
    assert headers_lower["authorization"].startswith("Bearer eyJ")


def test_validate_returns_none_on_401(monkeypatch):
    import urllib.error
    def fake(*_a, **_kw):
        raise urllib.error.HTTPError("x", 401, "Unauthorized",
                                      None, io.BytesIO(b'{"msg":"expired"}'))  # type: ignore[arg-type]
    monkeypatch.setattr("urllib.request.urlopen", fake)
    assert auth_admin.validate_access_token("ey.expired.token") is None


def test_validate_returns_none_on_403(monkeypatch):
    import urllib.error
    def fake(*_a, **_kw):
        raise urllib.error.HTTPError("x", 403, "Forbidden",
                                      None, io.BytesIO(b"{}"))  # type: ignore[arg-type]
    monkeypatch.setattr("urllib.request.urlopen", fake)
    assert auth_admin.validate_access_token("ey.bad.token") is None


def test_validate_raises_on_500(monkeypatch):
    import urllib.error
    def fake(*_a, **_kw):
        raise urllib.error.HTTPError("x", 500, "Server Error",
                                      None, io.BytesIO(b"{}"))  # type: ignore[arg-type]
    monkeypatch.setattr("urllib.request.urlopen", fake)
    with pytest.raises(auth_admin.AdminError, match="HTTP 500"):
        auth_admin.validate_access_token("ey.token")


def test_validate_raises_on_network_error(monkeypatch):
    import urllib.error
    def fake(*_a, **_kw):
        raise urllib.error.URLError("DNS failure")
    monkeypatch.setattr("urllib.request.urlopen", fake)
    with pytest.raises(auth_admin.AdminError, match="unreachable"):
        auth_admin.validate_access_token("ey.token")


def test_validate_returns_none_when_response_has_no_id(monkeypatch):
    """Defensive — GoTrue should always return id but be paranoid."""
    monkeypatch.setattr("urllib.request.urlopen",
                        lambda *_a, **_kw: _FakeResp(200, b'{"email":"x"}'))
    assert auth_admin.validate_access_token("ey.token") is None


# ---- delete_user --------------------------------------------------------

def test_delete_raises_when_not_configured(monkeypatch):
    monkeypatch.delenv("PEBBLE_SUPABASE_URL")
    with pytest.raises(auth_admin.AdminError, match="not configured"):
        auth_admin.delete_user("11111111-2222-3333-4444-555555555555")


def test_delete_rejects_empty_user_id():
    with pytest.raises(auth_admin.AdminError, match="required"):
        auth_admin.delete_user("")


def test_delete_rejects_short_user_id():
    """Real Supabase user ids are 36-char UUIDs. Anything obviously
    smaller is garbage."""
    with pytest.raises(auth_admin.AdminError, match="shape"):
        auth_admin.delete_user("short")


def test_delete_rejects_user_id_with_path_traversal():
    with pytest.raises(auth_admin.AdminError, match="shape"):
        auth_admin.delete_user("../" * 20)


def test_delete_constructs_correct_url(monkeypatch):
    captured = {}
    def fake(req, *_a, **_kw):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.headers)
        captured["method"] = req.method
        return _FakeResp(200, b"{}")
    monkeypatch.setattr("urllib.request.urlopen", fake)
    auth_admin.delete_user("11111111-2222-3333-4444-555555555555")
    assert captured["method"] == "DELETE"
    assert captured["url"] == (
        "https://proj.supabase.co/auth/v1/admin/users/"
        "11111111-2222-3333-4444-555555555555"
    )
    headers_lower = {k.lower(): v for k, v in captured["headers"].items()}
    # Service-role bearer (the admin key, not the anon key)
    assert headers_lower["authorization"] == "Bearer service-role-jwt-fake"
    assert headers_lower["apikey"] == "anon-key-fake"


def test_delete_raises_on_supabase_error(monkeypatch):
    import urllib.error
    def fake(*_a, **_kw):
        raise urllib.error.HTTPError(
            "x", 404, "Not Found", None,
            io.BytesIO(json.dumps({"message": "user not found"}).encode()),  # type: ignore[arg-type]
        )
    monkeypatch.setattr("urllib.request.urlopen", fake)
    with pytest.raises(auth_admin.AdminError, match="user not found"):
        auth_admin.delete_user("11111111-2222-3333-4444-555555555555")


def test_delete_raises_on_network_error(monkeypatch):
    import urllib.error
    def fake(*_a, **_kw):
        raise urllib.error.URLError("dns")
    monkeypatch.setattr("urllib.request.urlopen", fake)
    with pytest.raises(auth_admin.AdminError, match="unreachable"):
        auth_admin.delete_user("11111111-2222-3333-4444-555555555555")
