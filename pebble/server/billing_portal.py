"""POST /api/billing/portal — mint a Stripe Customer Portal session.

The Customer Portal is Stripe's hosted self-serve UI for subscriptions:
plan changes, cancellation, payment-method updates, invoice history.
Using it means we don't have to build any of that surface ourselves;
the v3 settings page just has a "Manage billing" button that calls this
endpoint and redirects the browser to the returned URL.

How it resolves the Stripe customer
-----------------------------------
The Stripe webhook (``pebble/server/stripe_webhook.py``) stamps
``stripe_customer_id`` into ``output/.users/<uid>/subscription.json``
every time it processes a ``customer.subscription.*`` event. This
endpoint just reads that sentinel — no Stripe API call needed to look
the customer up. If the user has never subscribed (no sentinel) we
return 404 so v3 can show "choose a plan first" instead of a vague
Stripe error.

Auth & errors
-------------
- 401 — :func:`pebble.security.require_user` rejected the caller.
- 503 — ``STRIPE_SECRET_KEY`` missing in env.
- 404 — no sentinel, malformed sentinel, or sentinel missing
        ``stripe_customer_id``. v3 surfaces "no active subscription."
- 502 — Stripe API unreachable / transient error.
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import stripe

from pebble.security import require_user, safe_user_id


log = logging.getLogger("pebble.billing_portal")


def _output_dir() -> Path:
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path(__file__).parent.parent.parent.resolve() / "output"


def _public_base_url() -> str:
    return (os.environ.get("PEBBLE_PUBLIC_URL", "").strip().rstrip("/")
            or "http://localhost:3001")


# Subscription statuses we'll mint a portal session for. Excluded:
# `incomplete_expired` (Stripe's terminal state ~23h after a payment
# never confirms — the subscription is dead, no point in portal), and
# `unpaid` (also a terminal-failure state). We DO allow `incomplete`
# because the user can complete payment via the portal, and `canceled`
# because users should still be able to view invoice history.
# NLM round 3 R3.A2.
_PORTAL_ALLOWED_STATUSES = frozenset({
    "active", "trialing", "past_due", "incomplete", "canceled",
})


def _load_customer_id(user_id: str) -> Optional[str]:
    """Read the Stripe customer_id from the user's subscription sentinel,
    or return None if there isn't one (no subscription / corrupt file /
    sentinel exists but status indicates a dead subscription).

    NLM round 2 Finding #R2.4: pass user_id through ``safe_user_id`` —
    not just ``.lower()`` — so a malicious ``../victim`` id can't read a
    different user's sentinel. The webhook writes through the same
    validation; readers must enforce it too.

    NLM round 3 R3.A2: status filter — don't mint a portal session for
    `incomplete_expired` / `unpaid` (terminal-failure states). Those
    users get the same 404 as never-subscribed users; v3 can route them
    to a fresh checkout instead.
    """
    safe_uid = safe_user_id(user_id)
    if not safe_uid:
        return None
    sentinel = _output_dir() / ".users" / safe_uid / "subscription.json"
    if not sentinel.exists():
        return None
    try:
        data = json.loads(sentinel.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    # NLM round 4 R4.2 — fail CLOSED, not open. The previous form
    # `if isinstance(status, str) and status not in _ALLOWED: return None`
    # let through sentinels where status was missing/None/non-string,
    # because the isinstance check failed and skipped the membership
    # test entirely. Invert so any non-string status (None, int, dict)
    # OR any string outside the allowlist returns None.
    status = data.get("status")
    if not isinstance(status, str) or status not in _PORTAL_ALLOWED_STATUSES:
        return None
    cid = data.get("stripe_customer_id")
    return cid if isinstance(cid, str) and cid else None


def run_billing_portal(handler) -> None:
    """Entry point — wired from PebbleHandler.do_POST."""
    user = require_user(handler)
    if user is None:
        return

    secret_key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not secret_key:
        handler._json(503, {"error": "Billing not configured on this Pebble instance"})
        return

    user_id = user.get("id", "")
    if not user_id or not isinstance(user_id, str):
        handler._json(404, {"error": "No active subscription"})
        return

    customer_id = _load_customer_id(user_id)
    if not customer_id:
        handler._json(404, {"error": "No active subscription"})
        return

    stripe.api_key = secret_key
    base_url = _public_base_url()

    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            # Land back on /settings so the user immediately sees their
            # updated plan once webhooks have synced.
            return_url=f"{base_url}/settings?billing=updated",
        )
    except stripe.error.StripeError:
        # Don't include the customer_id in the log line — it's PII.
        log.warning("stripe billing portal session create failed")
        handler._json(502, {"error": "Stripe is temporarily unavailable. Try again."})
        return

    handler._json(200, {"url": session.url})
