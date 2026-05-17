"""POST /api/internal/stripe-webhook — receive Stripe events and update
per-user subscription state.

How it gets called
------------------
Stripe POSTs to this endpoint whenever a subscription event the account
has subscribed to fires. The events we care about all originate in
checkouts started by ``pebble/server/stripe_checkout.py``, which stamps
``metadata.pebble_user_id`` on both the Checkout Session and the
resulting Subscription so the webhook can route events back to the
right Pebble user without join-on-email.

Security
--------
- ``STRIPE_WEBHOOK_SECRET`` (a ``whsec_...`` value from
  ``stripe listen`` locally, or the Dashboard for prod) is the HMAC
  secret. Without it set, the endpoint refuses ALL requests (503) —
  prefer visibly broken to silently insecure.
- ``stripe.Webhook.construct_event`` does the HMAC verification. We
  never act on an event whose signature didn't verify.
- ``pebble_user_id`` is validated against the same shape as
  ``engagement.py`` (alphanumerics + hyphen/underscore, not a Windows
  reserved name, case-insensitive lower) — defense-in-depth in case a
  badly-crafted Stripe Subscription's metadata is malicious.

Side effect
-----------
For ``customer.subscription.{created,updated,deleted}`` events with a
valid ``pebble_user_id``, writes::

    output/.users/<user_id>/subscription.json
    {
      "status":                 "active" | "past_due" | "canceled" | ...,
      "plan":                   "starter" | "pro",
      "stripe_subscription_id": "sub_...",
      "current_period_end":     1893456000,
      "updated_at":             "2026-05-17T..."
    }

This file is the source of truth for v3's "current plan" UI. The
webhook is single-writer for it; nothing else should mutate it.

Privacy
-------
We persist ONLY the fields needed for the v3 UI to render the user's
plan + renewal date. Card data, payment method ids, last4, brand,
exp_year — all stripped before write. Logs never include card data.
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import stripe


log = logging.getLogger("pebble.stripe_webhook")


# The four event types Stripe sends us on subscription state changes.
# We DON'T handle invoice.* / checkout.* directly because the subscription
# events cover everything the UI needs to render plan + renewal date.
_SUBSCRIPTION_EVENT_TYPES = frozenset({
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
})


# Mirrored from engagement.py — keep these definitions in sync if the
# security profile changes. Forward-defense for path traversal + Windows
# reserved device names that could redirect a write to NUL / CON / etc.
_SAFE_USER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_WINDOWS_RESERVED = frozenset(
    {"con", "nul", "aux", "prn"}
    | {f"com{i}" for i in range(1, 10)}
    | {f"lpt{i}" for i in range(1, 10)}
)


def _safe_user_id(raw: object) -> str:
    """Return a sanitized lowercase user-id, or '' if the input is unsafe.
    Caller treats '' as 'no valid attribution' and skips the side effect."""
    if not isinstance(raw, str):
        return ""
    if not _SAFE_USER_ID_RE.fullmatch(raw):
        return ""
    lower = raw.lower()
    if lower in _WINDOWS_RESERVED:
        return ""
    return lower


def _output_dir() -> Path:
    """Resolve OUTPUT_DIR via the same lookup pattern as security.py /
    engagement.py — pebble_engine.OUTPUT_DIR if loaded, else compute
    relative to this file."""
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path(__file__).parent.parent.parent.resolve() / "output"


def _read_raw_body(handler) -> Optional[bytes]:
    """Return the request body as raw bytes. Stripe's HMAC verifier
    needs the EXACT raw bytes, not a JSON re-encoding. Returns None on
    empty / oversized body so the caller can 400."""
    try:
        length = int(handler.headers.get("Content-Length", "0") or "0")
    except ValueError:
        return None
    if length <= 0 or length > 65536:
        # Real Stripe webhook payloads are ~2-4KB. 64KB is generous;
        # anything over that is misconfigured or abusive.
        return None
    return handler.rfile.read(length)


def _write_subscription_sentinel(user_id: str, *, status: str, plan: str,
                                 subscription_id: str,
                                 customer_id: str,
                                 current_period_end: Optional[int]) -> None:
    user_dir = _output_dir() / ".users" / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    out = {
        "status":                 status,
        "plan":                   plan,
        "stripe_subscription_id": subscription_id,
        "stripe_customer_id":     customer_id,
        "current_period_end":     current_period_end,
        "updated_at":             datetime.now(timezone.utc).isoformat(),
    }
    (user_dir / "subscription.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8",
    )


def run_stripe_webhook(handler) -> None:
    """Entry point — wired from PebbleHandler.do_POST."""
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()
    if not secret:
        log.warning("stripe-webhook called but STRIPE_WEBHOOK_SECRET not set")
        handler._json(503, {"error": "Webhook not configured on this host"})
        return

    sig_header = (handler.headers.get("Stripe-Signature") or "").strip()
    if not sig_header:
        handler._json(400, {"error": "Missing Stripe-Signature header"})
        return

    raw_body = _read_raw_body(handler)
    if raw_body is None:
        handler._json(400, {"error": "Invalid request body"})
        return

    try:
        event = stripe.Webhook.construct_event(raw_body, sig_header, secret)
    except stripe.error.SignatureVerificationError:
        log.info("stripe-webhook signature rejected")
        handler._json(400, {"error": "Invalid signature"})
        return
    except ValueError:
        # Malformed JSON in the payload — SDK raises ValueError before
        # the HMAC check.
        handler._json(400, {"error": "Invalid request body"})
        return

    if not isinstance(event, dict):
        # construct_event should always return a dict; defensive fallback.
        handler._json(400, {"error": "Invalid event shape"})
        return

    event_type = event.get("type", "")
    if event_type not in _SUBSCRIPTION_EVENT_TYPES:
        # Stripe sends many event types; we only act on subscription state
        # changes. Return 200 (not 422) so Stripe doesn't retry — the skip
        # is intentional on our side.
        handler._json(200, {"ok": True, "action": "ignored",
                            "reason": f"event {event_type}"})
        return

    obj = ((event.get("data") or {}).get("object")) or {}
    metadata = obj.get("metadata") or {}
    user_id = _safe_user_id(metadata.get("pebble_user_id"))
    if not user_id:
        log.info("stripe-webhook %s missing/invalid pebble_user_id metadata",
                 event_type)
        handler._json(200, {"ok": True, "action": "skipped",
                            "reason": "no pebble_user_id"})
        return

    plan = metadata.get("pebble_plan") or "unknown"
    if not isinstance(plan, str) or len(plan) > 32:
        plan = "unknown"
    status = obj.get("status", "unknown")
    if not isinstance(status, str) or len(status) > 32:
        status = "unknown"

    raw_period_end = obj.get("current_period_end")
    period_end = raw_period_end if isinstance(raw_period_end, int) else None

    sub_id_raw = obj.get("id", "")
    subscription_id = sub_id_raw if isinstance(sub_id_raw, str) and len(sub_id_raw) <= 128 else ""

    cus_id_raw = obj.get("customer", "")
    customer_id = cus_id_raw if isinstance(cus_id_raw, str) and len(cus_id_raw) <= 128 else ""

    _write_subscription_sentinel(
        user_id,
        status=status,
        plan=plan,
        subscription_id=subscription_id,
        customer_id=customer_id,
        current_period_end=period_end,
    )

    log.info("stripe-webhook %s applied user=%s plan=%s status=%s",
             event_type, user_id, plan, status)
    handler._json(200, {"ok": True, "action": "applied"})
