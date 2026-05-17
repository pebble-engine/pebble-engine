"""One-shot Stripe setup for the Pebble SaaS billing surface.

Run: ``python -m pebble.stripe_bootstrap``

What it does
------------
Creates (or reuses) the two Pebble plans in the Stripe account the
``STRIPE_SECRET_KEY`` env var points at:

* **Pebble Starter** — $29 / month USD
* **Pebble Pro**     — $59 / month USD

Idempotency
-----------
Each product carries ``metadata['pebble_plan'] = 'starter' | 'pro'``.
The script lists existing products and reuses the matching one if found,
so re-running never duplicates the catalog. Prices are matched on
``(product, currency='usd', unit_amount, recurring.interval='month',
active=True)`` and similarly reused.

Output
------
On success the script prints a paste-ready .env block:

    PEBBLE_STRIPE_STARTER_PRICE_ID=price_...
    PEBBLE_STRIPE_PRO_PRICE_ID=price_...

Copy those into the Pebble .env so the checkout endpoint knows which
prices to send users to.

Safety
------
Refuses to run against a ``sk_live_`` key unless the operator opts in
explicitly via ``PEBBLE_STRIPE_BOOTSTRAP_LIVE=1``. Test-mode keys
(``sk_test_``) run unattended — these are throwaway sandbox accounts.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Optional


# Plan definitions — single source of truth so adding a third plan is one
# entry, not a hunt across modules. The same keys ("starter"/"pro") are
# what the checkout endpoint accepts in its request body.
PLANS: list[dict[str, Any]] = [
    {
        "key": "starter",
        "name": "Pebble Starter",
        "description": "Pebble Starter — monthly subscription for solo small-business owners.",
        "amount_cents": 2900,
    },
    {
        "key": "pro",
        "name": "Pebble Pro",
        "description": "Pebble Pro — monthly subscription with everything in Starter plus advanced features.",
        "amount_cents": 5900,
    },
]


def _load_env(path: Path) -> None:
    """Stdlib-only .env loader matching pebble_engine.load_env_file so the
    CLI can run without depending on python-dotenv."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key and (key not in os.environ or not os.environ[key].strip()):
            os.environ[key] = val


def _stripe_metadata_get(obj: Any, key: str) -> Optional[str]:
    """Read a metadata field off a Stripe object. SDK 15.x's metadata
    isn't a plain dict — it's a ``StripeObject`` whose ``.get`` isn't
    inherited from ``dict``, so we use the indexing protocol + try/except
    rather than ``.get``."""
    meta = getattr(obj, "metadata", None)
    if meta is None:
        return None
    try:
        return meta[key]
    except (KeyError, AttributeError, TypeError):
        return None


def _stripe_recurring_interval(price: Any) -> Optional[str]:
    """Same shape gotcha as metadata — ``price.recurring`` is a StripeObject
    not a dict. Use indexing with a fallback."""
    rec = getattr(price, "recurring", None)
    if rec is None:
        return None
    try:
        return rec["interval"]
    except (KeyError, AttributeError, TypeError):
        return None


def find_existing_product(stripe_mod, plan_key: str) -> Optional[Any]:
    """Return the Pebble product whose ``metadata['pebble_plan']`` matches
    ``plan_key``, or None if no such product exists in the account."""
    # 100 is the upper bound of products a sandbox account is going to
    # have; if it ever exceeds that we'd see this fail loudly during a
    # bootstrap re-run and add pagination then.
    for product in stripe_mod.Product.list(limit=100, active=True).auto_paging_iter():
        if _stripe_metadata_get(product, "pebble_plan") == plan_key:
            return product
    return None


def find_existing_price(stripe_mod, product_id: str, amount_cents: int) -> Optional[Any]:
    """Return the active monthly USD price on ``product_id`` matching
    ``amount_cents``, or None if no matching price exists."""
    for price in stripe_mod.Price.list(product=product_id, limit=100, active=True).auto_paging_iter():
        if (
            price.unit_amount == amount_cents
            and price.currency == "usd"
            and _stripe_recurring_interval(price) == "month"
        ):
            return price
    return None


def ensure_plan(stripe_mod, plan: dict[str, Any]) -> dict[str, str]:
    """Ensure a single plan's product + price exist, creating them if not.
    Returns ``{"product_id": ..., "price_id": ...}``."""
    product = find_existing_product(stripe_mod, plan["key"])
    if product is None:
        product = stripe_mod.Product.create(
            name=plan["name"],
            description=plan["description"],
            metadata={"pebble_plan": plan["key"]},
        )

    price = find_existing_price(stripe_mod, product.id, plan["amount_cents"])
    if price is None:
        price = stripe_mod.Price.create(
            product=product.id,
            currency="usd",
            unit_amount=plan["amount_cents"],
            recurring={"interval": "month"},
            metadata={"pebble_plan": plan["key"]},
        )

    return {"product_id": product.id, "price_id": price.id}


def bootstrap(stripe_mod) -> dict[str, dict[str, str]]:
    """Run the full bootstrap. Pure of side-effects beyond the Stripe API
    so callers can inject a stub stripe module in tests."""
    return {plan["key"]: ensure_plan(stripe_mod, plan) for plan in PLANS}


def main(argv: Optional[list[str]] = None) -> int:  # noqa: ARG001
    project_root = Path(__file__).resolve().parent.parent
    _load_env(project_root / ".env")

    key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not key:
        print("ERROR: STRIPE_SECRET_KEY is not set in .env", file=sys.stderr)
        return 1
    if not key.startswith(("sk_test_", "sk_live_")):
        print(
            f"ERROR: STRIPE_SECRET_KEY does not look like a Stripe secret key "
            f"(got prefix {key[:8]!r}). Expected sk_test_ or sk_live_.",
            file=sys.stderr,
        )
        return 1
    if key.startswith("sk_live_") and os.environ.get("PEBBLE_STRIPE_BOOTSTRAP_LIVE", "") != "1":
        print(
            "ERROR: refusing to bootstrap against a live Stripe key. "
            "Set PEBBLE_STRIPE_BOOTSTRAP_LIVE=1 to override.",
            file=sys.stderr,
        )
        return 1

    import stripe
    stripe.api_key = key

    # ASCII-only output — Windows consoles default to cp1252 which doesn't
    # encode the U+2192 arrow / U+2713 check, and Python raises rather than
    # silently mojibake. Keep it portable.
    print("Looking up / creating Pebble products and prices in Stripe...")
    result = bootstrap(stripe)

    print("\nDone. Paste these lines into your .env:\n")
    print(f"PEBBLE_STRIPE_STARTER_PRICE_ID={result['starter']['price_id']}")
    print(f"PEBBLE_STRIPE_PRO_PRICE_ID={result['pro']['price_id']}")
    print()
    print("Reference IDs (for the Stripe Dashboard if you want to confirm):")
    for plan_key, ids in result.items():
        print(f"  {plan_key:<8} product={ids['product_id']}  price={ids['price_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
