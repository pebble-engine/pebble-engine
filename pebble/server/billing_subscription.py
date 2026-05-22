"""GET /api/billing/subscription — read-only "what plan am I on?" endpoint.

The webhook (``pebble/server/stripe_webhook.py``) is single-writer for
``output/.users/<uid>/subscription.json``; this endpoint is just a
filtered reader so v3's settings page can render a "currently on Pebble
Starter — renews May 17, 2027" badge without round-tripping to Stripe.

Why a separate endpoint and not just `/api/billing/portal`:
- /api/billing/portal redirects the browser into Stripe-hosted UX. That's
  a destination, not a data fetch. The badge is a data fetch.
- Keeping them separate means v3 can show the badge for canceled /
  past_due states too, without first needing to mint a portal session.

Auth: same require_user gate as the other billing endpoints. No
subscription -> 200 with ``{plan: null, status: null,
current_period_end: null}`` (rather than 404) so v3 can branch on the
field instead of try/catch. PII (customer_id, subscription_id, last
event tracking) is stripped before the response goes out.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Optional

from pebble.security import require_user, safe_user_id


log = logging.getLogger("pebble.billing_subscription")


def _output_dir() -> Path:
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path(__file__).parent.parent.parent.resolve() / "output"


def _load_sentinel(user_id: str) -> Optional[dict]:
    """Read the user's subscription sentinel via the strict ``safe_user_id``
    validation. NLM round 2 Finding #R2.4: a ``.lower()``-only fix lets
    ``../victim`` traverse out of ``output/.users/`` and read a different
    user's sentinel. Returns None for invalid uid, missing, or corrupt
    files."""
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
    return data if isinstance(data, dict) else None


def run_get_subscription(handler) -> None:
    """Entry point — wired from PebbleHandler.do_GET."""
    user = require_user(handler)
    if user is None:
        return

    # Phase 54b — surface whether the user still needs to pick a plan.
    # v3 uses this to decide whether to mount the plan-picker modal
    # (Phase 54c offer wall). Imported inside the function so a bad
    # user_plan import never breaks the subscription endpoint.
    needs_pick = False
    try:
        from pebble.user_plan import needs_plan_selection
        needs_pick = needs_plan_selection(user.get("id", ""))
    except Exception:
        pass

    sentinel = _load_sentinel(user.get("id", ""))
    if sentinel is None:
        # No subscription. Respond 200 with explicit nulls so v3 can
        # render an "upgrade to a plan" CTA without parsing exception
        # messages.
        handler._json(200, {
            "plan":                  None,
            "status":                None,
            "current_period_end":    None,
            "needs_plan_selection":  needs_pick,
        })
        return

    # Curated subset — never echo customer_id / subscription_id (PII /
    # internal stripe identifiers) or the dedup tracking fields.
    handler._json(200, {
        "plan":                  sentinel.get("plan"),
        "status":                sentinel.get("status"),
        "current_period_end":    sentinel.get("current_period_end"),
        "needs_plan_selection":  needs_pick,
    })
