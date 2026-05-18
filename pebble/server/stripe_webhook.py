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
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import stripe

from pebble.security import safe_user_id


log = logging.getLogger("pebble.stripe_webhook")


# The four event types Stripe sends us on subscription state changes.
# We DON'T handle invoice.* directly because the subscription events
# cover everything the UI needs to render plan + renewal date.
_SUBSCRIPTION_EVENT_TYPES = frozenset({
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
})

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


def _read_existing_sentinel(user_id: str) -> Optional[dict]:
    """Load the user's current subscription state, or None if no sentinel
    exists yet / it's malformed. Treat unreadable as 'no prior state' so
    a single corrupt file doesn't permanently jam the webhook."""
    sentinel = _output_dir() / ".users" / user_id / "subscription.json"
    if not sentinel.exists():
        return None
    try:
        data = json.loads(sentinel.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def _write_subscription_sentinel(user_id: str, *, status: str, plan: str,
                                 subscription_id: str,
                                 customer_id: str,
                                 current_period_end: Optional[int],
                                 last_event_id: str,
                                 last_event_created: int) -> None:
    """Write the sentinel atomically — unique tmp file + os.replace so
    (a) a reader racing the write never sees a truncated/half-written
    JSON, and (b) two concurrent webhook handlers for the same user
    don't stomp each other's tmp file. The engine runs on
    ThreadingHTTPServer, so two Stripe deliveries for the same user can
    land in parallel — a fixed tmp filename would race (NLM round 2
    Finding #R2.1).

    On both POSIX and NTFS, ``os.replace`` is atomic across same-volume
    renames, so the destination either has the OLD contents or the NEW
    contents, never partial.
    """
    user_dir = _output_dir() / ".users" / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    out = {
        "status":                 status,
        "plan":                   plan,
        "stripe_subscription_id": subscription_id,
        "stripe_customer_id":     customer_id,
        "current_period_end":     current_period_end,
        "updated_at":             datetime.now(timezone.utc).isoformat(),
        # NLM round 1: track last-applied event so subsequent deliveries
        # of the SAME event.id are dedup'd, and stale (.created earlier
        # than what we already have) events are rejected.
        "last_event_id":          last_event_id,
        "last_event_created":     last_event_created,
    }
    target = user_dir / "subscription.json"
    # uuid4().hex is collision-free across handler threads for our
    # purposes (122 bits of entropy). Don't reuse — each write gets a
    # fresh tmp so concurrent writers never stomp each other.
    tmp = user_dir / f"subscription.json.{uuid.uuid4().hex}.tmp"
    try:
        tmp.write_text(json.dumps(out, indent=2), encoding="utf-8")
        os.replace(tmp, target)
    finally:
        # Best-effort cleanup if the rename failed (e.g. Windows held
        # the destination open). Leaves no orphan tmp files in the
        # user's dir.
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


def run_stripe_webhook(handler) -> None:
    """Entry point — wired from PebbleHandler.do_POST."""
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()
    if not secret:
        log.warning("stripe-webhook called but STRIPE_WEBHOOK_SECRET not set")
        handler._json(503, {"error": "Webhook not configured on this host"})
        return
    # NLM round 3 R3.D1 — catch the most common misconfig pattern: pasting
    # something that isn't a Stripe webhook signing secret into the env
    # var (we've literally seen an rk_test_ key pasted into this slot on
    # 2026-05-17). A real whsec_... value starts with that prefix; the
    # HMAC verifier below would 400 the request anyway, but a clearer
    # log line saves operators a debugging session.
    if not secret.startswith("whsec_"):
        log.warning(
            "stripe-webhook STRIPE_WEBHOOK_SECRET prefix=%r does not match "
            "expected 'whsec_'. Webhooks will fail signature verification. "
            "Run `stripe listen` locally to mint one, or copy from Stripe "
            "Dashboard -> Developers -> Webhooks -> <endpoint> -> Signing secret.",
            secret[:6],
        )

    sig_header = (handler.headers.get("Stripe-Signature") or "").strip()
    if not sig_header:
        handler._json(400, {"error": "Missing Stripe-Signature header"})
        return

    raw_body = _read_raw_body(handler)
    if raw_body is None:
        handler._json(400, {"error": "Invalid request body"})
        return

    # SDK-15.x compat notes (the chain of bugs that 400'd every real
    # event in the 2026-05-17 E2E run; test suite missed both because
    # it mocks construct_event to return a plain dict):
    #
    # 1. stripe.Webhook.construct_event returns a StripeObject — NOT a
    #    plain dict, and NOT compatible with isinstance(event, dict) or
    #    `.get()` calls.
    # 2. stripe.WebhookSignature.verify_header does `"%d.%s" % (ts,
    #    payload)` internally. When payload is BYTES, %s renders the
    #    literal Python repr (`b'{"x":1}'`), so the computed signature
    #    NEVER matches what Stripe signed. Workaround: decode to str
    #    before passing in.
    #
    # We split the SDK's "verify + parse" into two steps: decode-then-
    # verify the HMAC ourselves, then json.loads as a plain dict.
    try:
        decoded_body = raw_body.decode("utf-8")
    except UnicodeDecodeError:
        handler._json(400, {"error": "Invalid request body"})
        return

    try:
        stripe.WebhookSignature.verify_header(decoded_body, sig_header, secret)
    except stripe.error.SignatureVerificationError:
        log.info("stripe-webhook signature rejected")
        handler._json(400, {"error": "Invalid signature"})
        return

    try:
        event = json.loads(decoded_body)
    except json.JSONDecodeError:
        handler._json(400, {"error": "Invalid request body"})
        return

    if not isinstance(event, dict):
        # JSON parsed to a list/scalar — not a Stripe event shape.
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
    # safe_user_id is the canonical shared helper (pebble.security).
    # Replaces the local _safe_user_id copy that lived here through
    # rounds 1-2 — same semantics, one source of truth.
    user_id = safe_user_id(metadata.get("pebble_user_id"))
    if not user_id:
        log.info("stripe-webhook %s missing/invalid pebble_user_id metadata",
                 event_type)
        handler._json(200, {"ok": True, "action": "skipped",
                            "reason": "no pebble_user_id"})
        return

    # NLM round 1 (Finding #1, #5): dedup by event.id, reject stale
    # events. Stripe webhooks can be retried (legitimate — our 200 ACK
    # was lost in transit) and can deliver out of order (rare, but
    # documented). Both classes look identical from our side; the same
    # check handles both.
    event_id_raw = event.get("id", "")
    if not isinstance(event_id_raw, str) or len(event_id_raw) > 128:
        event_id_raw = ""
    event_created_raw = event.get("created")
    event_created = event_created_raw if isinstance(event_created_raw, int) else 0

    existing = _read_existing_sentinel(user_id)
    if existing is not None:
        if event_id_raw and existing.get("last_event_id") == event_id_raw:
            # Same event.id — Stripe re-delivered after a dropped ACK
            # or an attacker replayed within the 5-min HMAC tolerance.
            # Idempotent: don't rewrite the file.
            handler._json(200, {"ok": True, "action": "deduped",
                                "reason": "event already applied"})
            return
        prior_created = existing.get("last_event_created")
        if (
            isinstance(prior_created, int)
            and event_created
            and event_created < prior_created
        ):
            # Out-of-order delivery — this event is older than what we
            # already applied. Skip it; the newer event already reflects
            # the truer state.
            log.info(
                "stripe-webhook %s stale event_created=%s < prior=%s for user=%s",
                event_type, event_created, prior_created, user_id,
            )
            handler._json(200, {"ok": True, "action": "skipped",
                                "reason": "stale event"})
            return

    plan = metadata.get("pebble_plan") or "unknown"
    if not isinstance(plan, str) or len(plan) > 32:
        plan = "unknown"
    status = obj.get("status", "unknown")
    if not isinstance(status, str) or len(status) > 32:
        status = "unknown"

    # Stripe API 2026-04-22.dahlia moved `current_period_end` from the
    # Subscription root onto SubscriptionItem. Read root first
    # (preserves older API versions), fall back to items[0] for newer
    # ones. Multi-item subscriptions all share the same period in
    # practice, so items[0] is authoritative.
    raw_period_end = obj.get("current_period_end")
    if not isinstance(raw_period_end, int):
        items = (obj.get("items") or {}).get("data") or []
        if items and isinstance(items[0], dict):
            raw_period_end = items[0].get("current_period_end")
    period_end = raw_period_end if isinstance(raw_period_end, int) else None

    sub_id_raw = obj.get("id", "")
    subscription_id = sub_id_raw if isinstance(sub_id_raw, str) and len(sub_id_raw) <= 128 else ""

    cus_id_raw = obj.get("customer", "")
    customer_id = cus_id_raw if isinstance(cus_id_raw, str) and len(cus_id_raw) <= 128 else ""

    # If the incoming subscription_id differs from what we already track,
    # we're in the multi-sub case (NLM Finding #3). Pebble's data model
    # assumes one active subscription per user, so we still write — but
    # we log so ops can investigate whether the user actually has two.
    if (
        existing is not None
        and existing.get("stripe_subscription_id")
        and subscription_id
        and existing["stripe_subscription_id"] != subscription_id
    ):
        # Redact subscription IDs to last 4 chars so logs forwarded to a
        # lower-trust system (Datadog, ELK, support tools) don't expose
        # full billing identifiers. The user_id is enough for an operator
        # to cross-reference in the Stripe Dashboard. NLM round 3 R3.C1.
        prior_short = existing["stripe_subscription_id"][-4:]
        new_short = subscription_id[-4:]
        log.warning(
            "stripe-webhook user=%s subscription changed ...%s -> ...%s (was the user double-subscribed?)",
            user_id, prior_short, new_short,
        )

    _write_subscription_sentinel(
        user_id,
        status=status,
        plan=plan,
        subscription_id=subscription_id,
        customer_id=customer_id,
        current_period_end=period_end,
        last_event_id=event_id_raw,
        last_event_created=event_created,
    )

    log.info("stripe-webhook %s applied user=%s plan=%s status=%s",
             event_type, user_id, plan, status)
    handler._json(200, {"ok": True, "action": "applied"})
