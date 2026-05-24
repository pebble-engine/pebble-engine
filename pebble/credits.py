"""Credits — per-user balance with DB-enforced ceiling + append-only ledger.

Schema (Supabase, applied 2026-05-24):

  credits (
    user_id            UUID PRIMARY KEY,
    balance            INT NOT NULL DEFAULT 0,
    plan_monthly_grant INT NOT NULL DEFAULT 0,
    hard_cap           INT NOT NULL DEFAULT 400,
    last_refilled_at   TIMESTAMPTZ,
    CHECK (balance >= 0),
    CHECK (balance <= hard_cap)
  )

  credit_ledger (
    id          UUID PRIMARY KEY,
    user_id     UUID,
    delta       INT NOT NULL,   -- +20 for refill, -1 for refinement
    reason      TEXT NOT NULL,
    ref_id      TEXT,           -- slug, stripe session id, etc.
    created_at  TIMESTAMPTZ DEFAULT NOW()
  )

The DB CHECK constraints are the LAST line of defense — but we also
pre-check in Python so a buy-more-by-accident gets a clean error
message instead of a 500 from Postgres. Marc's 2026-05-24 ask:
"how can we make sure they don't end up buying more by accident,
breaking the website."

Every change to `balance` ALSO writes a `credit_ledger` row. We never
hand-edit balance without a ledger entry — that's how we answer "where
did my credits go" support tickets without sweating.

Plan defaults (the monthly-refill amounts attached to each tier):

  free      → 20 credits/month, hard_cap 100
  starter   → 100 credits/month, hard_cap 400
  pro       → 400 credits/month, hard_cap 400

The hard cap is universal but plans differ — Free + Starter can buy
packs up to their cap; Pro is always near cap so packs typically
refuse. The fail mode for "you'd exceed the cap" is a clean error
shown BEFORE Stripe Checkout opens, not a refund dance after.

This module is fail-soft like pebble.events: returns sentinel values
on Supabase errors, never raises at the caller.
"""
from __future__ import annotations

import os
from typing import Optional

from pebble.log import log


# ─── Plan / cap defaults ─────────────────────────────────────────── #

DEFAULT_HARD_CAP = 400

PLAN_GRANTS: dict[str, int] = {
    "free":    20,
    "starter": 100,
    "pro":     400,
}

PLAN_CAPS: dict[str, int] = {
    "free":    100,
    "starter": 400,
    "pro":     400,
}


# ─── Spend reason constants — pinned so callers can't typo ────────── #

REASON_REFINEMENT      = "refinement"
REASON_BLOCK_INSERT    = "block_insert"
REASON_REGENERATE      = "regenerate"
REASON_PACK_PURCHASED  = "pack_purchased"
REASON_MONTHLY_REFILL  = "monthly_refill"
REASON_ADMIN_GRANT     = "admin_grant"
REASON_SIGNUP_GRANT    = "signup_grant"

VALID_SPEND_REASONS = {
    REASON_REFINEMENT, REASON_BLOCK_INSERT, REASON_REGENERATE,
}
VALID_REFILL_REASONS = {
    REASON_PACK_PURCHASED, REASON_MONTHLY_REFILL,
    REASON_ADMIN_GRANT, REASON_SIGNUP_GRANT,
}


# ─── Env + config ────────────────────────────────────────────────── #

def _env_url() -> str:
    val = (os.environ.get("PEBBLE_SUPABASE_URL")
           or os.environ.get("SUPABASE_URL")
           or "").strip()
    return val.rstrip("/")


def _env_service_role() -> str:
    return (os.environ.get("PEBBLE_SUPABASE_SERVICE_ROLE_KEY")
            or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            or "").strip()


def is_configured() -> bool:
    return bool(_env_url()) and bool(_env_service_role())


def _headers() -> dict:
    key = _env_service_role()
    return {
        "apikey":        key,
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
    }


# ─── Core read ───────────────────────────────────────────────────── #


def get_or_init_row(user_id: str, plan: str = "free") -> Optional[dict]:
    """Return the user's credits row. If they don't have one yet,
    create one with the plan's default grant + cap + an initial
    signup_grant ledger entry. Idempotent — calling twice on a fresh
    user grants credits once, then subsequent calls just return the
    existing row.
    """
    if not is_configured() or not user_id:
        return None
    existing = _read_row(user_id)
    if existing:
        return existing

    # Init path — never grant beyond the cap. The cap from PLAN_CAPS
    # is the source of truth; the legacy hard_cap default of 400 is
    # only a fallback when a plan name we don't recognize is passed.
    plan_key = plan if plan in PLAN_GRANTS else "free"
    grant = PLAN_GRANTS[plan_key]
    cap = PLAN_CAPS.get(plan_key, DEFAULT_HARD_CAP)
    starting_balance = min(grant, cap)

    try:
        import httpx
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        payload = {
            "user_id":            user_id,
            "balance":            starting_balance,
            "plan_monthly_grant": grant,
            "hard_cap":           cap,
            "last_refilled_at":   now_iso,
        }
        # Upsert via PostgREST so a concurrent init doesn't crash.
        resp = httpx.post(
            f"{_env_url()}/rest/v1/credits",
            headers={**_headers(), "Prefer": "resolution=merge-duplicates,return=representation"},
            params={"on_conflict": "user_id"},
            json=payload,
            timeout=5.0,
        )
        if resp.status_code >= 400:
            log.warning("[credits] init upsert failed: %s", resp.text[:200])
            return None
        rows = resp.json() or []
        row = rows[0] if rows else payload

        # Ledger entry for the initial grant. Only write when we
        # actually created the row (balance came from us, not Postgres).
        # If row.balance > starting_balance, someone else inited first.
        if row.get("balance") == starting_balance:
            _write_ledger(user_id, +starting_balance, REASON_SIGNUP_GRANT)

        return row
    except Exception as e:
        log.warning("[credits] init errored: %s", e)
        return None


def get_balance(user_id: str) -> Optional[int]:
    """Current balance for the user. Returns None if Supabase is down
    or the row genuinely doesn't exist — the caller decides whether
    to lazy-init (signup flow) or treat as no-access."""
    row = _read_row(user_id)
    if row is None:
        return None
    val = row.get("balance")
    return int(val) if isinstance(val, int) else None


def _read_row(user_id: str) -> Optional[dict]:
    if not is_configured() or not user_id:
        return None
    try:
        import httpx
        resp = httpx.get(
            f"{_env_url()}/rest/v1/credits",
            headers=_headers(),
            params={"select": "*", "user_id": f"eq.{user_id}"},
            timeout=5.0,
        )
        if resp.status_code >= 400:
            return None
        rows = resp.json() or []
        return rows[0] if rows else None
    except Exception as e:
        log.warning("[credits] read errored: %s", e)
        return None


# ─── Spend ───────────────────────────────────────────────────────── #


def spend(
    user_id: str,
    amount: int,
    reason: str,
    ref_id: Optional[str] = None,
) -> bool:
    """Decrement balance by `amount` and write a ledger row. Returns
    True on success, False on:
      - insufficient balance (no change made)
      - unknown spend reason (no change made)
      - Supabase error (no change made)

    The caller is responsible for showing a "buy more credits" prompt
    on False. We never go negative — the DB CHECK constraint would
    reject it anyway, but pre-checking in Python gives a clean error
    message instead of a 500.

    NOT a transaction — we read balance, validate, then write. A
    racing parallel spend could over-spend in theory; in practice
    refinements are user-initiated clicks (<1/sec) and the DB CHECK
    catches the rare race. Phase 28+ would move this to a Postgres
    function for true atomicity.
    """
    if amount <= 0:
        log.warning("[credits] spend amount must be positive, got %d", amount)
        return False
    if reason not in VALID_SPEND_REASONS:
        log.warning("[credits] unknown spend reason %r", reason)
        return False
    if not is_configured() or not user_id:
        return False

    row = _read_row(user_id)
    if row is None:
        log.warning("[credits] spend: no row for user %s", user_id[:8])
        return False
    balance = int(row.get("balance") or 0)
    if balance < amount:
        log.info("[credits] insufficient balance: user has %d, needs %d", balance, amount)
        return False

    new_balance = balance - amount
    ok = _update_balance(user_id, new_balance)
    if not ok:
        return False
    _write_ledger(user_id, -amount, reason, ref_id)
    return True


# ─── Refill (monthly + pack purchase + admin) ────────────────────── #


def refill(
    user_id: str,
    amount: int,
    reason: str,
    ref_id: Optional[str] = None,
) -> bool:
    """Add `amount` to balance, capped at hard_cap. Returns True on
    success including a partial-cap clamp (we still credit what we can
    and write a ledger row for the actual delta). Returns False on:
      - non-positive amount
      - unknown refill reason
      - Supabase error
      - balance already at cap (no credit possible, no ledger write).

    Marc's "buy by accident" protection: callers like the Stripe
    webhook should call can_purchase() FIRST to refuse the checkout.
    This helper is the second line — if a purchase does sneak through
    (race condition), it credits what fits and refunds the rest via
    a stripe.refunds.create call (caller's responsibility).
    """
    if amount <= 0:
        log.warning("[credits] refill amount must be positive, got %d", amount)
        return False
    if reason not in VALID_REFILL_REASONS:
        log.warning("[credits] unknown refill reason %r", reason)
        return False
    if not is_configured() or not user_id:
        return False

    row = get_or_init_row(user_id)
    if row is None:
        return False
    balance = int(row.get("balance") or 0)
    cap = int(row.get("hard_cap") or DEFAULT_HARD_CAP)
    if balance >= cap:
        log.info("[credits] refill refused: already at cap %d", cap)
        return False
    delta = min(amount, cap - balance)
    new_balance = balance + delta
    ok = _update_balance(user_id, new_balance)
    if not ok:
        return False
    _write_ledger(user_id, +delta, reason, ref_id)
    return True


def can_purchase(user_id: str, pack_amount: int) -> tuple[bool, str]:
    """Pre-checkout validation. Returns (ok, reason) where reason is
    a human-readable explanation when ok is False. Call this BEFORE
    creating the Stripe Checkout session so the user never pays for
    credits that won't fit.

    Examples:
      can_purchase(uid, 50)  → (True, "")
      can_purchase(uid, 50)  → (False, "You're at 380 / 400. A 50-pack would exceed your cap. Spend some first or upgrade to Pro.")
    """
    if pack_amount <= 0:
        return False, "Invalid pack size."
    row = get_or_init_row(user_id)
    if row is None:
        return False, "Couldn't read your credit balance."
    balance = int(row.get("balance") or 0)
    cap = int(row.get("hard_cap") or DEFAULT_HARD_CAP)
    if balance + pack_amount > cap:
        return False, (
            f"You're at {balance} of {cap} credits. A {pack_amount}-pack would push you "
            f"past the cap. Use some credits first, or upgrade to a higher plan."
        )
    return True, ""


# ─── Helpers — internal ──────────────────────────────────────────── #


def _update_balance(user_id: str, new_balance: int) -> bool:
    if not is_configured():
        return False
    try:
        import httpx
        resp = httpx.patch(
            f"{_env_url()}/rest/v1/credits",
            headers=_headers(),
            params={"user_id": f"eq.{user_id}"},
            json={"balance": new_balance},
            timeout=5.0,
        )
        if resp.status_code >= 400:
            # Most common reason: DB CHECK constraint rejected the new
            # value (negative or over-cap). We logged the upstream
            # error too — surface it without raising.
            log.warning(
                "[credits] update_balance failed (HTTP %d): %s",
                resp.status_code, resp.text[:200],
            )
            return False
        return True
    except Exception as e:
        log.warning("[credits] update_balance errored: %s", e)
        return False


def _write_ledger(
    user_id: str,
    delta: int,
    reason: str,
    ref_id: Optional[str] = None,
) -> bool:
    if not is_configured():
        return False
    try:
        import httpx
        payload = {
            "user_id": user_id,
            "delta":   delta,
            "reason":  reason,
            "ref_id":  ref_id,
        }
        resp = httpx.post(
            f"{_env_url()}/rest/v1/credit_ledger",
            headers=_headers(),
            json=payload,
            timeout=5.0,
        )
        if resp.status_code >= 400:
            log.warning("[credits] ledger insert failed: %s", resp.text[:200])
            return False
        return True
    except Exception as e:
        log.warning("[credits] ledger insert errored: %s", e)
        return False


def list_recent_ledger(user_id: str, limit: int = 50) -> list[dict]:
    """Return recent ledger entries for the user, newest first. Used
    by the settings page so users can audit their own spend."""
    if not is_configured() or not user_id:
        return []
    try:
        import httpx
        resp = httpx.get(
            f"{_env_url()}/rest/v1/credit_ledger",
            headers=_headers(),
            params={
                "select":  "id,delta,reason,ref_id,created_at",
                "user_id": f"eq.{user_id}",
                "order":   "created_at.desc",
                "limit":   str(limit),
            },
            timeout=5.0,
        )
        if resp.status_code >= 400:
            return []
        return resp.json() or []
    except Exception as e:
        log.warning("[credits] list_ledger errored: %s", e)
        return []


__all__ = [
    "get_or_init_row",
    "get_balance",
    "spend",
    "refill",
    "can_purchase",
    "list_recent_ledger",
    "is_configured",
    "DEFAULT_HARD_CAP",
    "PLAN_GRANTS",
    "PLAN_CAPS",
    # Reason constants
    "REASON_REFINEMENT",
    "REASON_BLOCK_INSERT",
    "REASON_REGENERATE",
    "REASON_PACK_PURCHASED",
    "REASON_MONTHLY_REFILL",
    "REASON_ADMIN_GRANT",
    "REASON_SIGNUP_GRANT",
    "VALID_SPEND_REASONS",
    "VALID_REFILL_REASONS",
]
