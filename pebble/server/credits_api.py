"""Credits endpoint — balance + ledger + pack purchase intent (2026-05-24).

  GET  /api/credits             → balance, plan grant, cap, recent ledger
  POST /api/credits/purchase    → pre-validate cap + create Stripe checkout

Auth-gated. Lazy-inits the user's credits row on first read so a
brand-new signup sees their plan's grant immediately rather than 0.

The purchase flow uses `credits.can_purchase()` BEFORE talking to
Stripe. If the user is already at cap (Pro plan, or near-full
Starter), they get a clean error explaining why instead of paying
for credits that won't fit.
"""
from __future__ import annotations

import json
import os

from pebble import credits
from pebble.log import log
from pebble.security import client_ip, plan_limiter, resolve_user_id


# Pack catalog — Marc creates the Stripe prices for these in the
# dashboard, then drops the price IDs into .env. We don't hardcode
# dollar amounts here because Stripe is the source of truth for price
# (we'd otherwise drift on every promo / currency change).
PACK_CATALOG: list[dict] = [
    {"key": "credits_20",  "amount": 20,  "env_var": "PEBBLE_STRIPE_CREDITS_20_PRICE_ID",  "label": "20 credits"},
    {"key": "credits_50",  "amount": 50,  "env_var": "PEBBLE_STRIPE_CREDITS_50_PRICE_ID",  "label": "50 credits"},
    {"key": "credits_100", "amount": 100, "env_var": "PEBBLE_STRIPE_CREDITS_100_PRICE_ID", "label": "100 credits"},
]


def _pack_by_key(key: str) -> dict | None:
    for p in PACK_CATALOG:
        if p["key"] == key:
            return p
    return None


# ─── GET /api/credits ─────────────────────────────────────────── #


def run_get_credits(handler) -> None:
    """Returns the caller's current balance + recent ledger entries,
    plus the pack catalog (so the v3 settings page knows which packs
    to render). Lazy-inits the credits row on first call."""
    uid = resolve_user_id(handler)
    if not uid:
        handler._json(401, {"error": "sign in required"}); return

    ip = client_ip(handler)
    if not plan_limiter.allow(ip or ""):
        handler._json(429, {"error": "slow down"}); return

    row = credits.get_or_init_row(uid)
    if row is None:
        # Supabase missing or unreachable — surface a real error so
        # the settings page can show "Credit system unavailable" rather
        # than render 0 and confuse the user.
        handler._json(503, {
            "error": "credit system unavailable",
            "balance": None,
        })
        return

    ledger = credits.list_recent_ledger(uid, limit=30)

    # Surface only packs whose Stripe price ID is configured. A pack
    # without a price ID can't be purchased, so showing it would be
    # a dead-end button. Each pack also tells the UI if it can fit.
    available_packs = []
    balance = int(row.get("balance") or 0)
    cap = int(row.get("hard_cap") or credits.DEFAULT_HARD_CAP)
    for pack in PACK_CATALOG:
        price_id = (os.environ.get(pack["env_var"]) or "").strip()
        if not price_id:
            continue
        would_exceed = (balance + pack["amount"]) > cap
        available_packs.append({
            "key":           pack["key"],
            "amount":        pack["amount"],
            "label":         pack["label"],
            "would_exceed":  would_exceed,
        })

    handler._json(200, {
        "balance":            row.get("balance"),
        "plan_monthly_grant": row.get("plan_monthly_grant"),
        "hard_cap":           row.get("hard_cap"),
        "last_refilled_at":   row.get("last_refilled_at"),
        "ledger":             ledger,
        "packs":              available_packs,
    })


# ─── POST /api/credits/purchase ───────────────────────────────── #


def run_purchase_pack(handler) -> None:
    """Body: {pack_key: "credits_50"}

    Sequence:
      1. Validate pack_key against PACK_CATALOG
      2. credits.can_purchase() — refuse if cap would be exceeded
      3. Confirm Stripe price is configured for this pack
      4. Create a Stripe Checkout session with metadata
         {pebble_user_id, purpose: "credit_pack", pack_key, amount}
      5. Return {url} for the v3 to redirect to

    The webhook handler (stripe_webhook.py) is what actually grants
    the credits — never trust the client's "success" callback.
    """
    uid = resolve_user_id(handler)
    if not uid:
        handler._json(401, {"error": "sign in required"}); return

    ip = client_ip(handler)
    if not plan_limiter.allow(ip or ""):
        handler._json(429, {"error": "slow down"}); return

    try:
        length = int(handler.headers.get("Content-Length", "0"))
        body = json.loads(handler.rfile.read(length).decode("utf-8")) if length > 0 else {}
    except Exception:
        handler._json(400, {"error": "invalid json"}); return

    pack_key = (body.get("pack_key") or "").strip()
    pack = _pack_by_key(pack_key)
    if not pack:
        handler._json(400, {"error": f"unknown pack: {pack_key!r}"}); return

    # The Marc-protection step. Refuses BEFORE Stripe is touched.
    ok, why = credits.can_purchase(uid, pack["amount"])
    if not ok:
        handler._json(409, {
            "error":         "cap exceeded",
            "message":       why,
            "pack_key":      pack_key,
            "pack_amount":   pack["amount"],
        })
        return

    price_id = (os.environ.get(pack["env_var"]) or "").strip()
    if not price_id:
        # Configuration gap, not user error — give a 500 with a
        # clear message so Marc sees it during setup.
        log.warning("[credits] pack %s missing Stripe price (%s)", pack_key, pack["env_var"])
        handler._json(500, {
            "error":   "pack not yet configured",
            "message": f"Stripe price for {pack['label']} hasn't been set up yet. Email support.",
        })
        return

    # Build the Stripe session via the existing checkout helper. We
    # piggyback on the same flow as plan subscriptions — webhook
    # discriminates via metadata.purpose.
    try:
        import stripe  # type: ignore[import]
    except ImportError:
        handler._json(500, {"error": "stripe SDK not installed"}); return

    stripe_secret = (os.environ.get("STRIPE_SECRET_KEY") or "").strip()
    if not stripe_secret:
        handler._json(500, {"error": "STRIPE_SECRET_KEY not configured"}); return
    stripe.api_key = stripe_secret

    public_base = (os.environ.get("PEBBLE_PUBLIC_URL") or "http://localhost:3001").rstrip("/")
    success_url = f"{public_base}/settings?credits_purchased=1"
    cancel_url  = f"{public_base}/settings?credits_purchased=0"

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=uid,
            metadata={
                "pebble_user_id": uid,
                "purpose":        "credit_pack",
                "pack_key":       pack_key,
                "pack_amount":    str(pack["amount"]),
            },
            payment_intent_data={
                "metadata": {
                    "pebble_user_id": uid,
                    "purpose":        "credit_pack",
                    "pack_key":       pack_key,
                    "pack_amount":    str(pack["amount"]),
                },
            },
        )
    except Exception as e:
        log.warning("[credits] stripe checkout create failed: %s", e)
        handler._json(500, {"error": f"checkout failed: {e}"}); return

    handler._json(200, {"url": session.url, "session_id": session.id})


__all__ = ["run_get_credits", "run_purchase_pack", "PACK_CATALOG"]
