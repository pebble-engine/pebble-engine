"""Supabase-backed storage for short-lived pending tokens.

Replaces the local-filesystem approach (output/.users/**/email_change_pending.json
and output/.exports/**/*.manifest.json) with two Supabase tables so pending state
survives across multiple engine instances.

NLM 2026-05-25 critique: local-file state breaks multi-instance scale.
Instance A writes the token, Instance B's confirmation lookup 404s.
This module is the single point of Supabase interaction for both flows.

Tables managed (migration 006_pending_state.sql):
  public.email_change_pending   — single-use email-change tokens (24h TTL)
  public.data_export_manifests  — data-export download tokens (24h TTL)

Pattern mirrors pebble.audit_log:
  - urllib (stdlib) against Supabase PostgREST REST API — no extra SDK dep.
  - Tests monkeypatch _supabase_insert / _supabase_select / _supabase_delete.
  - Failures RAISE (not silently no-op) because these are auth-adjacent tokens.
    Silent no-ops on a confirmation lookup could let an attacker re-use a token
    or let a user believe their email changed when it didn't.

Env vars: SUPABASE_URL (or PEBBLE_SUPABASE_URL) and
          SUPABASE_SERVICE_ROLE_KEY (or PEBBLE_SUPABASE_SERVICE_ROLE_KEY).
Raises RuntimeError on first call if either is missing — fail-closed.
"""
from __future__ import annotations

import json
import os
import secrets
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from pebble.log import log

_DEFAULT_TIMEOUT_SEC = 5.0


# ---------------------------------------------------------------------------
# Env helpers (same pattern as audit_log)
# ---------------------------------------------------------------------------

def _env_url() -> str:
    val = (os.environ.get("PEBBLE_SUPABASE_URL")
           or os.environ.get("SUPABASE_URL")
           or "").strip()
    return val.rstrip("/")


def _env_service_role() -> str:
    return (os.environ.get("PEBBLE_SUPABASE_SERVICE_ROLE_KEY")
            or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            or "").strip()


def _require_config() -> tuple[str, str]:
    """Return (url, key). Raises RuntimeError if either is missing."""
    url = _env_url()
    key = _env_service_role()
    if not url or not key:
        raise RuntimeError(
            "pending_state: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set. "
            "This module stores auth-adjacent tokens — misconfiguration is not silently ignored."
        )
    return url, key


# ---------------------------------------------------------------------------
# Low-level Supabase helpers — monkeypatched by tests
# ---------------------------------------------------------------------------

def _supabase_insert(table: str, row: dict[str, Any]) -> None:
    """POST one row to the given PostgREST table. Raises on any failure."""
    url, key = _require_config()
    endpoint = f"{url}/rest/v1/{table}"
    body = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "apikey":        key,
            "Authorization": f"Bearer {key}",
            "Content-Type":  "application/json",
            "Prefer":        "return=minimal",
            "User-Agent":    "PebbleEngine/1.0 (+https://pebbleapp.ai)",
        },
    )
    with urllib.request.urlopen(req, timeout=_DEFAULT_TIMEOUT_SEC) as resp:
        if resp.status >= 300:
            raise RuntimeError(
                f"pending_state: PostgREST INSERT into {table} returned HTTP {resp.status}"
            )


def _supabase_select(table: str, token: str) -> Optional[dict[str, Any]]:
    """GET a single row by primary key (token). Returns None on 404.
    Raises on other failures."""
    url, key = _require_config()
    # PostgREST eq filter via query string: ?token=eq.<value>
    qs = urllib.parse.urlencode({"token": f"eq.{token}"})
    endpoint = f"{url}/rest/v1/{table}?{qs}"
    req = urllib.request.Request(
        endpoint,
        headers={
            "apikey":        key,
            "Authorization": f"Bearer {key}",
            "Accept":        "application/json",
            "User-Agent":    "PebbleEngine/1.0 (+https://pebbleapp.ai)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=_DEFAULT_TIMEOUT_SEC) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
            if not rows:
                return None
            return rows[0]
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise RuntimeError(
            f"pending_state: PostgREST SELECT from {table} returned HTTP {exc.code}"
        ) from exc


def _supabase_delete(table: str, token: str) -> bool:
    """DELETE the row with the given token. Returns True if the DELETE HTTP
    call succeeded (the row may or may not have existed — PostgREST 204s
    either way). Raises on network/server failures."""
    url, key = _require_config()
    qs = urllib.parse.urlencode({"token": f"eq.{token}"})
    endpoint = f"{url}/rest/v1/{table}?{qs}"
    req = urllib.request.Request(
        endpoint,
        method="DELETE",
        headers={
            "apikey":        key,
            "Authorization": f"Bearer {key}",
            "Prefer":        "return=minimal",
            "User-Agent":    "PebbleEngine/1.0 (+https://pebbleapp.ai)",
        },
    )
    with urllib.request.urlopen(req, timeout=_DEFAULT_TIMEOUT_SEC) as resp:
        return resp.status in (200, 204)


# ---------------------------------------------------------------------------
# Public API — email_change_pending
# ---------------------------------------------------------------------------

def create_email_change_pending(
    user_id: str,
    new_email: str,
    ttl_hours: int = 24,
) -> dict[str, str]:
    """Insert a new email-change pending token.

    Returns a dict with the generated token and its expires_at ISO string.
    Raises on Supabase failure (fail-closed — caller should surface the error).
    """
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(hours=ttl_hours)).isoformat()
    row = {
        "token":        token,
        "user_id":      user_id,
        "new_email":    new_email,
        "requested_at": now.isoformat(),
        "expires_at":   expires_at,
    }
    _supabase_insert("email_change_pending", row)
    log.info("[pending_state] email_change_pending created for user %s", user_id[:8])
    return {"token": token, "expires_at": expires_at}


def lookup_email_change_pending(token: str) -> Optional[dict[str, Any]]:
    """Look up a pending email-change token.

    Returns the row dict if found AND not yet expired, or None if the token
    is unknown or has expired. Expired tokens are returned as None without
    deleting them (the confirm endpoint handles cleanup).

    Raises on Supabase failure (fail-closed).
    """
    row = _supabase_select("email_change_pending", token)
    if row is None:
        return None
    try:
        expires = datetime.fromisoformat(row["expires_at"])
    except (KeyError, ValueError):
        # Malformed row — treat as not found.
        return None
    if datetime.now(timezone.utc) > expires:
        return None
    return row


def delete_email_change_pending(token: str) -> bool:
    """Consume (delete) an email-change pending token.

    Returns True if the DELETE request succeeded. Raises on Supabase failure.
    """
    result = _supabase_delete("email_change_pending", token)
    log.info("[pending_state] email_change_pending deleted token (result=%s)", result)
    return result


# ---------------------------------------------------------------------------
# Public API — data_export_manifests
# ---------------------------------------------------------------------------

def create_data_export_manifest(
    user_id: str,
    zip_path: str,
    ttl_hours: int = 24,
) -> dict[str, str]:
    """Insert a new data-export manifest entry.

    zip_path is the absolute path to the ZIP file on the current engine host.
    NOTE: the ZIP file itself still lives on local disk; only its metadata is
    stored in Supabase. This means the download endpoint must run on the same
    instance that created the ZIP. Multi-instance ZIP storage (S3/R2) is
    future work — tracked as a follow-up to the NLM 2026-05-25 critique.

    Returns a dict with the generated token and its expires_at ISO string.
    Raises on Supabase failure (fail-closed).
    """
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(hours=ttl_hours)).isoformat()
    row = {
        "token":        token,
        "user_id":      user_id,
        "zip_path":     zip_path,
        "requested_at": now.isoformat(),
        "expires_at":   expires_at,
    }
    _supabase_insert("data_export_manifests", row)
    log.info("[pending_state] data_export_manifest created for user %s", user_id[:8])
    return {"token": token, "expires_at": expires_at}


def lookup_data_export_manifest(token: str) -> Optional[dict[str, Any]]:
    """Look up a data-export manifest by token.

    Returns the row dict if found AND not yet expired, or None if the token
    is unknown or has expired. Expired tokens return None (caller may show
    a 410 Gone).

    Raises on Supabase failure (fail-closed).
    """
    row = _supabase_select("data_export_manifests", token)
    if row is None:
        return None
    try:
        expires = datetime.fromisoformat(row["expires_at"])
    except (KeyError, ValueError):
        return None
    if datetime.now(timezone.utc) > expires:
        return None
    return row


__all__ = [
    "create_email_change_pending",
    "lookup_email_change_pending",
    "delete_email_change_pending",
    "create_data_export_manifest",
    "lookup_data_export_manifest",
]
