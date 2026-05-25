"""POST /api/account/mfa-event — record an MFA enable / disable event.

Phase D.1 (2026-05-24) — MFA enrollment is client-driven (the v3
SecurityTab calls Supabase's mfa.enroll/verify SDK directly). After the
SDK round-trip succeeds, the frontend hits this endpoint so the engine
can:

  1. write an audit_log row (mfa_enabled / mfa_disabled) — visible in
     /settings → Activity, queryable for forensics
  2. send the user a notification email so a real customer who DIDN'T
     enable MFA (i.e. their session is compromised) finds out fast

Why a thin engine endpoint and not a Supabase database webhook?

  Webhook would need a new ingress + HMAC signing + ordering guarantees.
  The client-side fetch is two lines of v3 code, has the user's Bearer
  JWT already in hand, and lets the engine attach the calling IP +
  User-Agent to the audit row (which Supabase wouldn't know about). The
  trade-off is that a logged-in attacker could spam fake `mfa_enabled`
  events without actually enrolling — the event_type allow-list +
  per-user rate-limit (5/minute) keeps that to noise level.

The audit_log row is the source of truth for "did this user enable MFA"
— the email is best-effort and a failure to send NEVER fails the
endpoint (same fire-and-forget pattern as
:func:`send_password_changed_notification`).
"""
from __future__ import annotations

import json

from pebble.log import log
from pebble.security import RateLimiter, require_user


# ── allow-list ──────────────────────────────────────────────────────────────
# Restricting to a small set prevents arbitrary log-spam through this
# endpoint. New event types added here ALSO need to be wired into
# pebble/audit_log.py's module docstring vocab + paired with an email
# function below (if user-facing notification is desired).
_ALLOWED_EVENT_TYPES = frozenset({"mfa_enabled", "mfa_disabled"})


# Per-user rate limit. 5 events/minute is far above any human-driven
# enable-disable cadence (you don't toggle MFA that often), tight enough
# to make audit-log spam pointless. The bucket key is the Supabase user
# id, not the IP — a stolen-session attacker on a different IP would
# still hit the same bucket.
_mfa_event_limiter = RateLimiter(rate=5 / 60.0, burst=5)


def _reset_mfa_event_limiter_for_tests() -> None:
    """Test hook — clear the bucket between tests so rate-limit assertions
    are hermetic. Production callers never reach this."""
    global _mfa_event_limiter
    _mfa_event_limiter = RateLimiter(rate=5 / 60.0, burst=5)


def run_record_mfa_event(handler) -> None:
    """POST /api/account/mfa-event — { event_type: 'mfa_enabled' | 'mfa_disabled' }.

    Requires bearer JWT. Writes an audit_log row + sends a notification
    email to the calling user. Email failures are logged but don't fail
    the response.
    """
    user = require_user(handler)
    if not user:
        return  # 401 already written

    # Rate-limit BEFORE parsing the body so a flooder can't waste cycles.
    if not _mfa_event_limiter.allow(user["id"]):
        handler._json(429, {"error": "Too many MFA events. Please wait and try again."})
        return

    try:
        length = int(handler.headers.get("Content-Length", "0") or "0")
        body = json.loads(handler.rfile.read(min(length, 4096)).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid JSON body"})
        return

    if not isinstance(body, dict):
        handler._json(400, {"error": "invalid body"})
        return

    event_type = (body.get("event_type") or "").strip()
    if event_type not in _ALLOWED_EVENT_TYPES:
        handler._json(400, {"error": "invalid event_type"})
        return

    # Audit row first — that's the load-bearing forensic record. Email
    # is best-effort. Both wrapped in their own try/except so neither
    # crashes the endpoint when a downstream is unavailable.
    try:
        from pebble.audit_log import log_event_for_handler
        log_event_for_handler(
            handler=handler,
            user_id=user["id"],
            event_type=event_type,
            metadata=body.get("metadata") or {},
        )
    except Exception as exc:
        log.warning("[account_mfa] audit log write failed: %s", exc)

    try:
        if event_type == "mfa_enabled":
            from pebble.email import send_mfa_enabled_notification
            send_mfa_enabled_notification(user["email"])
        elif event_type == "mfa_disabled":
            from pebble.email import send_mfa_disabled_notification
            send_mfa_disabled_notification(user["email"])
    except Exception as exc:
        # Email outage MUST NOT fail this endpoint — the audit row is
        # already written and IS the source of truth.
        log.warning(
            "[account_mfa] %s notification email failed: %s",
            event_type, exc,
        )

    handler._json(200, {"ok": True})


__all__ = [
    "run_record_mfa_event",
    "_reset_mfa_event_limiter_for_tests",
]
