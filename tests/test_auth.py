"""Tests for pebble.auth — password hashing, user creation, sessions, cookies."""
from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import pytest

import pebble_engine
import pebble.auth as auth
import pebble.server.auth as auth_server


@pytest.fixture
def fake_output(tmp_path, monkeypatch):
    """Redirect pebble_engine.OUTPUT_DIR so auth writes to tmp."""
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    return out


# ---- Password hashing -----------------------------------------------------

def test_hash_password_roundtrips(fake_output):
    h = auth.hash_password("hunter2-correct-horse")
    assert h.startswith("scrypt$")
    assert auth.verify_password("hunter2-correct-horse", h) is True


def test_verify_password_rejects_wrong(fake_output):
    h = auth.hash_password("correct")
    assert auth.verify_password("wrong", h) is False


def test_hash_password_is_salted(fake_output):
    """Identical passwords should hash differently because of the salt."""
    h1 = auth.hash_password("same")
    h2 = auth.hash_password("same")
    assert h1 != h2


def test_verify_handles_garbage_hash(fake_output):
    assert auth.verify_password("anything", "not-a-real-hash") is False
    assert auth.verify_password("anything", "") is False


# ---- User creation --------------------------------------------------------

def test_create_user_persists_record(fake_output):
    user = auth.create_user("alice@example.com", "hunter2hunter")
    assert user.email == "alice@example.com"
    assert user.id and len(user.id) >= 32  # UUID4
    assert user.password_hash.startswith("scrypt$")
    path = fake_output / ".users" / f"{user.id}.json"
    assert path.exists()


def test_create_user_rejects_duplicate_email(fake_output):
    auth.create_user("bob@example.com", "first-password-1")
    with pytest.raises(auth.AuthError, match="already in use"):
        auth.create_user("bob@example.com", "different-password-2")


def test_create_user_normalizes_email_case(fake_output):
    auth.create_user("Carol@Example.com", "valid-password")
    with pytest.raises(auth.AuthError):
        auth.create_user("CAROL@example.com", "valid-password")


def test_create_user_rejects_invalid_email(fake_output):
    with pytest.raises(auth.AuthError, match="valid email"):
        auth.create_user("not-an-email", "valid-password")


def test_create_user_rejects_short_password(fake_output):
    with pytest.raises(auth.AuthError, match="at least 8"):
        auth.create_user("dan@example.com", "short")


def test_find_user_by_email(fake_output):
    u = auth.create_user("eve@example.com", "valid-password")
    found = auth.find_user_by_email("eve@example.com")
    assert found is not None
    assert found.id == u.id


def test_find_user_by_email_case_insensitive(fake_output):
    auth.create_user("frank@example.com", "valid-password")
    assert auth.find_user_by_email("FRANK@example.com") is not None


def test_authenticate_returns_user_on_match(fake_output):
    auth.create_user("grace@example.com", "valid-password")
    user = auth.authenticate("grace@example.com", "valid-password")
    assert user is not None
    assert user.email == "grace@example.com"


def test_authenticate_rejects_wrong_password(fake_output):
    auth.create_user("hank@example.com", "right-password")
    assert auth.authenticate("hank@example.com", "wrong-password") is None


def test_authenticate_unknown_email_returns_none(fake_output):
    assert auth.authenticate("ghost@example.com", "anything") is None


# ---- Sessions -------------------------------------------------------------

def test_session_roundtrip(fake_output):
    u = auth.create_user("ivy@example.com", "valid-password")
    sess = auth.create_session(u.id)
    assert sess.token and len(sess.token) >= 32
    loaded = auth.get_session(sess.token)
    assert loaded is not None
    assert loaded.user_id == u.id


def test_session_revoke(fake_output):
    u = auth.create_user("juno@example.com", "valid-password")
    sess = auth.create_session(u.id)
    assert auth.revoke_session(sess.token) is True
    assert auth.get_session(sess.token) is None


def test_session_to_user(fake_output):
    u = auth.create_user("kara@example.com", "valid-password")
    sess = auth.create_session(u.id)
    found = auth.session_to_user(sess.token)
    assert found is not None
    assert found.id == u.id


def test_get_session_unknown_token_returns_none(fake_output):
    assert auth.get_session("totally-fake-token") is None


def test_parse_session_token():
    cookie = "other=foo; pebble_session=ABC123; bar=baz"
    assert auth.parse_session_token(cookie) == "ABC123"
    assert auth.parse_session_token("") == ""
    assert auth.parse_session_token("no-token-here") == ""


def test_cookie_for_session_has_secure_flag_when_requested():
    cookie = auth.cookie_for_session("tok", secure=True)
    assert "Secure" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie


def test_cookie_for_session_omits_secure_in_dev():
    cookie = auth.cookie_for_session("tok", secure=False)
    assert "Secure" not in cookie
    assert "HttpOnly" in cookie


# ---- HTTP handlers (synthetic FakeHandler) -------------------------------

class FakeHandler:
    """Minimal handler that captures responses + accepts Cookie headers."""
    def __init__(self, body: dict | None = None, cookie: str | None = None):
        raw = json.dumps(body).encode("utf-8") if body is not None else b""
        self.rfile = BytesIO(raw)
        self.headers = {"Content-Length": str(len(raw))}
        if cookie:
            self.headers["Cookie"] = cookie
        self.status: int | None = None
        self.json_body: dict | None = None
        self.extra_headers: list = []

    def _json(self, status: int, payload: dict, extra_headers=None):
        self.status = status
        self.json_body = payload
        self.extra_headers = list(extra_headers or [])


def test_signup_handler_creates_user_and_sets_cookie(fake_output):
    h = FakeHandler({"email": "leo@example.com", "password": "valid-password"})
    auth_server.run_signup(h)
    assert h.status == 201
    assert h.json_body["user"]["email"] == "leo@example.com"
    set_cookie = next((v for k, v in h.extra_headers if k == "Set-Cookie"), None)
    assert set_cookie and "pebble_session=" in set_cookie


def test_signup_handler_validates(fake_output):
    h = FakeHandler({"email": "not-an-email", "password": "short"})
    auth_server.run_signup(h)
    assert h.status == 400


def test_login_handler_returns_cookie_on_success(fake_output):
    auth.create_user("mira@example.com", "valid-password")
    h = FakeHandler({"email": "mira@example.com", "password": "valid-password"})
    auth_server.run_login(h)
    assert h.status == 200
    set_cookie = next((v for k, v in h.extra_headers if k == "Set-Cookie"), None)
    assert set_cookie and "pebble_session=" in set_cookie


def test_login_handler_rejects_wrong_password(fake_output):
    auth.create_user("noa@example.com", "right-password")
    h = FakeHandler({"email": "noa@example.com", "password": "wrong-password"})
    auth_server.run_login(h)
    assert h.status == 401
    assert "wrong" in h.json_body["error"].lower() or "password" in h.json_body["error"].lower()


def test_me_handler_returns_user_when_session_valid(fake_output):
    u = auth.create_user("ola@example.com", "valid-password")
    sess = auth.create_session(u.id)
    h = FakeHandler(cookie=f"pebble_session={sess.token}")
    auth_server.run_me(h)
    assert h.status == 200
    assert h.json_body["user"]["email"] == "ola@example.com"


def test_me_handler_returns_401_without_session(fake_output):
    h = FakeHandler()
    auth_server.run_me(h)
    assert h.status == 401


def test_logout_handler_revokes_session(fake_output):
    u = auth.create_user("pam@example.com", "valid-password")
    sess = auth.create_session(u.id)
    h = FakeHandler(cookie=f"pebble_session={sess.token}")
    auth_server.run_logout(h)
    assert h.status == 200
    # Session is gone
    assert auth.get_session(sess.token) is None


# ---- Phase A.5 deprecation (2026-05-16) ---------------------------------

def _has_deprecation_headers(headers: list) -> bool:
    """The three headers every legacy /api/auth/* response should carry."""
    keys = {k for k, _ in headers}
    return (
        "Deprecation" in keys
        and "Sunset" in keys
        and any(k == "Link" for k in keys)
    )


def test_legacy_signup_emits_deprecation_headers(fake_output):
    """Every legacy auth response carries Deprecation + Sunset + Link
    headers so clients see the EOL signal explicitly."""
    h = FakeHandler({"email": "phase-a5@example.com", "password": "valid-password"})
    auth_server.run_signup(h)
    assert h.status == 201
    assert _has_deprecation_headers(h.extra_headers), \
        f"expected deprecation headers, got {h.extra_headers!r}"


def test_legacy_login_emits_deprecation_headers(fake_output):
    auth.create_user("dep-login@example.com", "valid-password")
    h = FakeHandler({"email": "dep-login@example.com", "password": "valid-password"})
    auth_server.run_login(h)
    assert h.status == 200
    assert _has_deprecation_headers(h.extra_headers)


def test_legacy_me_emits_deprecation_headers(fake_output):
    u = auth.create_user("dep-me@example.com", "valid-password")
    sess = auth.create_session(u.id)
    h = FakeHandler(cookie=f"pebble_session={sess.token}")
    auth_server.run_me(h)
    assert h.status == 200
    assert _has_deprecation_headers(h.extra_headers)


def test_legacy_logout_emits_deprecation_headers(fake_output):
    u = auth.create_user("dep-logout@example.com", "valid-password")
    sess = auth.create_session(u.id)
    h = FakeHandler(cookie=f"pebble_session={sess.token}")
    auth_server.run_logout(h)
    assert h.status == 200
    assert _has_deprecation_headers(h.extra_headers)


def test_legacy_endpoints_return_410_when_disabled(fake_output, monkeypatch):
    """PEBBLE_LEGACY_AUTH_DISABLED=true flips every legacy endpoint to
    410 Gone with the migration JSON. Production posture once Supabase
    Auth migration is verified end-to-end."""
    monkeypatch.setenv("PEBBLE_LEGACY_AUTH_DISABLED", "true")
    # No matter which legacy endpoint we hit, response is 410.
    for run_fn in (
        auth_server.run_signup,
        auth_server.run_login,
        auth_server.run_logout,
        auth_server.run_me,
        auth_server.run_forgot,
        auth_server.run_reset,
    ):
        h = FakeHandler({"email": "x@example.com", "password": "valid-password"})
        run_fn(h)
        assert h.status == 410, f"{run_fn.__name__} should return 410 when disabled, got {h.status}"
        assert "migration" in h.json_body, f"{run_fn.__name__} should include migration pointer"
        # 410 responses ALSO carry deprecation headers
        assert _has_deprecation_headers(h.extra_headers), \
            f"{run_fn.__name__} 410 should still carry deprecation headers"


def test_legacy_disabled_supports_various_truthy_values(fake_output, monkeypatch):
    """Env-var parsing should accept the standard truthy spellings."""
    for val in ("1", "true", "True", "yes", "ON"):
        monkeypatch.setenv("PEBBLE_LEGACY_AUTH_DISABLED", val)
        h = FakeHandler({"email": "x@example.com", "password": "valid-password"})
        auth_server.run_signup(h)
        assert h.status == 410, f"value {val!r} should disable legacy auth"


def test_legacy_disabled_default_is_off(fake_output, monkeypatch):
    """Without the env var, the endpoints stay enabled (backwards compat)."""
    monkeypatch.delenv("PEBBLE_LEGACY_AUTH_DISABLED", raising=False)
    h = FakeHandler({"email": "default-on@example.com", "password": "valid-password"})
    auth_server.run_signup(h)
    assert h.status == 201, "default should keep legacy auth enabled"


def test_legacy_auth_client_was_removed_from_v3():
    """Sanity check: ui/v3/lib/auth.ts was deleted in Phase A.5.
    The new auth flow is via @supabase/ssr — see ui/v3/lib/supabase/*.

    If anything imports the legacy module again, the build fails fast
    via the TS compiler, but a Python-side regression test pins the
    deletion so a future "restore from git" can't silently bring it
    back without the deprecation discussion."""
    legacy_path = Path(__file__).resolve().parent.parent / "ui" / "v3" / "lib" / "auth.ts"
    assert not legacy_path.exists(), (
        f"{legacy_path} still exists. The Phase A.5 deprecation removed "
        f"the legacy auth client; restore would re-introduce a parallel "
        f"auth surface alongside Supabase. Don't."
    )
