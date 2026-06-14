#!/usr/bin/env python3
"""Verify Stripe env vars and API reachability (no charge).

Reads .env from repo root. Safe to run in CI without secrets if vars unset.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def main() -> int:
    _load_dotenv()
    print("Stripe setup check\n")

    required = [
        "STRIPE_SECRET_KEY",
        "STRIPE_PUBLISHABLE_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "PEBBLE_STRIPE_STARTER_PRICE_ID",
        "PEBBLE_STRIPE_PRO_PRICE_ID",
    ]
    missing = [k for k in required if not os.environ.get(k, "").strip()]
    if missing:
        print("  [WARN] Missing in .env:")
        for k in missing:
            print(f"         - {k}")
        print("\n  Run: python -m pebble.stripe_bootstrap")
        print("  See: docs/STRIPE_E2E.md")
        return 1

    sk = os.environ["STRIPE_SECRET_KEY"]
    if sk.startswith("sk_live_"):
        print("  [WARN] Live Stripe key detected — use test mode for E2E")
        return 1

    try:
        import stripe
        stripe.api_key = sk
        stripe.Product.list(limit=1)
        print("  [OK] Stripe API responds (test key)")
    except Exception as e:
        print(f"  [FAIL] Stripe API: {e}")
        return 1

    print("\nStripe env looks ready. Complete payment test per docs/STRIPE_E2E.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
