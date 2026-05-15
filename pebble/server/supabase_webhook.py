"""POST /api/internal/supabase-webhook — receives Supabase Database Webhook
events and triggers Pebble-side side-effects.

Today this handler does exactly one thing: when a new row lands in
``public.profiles`` (which only happens via the auto-insert trigger
created by ``001_profiles.sql`` on every signup, including OAuth), it
sends the polished welcome email through the engine's existing email
pipeline.

WHY ROUTE EMAIL THROUGH HERE INSTEAD OF SUPABASE'S BUILT-IN EMAIL:
- Supabase Auth's built-in confirmation email only fires for
  email/password signups. OAuth users (Google, GitHub) never trigger
  one — they're already verified by the provider.
- We want a single, branded welcome email for ALL signups regardless
  of method. Hooking the `profiles` INSERT (which fires for every new
  user) is the only event that's actually universal.
- Supabase Auth email templates also don't support arbitrary HTML or
  the personalisation we want; the engine's email.py module already
  has a full pluggable sender + Pebble-branded template.

SECURITY:
- The endpoint accepts an ``Authorization: Bearer <secret>`` header
  matching ``PEBBLE_SUPABASE_WEBHOOK_SECRET``. Constant-time compare to
  prevent timing-attack secret discovery.
- Without that env var set, the endpoint refuses ALL requests (503)
  — we'd rather be visibly broken than silently insecure.
- Validates payload structure before doing anything; malformed bodies
  return 400, not 500.

WIRING:
- Supabase Dashboard → Database → Webhooks → Create a new hook:
    Name: "Pebble welcome email"
    Table: public.profiles
    Events: Insert
    Type: HTTP Request
    Method: POST
    URL: https://engine.pebbleapp.ai/api/internal/supabase-webhook
    HTTP Headers:
      Authorization: Bearer <PEBBLE_SUPABASE_WEBHOOK_SECRET value>
      Content-Type: application/json
"""
from __future__ import annotations

import hmac
import json
import logging
import os
from typing import Any, Optional

from pebble.email import send_welcome_async, EmailError

log = logging.getLogger("pebble.supabase_webhook")


def _read_body(handler) -> Optional[dict]:
    """Read + parse the request body as JSON. Returns None on bad input."""
    try:
        length = int(handler.headers.get("Content-Length", "0") or "0")
    except ValueError:
        return None
    if length <= 0 or length > 65536:
        # Sane upper bound — Supabase payloads are tiny (~1KB). Anything
        # this big is almost certainly malicious or misconfigured.
        return None
    try:
        raw = handler.rfile.read(length)
        return json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _check_auth(handler) -> bool:
    """Constant-time compare of the Authorization header against the
    configured secret. Returns False if either is missing."""
    secret = os.environ.get("PEBBLE_SUPABASE_WEBHOOK_SECRET", "").strip()
    if not secret:
        return False
    header = handler.headers.get("Authorization", "") or ""
    expected = f"Bearer {secret}"
    # hmac.compare_digest avoids leaking match progress via timing.
    return hmac.compare_digest(header.encode("utf-8"), expected.encode("utf-8"))


def run_supabase_webhook(handler) -> None:
    """Entry point — wired from pebble_engine.py POST routing."""
    # First gate: secret must be configured. If it isn't, return 503 so
    # the misconfiguration is visible (rather than silently accepting
    # any request).
    if not os.environ.get("PEBBLE_SUPABASE_WEBHOOK_SECRET", "").strip():
        log.warning("supabase webhook called but PEBBLE_SUPABASE_WEBHOOK_SECRET not set")
        handler._json(503, {"error": "Webhook not configured on this host"})
        return

    # Second gate: secret on the request must match.
    if not _check_auth(handler):
        log.info("supabase webhook auth rejected")
        handler._json(401, {"error": "Unauthorized"})
        return

    payload = _read_body(handler)
    if not isinstance(payload, dict):
        handler._json(400, {"error": "Invalid JSON body"})
        return

    event_type = payload.get("type")
    table = payload.get("table")
    schema = payload.get("schema") or "public"
    record = payload.get("record") or {}

    # We only act on INSERTs to public.profiles. Anything else is silently
    # accepted with a 200 so Supabase doesn't retry — useful if Marc
    # later wires more events through the same hook.
    if event_type != "INSERT" or table != "profiles" or schema != "public":
        handler._json(200, {"ok": True, "action": "ignored", "reason": f"event {schema}.{table} {event_type}"})
        return

    email = (record.get("email") or "").strip()
    if not email:
        # Probably a profile row inserted without email — unlikely but
        # not worth crashing for.
        handler._json(200, {"ok": True, "action": "skipped", "reason": "no email on record"})
        return

    first_name = _clean_first_name(record.get("first_name"))

    try:
        # Fire-and-forget — sending blocks on a network call to Resend
        # and we don't want Supabase's webhook to wait. The async pool
        # handles retries internally; failures get logged.
        send_welcome_async(email, first_name=first_name)
    except EmailError as e:
        log.exception("welcome email failed for %s: %s", email, e)
        # Still 200 — the user IS signed up; an email failure shouldn't
        # cause Supabase to retry (which would double-send when the
        # transient issue resolves).
        handler._json(200, {"ok": True, "action": "queued_with_error", "error": str(e)})
        return

    log.info("welcome email queued for %s (first_name=%r)", email, first_name)
    handler._json(200, {"ok": True, "action": "welcome_sent", "email": email})


def _clean_first_name(raw: Any) -> Optional[str]:
    """Normalize first_name. Supabase profiles trigger pulls it from
    `auth.users.raw_user_meta_data->>'first_name'` OR the local-part of
    the email if neither metadata field is present, so it can be
    anything from a real name to a username-looking string. Trim, cap
    at 80 chars, and return None when empty so the email template
    falls back to "there"."""
    if not isinstance(raw, str):
        return None
    cleaned = raw.strip()[:80]
    return cleaned or None
