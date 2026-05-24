"""User plan resolution + monthly usage tracking — Phase 54a (2026-05-23).

Single source of truth for "what plan is this user on?" + "how much
have they used this month?". Used by every gated endpoint to make
authoritative plan decisions.

Why this module exists
----------------------
Before Phase 54a, plan enforcement was a single binary gate in
``pebble/server/publish.py``: ``_subscription_active(user_id)`` returned
True/False based on whether ``subscription.json`` existed with status
``"active"``. Only the publish endpoint used it; everything else
(refinements, custom domains, blocks insert, analytics) was open to
all signed-in users.

Phase 54a centralizes the question. Every gated endpoint asks the
same three things:

  1. ``get_user_plan(user_id)`` → ``"free" | "starter" | "pro" | "enterprise"``
  2. ``get_limit(user_id, key)`` → numeric or boolean limit
  3. For variable-cost features: ``check_and_increment(user_id, key)``
     atomically increments a monthly counter + returns whether the
     user has remaining quota

Storage
-------
Subscription state is owned by ``pebble/server/stripe_webhook.py`` and
lives in ``output/.users/<uid>/subscription.json``.

Usage state is owned by this module and lives in
``output/.users/<uid>/usage_YYYY-MM.json``. New file each calendar
month (UTC) so counters reset automatically without a cron job.

PII / safety
------------
All disk I/O routes through ``pebble.security.safe_user_id`` so that
``../victim`` traversal can't read or corrupt a different user's
usage file. Atomic temp+rename writes prevent torn JSON if the
process dies mid-write.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pebble.security import safe_user_id


# --------- Plan-tier limit tables ----------------------------------------

# These mirror the PRICING_TIERS array in
# ui/v3/components/phases/welcome-phase.tsx. Keep them in sync — if the
# pricing page advertises a different number, this is the source of
# truth for enforcement and the page is wrong.
#
# Convention: -1 means "unlimited" (we want to keep ints, not float inf,
# so JSON serialization stays clean and comparisons stay simple).
PLAN_LIMITS: dict[str, dict[str, int | bool | list[str]]] = {
    "free": {
        # 2026-05-24: published_sites cap removed in favor of credit-based
        # pricing — credits per build IS the cap. Kept as -1 for backwards
        # compat with code that still reads this key.
        "published_sites":             -1,
        "ai_refinements_per_month":    30,
        "custom_domains":              0,
        "drop_in_sections_allowed":    False,
        "resend_email_forms":          False,
        "site_analytics":              False,
        "multi_page_sites":            True,
        "white_label":                 False,
        # 2026-05-24 funnel restructure:
        "integrations_allowed":        [],
        "stripe_checkout":             False,
        "api_access":                  False,
        "money_back_days":             0,
        "priority_support":            False,
        "remove_pebble_badge":         False,
        "lead_inbox":                  False,
        "form_autoresponder":          False,
    },
    "starter": {
        "published_sites":             -1,
        "ai_refinements_per_month":    150,
        "custom_domains":              1,
        "drop_in_sections_allowed":    False,
        "resend_email_forms":          True,
        "site_analytics":              False,
        "multi_page_sites":            True,
        "white_label":                 False,
        "integrations_allowed":        ["whatsapp", "booking", "google-maps", "cookie-consent"],
        "stripe_checkout":             False,
        "api_access":                  False,
        "money_back_days":             7,
        "priority_support":            False,
        "remove_pebble_badge":         True,
        "lead_inbox":                  True,
        "form_autoresponder":          True,
    },
    "pro": {
        "published_sites":             -1,
        "ai_refinements_per_month":    400,
        "custom_domains":              5,
        "drop_in_sections_allowed":    True,
        "resend_email_forms":          True,
        "site_analytics":              True,
        "multi_page_sites":            True,
        "white_label":                 True,
        "integrations_allowed":        ["whatsapp", "booking", "google-maps", "cookie-consent",
                                        "stripe", "custom-code", "social"],
        "stripe_checkout":             True,
        "api_access":                  True,
        "money_back_days":             14,
        "priority_support":            True,
        "remove_pebble_badge":         True,
        "lead_inbox":                  True,
        "form_autoresponder":          True,
    },
    "enterprise": {
        "published_sites":             -1,
        "ai_refinements_per_month":    -1,
        "custom_domains":              -1,
        "drop_in_sections_allowed":    True,
        "resend_email_forms":          True,
        "site_analytics":              True,
        "multi_page_sites":            True,
        "white_label":                 True,
        "integrations_allowed":        ["whatsapp", "booking", "google-maps", "cookie-consent",
                                        "stripe", "custom-code", "social"],
        "stripe_checkout":             True,
        "api_access":                  True,
        "money_back_days":             30,
        "priority_support":            True,
        "remove_pebble_badge":         True,
        "lead_inbox":                  True,
        "form_autoresponder":          True,
    },
}

# Hard ceilings — defense-in-depth caps that apply REGARDLESS of plan.
# Even if a user has subscription.json claiming "enterprise" (with the
# tier's -1 "unlimited" limit), they can never exceed these without an
# explicit per-user override. Protects against:
#   - compromised sentinel files
#   - code bugs that accidentally upgrade a user
#   - frontend retry-loops hammering an endpoint
#   - webhook replay / spoofed Stripe events
#
# Real Enterprise customers (when they exist) get their ceilings lifted
# via a manual override file at output/.users/<uid>/ceiling_override.json
# which can ONLY be written server-side — no API path to it.
HARD_CEILINGS: dict[str, int] = {
    "ai_refinements_per_month":  1000,   # 2.5× Pro's advertised 400
    "custom_domains":            20,
    "published_sites":           100,
}

# Active subscription statuses that grant the user their paid plan's
# benefits. Lapsed states (canceled, past_due, unpaid, paused) drop the
# user back to "free" until they resubscribe or pay the past-due amount.
_ACTIVE_STATUSES = frozenset({"active", "trialing"})

# Valid plan names. Anything else in subscription.json (typos,
# misconfigured price IDs, future plans we haven't shipped) downgrades
# to "free" rather than crashing the gate.
_VALID_PLANS = frozenset(PLAN_LIMITS.keys()) - {"free"}


# --------- Paths ----------------------------------------------------------

def _output_dir() -> Path:
    """Resolve OUTPUT_DIR through the engine module so tests can monkeypatch."""
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path(__file__).parent.parent.resolve() / "output"


def _subscription_sentinel(safe_uid: str) -> Path:
    return _output_dir() / ".users" / safe_uid / "subscription.json"


def _usage_sentinel(safe_uid: str, month: str) -> Path:
    return _output_dir() / ".users" / safe_uid / f"usage_{month}.json"


def _profile_sentinel(safe_uid: str) -> Path:
    """Phase 54b — user-level flags that aren't billing-specific.

    Holds the ``needs_plan_selection`` boolean and any future per-user
    state (notification prefs, beta flags, etc.) that doesn't belong in
    subscription.json (Stripe-owned). Written on signup, cleared when
    the user explicitly picks a plan.
    """
    return _output_dir() / ".users" / safe_uid / "profile.json"


def _current_month() -> str:
    """YYYY-MM in UTC. Used as the suffix for monthly usage files."""
    return datetime.now(timezone.utc).strftime("%Y-%m")


# --------- Plan resolution ------------------------------------------------

def get_user_plan(user_id: str) -> str:
    """Return the user's effective plan name as a lowercase string.

    Resolution order:
      1. Invalid / missing user_id → "free"
      2. No subscription.json → "free"
      3. Subscription status not in {active, trialing} → "free"
      4. Subscription plan not in our valid plan set → "free"
      5. Otherwise → the plan name from the sentinel

    Fail-closed: any read error downgrades to "free" so a corrupt
    sentinel never grants paid features by accident.
    """
    safe_uid = safe_user_id(user_id)
    if not safe_uid:
        return "free"
    sentinel = _subscription_sentinel(safe_uid)
    if not sentinel.exists():
        return "free"
    try:
        data = json.loads(sentinel.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return "free"
    if not isinstance(data, dict):
        return "free"
    status = data.get("status")
    if status not in _ACTIVE_STATUSES:
        return "free"
    plan = data.get("plan")
    if not isinstance(plan, str):
        return "free"
    plan_lower = plan.lower()
    if plan_lower not in _VALID_PLANS:
        return "free"
    return plan_lower


def _ceiling_override(user_id: str, key: str) -> Optional[int]:
    """Read a per-user manual ceiling override.

    Real Enterprise customers occasionally need limits above the
    HARD_CEILINGS defaults. The override file
    ``output/.users/<uid>/ceiling_override.json`` lets ops staff lift a
    cap without code changes — but ONLY via filesystem write, never via
    API. Format:: ``{"<key>": <int>}``. Returns the override value if
    present and valid, else None.
    """
    safe_uid = safe_user_id(user_id)
    if not safe_uid:
        return None
    path = _output_dir() / ".users" / safe_uid / "ceiling_override.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    value = data.get(key)
    if isinstance(value, int) and value > 0:
        return value
    return None


def get_limit(user_id: str, key: str) -> int | bool:
    """Return the limit value for ``key`` under the user's plan.

    Numeric values: -1 means unlimited. Boolean values: True/False.
    Unknown keys raise KeyError — every gated feature must have an
    entry in PLAN_LIMITS or the gate is unsafe.

    Hard ceiling pass: when ``key`` has a HARD_CEILINGS entry, the
    plan-tier value is clamped down. Even an Enterprise user with a
    -1 (unlimited) plan value gets the ceiling. Per-user override at
    ``ceiling_override.json`` lifts the cap for specific accounts.
    """
    plan = get_user_plan(user_id)
    plan_limit = PLAN_LIMITS[plan][key]

    # Booleans don't have ceilings — they're feature flags, not counters.
    if isinstance(plan_limit, bool):
        return plan_limit

    ceiling = HARD_CEILINGS.get(key)
    if ceiling is None:
        return plan_limit  # no defensive cap configured for this key

    # Per-user override beats the global ceiling. Override is a manual
    # filesystem write; can't be set via API.
    override = _ceiling_override(user_id, key)
    effective_ceiling = override if override is not None else ceiling

    # Unlimited (-1) plan value clamps to the ceiling.
    if plan_limit == -1:
        return effective_ceiling
    # Plan-tier value above the ceiling clamps down. (Shouldn't happen
    # with current PLAN_LIMITS, but defensive against future tier edits.)
    if plan_limit > effective_ceiling:
        return effective_ceiling
    return plan_limit


# --------- needs_plan_selection (Phase 54b) ------------------------------

def needs_plan_selection(user_id: str) -> bool:
    """Phase 54b — has the user explicitly chosen a plan (Free / Starter /
    Pro) since signing up?

    Default semantics:
      * profile.json missing      → False (legacy users + dev accounts
                                    aren't subject to the gate; only NEW
                                    signups after this flag was added
                                    get the profile.json that triggers it)
      * profile.json invalid/corrupt → False (fail-open for read errors
                                    so existing users never get stuck
                                    behind a busted sentinel)
      * profile.json with needs_plan_selection=true → True (the gate fires)
      * profile.json with needs_plan_selection=false → False (selection done)

    Set to True by the signup path (supabase_webhook or legacy auth);
    cleared by POST /api/account/select-plan.
    """
    safe_uid = safe_user_id(user_id)
    if not safe_uid:
        return False
    path = _profile_sentinel(safe_uid)
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return False
    if not isinstance(data, dict):
        return False
    return bool(data.get("needs_plan_selection"))


def set_needs_plan_selection(user_id: str, value: bool) -> bool:
    """Phase 54b — atomic write of the gate flag. Returns True on success,
    False on invalid uid or write error. Preserves any other fields
    already in profile.json.
    """
    safe_uid = safe_user_id(user_id)
    if not safe_uid:
        return False
    path = _profile_sentinel(safe_uid)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Read-modify-write so other profile fields (future: notification
    # prefs, beta flags) survive the toggle.
    data: dict = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(existing, dict):
                data = existing
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            pass
    data["needs_plan_selection"] = bool(value)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp, path)
        return True
    except OSError:
        return False


def get_project_plan(slug: str) -> str:
    """Return the plan of the project owner — used by site-side endpoints
    where the visitor isn't the customer (form submissions, analytics
    collection, etc.) but the action's billing tier depends on whose
    project it is.

    Reads ``output/<slug>/brief.json`` for ``_user_id`` and looks up
    that user's plan. Unclaimed (no _user_id) or missing-brief projects
    return "free" by default — fail-closed.
    """
    if not isinstance(slug, str) or not slug:
        return "free"
    # Avoid circular: import OUTPUT_DIR via the engine module like
    # _output_dir() does, then read brief.json. Inline because
    # importing pebble.history just for this is overkill.
    brief_path = _output_dir() / slug / "brief.json"
    if not brief_path.exists():
        return "free"
    try:
        brief = json.loads(brief_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return "free"
    if not isinstance(brief, dict):
        return "free"
    user_id = brief.get("_user_id")
    if not isinstance(user_id, str) or not user_id:
        return "free"
    return get_user_plan(user_id)


def project_has_feature(slug: str, key: str) -> bool:
    """Boolean feature check for a project, using its owner's plan."""
    plan = get_project_plan(slug)
    limit = PLAN_LIMITS[plan][key]
    if isinstance(limit, bool):
        return limit
    return limit != 0


def has_feature(user_id: str, key: str) -> bool:
    """Boolean-typed limit helper — True iff the user's plan grants the feature.

    For boolean keys (drop_in_sections_allowed, resend_email_forms,
    site_analytics, white_label) this is the natural read. For numeric
    keys (published_sites, custom_domains, refinements) it returns True
    iff the limit is non-zero (i.e. the user gets *any* of the thing).
    Use the explicit ``get_limit`` for actual quota math.
    """
    limit = get_limit(user_id, key)
    if isinstance(limit, bool):
        return limit
    return limit != 0


# --------- Monthly usage counters ----------------------------------------

def _read_usage(safe_uid: str, month: str) -> dict:
    """Read the current month's usage dict. Empty dict if missing/corrupt."""
    path = _usage_sentinel(safe_uid, month)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_usage_atomic(safe_uid: str, month: str, data: dict) -> None:
    """Atomic write via temp + rename. Creates the .users/<uid>/ dir on demand."""
    path = _usage_sentinel(safe_uid, month)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def would_exceed_quota(
    user_id: str, key: str, limit_key: str,
) -> tuple[bool, int, int]:
    """Read-only pre-check. Returns ``(would_exceed, current_count, limit)``.

    Used by endpoints that want to deny BEFORE running expensive work so
    the user doesn't burn a quota unit on a request that's about to fail
    for an unrelated reason. After the work succeeds, call
    :func:`increment_usage` to commit the +1.

    Race condition note: two concurrent requests from the same user can
    both pass this check before either calls increment_usage. Cost: at
    most one extra unit of usage. Acceptable for now; revisit when
    counters move to Postgres with row-level locks.
    """
    limit = get_limit(user_id, limit_key)
    if not isinstance(limit, int):
        # Boolean-keyed limits aren't countable. Allow if true, deny if false.
        return (not bool(limit), 0, 0 if not limit else -1)
    if limit == -1:
        # Unlimited plan — never exceeds.
        return (False, get_usage_count(user_id, key), -1)
    current = get_usage_count(user_id, key)
    return (current >= limit, current, limit)


def increment_usage(user_id: str, key: str) -> int:
    """Atomically +1 the monthly counter for ``key``. Returns new count.

    Caller's responsibility to gate via :func:`would_exceed_quota` first.
    This function unconditionally increments — it's the "commit" half of
    the check-then-commit pattern and trusts the caller to have already
    paid the gate.

    Returns 0 if the user_id is invalid (no-op write to nowhere).
    """
    safe_uid = safe_user_id(user_id)
    if not safe_uid:
        return 0
    month = _current_month()
    data = _read_usage(safe_uid, month)
    current = data.get(key, 0)
    if not isinstance(current, int) or current < 0:
        current = 0
    data[key] = current + 1
    _write_usage_atomic(safe_uid, month, data)
    return current + 1


def get_usage_count(user_id: str, key: str) -> int:
    """How many times has the user consumed ``key`` this calendar month?

    Returns 0 for invalid uid, missing file, or missing key. The caller
    decides what limit applies and whether the count is over.
    """
    safe_uid = safe_user_id(user_id)
    if not safe_uid:
        return 0
    data = _read_usage(safe_uid, _current_month())
    value = data.get(key, 0)
    if not isinstance(value, int) or value < 0:
        return 0
    return value


def check_and_increment(user_id: str, key: str, limit_key: str) -> tuple[bool, int, int]:
    """Atomically check + increment a monthly counter.

    Returns ``(allowed, new_count, limit)``:
      * allowed: True if the user had quota remaining BEFORE this call
                 (and the counter was incremented). False if they were
                 already at or over the limit (counter NOT incremented).
      * new_count: the count after the operation (= prev+1 if allowed,
                   prev unchanged if denied).
      * limit: the plan's limit for ``limit_key``. -1 means unlimited.

    Race condition note: file-system reads + writes here are NOT atomic
    across concurrent processes. If a user fires two refines within the
    same millisecond, both might pass the check. Acceptable for now
    (cost impact: one extra refinement worth ~$0.005). When this becomes
    a real problem, move counters to Postgres with row-level locks.

    Fail-closed: invalid uid returns (False, 0, 0) — the request gets
    denied with no usage recorded.
    """
    safe_uid = safe_user_id(user_id)
    if not safe_uid:
        return (False, 0, 0)

    limit = get_limit(user_id, limit_key)
    if not isinstance(limit, int):
        # Boolean-keyed limits don't have countable usage; treat as
        # gate-only and return current_count=0.
        return (bool(limit), 0, 0 if not limit else -1)

    month = _current_month()
    data = _read_usage(safe_uid, month)
    current = data.get(key, 0)
    if not isinstance(current, int) or current < 0:
        current = 0

    # Unlimited plans (limit == -1) always allow; still increment so
    # we have honest usage telemetry on Pro/Enterprise customers.
    if limit == -1 or current < limit:
        data[key] = current + 1
        _write_usage_atomic(safe_uid, month, data)
        return (True, current + 1, limit)

    # At or over limit — deny without incrementing.
    return (False, current, limit)


def get_quota_summary(user_id: str) -> dict:
    """Convenience for the /api/billing/subscription response — returns the
    user's plan + key usage counters + limits for the v3 frontend to
    render quota progress bars.
    """
    plan = get_user_plan(user_id)
    return {
        "plan":         plan,
        "limits":       PLAN_LIMITS[plan],
        "usage": {
            "ai_refinements_this_month": get_usage_count(user_id, "ai_refinements"),
        },
    }


# --------- 402 response helper -------------------------------------------

def gate_response(
    *,
    feature_label: str,
    required_plan: str,
    current_plan: str,
    current: Optional[int] = None,
    limit: Optional[int] = None,
) -> dict:
    """Standard JSON body for a 402 Payment Required response.

    Every gated endpoint returns this shape so the v3 frontend can
    render a consistent upgrade UI without parsing free-form text.
    """
    body: dict = {
        "error":         f"This is a {required_plan.title()} plan feature.",
        "feature":       feature_label,
        "required_plan": required_plan,
        "current_plan":  current_plan,
        "upgrade_url":   "/pricing",
    }
    if current is not None:
        body["current_usage"] = current
    if limit is not None and limit > 0:
        body["limit"] = limit
    return body


def get_feature(plan: str, key: str):
    """Look up a feature flag for a plan tier with safe fallback.

    Returns the matching value from PLAN_LIMITS[plan][key], or a safe
    "default off" value if the plan or key is unknown:

      - missing list  → []
      - missing bool  → False
      - missing int   → 0

    Used by every gated endpoint and the v3 plan-features.ts mirror.
    Fail-soft so that an unknown feature can never accidentally grant
    access (defaults to "off"). Adding a new feature requires updating
    PLAN_LIMITS for every tier — there is no implicit inheritance.
    """
    tier = PLAN_LIMITS.get(plan) or PLAN_LIMITS["free"]
    if key not in tier:
        return False
    return tier[key]
