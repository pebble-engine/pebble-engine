"""GET /api/account/invoices — list the calling user's last N Stripe invoices.

Reads stripe_customer_id from output/.users/<uid>/subscription.json, then
queries Stripe via the SDK. Returns a normalized shape the v3 Billing
tab can render directly.

Free-tier users (no customer ID yet) receive {invoices: []} immediately —
never 404; the empty list is a valid state. The UI should display a
friendly "No invoices yet" message in that case.

Auth: same require_user gate as other billing endpoints.
PII: stripe_customer_id never appears in the response; it's only used
internally to fetch invoices.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pebble.log import log
from pebble.security import require_user, safe_user_id


def _output_dir() -> Path:
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path(__file__).parent.parent.parent.resolve() / "output"


# Overrideable at module level for tests (monkeypatch OUTPUT_DIR directly).
OUTPUT_DIR: Path | None = None


def _get_output_dir() -> Path:
    if OUTPUT_DIR is not None:
        return OUTPUT_DIR
    return _output_dir()


def _list_stripe_invoices(customer_id: str, limit: int = 12) -> list[Any]:
    """Call Stripe and return raw Invoice objects.

    Separate function so tests can monkeypatch without touching Stripe.
    Import is deferred so missing SDK only raises when a paid user actually
    hits this endpoint.

    Raises RuntimeError (caught by caller → 503) if STRIPE_SECRET_KEY is
    not configured, instead of raising a bare KeyError that would surface
    as a generic 500 "Couldn't load invoices" message.
    """
    import os
    import stripe  # type: ignore[import]
    secret = (os.environ.get("STRIPE_SECRET_KEY") or "").strip()
    if not secret:
        raise RuntimeError("STRIPE_SECRET_KEY not configured")
    stripe.api_key = secret
    return stripe.Invoice.list(customer=customer_id, limit=limit).data


def _format_invoice(inv: Any) -> dict[str, Any]:
    """Normalize a Stripe Invoice into a UI-friendly dict."""
    created_ts = getattr(inv, "created", 0) or 0
    created_iso = datetime.fromtimestamp(created_ts, tz=timezone.utc).isoformat()
    return {
        "id":           getattr(inv, "id", None),
        "number":       getattr(inv, "number", None),
        "amount_cents": getattr(inv, "amount_paid", 0),
        "currency":     getattr(inv, "currency", "usd"),
        "status":       getattr(inv, "status", "unknown"),
        "created_at":   created_iso,
        "pdf_url":      getattr(inv, "invoice_pdf", None),
        "hosted_url":   getattr(inv, "hosted_invoice_url", None),
    }


def _load_customer_id(user_id: str) -> str | None:
    """Read stripe_customer_id from the user's subscription sentinel.

    Uses safe_user_id (not just .lower()) to prevent path-traversal.
    Returns None if no sentinel, corrupt file, or missing customer_id.
    """
    safe_uid = safe_user_id(user_id)
    if not safe_uid:
        return None
    sentinel = _get_output_dir() / ".users" / safe_uid / "subscription.json"
    if not sentinel.exists():
        return None
    try:
        data = json.loads(sentinel.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    cid = data.get("stripe_customer_id")
    return cid if isinstance(cid, str) and cid else None


def run_get_invoice_history(handler) -> None:
    """GET /api/account/invoices — last 12 invoices for the user's Stripe
    customer. Returns {invoices: []} for free-tier users (no customer ID
    yet) — never 404; the empty list is a valid state."""
    user = require_user(handler)
    if user is None:
        return

    user_id = user.get("id", "")
    customer_id = _load_customer_id(user_id)

    if not customer_id:
        handler._json(200, {"invoices": []})
        return

    try:
        invoices = _list_stripe_invoices(customer_id, limit=12)
        rows = [_format_invoice(i) for i in invoices]
    except Exception as e:
        log.warning("[billing_api] stripe invoice fetch failed for %s: %s",
                    user_id, type(e).__name__)
        handler._json(500, {"error": "Couldn't load invoices. Please try again."})
        return

    handler._json(200, {"invoices": rows})
