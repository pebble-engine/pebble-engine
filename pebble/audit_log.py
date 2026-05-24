"""Append-only audit log for security-relevant account events.

Writes to public.audit_log via the Supabase service role (PostgREST
REST API). The helper is fire-and-forget — exceptions are logged but
never raised. This guarantees that an audit-log outage cannot break the
calling endpoint (which is far worse than a missed log entry).

Public entry points:
  log_event(user_id, event_type, ip, user_agent, metadata)
  log_event_for_handler(handler, user_id, event_type, metadata)

Standard event_type values (extend as needed, but keep them short snake_case):
  password_change, password_change_failed, email_change_requested,
  email_change_confirmed, account_delete_requested, account_delete_executed,
  plan_changed, payment_method_changed, mfa_enabled, mfa_disabled,
  signed_in_new_device, global_signout, data_export_requested,
  data_export_delivered.

Requires env vars: SUPABASE_URL (or PEBBLE_SUPABASE_URL) and
SUPABASE_SERVICE_ROLE_KEY (or PEBBLE_SUPABASE_SERVICE_ROLE_KEY).
If either is missing the helper no-ops with a warning — callers don't
need to care.

Implementation notes:
- Uses urllib (stdlib) against Supabase's PostgREST REST API — the same
  pattern as pebble.auth_admin and pebble.storage. No extra SDK dep.
- Tests monkeypatch the _supabase_insert symbol to stay fully offline.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

from pebble.log import log


_MAX_UA_LEN = 512
_DEFAULT_TIMEOUT_SEC = 5.0


# ---------------------------------------------------------------------------
# Internal helpers — patched by tests
# ---------------------------------------------------------------------------

def _env_url() -> str:
    """Resolve Supabase project URL. Accepts both the PEBBLE_-prefixed and
    Supabase-native env var names, same convention as pebble.storage."""
    val = (os.environ.get("PEBBLE_SUPABASE_URL")
           or os.environ.get("SUPABASE_URL")
           or "").strip()
    return val.rstrip("/")


def _env_service_role() -> str:
    return (os.environ.get("PEBBLE_SUPABASE_SERVICE_ROLE_KEY")
            or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            or "").strip()


def _is_configured() -> bool:
    return bool(_env_url()) and bool(_env_service_role())


def _supabase_insert(row: dict[str, Any]) -> None:
    """POST one row to public.audit_log via PostgREST.

    This is the single point of Supabase interaction. Tests monkeypatch
    this symbol — keeping all network logic here makes that reliable.
    """
    if not _is_configured():
        log.info(
            "[audit_log] Supabase not configured — skipping write: %s",
            row.get("event_type"),
        )
        return

    url = f"{_env_url()}/rest/v1/audit_log"
    body = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "apikey":        _env_service_role(),
            "Authorization": f"Bearer {_env_service_role()}",
            "Content-Type":  "application/json",
            "Prefer":        "return=minimal",
            "User-Agent":    "PebbleEngine/1.0 (+https://pebbleapp.ai)",
        },
    )
    with urllib.request.urlopen(req, timeout=_DEFAULT_TIMEOUT_SEC) as resp:
        # 201 Created expected; anything 2xx is fine.
        if resp.status >= 300:
            raise RuntimeError(f"audit_log: PostgREST returned HTTP {resp.status}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_event(
    *,
    user_id: str,
    event_type: str,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    """Append one row to public.audit_log. Never raises.

    Args:
        user_id:    Supabase UUID of the acting user.
        event_type: Short snake_case label (see module docstring for
                    the standard vocabulary).
        ip:         Client IP address, or None.
        user_agent: Raw User-Agent header value, or None. Capped at
                    512 chars before insertion.
        metadata:   Arbitrary JSON-serialisable dict. Empty dict when
                    no extra context is available.
    """
    ua = (user_agent or "")[:_MAX_UA_LEN]
    row: dict[str, Any] = {
        "user_id":    user_id,
        "event_type": event_type,
        "ip":         ip,
        "user_agent": ua or None,
        "metadata":   metadata or {},
    }
    try:
        _supabase_insert(row)
    except Exception as exc:
        log.warning(
            "[audit_log] write failed for %s/%s: %s",
            user_id, event_type, exc,
        )


def log_event_for_handler(
    *,
    handler: Any,
    user_id: str,
    event_type: str,
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    """Convenience wrapper: extract IP + User-Agent from a stdlib
    BaseHTTPRequestHandler instance.

    IP resolution order:
      1. First address in X-Forwarded-For (Railway / reverse-proxy convention).
      2. handler.client_address[0] (direct connection IP).

    Never raises.
    """
    headers = getattr(handler, "headers", {}) or {}
    xff: str = headers.get("X-Forwarded-For", "") or ""
    if xff:
        ip: Optional[str] = xff.split(",")[0].strip() or None
    else:
        ca = getattr(handler, "client_address", ("", 0))
        ip = (ca[0] if ca else "") or None

    ua: str = headers.get("User-Agent", "") or ""
    log_event(
        user_id=user_id,
        event_type=event_type,
        ip=ip,
        user_agent=ua or None,
        metadata=metadata,
    )


__all__ = ["log_event", "log_event_for_handler"]
