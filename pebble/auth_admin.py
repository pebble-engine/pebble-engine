"""Supabase Auth admin operations — server-side only.

This module is the one place that talks to Supabase's GoTrue admin
API. Used by the engine's GDPR-delete endpoint (Ch 7.7) and any
future admin operation (suspend user, force password reset, list
sessions, etc.).

Why route through the engine instead of v3 directly:
- The service-role key (PEBBLE_SUPABASE_SERVICE_ROLE_KEY) lives in
  the engine's .env. Putting it in v3 means a second place to leak.
- v3 already passes the user's Supabase access token via the
  Authorization header on cross-origin calls; this module validates
  that token before any privileged action.

Endpoints used:
- GET  /auth/v1/user                       — validate a bearer JWT,
                                              returns the calling user
- DELETE /auth/v1/admin/users/<id>         — admin delete (service
                                              role required, bypasses RLS)

The FK in migration 001 (profiles.id → auth.users.id ON DELETE
CASCADE) means deleting an auth user also wipes the profiles row.
Project files in output/<slug>/ are NOT auto-cleaned by this module
— that's a follow-up sweep (see Ch 7.7 notes).
"""
from __future__ import annotations

import base64
import binascii
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional


class AdminError(Exception):
    """Anything that goes wrong calling Supabase's admin API.
    Caller surfaces a 502 (vendor problem) or 500 to the user.

    SECURITY NOTE — DO NOT put bearer tokens, service-role keys, or
    other secrets in the .args of an AdminError. The engine's
    ``_handle_500`` logs ``repr(exc)`` plus the full traceback under
    a correlation id. Anything in the exception message lands in
    engine.log. Use generic strings ("HTTP 401", "unreachable",
    "validate token failed") — never inline a token value.
    (NLM round on Track 12 flagged this as a defense-in-depth gap.)"""


# Default 10s — admin calls hit the same Supabase project the rest of
# the engine talks to. Override for tests.
_DEFAULT_TIMEOUT_SEC = 10.0


def _env_url() -> str:
    """Resolve project URL — same dual-name fallback as pebble.storage
    so a single Supabase config works for both modules."""
    val = (os.environ.get("PEBBLE_SUPABASE_URL")
           or os.environ.get("SUPABASE_URL")
           or "").strip()
    return val.rstrip("/")


def _env_service_role() -> str:
    return (os.environ.get("PEBBLE_SUPABASE_SERVICE_ROLE_KEY")
            or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            or "").strip()


def _env_anon() -> str:
    """The anon (public) key. GoTrue's GET /auth/v1/user requires the
    `apikey` header even when authenticated with a bearer JWT."""
    return (os.environ.get("PEBBLE_SUPABASE_ANON_KEY")
            or os.environ.get("SUPABASE_ANON_KEY")
            or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
            or "").strip()


def is_configured() -> bool:
    """True iff URL + service-role + anon are all set. The admin
    endpoint needs all three to function."""
    return bool(_env_url()) and bool(_env_service_role()) and bool(_env_anon())


def _expected_iss() -> str:
    """The `iss` claim every legitimate Supabase JWT for THIS project
    carries. GoTrue stamps it as ``<project_url>/auth/v1``."""
    return f"{_env_url()}/auth/v1"


def _decode_jwt_claims(token: str) -> Optional[dict]:
    """Decode the JWT payload claims WITHOUT signature verification.

    We never verify the signature locally — that's GoTrue's job server-
    side, and we don't have the signing key here. This helper exists
    so :func:`validate_access_token` can read the ``iss`` claim BEFORE
    making a network call: a JWT whose iss doesn't match our project
    gets rejected without ever exposing the token to a potentially-
    misconfigured upstream.

    Returns the claims dict on success, or ``None`` on any structural
    error (wrong number of parts, bad base64, bad JSON, non-dict
    payload). The empty / non-string token cases are caller-checked.
    """
    parts = token.split(".")
    if len(parts) != 3:
        return None
    payload_b64 = parts[1]
    if not payload_b64:
        return None
    # base64url decode — pad to a multiple of 4 since JWTs strip '='.
    padding = "=" * (-len(payload_b64) % 4)
    try:
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
    except (binascii.Error, ValueError):
        return None
    try:
        claims = json.loads(payload_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    # RFC 7519: claims MUST be a JSON object. Defend against a hostile
    # JWT that encodes `["x"]` or `"string"` or any non-dict.
    if not isinstance(claims, dict):
        return None
    return claims


def validate_access_token(
    bearer_token: str,
    *,
    timeout_sec: float = _DEFAULT_TIMEOUT_SEC,
) -> Optional[dict]:
    """Validate a Supabase JWT by calling GoTrue's /auth/v1/user.

    Returns the user dict (with `id`, `email`, etc.) on success, None
    on any auth failure (expired token, wrong signature, etc.).

    Caller is responsible for sanitizing the token shape before
    calling; we strip whitespace and reject obvious garbage but don't
    parse the JWT.

    Raises AdminError on env-misconfig or network failure (not on
    auth-rejection — that returns None so the caller can 401 cleanly).
    """
    if not isinstance(bearer_token, str):
        return None
    token = bearer_token.strip()
    if not token or " " in token or "\n" in token:
        return None
    if not is_configured():
        raise AdminError(
            "Supabase admin not configured. Set PEBBLE_SUPABASE_URL, "
            "PEBBLE_SUPABASE_SERVICE_ROLE_KEY, and PEBBLE_SUPABASE_ANON_KEY."
        )

    # NLM round 1 finding R1 #6 — defense-in-depth iss-claim check.
    # GoTrue verifies the JWT's signature against OUR project's signing
    # keys (so a JWT from a different project would 401 there anyway),
    # but an explicit local iss check catches operator misconfiguration
    # where PEBBLE_SUPABASE_URL points at the wrong project, AND avoids
    # exposing a possibly-attacker-controlled token to a possibly-
    # misconfigured upstream. Reject malformed JWTs (wrong segment count,
    # bad base64, non-JSON payload, non-dict claims) the same way.
    claims = _decode_jwt_claims(token)
    if claims is None or claims.get("iss") != _expected_iss():
        return None

    req = urllib.request.Request(
        f"{_env_url()}/auth/v1/user",
        headers={
            # GoTrue expects BOTH headers — the apikey for project routing
            # and the bearer for the actual session.
            "apikey":        _env_anon(),
            "Authorization": f"Bearer {token}",
            "User-Agent":    "PebbleEngine/1.0 (+https://pebbleapp.ai)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # 401 / 403 → token rejected. Return None so the caller emits 401.
        if e.code in (400, 401, 403):
            return None
        # Other codes are real errors.
        raise AdminError(f"validate token: HTTP {e.code}") from e
    except urllib.error.URLError as e:
        raise AdminError(f"validate token: Supabase unreachable: {e.reason}") from e
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise AdminError(f"validate token: malformed response: {e}") from e

    user_id = data.get("id")
    if not isinstance(user_id, str) or not user_id:
        # Defensive — GoTrue always returns id on success but be paranoid.
        return None
    return data


def get_aal(bearer_token: str) -> str:
    """Return the AAL (Authenticator Assurance Level) claim from a JWT.

    Reads the ``aal`` claim from the JWT payload WITHOUT signature verification
    — useful for a fast local check after :func:`validate_access_token` has
    already confirmed the token is genuine.

    Returns ``"aal2"`` if the claim is ``"aal2"``, otherwise ``"aal1"``
    (safe default — assume weakest assurance when the claim is absent or
    unreadable so callers always block rather than accidentally allow).

    Does NOT validate the token. Call :func:`validate_access_token` first.
    """
    claims = _decode_jwt_claims(bearer_token) if isinstance(bearer_token, str) else None
    if not isinstance(claims, dict):
        return "aal1"
    return "aal2" if claims.get("aal") == "aal2" else "aal1"


def delete_user(
    user_id: str,
    *,
    timeout_sec: float = _DEFAULT_TIMEOUT_SEC,
) -> None:
    """Admin-delete a Supabase user by id. Bypasses RLS via the
    service-role key. The FK in migration 001 cascades to profiles.

    Raises AdminError on env-misconfig, bad id shape, or Supabase
    failure. Successful delete returns None.
    """
    if not is_configured():
        raise AdminError("Supabase admin not configured")
    if not isinstance(user_id, str) or not user_id.strip():
        raise AdminError("user_id is required")
    # Supabase user ids are UUIDs (8-4-4-4-12 hex). A loose check to
    # reject obvious garbage before opening a socket.
    uid = user_id.strip()
    if len(uid) < 32 or len(uid) > 64 or "/" in uid or "\\" in uid:
        raise AdminError("user_id has unexpected shape")

    req = urllib.request.Request(
        f"{_env_url()}/auth/v1/admin/users/{urllib.parse.quote(uid)}",
        method="DELETE",
        headers={
            "apikey":        _env_anon(),
            "Authorization": f"Bearer {_env_service_role()}",
            "User-Agent":    "PebbleEngine/1.0 (+https://pebbleapp.ai)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            _ = resp.read(1024)
    except urllib.error.HTTPError as e:
        # Try to extract the GoTrue error JSON for the message.
        try:
            payload = json.loads(e.read().decode("utf-8"))
            msg = payload.get("message") or payload.get("msg") or str(e)
        except Exception:
            msg = f"HTTP {e.code}"
        raise AdminError(f"delete user failed: {msg}") from e
    except urllib.error.URLError as e:
        raise AdminError(f"delete user: Supabase unreachable: {e.reason}") from e


def get_profile(
    user_id: str,
    *,
    timeout_sec: float = _DEFAULT_TIMEOUT_SEC,
) -> Optional[dict]:
    """Fetch the public.profiles row for *user_id* via PostgREST.

    Returns the profile dict or None if not found.
    Raises AdminError on config / network failure.
    """
    if not is_configured():
        raise AdminError("Supabase admin not configured")
    uid = (user_id or "").strip()
    if not uid or len(uid) > 64 or "/" in uid or "\\" in uid:
        raise AdminError("user_id has unexpected shape")
    url = (
        f"{_env_url()}/rest/v1/profiles"
        f"?id=eq.{urllib.parse.quote(uid)}&select=*&limit=1"
    )
    req = urllib.request.Request(url, headers={
        "apikey":        _env_service_role(),
        "Authorization": f"Bearer {_env_service_role()}",
        "Accept":        "application/json",
        "User-Agent":    "PebbleEngine/1.0 (+https://pebbleapp.ai)",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise AdminError(f"get_profile: HTTP {e.code}") from e
    except urllib.error.URLError as e:
        raise AdminError(f"get_profile: Supabase unreachable: {e.reason}") from e
    if not isinstance(rows, list) or not rows:
        return None
    return rows[0]


def update_profile(
    user_id: str,
    updates: dict,
    *,
    timeout_sec: float = _DEFAULT_TIMEOUT_SEC,
) -> Optional[dict]:
    """PATCH the public.profiles row for *user_id* via PostgREST.

    Only the fields in *updates* that are in the allowed set
    (``first_name``, ``display_name``, ``timezone``) are forwarded.
    Returns the updated row, or None if the row wasn't found.
    Raises AdminError on config / network / validation failure.
    """
    if not is_configured():
        raise AdminError("Supabase admin not configured")
    uid = (user_id or "").strip()
    if not uid or len(uid) > 64 or "/" in uid or "\\" in uid:
        raise AdminError("user_id has unexpected shape")
    allowed = {"first_name", "display_name", "timezone"}
    safe: dict = {}
    for k, v in (updates or {}).items():
        if k not in allowed:
            continue
        if not isinstance(v, (str, type(None))):
            raise AdminError(f"field {k!r} must be a string or null")
        if isinstance(v, str) and len(v) > 256:
            raise AdminError(f"field {k!r} is too long (max 256 chars)")
        safe[k] = v
    if not safe:
        raise AdminError("no updatable fields provided")
    url = (
        f"{_env_url()}/rest/v1/profiles"
        f"?id=eq.{urllib.parse.quote(uid)}"
    )
    body = json.dumps(safe).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PATCH", headers={
        "apikey":        _env_service_role(),
        "Authorization": f"Bearer {_env_service_role()}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
        "User-Agent":    "PebbleEngine/1.0 (+https://pebbleapp.ai)",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise AdminError(f"update_profile: HTTP {e.code}") from e
    except urllib.error.URLError as e:
        raise AdminError(f"update_profile: Supabase unreachable: {e.reason}") from e
    if not isinstance(rows, list) or not rows:
        return None
    return rows[0]


__all__ = [
    "AdminError",
    "is_configured",
    "validate_access_token",
    "get_aal",
    "delete_user",
    "get_profile",
    "update_profile",
]
