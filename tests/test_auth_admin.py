"""Tests for `pebble.auth_admin` — Supabase Auth admin operations.

No real network calls. All Supabase REST calls are mocked at the
`urllib.request.urlopen` layer.
"""
from __future__ import annotations

import base64
import io
import json
from typing import Any, Optional

import pytest

from pebble import auth_admin


# ---- JWT helper ----------------------------------------------------------

def _b64url(raw: bytes) -> str:
    """RFC 7515 base64url — strips trailing '=' padding."""
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _make_jwt(
    iss: Optional[str] = "https://proj.supabase.co/auth/v1",
    extra: Optional[dict] = None,
    *,
    omit_iss: bool = False,
    raw_payload: Optional[bytes] = None,
) -> str:
    """Build a JWT-shaped string. Signature is a placeholder — auth_admin
    NEVER verifies the signature locally (that's GoTrue's job server-side);
    the iss check is defense-in-depth on the routing target, not the
    cryptography."""
    header = _b64url(b'{"alg":"HS256","typ":"JWT"}')
    if raw_payload is not None:
        payload = _b64url(raw_payload)
    else:
        body: dict = {"sub": "11111111-2222-3333-4444-555555555555"}
        if not omit_iss and iss is not None:
            body["iss"] = iss
        if extra:
            body.update(extra)
        payload = _b64url(json.dumps(body).encode("utf-8"))
    sig = _b64url(b"fake-signature-not-verified-locally")
    return f"{header}.{payload}.{sig}"


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
    user = auth_admin.validate_access_token(_make_jwt())
    assert user is not None
    assert user["id"] == "11111111-2222-3333-4444-555555555555"
    assert user["email"] == "marc@example.com"
    # Hits GoTrue's /auth/v1/user
    assert captured["url"].endswith("/auth/v1/user")
    # Sends both apikey + Authorization headers
    headers_lower = {k.lower(): v for k, v in captured["headers"].items()}
    assert headers_lower["apikey"] == "anon-key-fake"
    assert headers_lower["authorization"].startswith("Bearer eyJ")


# ---- iss claim hardening (NLM round 1 R1 #6) -----------------------------
#
# Defense-in-depth: GoTrue already verifies the JWT's signature against
# OUR project's signing keys, so a JWT minted by a different project
# would 401 there anyway. The iss check on top catches:
#  (a) Operator misconfig where PEBBLE_SUPABASE_URL points at the wrong
#      project — without iss check, a JWT minted for that *wrong* project
#      would validate cleanly.
#  (b) Any future scenario where two Supabase projects share enough
#      signing infrastructure for cross-project JWT validation to succeed.

def test_validate_rejects_when_iss_does_not_match_configured_url(monkeypatch):
    """A JWT minted for a DIFFERENT Supabase project must be rejected
    BEFORE we send it to GoTrue. Network never happens — this is a
    pure local-validation check."""
    def must_not_call(*_a, **_kw):
        raise AssertionError("urlopen should not be called for mismatched iss")
    monkeypatch.setattr("urllib.request.urlopen", must_not_call)
    token = _make_jwt(iss="https://different-project.supabase.co/auth/v1")
    assert auth_admin.validate_access_token(token) is None


def test_validate_rejects_when_iss_claim_missing(monkeypatch):
    """A real Supabase JWT always has an iss claim. A token without one
    is either tampered with or from an upstream we don't recognize."""
    def must_not_call(*_a, **_kw):
        raise AssertionError("urlopen should not be called when iss missing")
    monkeypatch.setattr("urllib.request.urlopen", must_not_call)
    token = _make_jwt(omit_iss=True)
    assert auth_admin.validate_access_token(token) is None


def test_validate_accepts_jwt_with_matching_iss(monkeypatch):
    """The happy-path baseline: iss matches the configured URL +
    /auth/v1 suffix, GoTrue returns the user, we trust it."""
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *_a, **_kw: _FakeResp(200, json.dumps({
            "id":    "11111111-2222-3333-4444-555555555555",
            "email": "marc@example.com",
        }).encode("utf-8")),
    )
    token = _make_jwt(iss="https://proj.supabase.co/auth/v1")
    user = auth_admin.validate_access_token(token)
    assert user is not None
    assert user["id"] == "11111111-2222-3333-4444-555555555555"


def test_validate_rejects_malformed_jwt_shape(monkeypatch):
    """Not three dot-separated parts → not a JWT → reject without
    network call. Existing tests already cover whitespace + empty;
    this pins the structural check."""
    def must_not_call(*_a, **_kw):
        raise AssertionError("urlopen should not be called for malformed JWT")
    monkeypatch.setattr("urllib.request.urlopen", must_not_call)
    assert auth_admin.validate_access_token("only.two-parts") is None
    assert auth_admin.validate_access_token("one-part-no-dots") is None
    assert auth_admin.validate_access_token("four.parts.are.bad") is None


def test_validate_rejects_jwt_with_invalid_base64_payload(monkeypatch):
    """JWT-shaped but the payload section isn't valid base64url —
    reject without network call."""
    def must_not_call(*_a, **_kw):
        raise AssertionError("urlopen should not be called for bad base64")
    monkeypatch.setattr("urllib.request.urlopen", must_not_call)
    assert auth_admin.validate_access_token("header.!!!not-base64!!!.sig") is None


def test_validate_rejects_jwt_with_non_json_payload(monkeypatch):
    """JWT-shaped, payload decodes to bytes, but the bytes aren't JSON."""
    def must_not_call(*_a, **_kw):
        raise AssertionError("urlopen should not be called for non-JSON payload")
    monkeypatch.setattr("urllib.request.urlopen", must_not_call)
    token = _make_jwt(raw_payload=b"this is not json")
    assert auth_admin.validate_access_token(token) is None


def test_validate_rejects_jwt_payload_that_is_a_list_not_a_dict(monkeypatch):
    """Defensive — RFC 7519 says JWT claims MUST be a JSON object, but
    a hostile JWT could legally encode `["iss", "x"]` which json.loads
    happily returns. .get() would AttributeError on a list."""
    def must_not_call(*_a, **_kw):
        raise AssertionError("urlopen should not be called for list payload")
    monkeypatch.setattr("urllib.request.urlopen", must_not_call)
    token = _make_jwt(raw_payload=b'["this", "is", "a", "list"]')
    assert auth_admin.validate_access_token(token) is None


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
    # Use a JWT with correct iss so the local iss-check passes and the
    # network mock is allowed to fire (which then raises HTTP 500).
    with pytest.raises(auth_admin.AdminError, match="HTTP 500"):
        auth_admin.validate_access_token(_make_jwt())


def test_validate_raises_on_network_error(monkeypatch):
    import urllib.error
    def fake(*_a, **_kw):
        raise urllib.error.URLError("DNS failure")
    monkeypatch.setattr("urllib.request.urlopen", fake)
    with pytest.raises(auth_admin.AdminError, match="unreachable"):
        auth_admin.validate_access_token(_make_jwt())


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
