"""POST /api/checkout/create-session — Stripe Checkout (subscription mode).

The user picks a plan in v3's pricing UI, the v3 client hits this endpoint
with ``{"plan": "starter" | "pro"}`` and an ``Authorization: Bearer <jwt>``
header, and we return ``{"url": "https://checkout.stripe.com/..."}``. The
v3 client redirects the browser there; Stripe-hosted payment UX handles
collection + 3DS + saved payment methods.

The Stripe webhook (``pebble/server/stripe_webhook.py``) is what actually
sets the user's subscription state — this endpoint just opens the
Checkout session and walks away.

Security & money safety:
- Auth-gated via :func:`pebble.security.require_user` — never let an
  anonymous caller mint a paid session.
- Plan key is whitelisted to {"starter", "pro"} and resolved to a price ID
  from env; we never read a price ID off the request body.
- DO NOT include ``payment_method_types`` in the SDK call. Stripe
  recommends omitting it so payment methods are chosen dynamically via
  Dashboard settings — hardcoding ``['card']`` would lock out Link / Apple
  Pay / Google Pay and tank conversion. (See stripe-best-practices skill.)
- Customer is identified by ``customer_email`` so Stripe deduplicates
  Customer objects automatically; for repeat checkouts the same Stripe
  Customer is reused.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Optional

import stripe

from pebble.security import require_user


log = logging.getLogger("pebble.stripe_checkout")


# Plan key → env-var name for the matching Stripe price ID. Single source
# of truth; adding a third plan is one entry here, one in stripe_bootstrap,
# and one v3 button.
_PRICE_ENV: dict[str, str] = {
    "starter": "PEBBLE_STRIPE_STARTER_PRICE_ID",
    "pro":     "PEBBLE_STRIPE_PRO_PRICE_ID",
}


def _read_body(handler) -> Optional[dict]:
    """Read + parse the JSON request body. Returns None on malformed
    input — caller is expected to have already 400'd."""
    try:
        length = int(handler.headers.get("Content-Length", "0") or "0")
    except ValueError:
        return None
    if length <= 0 or length > 8 * 1024:
        # Checkout bodies are tiny ({"plan": "starter"} is 19 bytes).
        # Anything over 8KB is misconfigured or malicious.
        return None
    try:
        raw = handler.rfile.read(length)
        return json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _public_base_url() -> str:
    """Resolve the v3 frontend base URL for success/cancel redirects."""
    return (os.environ.get("PEBBLE_PUBLIC_URL", "").strip().rstrip("/")
            or "http://localhost:3001")


def _trial_period_days() -> Optional[int]:
    """Return the configured trial length, or None for "no trial".

    Reads ``PEBBLE_TRIAL_DAYS`` from env. Accepts only positive integers;
    anything else (unset, ``"0"``, negative, non-numeric) returns None
    so the Checkout call omits ``trial_period_days`` entirely. Stripe
    treats ``trial_period_days=0`` as a 1-day trial — explicitly NOT
    what the operator means when they set the env to 0.
    """
    raw = os.environ.get("PEBBLE_TRIAL_DAYS", "").strip()
    if not raw:
        return None
    try:
        n = int(raw)
    except ValueError:
        return None
    return n if n > 0 else None


def run_create_session(handler) -> None:
    """Entry point — wired from PebbleHandler.do_POST."""
    user = require_user(handler)
    if user is None:
        return

    body = _read_body(handler)
    if not isinstance(body, dict):
        handler._json(400, {"error": "Invalid JSON body"})
        return

    plan = body.get("plan")
    if plan not in _PRICE_ENV:
        handler._json(400, {"error": "plan must be 'starter' or 'pro'"})
        return

    secret_key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not secret_key:
        handler._json(503, {"error": "Billing not configured on this Pebble instance"})
        return

    price_id = os.environ.get(_PRICE_ENV[plan], "").strip()
    if not price_id:
        handler._json(503, {
            "error": f"Billing not configured: no price ID for plan '{plan}'",
        })
        return

    # SDK auth is per-process module state, set right before the call so
    # we never depend on whoever last touched stripe.api_key.
    stripe.api_key = secret_key

    base_url = _public_base_url()
    pebble_user_id = user.get("id", "")

    subscription_data: dict = {
        "metadata": {"pebble_user_id": pebble_user_id, "pebble_plan": plan},
    }
    trial_days = _trial_period_days()
    if trial_days is not None:
        # Chapter 9.5 — env-gated free trial. Stripe charges the card
        # `trial_days` after Checkout completes (Customer Portal users
        # can cancel during the trial with no charge).
        subscription_data["trial_period_days"] = trial_days

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            customer_email=user.get("email"),
            # CRITICAL — no payment_method_types here. Stripe picks the best
            # methods dynamically; hardcoding ['card'] tanks conversion.
            success_url=f"{base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/billing/cancel",
            # Stamp the Supabase user id on BOTH the session and the future
            # subscription so the webhook can route events back to a Pebble
            # user without join-on-email (emails can be changed).
            metadata={"pebble_user_id": pebble_user_id, "pebble_plan": plan},
            subscription_data=subscription_data,
        )
    except stripe.error.StripeError:
        # Don't log .args of the exception — they can contain message
        # text Stripe doesn't promise is secret-free.
        log.warning("stripe checkout session create failed (plan=%s)", plan)
        handler._json(502, {"error": "Stripe is temporarily unavailable. Try again."})
        return

    # Resilient unwrap — the SDK returns an object with .id / .url
    # attributes; tests may use a MagicMock that behaves the same way.
    handler._json(200, {
        "url":        session.url,
        "session_id": session.id,
    })
