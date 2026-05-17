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

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional


class AdminError(Exception):
    """Anything that goes wrong calling Supabase's admin API.
    Caller surfaces a 502 (vendor problem) or 500 to the user."""


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

    req = urllib.request.Request(
        f"{_env_url()}/auth/v1/user",
        headers={
            # GoTrue expects BOTH headers — the apikey for project routing
            # and the bearer for the actual session.
            "apikey":        _env_anon(),
            "Authorization": f"Bearer {token}",
            "User-Agent":    "PebbleEngine/1.0 (+https://getpebble.net)",
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
            "User-Agent":    "PebbleEngine/1.0 (+https://getpebble.net)",
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


__all__ = [
    "AdminError",
    "is_configured",
    "validate_access_token",
    "delete_user",
]
