"""Tier-aware model selection for OpenRouter builds.

Marc's pricing thesis (2026-05-19): charge premium prices, pay cheap-model
costs. Free tier users get the fastest Qwen variant (Flash, ~2-3× faster +
~40% cheaper than Plus). Paid tiers get Qwen 3.6 Plus (better quality +
1M context for full multi-page builds).

The mapping is intentionally narrow — only OpenRouter is tier-aware; if
the engine is on Anthropic or Gemini, the configured PEBBLE_MODEL wins
unchanged. This preserves the manual-override path for testing without
forcing every provider to model-shop on plan.

If the user has no subscription sentinel (anonymous / signed up but
never paid), we default to FREE behavior — cheapest model. If the
sentinel is corrupt / unreadable, same fallback. Conservative fail-safe:
better to ship a slightly cheaper build than to deny the build entirely.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from pebble.security import safe_user_id


# Model IDs map to OpenRouter's catalog. Bumped when we re-validate.
# Kept here (not in pebble/llm.py) because the choice is a billing
# concern, not an LLM-client concern.
MODEL_FOR_FREE_TIER = "qwen/qwen3.6-flash"
MODEL_FOR_PAID_TIER = "qwen/qwen3.6-plus-04-02"


def resolve_user_plan(user_id: Optional[str], output_root: Optional[Path] = None) -> str:
    """Return one of {"free", "starter", "pro"} for the given user.

    Reads ``output/.users/<safe_uid>/subscription.json``. Returns "free"
    if uid is None, malformed, missing, or the file is corrupt. Returns
    the recorded plan string when the sentinel is healthy.

    ``output_root`` lets tests point at a tmp directory. Production
    leaves it None to use the real OUTPUT_DIR.
    """
    if not user_id:
        return "free"
    safe_uid = safe_user_id(user_id)
    if not safe_uid:
        return "free"

    if output_root is None:
        # Import lazily so this module can be imported in test contexts
        # that haven't initialised the engine config yet.
        from pebble.evals import OUTPUT_DIR
        output_root = Path(OUTPUT_DIR)

    sentinel = output_root / ".users" / safe_uid / "subscription.json"
    if not sentinel.exists():
        return "free"
    try:
        data = json.loads(sentinel.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return "free"
    if not isinstance(data, dict):
        return "free"

    # Subscription must be in an active-ish state to count as paid.
    # We accept "active" + "trialing" — both produce real billing intent.
    # "canceled", "past_due", "incomplete", etc → treat as free tier so
    # the user keeps building but on the cheap model.
    status = (data.get("status") or "").lower()
    if status not in ("active", "trialing"):
        return "free"

    plan = (data.get("plan") or "").lower()
    if plan == "pro":
        return "pro"
    if plan == "starter":
        return "starter"
    # Unknown plan name on an active subscription — treat as starter
    # (paid floor). Don't downgrade real customers to free over a typo.
    return "starter"


def model_for_plan(plan: str) -> str:
    """Map a plan string to the OpenRouter model id to use."""
    if plan == "free":
        return MODEL_FOR_FREE_TIER
    # Both starter and pro currently route to Plus. When we add
    # Max-tier (qwen3.6-max-preview-...) as a Pro-only perk, branch here.
    return MODEL_FOR_PAID_TIER


__all__ = [
    "resolve_user_plan",
    "model_for_plan",
    "MODEL_FOR_FREE_TIER",
    "MODEL_FOR_PAID_TIER",
]
