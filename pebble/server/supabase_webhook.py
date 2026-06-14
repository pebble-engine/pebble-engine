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
import re
from typing import Any, Optional

from pebble.email import send_welcome_async, EmailError
from pebble.security import RateLimiter

log = logging.getLogger("pebble.supabase_webhook")


# Per-recipient throttle. Even with a valid bearer secret, no single
# address can receive more than ``burst`` welcomes in any (1/rate) seconds
# window. Legitimate Supabase signup fires this endpoint once per address;
# anything beyond that is leaked-secret abuse or a misconfigured webhook.
#
# Numbers picked for: a duplicate signup within the hour is generous
# (sometimes the user re-clicks confirm); 100 in an hour is not.
webhook_email_limiter = RateLimiter(rate=1/3600.0, burst=2)


# Match any C0/C1 control character. Used by `_clean_first_name` to
# defang values that come from `auth.users.raw_user_meta_data` (fully
# client-controlled at signup) before they reach the welcome email subject.
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f-\x9f]+")


def _redact_email(addr: str) -> str:
    """Replace the local-part with ``<first>***`` so engine logs keep the
    domain (useful for debugging deliverability) without spreading raw
    addresses across log retention. Returns ``"?"`` for unparseable input."""
    if not addr or "@" not in addr:
        return "?"
    local, _, domain = addr.partition("@")
    if not local:
        return f"***@{domain}"
    return f"{local[0]}***@{domain}"


def _reset_rate_limiters_for_tests() -> None:
    """Test hook — clear the per-email bucket between tests. Production
    callers never reach this; the module-level limiter naturally decays."""
    global webhook_email_limiter
    webhook_email_limiter = RateLimiter(rate=1/3600.0, burst=2)


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

    # Phase 54b (2026-05-23) — flag the new account as needing an
    # explicit plan selection BEFORE we send the welcome email. The
    # Supabase profiles row typically has `id` = the auth.users UUID;
    # if it's absent the flag silently no-ops (and the user lands on
    # the legacy auto-Free path). Fail-open on any sentinel error so a
    # bad disk write never blocks signups.
    user_id = (record.get("id") or "").strip()
    if user_id:
        try:
            from pebble.user_plan import set_needs_plan_selection
            set_needs_plan_selection(user_id, True)
        except Exception as e:
            log.warning("needs_plan_selection set failed for %s: %s",
                        _redact_email(email), e)

    first_name = _clean_first_name(record.get("first_name"))
    redacted = _redact_email(email)

    # Per-address throttle. Even with a valid secret, no one address can
    # receive welcome floods. Return 200 (not 429) so Supabase doesn't
    # retry — the throttle decision is intentional on our side.
    if not webhook_email_limiter.allow(email.lower()):
        log.info("welcome email throttled for %s (per-address limit)", redacted)
        handler._json(200, {"ok": True, "action": "throttled",
                            "reason": "per-address rate limit"})
        return

    try:
        # Fire-and-forget — sending blocks on a network call to Resend
        # and we don't want Supabase's webhook to wait. The async pool
        # handles retries internally; failures get logged.
        send_welcome_async(email, first_name=first_name)
    except EmailError as e:
        log.exception("welcome email failed for %s: %s", redacted, e)
        # Still 200 — the user IS signed up; an email failure shouldn't
        # cause Supabase to retry (which would double-send when the
        # transient issue resolves).
        handler._json(200, {"ok": True, "action": "queued_with_error", "error": str(e)})
        return

    # Public community feed row — no email/PII in title or body.
    try:
        from pebble import events as _events
        _events.record(
            user_id=user_id or None,
            kind=_events.KIND_JOINED_PEBBLE,
            title="A new builder joined Pebble",
            body="Someone new just signed up. Welcome them to the community.",
            visibility=_events.VISIBILITY_PUBLIC,
        )
    except Exception as e:
        log.warning("joined_pebble event failed for %s: %s", redacted, e)

    log.info("welcome email queued for %s (first_name_len=%d)",
             redacted, len(first_name) if first_name else 0)
    # 2026-05-24 security smoke M5: redact raw email in response so it
    # doesn't land in Supabase webhook-delivery logs as PII.
    handler._json(200, {"ok": True, "action": "welcome_sent", "email": redacted})


def _clean_first_name(raw: Any) -> Optional[str]:
    """Normalize first_name. Supabase profiles trigger pulls it from
    ``auth.users.raw_user_meta_data->>'first_name'`` OR the local-part
    of the email if neither metadata field is present, so it can be
    anything from a real name to a username-looking string.

    Hardening: ``raw_user_meta_data`` is fully client-controlled at signup.
    A name containing CR/LF could turn the welcome email subject into a
    header-injection vehicle on email providers that don't normalize
    subjects themselves. Replace runs of C0/C1 control characters with a
    single space before the strip + cap, so the cleaned value is always
    safe to drop into a header or log line."""
    if not isinstance(raw, str):
        return None
    no_ctrl = _CONTROL_CHARS_RE.sub(" ", raw)
    cleaned = no_ctrl.strip()[:80]
    return cleaned or None
