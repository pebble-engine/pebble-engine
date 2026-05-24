# Template-First Funnel + Tier Gating + Pricing Restructure — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Shift the funnel from "engine-build-from-prompt" to "template-match-from-prompt → paid engine build", with Pro positioned as the rockstar tier. Stop selling sites-count; start selling credits + integrations. Add "Pro Feature" / "Starter Feature" badges throughout the workspace so the upgrade path is always visible.

**Architecture:** Three independent subsystems, sequenced so each builds on stable ground:

1. **Foundation (Phases A + B)** — extend `pebble/user_plan.py` PLAN_LIMITS with new feature flags (integrations, stripe_checkout, white_label, api_access, money_back_days), drop `published_sites` cap, surface plan tier to the v3 client via a typed helper. Without this, every later UI gate has no source of truth.
2. **UI gating + pricing UI (Phases C + D + E)** — Pro Feature / Starter Feature badge component, gated integration cards, restructured pricing page emphasising credits, conversion-optimized Pro card.
3. **Funnel re-ordering + smart matcher (Phases F + G)** — re-order so prompt-capture comes first, then signup, then template match (using a cheap LLM intent extract scored against `industries.json`), then template gallery, then "buy credits or stay free." Funnel polish: first-build celebration screen, cart-abandon nudge.

Each phase is independently shippable — Phases A+B unblock B-G but ship value alone (cleaner tier model). Phases C-E ship UI value alone (clearer upgrade story). Phases F-G ship conversion value alone (template-first funnel).

**Tech Stack:** Python 3.11 (engine), Next.js 15 App Router + TypeScript + Tailwind v4 (v3 frontend), Supabase Auth, Stripe Checkout, pytest for engine tests.

**Conventions:** Tests live in `tests/test_*.py`. v3 has no test suite — TypeScript (`./node_modules/.bin/tsc --noEmit` from `ui/v3/`) is the correctness gate. Commits include `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`. Push to `squitopest` (NOT `pebblewebsite` — Marc owns the production push).

**Out of scope (deliberately):**
- Annual billing toggle (post-launch — needs Stripe Prices set up first)
- A/B variant builds (post-launch — needs more thought on UX)
- API access (post-launch — needs API key minting + rate-limit infra)
- White-label removal of "Built with Pebble" badge (separate plan)
- Cloudflare WAF / Bot Fight Mode (Marc handles in dashboard)

---

## File Structure

**Engine (Python):**
- `pebble/user_plan.py` — extend PLAN_LIMITS, add new feature flags, drop `published_sites` cap. Single source of truth.
- `pebble/server/integrations.py` — add tier gate per integration_id on save/delete.
- `pebble/server/template_match.py` — NEW. `/api/template-match` endpoint: take a free-text prompt, return top-3 matching templates from `pebble/templates_registry.py` using industries.json keyword overlap + optional GPT-4o-mini intent extract fallback.
- `tests/test_user_plan_features.py` — NEW. Unit tests for the new feature flags.
- `tests/test_integrations_gating.py` — NEW. Endpoint-level test that free user gets 402 when saving WhatsApp.
- `tests/test_template_match.py` — NEW. Mock LLM, assert matcher ranks deterministically.

**v3 frontend (TypeScript):**
- `ui/v3/lib/plan-features.ts` — NEW. TypeScript mirror of PLAN_LIMITS; `getFeature(plan, key)` helper used by every gated UI.
- `ui/v3/components/tier-badge.tsx` — NEW. Reusable "Pro" / "Starter" pill (with optional lock icon + tooltip). 60 lines.
- `ui/v3/components/locked-feature.tsx` — NEW. Ghost-state overlay that wraps a feature surface; for free users renders the feature greyed out with a "Pro Feature — upgrade to unlock" CTA. 80 lines.
- `ui/v3/components/phases/welcome-phase.tsx` — modify PRICING_TIERS array (lines 182-220): drop `1 site / 5 sites / unlimited sites`, replace with credit-based + integration list + Pro rockstar polish.
- `ui/v3/components/phases/integrations-phase.tsx` — wrap each integration in `<LockedFeature plan="starter"|"pro">` based on the tier required.
- `ui/v3/app/api/template-match/route.ts` — NEW. Proxy route that forwards to engine `/api/template-match`.
- `ui/v3/components/template-match-modal.tsx` — NEW. After signup, displays the top-3 template suggestions with "Use this one" / "See more options" / "Build from scratch (10 credits)" CTAs.
- `ui/v3/components/first-build-celebration.tsx` — NEW. Confetti + upgrade CTA shown when free user finishes first build.
- `ui/v3/components/workspace-shell.tsx` — wire up template-match flow as a new phase between `welcome` and `draft`.

---

## Phase A — Plan model: feature flags + credit-based positioning

### Task A1: Extend PLAN_LIMITS with new feature flags

**Files:**
- Modify: `pebble/user_plan.py` (PLAN_LIMITS dict, lines 62-100)
- Test: `tests/test_user_plan_features.py` (create)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_user_plan_features.py
"""Phase A1 — extended PLAN_LIMITS with new feature flags.

Pebble pricing restructure 2026-05-24: drop the `published_sites`
cap as the headline metric, add integration / stripe_checkout /
white_label / api_access / money_back_days flags.
"""
from pebble import user_plan


def test_free_has_no_integrations_allowed():
    assert user_plan.PLAN_LIMITS["free"]["integrations_allowed"] == []


def test_starter_has_basic_integrations():
    assert "whatsapp"     in user_plan.PLAN_LIMITS["starter"]["integrations_allowed"]
    assert "booking"      in user_plan.PLAN_LIMITS["starter"]["integrations_allowed"]
    assert "google-maps"  in user_plan.PLAN_LIMITS["starter"]["integrations_allowed"]
    assert "cookie-consent" in user_plan.PLAN_LIMITS["starter"]["integrations_allowed"]
    # Stripe + custom-code are Pro-only
    assert "stripe"      not in user_plan.PLAN_LIMITS["starter"]["integrations_allowed"]
    assert "custom-code" not in user_plan.PLAN_LIMITS["starter"]["integrations_allowed"]


def test_pro_has_all_integrations():
    pro = user_plan.PLAN_LIMITS["pro"]["integrations_allowed"]
    for iid in ("whatsapp", "booking", "google-maps", "cookie-consent",
                "stripe", "custom-code", "social"):
        assert iid in pro, f"{iid} missing from pro integrations"


def test_money_back_days_progression():
    assert user_plan.PLAN_LIMITS["free"]["money_back_days"]    == 0
    assert user_plan.PLAN_LIMITS["starter"]["money_back_days"] == 7
    assert user_plan.PLAN_LIMITS["pro"]["money_back_days"]     == 14


def test_white_label_pro_only():
    assert user_plan.PLAN_LIMITS["free"]["white_label"]    is False
    assert user_plan.PLAN_LIMITS["starter"]["white_label"] is False
    assert user_plan.PLAN_LIMITS["pro"]["white_label"]     is True


def test_api_access_pro_only():
    assert user_plan.PLAN_LIMITS["free"]["api_access"]    is False
    assert user_plan.PLAN_LIMITS["starter"]["api_access"] is False
    assert user_plan.PLAN_LIMITS["pro"]["api_access"]     is True


def test_published_sites_cap_removed():
    # 2026-05-24: published_sites cap deprecated in favor of credit-based
    # pricing. The key still exists for backwards compat but is now -1
    # (unlimited) across every tier — sites are gated by credit cost,
    # not by a sites-count cap.
    for tier in ("free", "starter", "pro", "enterprise"):
        assert user_plan.PLAN_LIMITS[tier]["published_sites"] == -1


def test_get_feature_helper_exists():
    """get_feature(user_id, key) → typed lookup, fail-soft default."""
    assert user_plan.get_feature("free",    "integrations_allowed") == []
    assert user_plan.get_feature("starter", "white_label") is False
    assert user_plan.get_feature("pro",     "api_access")  is True
    # Unknown feature → safe default
    assert user_plan.get_feature("pro", "made_up_key") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_user_plan_features.py -v`
Expected: 8 FAILs (KeyError on `integrations_allowed` / `money_back_days` / `api_access`; AttributeError on `get_feature`)

- [ ] **Step 3: Implement the feature flag additions**

In `pebble/user_plan.py`, replace the existing `PLAN_LIMITS` dict (lines 62-100) with:

```python
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
```

Then add at the bottom of the file (before `__all__`):

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_user_plan_features.py -v`
Expected: 8 PASS

- [ ] **Step 5: Run full pytest to confirm no regressions**

Run: `python -m pytest -q`
Expected: ≥ 1981 PASS (the pre-existing test count from CLAUDE.md), 0 FAIL

- [ ] **Step 6: Commit**

```bash
git add pebble/user_plan.py tests/test_user_plan_features.py
git commit -m "$(cat <<'EOF'
feat(plan): extend PLAN_LIMITS with integrations/stripe/white-label/api/refund-days flags

2026-05-24 funnel restructure. published_sites cap deprecated (now -1
across all tiers) — credit cost per build IS the cap. New flags:

  - integrations_allowed: list[str] (which integration_ids this tier can save)
  - stripe_checkout: bool (customer-site Stripe Checkout integration)
  - api_access: bool (programmatic /v1/sites endpoint, pro-only)
  - money_back_days: int (0/7/14/30 per tier)
  - lead_inbox + form_autoresponder: bool (was always-free, now starter+)
  - remove_pebble_badge: bool (white-label on built sites)
  - priority_support: bool (24-hr SLA on pro)

New helper: get_feature(plan, key) — fail-soft lookup, defaults to
False/0/[] so unknown features can never accidentally grant access.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task A2: Surface plan-tier features to the v3 client (TS mirror)

**Files:**
- Create: `ui/v3/lib/plan-features.ts`
- Test: TypeScript type-check (no v3 test suite)

- [ ] **Step 1: Create the TS mirror**

```typescript
// ui/v3/lib/plan-features.ts
/**
 * TypeScript mirror of pebble/user_plan.py PLAN_LIMITS.
 *
 * 2026-05-24 funnel restructure. Keep IN SYNC with the Python source —
 * if either copy drifts, every gated UI will lie to the user about
 * what they can / can't do.
 *
 * Why a mirror (not a fetch): client-side gates (lock overlays, "Pro
 * Feature" badges, integration card states) need to render synchronously
 * during the first paint. A fetch would force a loading flash. The
 * authoritative server-side check still runs on every gated API call,
 * so a drifted client only annoys, never breaks security.
 */

export type PlanTier = "free" | "starter" | "pro" | "enterprise";

export type IntegrationId =
  | "whatsapp" | "booking" | "google-maps" | "cookie-consent"
  | "stripe"   | "custom-code" | "social";

export type PlanFeatures = {
  published_sites:           number;   // -1 = unlimited
  ai_refinements_per_month:  number;
  custom_domains:            number;
  drop_in_sections_allowed:  boolean;
  resend_email_forms:        boolean;
  site_analytics:            boolean;
  multi_page_sites:          boolean;
  white_label:               boolean;
  integrations_allowed:      IntegrationId[];
  stripe_checkout:           boolean;
  api_access:                boolean;
  money_back_days:           number;
  priority_support:          boolean;
  remove_pebble_badge:       boolean;
  lead_inbox:                boolean;
  form_autoresponder:        boolean;
};

export const PLAN_LIMITS: Record<PlanTier, PlanFeatures> = {
  free: {
    published_sites:           -1,
    ai_refinements_per_month:  30,
    custom_domains:            0,
    drop_in_sections_allowed:  false,
    resend_email_forms:        false,
    site_analytics:            false,
    multi_page_sites:          true,
    white_label:               false,
    integrations_allowed:      [],
    stripe_checkout:           false,
    api_access:                false,
    money_back_days:           0,
    priority_support:          false,
    remove_pebble_badge:       false,
    lead_inbox:                false,
    form_autoresponder:        false,
  },
  starter: {
    published_sites:           -1,
    ai_refinements_per_month:  150,
    custom_domains:            1,
    drop_in_sections_allowed:  false,
    resend_email_forms:        true,
    site_analytics:            false,
    multi_page_sites:          true,
    white_label:               false,
    integrations_allowed:      ["whatsapp", "booking", "google-maps", "cookie-consent"],
    stripe_checkout:           false,
    api_access:                false,
    money_back_days:           7,
    priority_support:          false,
    remove_pebble_badge:       true,
    lead_inbox:                true,
    form_autoresponder:        true,
  },
  pro: {
    published_sites:           -1,
    ai_refinements_per_month:  400,
    custom_domains:            5,
    drop_in_sections_allowed:  true,
    resend_email_forms:        true,
    site_analytics:            true,
    multi_page_sites:          true,
    white_label:               true,
    integrations_allowed:      ["whatsapp", "booking", "google-maps", "cookie-consent",
                                "stripe", "custom-code", "social"],
    stripe_checkout:           true,
    api_access:                true,
    money_back_days:           14,
    priority_support:          true,
    remove_pebble_badge:       true,
    lead_inbox:                true,
    form_autoresponder:        true,
  },
  enterprise: {
    published_sites:           -1,
    ai_refinements_per_month:  -1,
    custom_domains:            -1,
    drop_in_sections_allowed:  true,
    resend_email_forms:        true,
    site_analytics:            true,
    multi_page_sites:          true,
    white_label:               true,
    integrations_allowed:      ["whatsapp", "booking", "google-maps", "cookie-consent",
                                "stripe", "custom-code", "social"],
    stripe_checkout:           true,
    api_access:                true,
    money_back_days:           30,
    priority_support:          true,
    remove_pebble_badge:       true,
    lead_inbox:                true,
    form_autoresponder:        true,
  },
};

/** Look up a feature flag for a plan tier. Mirror of user_plan.get_feature(). */
export function getFeature<K extends keyof PlanFeatures>(
  plan: PlanTier | string | null | undefined,
  key:  K,
): PlanFeatures[K] {
  const tier = (plan && plan in PLAN_LIMITS ? plan : "free") as PlanTier;
  return PLAN_LIMITS[tier][key];
}

/** True when the given tier is allowed to use the given integration. */
export function canUseIntegration(plan: PlanTier | string | null, id: IntegrationId): boolean {
  return (getFeature(plan, "integrations_allowed") as IntegrationId[]).includes(id);
}

/** Cheapest tier that unlocks the given integration. "starter" or "pro". */
export function minTierFor(id: IntegrationId): PlanTier {
  if (canUseIntegration("starter", id)) return "starter";
  return "pro";
}
```

- [ ] **Step 2: TypeScript check**

Run from `ui/v3/`: `./node_modules/.bin/tsc --noEmit`
Expected: no output (clean)

- [ ] **Step 3: Commit**

```bash
git add ui/v3/lib/plan-features.ts
git commit -m "$(cat <<'EOF'
feat(v3): plan-features.ts — TS mirror of PLAN_LIMITS for client-side gates

Lets every gated UI (integration cards, lock overlays, "Pro Feature"
badges) render synchronously without a fetch loading-flash. Authoritative
server-side enforcement still runs on every API call, so a drifted
client only annoys, never breaks security.

Exports: PLAN_LIMITS, getFeature(plan, key), canUseIntegration(plan, id),
minTierFor(id). Add new features by updating BOTH this file and
pebble/user_plan.py PLAN_LIMITS — there is no implicit inheritance.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase B — Tier-gate the integrations endpoint

### Task B1: Add tier gate to integrations save endpoint

**Files:**
- Modify: `pebble/server/integrations.py` (handle_save function)
- Test: `tests/test_integrations_gating.py` (create)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_integrations_gating.py
"""Phase B1 — tier-gate /api/projects/<slug>/integrations save endpoint.

A free user trying to enable WhatsApp must get a 402 with the credit-
paywall envelope so the v3 PaywallModal shows the upgrade path. A
starter user enabling WhatsApp should succeed; a starter user trying
to enable Stripe should get 402."""
import json
import pytest
from unittest.mock import patch, MagicMock

from pebble.server import integrations as endpoint


class FakeHandler:
    def __init__(self):
        self.last_status = None
        self.last_body = None

    def _json(self, status, body):
        self.last_status = status
        self.last_body = body


@pytest.mark.parametrize("plan,integration_id,expected_status", [
    ("free",    "whatsapp",    402),
    ("free",    "stripe",      402),
    ("starter", "whatsapp",    200),
    ("starter", "booking",     200),
    ("starter", "stripe",      402),   # starter can't do Stripe
    ("starter", "custom-code", 402),   # starter can't do custom-code
    ("pro",     "whatsapp",    200),
    ("pro",     "stripe",      200),
    ("pro",     "custom-code", 200),
])
def test_save_tier_gate(plan, integration_id, expected_status):
    handler = FakeHandler()
    body = {"integration_id": integration_id, "enabled": True, "config": {}}
    fake_user = {"id": "user-test-1234567890123456"}

    with patch.object(endpoint, "require_user",            return_value=fake_user), \
         patch.object(endpoint, "require_project_owner",   return_value="test-slug"), \
         patch("pebble.user_plan.get_user_plan",          return_value=plan), \
         patch.object(endpoint, "_load_integrations",     return_value={}), \
         patch.object(endpoint, "_save_integrations",     return_value=None):
        endpoint.handle_save(handler, "test-slug", body)

    assert handler.last_status == expected_status, (
        f"plan={plan} integration={integration_id} expected {expected_status} "
        f"got {handler.last_status}: {handler.last_body}"
    )

    if expected_status == 402:
        assert handler.last_body["code"] == "tier_locked"
        assert handler.last_body["upgrade_url"] == "/pricing"
        assert "integration" in handler.last_body["message"].lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_integrations_gating.py -v`
Expected: 9 FAILs — all return 200 instead of 402 for free/locked cases (gate doesn't exist yet)

- [ ] **Step 3: Add the gate to handle_save**

Open `pebble/server/integrations.py`. Find `handle_save` and the spot right after `require_user` + `require_project_owner` succeed and before the actual save happens. Insert:

```python
# 2026-05-24 funnel restructure: tier gate. Free has no integrations
# at all; starter has 4 (whatsapp/booking/google-maps/cookie-consent);
# pro has all 7. Authoritative check — the v3 client also gates the
# UI but the API must refuse independently.
from pebble import user_plan as _user_plan
caller_plan = _user_plan.get_user_plan(user["id"]) or "free"
allowed = _user_plan.get_feature(caller_plan, "integrations_allowed")
if integration_id not in allowed:
    min_tier = "starter" if integration_id in _user_plan.get_feature("starter", "integrations_allowed") else "pro"
    pretty = {
        "whatsapp": "WhatsApp", "booking": "Booking link", "google-maps": "Google Maps",
        "cookie-consent": "Cookie consent", "stripe": "Stripe Checkout",
        "custom-code": "Custom code", "social": "Social embeds",
    }.get(integration_id, integration_id)
    handler._json(402, {
        "error":         "tier locked",
        "code":          "tier_locked",
        "feature":       integration_id,
        "min_tier":      min_tier,
        "message":       f"The {pretty} integration is part of {min_tier.capitalize()}. Upgrade to unlock.",
        "upgrade_url":   "/pricing",
    })
    return
```

(Place this AFTER the request body is parsed so `integration_id` is bound, and BEFORE the persist step.)

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_integrations_gating.py -v`
Expected: 9 PASS

- [ ] **Step 5: Confirm no regressions in full suite**

Run: `python -m pytest -q`
Expected: ≥ 1989 PASS (was 1981 + 8 new in A1)

- [ ] **Step 6: Commit**

```bash
git add pebble/server/integrations.py tests/test_integrations_gating.py
git commit -m "$(cat <<'EOF'
feat(integrations): tier-gate /save endpoint per PLAN_LIMITS integrations_allowed

Free → no integrations at all. Starter → whatsapp/booking/google-maps/
cookie-consent. Pro → all 7 (adds stripe/custom-code/social).

Returns 402 {code: "tier_locked", min_tier, upgrade_url} so the v3
PaywallModal can surface the upgrade path cleanly when a free user
clicks "Save" on a locked integration.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase C — TierBadge + LockedFeature components

### Task C1: TierBadge pill

**Files:**
- Create: `ui/v3/components/tier-badge.tsx`

- [ ] **Step 1: Create the component**

```tsx
// ui/v3/components/tier-badge.tsx
"use client";

/**
 * TierBadge — small "Pro" / "Starter" pill shown on locked features.
 *
 * 2026-05-24 funnel restructure: hints throughout the workspace tell
 * users WHICH tier unlocks a feature instead of hiding the feature
 * (which would make the app feel small). Renders inline next to the
 * locked feature's label — never blocks interaction, just signals.
 *
 * Usage:
 *
 *   <TierBadge tier="pro" />
 *   <button>
 *     Add Stripe Checkout <TierBadge tier="pro" />
 *   </button>
 *
 * Variants:
 *   - tier="starter" → soft amber pill, white text
 *   - tier="pro"     → soft violet pill, white text
 *
 * Add a `lock` prop to prepend a lock icon (used in LockedFeature
 * overlays where the visual lock cue is the whole point).
 */

import { Lock, Sparkles } from "lucide-react";

export type TierBadgeProps = {
  tier:  "starter" | "pro";
  lock?: boolean;
  className?: string;
};

const TIER_STYLES: Record<"starter" | "pro", { bg: string; label: string }> = {
  starter: { bg: "bg-amber-500/95  text-white", label: "Starter" },
  pro:     { bg: "bg-violet-600/95 text-white", label: "Pro" },
};

export function TierBadge({ tier, lock = false, className = "" }: TierBadgeProps) {
  const s = TIER_STYLES[tier];
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full ${s.bg} text-[10px] font-bold uppercase tracking-widest ${className}`}
      aria-label={`${s.label} tier feature`}
    >
      {lock ? <Lock className="w-2.5 h-2.5" /> : <Sparkles className="w-2.5 h-2.5" />}
      {s.label}
    </span>
  );
}
```

- [ ] **Step 2: TypeScript check**

Run from `ui/v3/`: `./node_modules/.bin/tsc --noEmit`
Expected: no output

- [ ] **Step 3: Commit**

```bash
git add ui/v3/components/tier-badge.tsx
git commit -m "$(cat <<'EOF'
feat(v3): TierBadge pill — Starter / Pro hint pills for locked features

Sparkles icon by default (signals "premium"), lock icon variant for
when the visual lock cue is the whole point. Used inline next to
feature labels so the upgrade path is always visible without
obscuring the feature itself.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task C2: LockedFeature overlay wrapper

**Files:**
- Create: `ui/v3/components/locked-feature.tsx`

- [ ] **Step 1: Create the component**

```tsx
// ui/v3/components/locked-feature.tsx
"use client";

/**
 * LockedFeature — ghost-state overlay that wraps a feature surface
 * (a card, panel, button, whole section). For users without the
 * required tier, renders the feature greyed out with a centered
 * "Upgrade to Pro" CTA. Authorized users see the children as normal.
 *
 * 2026-05-24 funnel restructure: making the gap concrete (Pro features
 * are visible, just locked) converts ~3x better than hiding them
 * altogether (free users don't know what they're missing).
 *
 * Usage:
 *
 *   <LockedFeature
 *     plan={currentPlan}
 *     requires="pro"
 *     featureLabel="Stripe Checkout"
 *   >
 *     <StripeCheckoutCard />
 *   </LockedFeature>
 *
 * Behavior:
 *   - If currentPlan tier is >= requires tier → render children as-is
 *   - Otherwise → render children in a pointer-events-none, opacity-50
 *     container, with a centered absolute overlay
 *     "{featureLabel} is a {requires} feature — Upgrade to unlock"
 *     + a primary CTA button routing to /pricing.
 *
 * Tier ordering (low to high): free < starter < pro < enterprise.
 */

import Link from "next/link";
import { motion } from "framer-motion";
import { TierBadge } from "@/components/tier-badge";
import type { PlanTier } from "@/lib/plan-features";

const TIER_RANK: Record<PlanTier, number> = {
  free: 0, starter: 1, pro: 2, enterprise: 3,
};

export type LockedFeatureProps = {
  plan:         PlanTier | string | null | undefined;
  requires:     "starter" | "pro";
  featureLabel: string;
  /** What to show as the CTA copy. Default: "Upgrade to {requires}". */
  ctaLabel?:    string;
  children:     React.ReactNode;
};

export function LockedFeature({
  plan,
  requires,
  featureLabel,
  ctaLabel,
  children,
}: LockedFeatureProps) {
  const callerRank = TIER_RANK[(plan && (plan as PlanTier)) in TIER_RANK ? (plan as PlanTier) : "free"];
  const requiredRank = TIER_RANK[requires];

  if (callerRank >= requiredRank) {
    // Authorized — render children as-is.
    return <>{children}</>;
  }

  const cta = ctaLabel || `Upgrade to ${requires.charAt(0).toUpperCase() + requires.slice(1)}`;

  return (
    <div className="relative isolate">
      <div className="pointer-events-none select-none opacity-40 blur-[1px]">
        {children}
      </div>
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.2 }}
        className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-3 p-6 bg-card/85 backdrop-blur-sm rounded-2xl border border-border"
      >
        <TierBadge tier={requires} lock />
        <p className="text-center text-base font-bold text-foreground">
          {featureLabel}
        </p>
        <p className="text-center text-xs text-muted-foreground max-w-[20rem]">
          This feature is part of the {requires.charAt(0).toUpperCase() + requires.slice(1)} plan. Upgrade to unlock.
        </p>
        <Link
          href="/pricing"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-primary text-primary-foreground text-xs font-bold hover:opacity-95"
        >
          {cta}
        </Link>
      </motion.div>
    </div>
  );
}
```

- [ ] **Step 2: TypeScript check**

Run from `ui/v3/`: `./node_modules/.bin/tsc --noEmit`
Expected: no output

- [ ] **Step 3: Commit**

```bash
git add ui/v3/components/locked-feature.tsx
git commit -m "$(cat <<'EOF'
feat(v3): LockedFeature wrapper — ghost-state overlay for tier-gated UI

For users below the required tier, wraps the feature in an
opacity-40 blurred container with a centered upgrade CTA. Authorized
users see children as-is. Tier ranking: free < starter < pro < enterprise.

The "show locked, don't hide" pattern converts 3x better than
hiding features altogether — users see what they're missing.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase D — Gate integrations panel with LockedFeature

### Task D1: Wrap each integration card with tier gate

**Files:**
- Modify: `ui/v3/components/phases/integrations-phase.tsx`

- [ ] **Step 1: Read the current integration panel structure**

Run: `wc -l ui/v3/components/phases/integrations-phase.tsx`
Then `head -80 ui/v3/components/phases/integrations-phase.tsx` to find where each integration card is rendered.

- [ ] **Step 2: Fetch current user plan inside the component**

At the top of the IntegrationsPhase component body, add:

```typescript
import { fetchSubscription } from "@/lib/api";
import { LockedFeature } from "@/components/locked-feature";
import { TierBadge } from "@/components/tier-badge";
import { canUseIntegration, type IntegrationId, type PlanTier } from "@/lib/plan-features";

// ... inside component:
const [plan, setPlan] = useState<PlanTier>("free");
useEffect(() => {
  fetchSubscription()
    .then((sub) => setPlan((sub.plan as PlanTier) || "free"))
    .catch(() => setPlan("free"));
}, []);
```

- [ ] **Step 3: Wrap each integration card with LockedFeature**

For each integration card render in `integrations-phase.tsx`, wrap it like this (example for WhatsApp — repeat the pattern per integration, using `minTierFor(id)` for the `requires` prop):

```tsx
<LockedFeature
  plan={plan}
  requires={canUseIntegration("starter", "whatsapp") ? "starter" : "pro"}
  featureLabel="WhatsApp button"
>
  <WhatsAppCard />
</LockedFeature>
```

For Stripe / custom-code / social (Pro-only), the wrapper uses `requires="pro"`. For whatsapp / booking / google-maps / cookie-consent, use `requires="starter"`. Confirm against `minTierFor(id)` from `plan-features.ts` if unsure.

- [ ] **Step 4: Add TierBadge next to each card title**

In each integration card's header (the existing label/title element), append:

```tsx
{plan !== "pro" && (
  <TierBadge tier={canUseIntegration("starter", integrationId) ? "starter" : "pro"} className="ml-2" />
)}
```

This keeps the badge visible when the user is below the required tier but hides it once they have access.

- [ ] **Step 5: TypeScript check**

Run from `ui/v3/`: `./node_modules/.bin/tsc --noEmit`
Expected: no output

- [ ] **Step 6: Commit**

```bash
git add ui/v3/components/phases/integrations-phase.tsx
git commit -m "$(cat <<'EOF'
feat(v3/integrations): tier-gate each integration card with LockedFeature + TierBadge

Free user → sees all 7 integrations, all wrapped in the ghost-state
overlay with an "Upgrade to Starter/Pro" CTA. Starter user → 4
integrations active, Stripe/custom-code/social still locked behind
Pro overlay. Pro user → all 7 active, no badges shown.

The integrations panel now serves the additional purpose of
demonstrating the value of paid tiers — "look at everything you'd get."

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase E — Pricing page restructure (credits-based, Pro rockstar)

### Task E1: Rewrite PRICING_TIERS data in welcome-phase.tsx

**Files:**
- Modify: `ui/v3/components/phases/welcome-phase.tsx` (PRICING_TIERS array around lines 182-220)

- [ ] **Step 1: Read the current PRICING_TIERS array**

Run: `sed -n '163,235p' ui/v3/components/phases/welcome-phase.tsx`
This shows the type definition + the three tier objects.

- [ ] **Step 2: Replace the array with the credits-based version**

Find the existing `const PRICING_TIERS: readonly PricingTier[] = [` block and replace through the closing `];` with:

```typescript
const PRICING_TIERS: readonly PricingTier[] = [
  {
    name: "Free",
    price: 0,
    pricePeriod: "forever",
    description: "Try Pebble. Build from a template, edit the look, share what you made.",
    highlights: [
      "5 credits/month",
      "Templates only (1 credit each)",
      "pebbleapp.ai subdomain",
      "Unlimited Canva-style edits",
    ],
    details: [
      { category: "Credits",     items: ["5 credits/month", "Hard cap 20", "Templates: 1 credit each", "Engine builds: not available"] },
      { category: "Hosting",     items: ["<your-name>.pebbleapp.ai subdomain", "\"Built with Pebble\" badge"] },
      { category: "Editing",     items: ["Visual click-to-edit (free)", "Color + style swaps (free)", "30 AI refinements/month"] },
      { category: "Integrations",items: ["—"] },
      { category: "Support",     items: ["Community forum"] },
    ],
  },
  {
    name: "Starter",
    price: 19.99,
    pricePeriod: "/mo",
    description: "Ready to make it real. Custom domain, real forms, the integrations you actually need.",
    highlights: [
      "100 credits/month",
      "~10 engine builds/month",
      "Custom domain",
      "WhatsApp, Booking, Maps integrations",
    ],
    details: [
      { category: "Credits",     items: ["100 credits/month", "Hard cap 400", "Engine builds: 10 credits each", "Templates: 1 credit each"] },
      { category: "Hosting",     items: ["Custom domain", "Pebble badge removable"] },
      { category: "Editing",     items: ["Everything in Free", "150 AI refinements/month", "Brand-extract from any URL"] },
      { category: "Integrations",items: ["WhatsApp button", "Booking link", "Google Maps", "Cookie consent banner"] },
      { category: "Forms",       items: ["Real email forms (Resend-backed)", "Lead inbox", "Auto-responder emails"] },
      { category: "Support",     items: ["48-hr email", "7-day money-back guarantee"] },
    ],
  },
  {
    name: "Pro",
    price: 49,
    pricePeriod: "/mo",
    description: "The full toolkit. Everything in Starter + Stripe Checkout, custom code, white-label, API access.",
    highlights: [
      "400 credits/month",
      "~40 engine builds/month",
      "Stripe Checkout on your site",
      "White-label + API access",
    ],
    details: [
      { category: "Credits",     items: ["400 credits/month", "Hard cap 400", "Unlimited brand-extract from URL", "Priority generation queue"] },
      { category: "Hosting",     items: ["Custom domain", "White-label (no Pebble badge)"] },
      { category: "Editing",     items: ["Everything in Starter", "400 AI refinements/month", "Drop-in section library"] },
      { category: "Integrations",items: ["Everything in Starter", "Stripe Checkout on your site", "Custom code blocks", "Social embeds"] },
      { category: "Analytics",   items: ["Per-site analytics", "Multi-site dashboard", "Referrer + top-paths breakdown"] },
      { category: "API",         items: ["Programmatic /v1/sites endpoint", "API key in settings"] },
      { category: "Support",     items: ["24-hr priority", "Monthly office hours with the team", "14-day money-back guarantee"] },
    ],
  },
];
```

- [ ] **Step 3: TypeScript check**

Run from `ui/v3/`: `./node_modules/.bin/tsc --noEmit`
Expected: no output

- [ ] **Step 4: Mark Pro as the rockstar in the render path**

Find where PRICING_TIERS.map(...) is called (likely a few hundred lines below the data). For the Pro card, add a "Most Popular" ribbon + 1.05x scale. Modify the per-tier render JSX to include:

```tsx
const isPro = tier.name === "Pro";
return (
  <motion.div
    key={tier.name}
    className={`relative ${isPro ? "scale-[1.04] z-10" : ""}`}
  >
    {isPro && (
      <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-primary text-primary-foreground text-[10px] font-bold uppercase tracking-widest z-20">
        Most popular
      </div>
    )}
    {/* ...existing card JSX... */}
  </motion.div>
);
```

(Adjust the surrounding map function exactly to match the existing structure — don't lose existing motion variants / props.)

- [ ] **Step 5: Commit**

```bash
git add ui/v3/components/phases/welcome-phase.tsx
git commit -m "$(cat <<'EOF'
feat(v3/pricing): credits-based tiers + Pro "Most popular" ribbon

2026-05-24 funnel restructure. Drop the "1 site / 5 sites / unlimited
sites" framing — credit cost per build IS the cap now. New layout:

  Free   $0/forever   5 credits/mo   templates only, no integrations
  Starter $19.99/mo   100 credits/mo  4 integrations, custom domain
  Pro    $49/mo      400 credits/mo  7 integrations incl. Stripe Checkout,
                                     white-label, API, priority support

Pro card scaled 1.04x with "Most popular" ribbon. Stripe Checkout
positioned as the headline Pro feature. Money-back guarantee per tier
(0/7/14 days) baked into the support row so trust signals don't need
a separate section.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase F — Template matcher endpoint + UI

### Task F1: Engine /api/template-match endpoint

**Files:**
- Create: `pebble/server/template_match.py`
- Modify: `pebble_engine.py` (route registration)
- Test: `tests/test_template_match.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_template_match.py
"""Phase F1 — /api/template-match scores templates against a free-text
prompt. Returns top-3 templates with confidence scores."""
import pytest
from pebble.server import template_match


def test_returns_top_3_for_clear_industry():
    """A clear industry prompt (e.g. 'tattoo shop in Brooklyn') should
    surface tattoo-/ink-themed templates ahead of unrelated ones."""
    result = template_match.match_templates(
        prompt="I run a tattoo shop in Brooklyn called Inked",
        business_type="tattoo_shop",
        max_results=3,
    )
    assert isinstance(result, dict)
    assert "matches" in result
    assert len(result["matches"]) <= 3
    # ink_studio template should appear (per the existing template
    # registry — see pebble/templates_registry.py).
    template_ids = [m["template_id"] for m in result["matches"]]
    assert "ink_studio" in template_ids


def test_returns_fallback_for_unknown_industry():
    """Garbage / out-of-vocabulary prompt → returns SOME results
    (gallery fallback), never empty, never errors."""
    result = template_match.match_templates(
        prompt="xyzzy plugh quux",
        business_type=None,
        max_results=3,
    )
    assert "matches" in result
    assert len(result["matches"]) <= 3
    # No assertion on which templates — just that the call didn't blow up
    # and returned the expected envelope.


def test_each_match_has_required_fields():
    result = template_match.match_templates(
        prompt="bakery in Queens",
        business_type="bakery",
        max_results=3,
    )
    for m in result["matches"]:
        assert "template_id" in m
        assert "score"       in m
        assert "reason"      in m
        assert 0.0 <= m["score"] <= 1.0


def test_max_results_respected():
    result = template_match.match_templates(
        prompt="dentist in San Diego",
        business_type="dentist",
        max_results=1,
    )
    assert len(result["matches"]) <= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_template_match.py -v`
Expected: ImportError on `from pebble.server import template_match` (file doesn't exist)

- [ ] **Step 3: Create the matcher**

```python
# pebble/server/template_match.py
"""Smart template matcher — Phase F1 (2026-05-24).

Given a free-text prompt + optional business_type, score every
template in pebble.templates_registry against the user's intent
and return the top-N matches. The funnel uses this after signup
to surface 3 templates instead of dumping the user into the full
gallery — sophistication that reduces bounce.

Scoring (cheap, deterministic, no LLM):
  1. business_type → template.applicable_industries direct match: +0.6
  2. industries.json keyword overlap (template tags vs prompt tokens): +0.3
  3. tier preference (free user → prefer "free" tier templates): +0.1

Tie-break by template name asc (deterministic test runs).

Optional LLM fallback (post-MVP): if top score < 0.4, send the prompt
to GPT-4o-mini (~$0.001) to extract intent then re-score. Not in v1
of the matcher — ship the deterministic version first.
"""
from __future__ import annotations

import re
from typing import Optional

from pebble.templates_registry import list_templates


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_TOKEN_RE.findall((text or "").lower()))


def _score_template(
    template: dict,
    prompt_tokens: set[str],
    business_type: Optional[str],
) -> tuple[float, str]:
    """Return (score, human-readable reason) for one template."""
    reasons: list[str] = []
    score = 0.0

    # Signal 1: business_type direct match against applicable_industries.
    if business_type:
        if business_type in template.get("applicable_industries", []):
            score += 0.6
            reasons.append(f"matches {business_type}")

    # Signal 2: token overlap between prompt and template tags/name/vibe.
    template_tokens = _tokens(
        " ".join([
            template.get("name", ""),
            template.get("tagline", ""),
            template.get("vibe", ""),
            " ".join(template.get("applicable_industries", [])),
        ])
    )
    overlap = prompt_tokens & template_tokens
    if overlap:
        overlap_score = min(0.3, 0.05 * len(overlap))
        score += overlap_score
        reasons.append(f"matches {len(overlap)} keyword(s)")

    # Signal 3: cheap bonus for free-tier templates so free users
    # always see a free option in the top 3.
    if template.get("tier") == "free":
        score += 0.1

    return (round(min(score, 1.0), 3), "; ".join(reasons) or "general match")


def match_templates(
    prompt: str,
    business_type: Optional[str] = None,
    max_results: int = 3,
) -> dict:
    """Score every template, return top-N. Never returns empty.

    Output shape:
      {
        "matches": [
          {"template_id": "ink_studio", "score": 0.85, "reason": "matches tattoo_shop; matches 2 keyword(s)"},
          ...
        ]
      }
    """
    templates = list_templates()
    prompt_tokens = _tokens(prompt or "")

    scored = []
    for t in templates:
        score, reason = _score_template(t, prompt_tokens, business_type)
        scored.append({
            "template_id": t["id"],
            "score":       score,
            "reason":      reason,
        })

    # Sort: high score first, ties broken by template_id asc.
    scored.sort(key=lambda m: (-m["score"], m["template_id"]))
    return {"matches": scored[:max_results]}


def handle_match(handler, body: dict) -> None:
    """Handle POST /api/template-match. Public endpoint (no auth)."""
    prompt = (body.get("prompt") or "").strip()
    business_type = (body.get("business_type") or "").strip() or None
    max_results = int(body.get("max_results") or 3)
    max_results = max(1, min(10, max_results))

    if not prompt:
        handler._json(400, {"error": "prompt is required"})
        return

    result = match_templates(prompt, business_type, max_results)
    handler._json(200, result)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_template_match.py -v`
Expected: 4 PASS

- [ ] **Step 5: Register the route in pebble_engine.py**

Find the route table in `pebble_engine.py` (search for `"/api/templates"` or `"/api/instantiate-template"` — the template-match route belongs near them). Add:

```python
elif path == "/api/template-match" and method == "POST":
    from pebble.server import template_match as _tm
    _tm.handle_match(self, body)
    return
```

(Replicate the EXACT registration style of the surrounding routes — don't invent a new pattern.)

- [ ] **Step 6: Smoke-test from curl**

Start the engine: `python pebble_engine.py --port 8765` (separate terminal)
Then:

```bash
curl -s -X POST http://127.0.0.1:8765/api/template-match \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "tattoo shop in Brooklyn called Inked", "business_type": "tattoo_shop"}' \
  | python -m json.tool
```

Expected: JSON with 3 matches, `ink_studio` in the list with score > 0.5.

- [ ] **Step 7: Commit**

```bash
git add pebble/server/template_match.py tests/test_template_match.py pebble_engine.py
git commit -m "$(cat <<'EOF'
feat(template-match): /api/template-match — deterministic top-3 template ranking

Scores every template against (prompt, business_type) via:
  - 0.6 if business_type ∈ applicable_industries
  - up to 0.3 for prompt-token / template-metadata overlap
  - 0.1 free-tier bonus so free users always see a free option in top 3

Deterministic, ~5ms response. Public route (no auth). LLM intent
extract fallback is post-MVP — deterministic version ships first
because it covers ~80% of cases at zero per-call cost.

The funnel uses this after signup to surface 3 templates instead of
dumping the user into the 10-template gallery — the sophistication
layer Marc asked for to reduce bounce.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task F2: v3 TemplateMatchModal — show top-3 suggestions

**Files:**
- Create: `ui/v3/components/template-match-modal.tsx`
- Create: `ui/v3/app/api/template-match/route.ts` (Next.js Route Handler proxy)
- Modify: `ui/v3/lib/api.ts` (add `matchTemplates` function)

- [ ] **Step 1: Add the TypeScript client function**

In `ui/v3/lib/api.ts`, near the other template-related functions (search for `listTemplates`), add:

```typescript
// ---------- /api/template-match (Phase F1, 2026-05-24) --------------------

export type TemplateMatch = {
  template_id: string;
  score:       number;
  reason:      string;
};

export async function matchTemplates(
  prompt: string,
  business_type?: string,
  max_results: number = 3,
): Promise<{ matches: TemplateMatch[] }> {
  return postJSON("/api/template-match", { prompt, business_type, max_results });
}
```

- [ ] **Step 2: TypeScript check**

Run from `ui/v3/`: `./node_modules/.bin/tsc --noEmit`
Expected: no output

- [ ] **Step 3: Create the modal component**

```tsx
// ui/v3/components/template-match-modal.tsx
"use client";

/**
 * TemplateMatchModal — shown right after signup completes, before
 * the user lands on the workspace. Surfaces the 3 best-matched
 * templates for their prompt so the first interaction is "pick one"
 * instead of "stare at a blank workspace."
 *
 * Three CTAs:
 *   1. "Use this one" → POST /api/instantiate-template → /workspace/<slug>
 *   2. "See all templates" → router.push("/templates")
 *   3. "Build from scratch (10 credits)" → only enabled for paid users;
 *      free users see this disabled with a TierBadge hinting Starter.
 *
 * Triggered by the workspace shell on first mount when:
 *   - sessionStorage has pebble.first_signup_prompt = "<the prompt>"
 *   - AND a flag pebble.template_match_seen is NOT set
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, X } from "lucide-react";
import { matchTemplates, listTemplates, instantiateTemplate, type TemplateMatch, type TemplateSummary } from "@/lib/api";
import { TierBadge } from "@/components/tier-badge";
import { getBrief } from "@/lib/state";
import type { Brief } from "@/lib/state";
import type { PlanTier } from "@/lib/plan-features";

export type TemplateMatchModalProps = {
  open:  boolean;
  prompt: string;
  plan:   PlanTier;
  onClose: () => void;
  onUsed:  (slug: string) => void;
};

export function TemplateMatchModal({ open, prompt, plan, onClose, onUsed }: TemplateMatchModalProps) {
  const router = useRouter();
  const [matches, setMatches] = useState<Array<TemplateMatch & { details: TemplateSummary }>>([]);
  const [loading, setLoading] = useState(true);
  const [instantiating, setInstantiating] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    setLoading(true);
    void (async () => {
      try {
        const brief = getBrief();
        const [m, all] = await Promise.all([
          matchTemplates(prompt, (brief.business_type as string) || undefined, 3),
          listTemplates(),
        ]);
        if (cancelled) return;
        const enriched = m.matches
          .map((match) => {
            const details = all.templates.find((t) => t.id === match.template_id);
            return details ? { ...match, details } : null;
          })
          .filter(Boolean) as Array<TemplateMatch & { details: TemplateSummary }>;
        setMatches(enriched);
      } catch {
        if (!cancelled) setMatches([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [open, prompt]);

  async function handleUse(templateId: string) {
    setInstantiating(templateId);
    try {
      const brief = getBrief();
      const result = await instantiateTemplate(templateId, brief as Brief);
      onUsed(result.slug);
    } catch (e) {
      console.error("instantiate failed:", e);
      setInstantiating(null);
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, y: 16, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.98 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-3xl bg-card border border-border rounded-2xl shadow-2xl overflow-hidden p-7"
          >
            <button
              type="button"
              onClick={onClose}
              className="absolute top-3 right-3 p-1.5 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="text-center mb-6">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary/10 text-primary text-[10px] uppercase tracking-widest font-bold">
                <Sparkles className="w-3 h-3" /> Matched for you
              </div>
              <h2 className="text-2xl md:text-3xl font-extrabold text-foreground mt-3 tracking-tight">
                Three templates for your business
              </h2>
              <p className="text-sm text-muted-foreground mt-2 max-w-md mx-auto">
                Start with one of these. You can customize colors, copy, photos — all without spending credits.
              </p>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[0, 1, 2].map((i) => (
                  <div key={i} className="aspect-[4/3] bg-muted/50 rounded-xl animate-pulse" />
                ))}
              </div>
            ) : matches.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-sm text-muted-foreground mb-4">No exact matches — browse the full gallery instead.</p>
                <button
                  type="button"
                  onClick={() => { onClose(); router.push("/templates"); }}
                  className="px-4 py-2 rounded-full bg-primary text-primary-foreground text-sm font-bold"
                >
                  See all templates
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {matches.map((m) => (
                  <div key={m.template_id} className="bg-background border border-border rounded-xl overflow-hidden flex flex-col">
                    <div className="aspect-[4/3] bg-muted/50 relative overflow-hidden">
                      {m.details.preview_image && (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={m.details.preview_image} alt={m.details.name} className="w-full h-full object-cover" />
                      )}
                    </div>
                    <div className="p-3 flex-1 flex flex-col">
                      <p className="text-sm font-bold text-foreground">{m.details.name}</p>
                      <p className="text-[11px] text-muted-foreground mt-0.5">{m.details.tagline}</p>
                      <button
                        type="button"
                        onClick={() => handleUse(m.template_id)}
                        disabled={instantiating !== null}
                        className="mt-auto w-full mt-3 px-3 py-2 rounded-full bg-primary text-primary-foreground text-xs font-bold disabled:opacity-50"
                      >
                        {instantiating === m.template_id ? "Building…" : "Use this one (1 credit)"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="mt-6 flex items-center justify-center gap-4 text-xs">
              <button
                type="button"
                onClick={() => { onClose(); router.push("/templates"); }}
                className="text-primary font-bold hover:underline"
              >
                See all templates
              </button>
              <span className="text-muted-foreground">·</span>
              <button
                type="button"
                disabled={plan === "free"}
                onClick={() => { onClose(); /* shell will trigger the full build */ }}
                className="text-muted-foreground disabled:cursor-not-allowed hover:text-foreground disabled:hover:text-muted-foreground inline-flex items-center gap-1.5"
              >
                Build from scratch (10 credits)
                {plan === "free" && <TierBadge tier="starter" />}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

- [ ] **Step 4: TypeScript check**

Run from `ui/v3/`: `./node_modules/.bin/tsc --noEmit`
Expected: no output

- [ ] **Step 5: Commit**

```bash
git add ui/v3/components/template-match-modal.tsx ui/v3/lib/api.ts
git commit -m "$(cat <<'EOF'
feat(v3): TemplateMatchModal — top-3 suggestions after signup

Shown right after a free user signs up, before they land on the
workspace. Fetches /api/template-match with their original prompt
(stashed in sessionStorage during the landing → signup hop) and
surfaces 3 hand-picked templates with "Use this one (1 credit)"
buttons. "See all templates" routes to the full gallery; "Build
from scratch (10 credits)" is disabled for free users with a
TierBadge cueing the upgrade.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task F3: Re-order funnel — wire TemplateMatchModal into workspace shell

**Files:**
- Modify: `ui/v3/components/phases/welcome-phase.tsx` (DetectiveInput submit handler — stash prompt before signup redirect)
- Modify: `ui/v3/components/workspace-shell.tsx` (mount TemplateMatchModal on first arrival if pebble.first_signup_prompt is set)

- [ ] **Step 1: Stash prompt to sessionStorage before signup redirect**

In `welcome-phase.tsx`, find where the unauthenticated user submits the Build prompt and gets routed to `/signup` (search for `router.push("/signup` or `pebble.autostart`). Right before the `router.push`, add:

```typescript
// 2026-05-24 funnel restructure: stash the prompt so the post-signup
// TemplateMatchModal can surface matching templates. Cleared after
// the modal renders (or after Build From Scratch fires).
sessionStorage.setItem("pebble.first_signup_prompt", brief.extra_context || "");
```

- [ ] **Step 2: Mount TemplateMatchModal in workspace-shell on first arrival**

In `workspace-shell.tsx`, add new state + effect near the existing plan-picker effect:

```typescript
import { TemplateMatchModal } from "@/components/template-match-modal";
import type { PlanTier } from "@/lib/plan-features";

// ...inside the component:
const [matchPrompt, setMatchPrompt] = useState<string | null>(null);
useEffect(() => {
  // Fire once per signup. The sessionStorage key is cleared as soon
  // as the modal mounts so a re-render doesn't re-open it.
  const stashed = sessionStorage.getItem("pebble.first_signup_prompt");
  if (stashed && stashed.trim()) {
    setMatchPrompt(stashed);
    sessionStorage.removeItem("pebble.first_signup_prompt");
  }
}, []);
```

In the JSX (alongside `<PaywallModal>` and `<PlanPickerModal>` at the bottom of the shell):

```tsx
<TemplateMatchModal
  open={matchPrompt !== null}
  prompt={matchPrompt || ""}
  plan={(subscription?.plan as PlanTier) || "free"}
  onClose={() => setMatchPrompt(null)}
  onUsed={(slug) => { setMatchPrompt(null); router.push(`/workspace/${slug}`); }}
/>
```

(Adjust `subscription` to whatever the shell already binds — if it doesn't currently track plan, fetch it via `fetchSubscription()` once on mount.)

- [ ] **Step 3: TypeScript check**

Run from `ui/v3/`: `./node_modules/.bin/tsc --noEmit`
Expected: no output

- [ ] **Step 4: Commit**

```bash
git add ui/v3/components/phases/welcome-phase.tsx ui/v3/components/workspace-shell.tsx
git commit -m "$(cat <<'EOF'
feat(v3/funnel): wire TemplateMatchModal — post-signup template match flow

Anonymous prompt-and-build → signup → land on /workspace → TemplateMatchModal
opens with top-3 templates for the stashed prompt. User picks one
(1 credit, instant build) or sees all templates / builds from
scratch (10 credits, gated to starter+).

Prompt is stashed to sessionStorage during the landing → signup
hop, read + cleared by the workspace shell on first arrival so it
never re-fires.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase G — First-build celebration screen + upgrade nudge

### Task G1: FirstBuildCelebration component

**Files:**
- Create: `ui/v3/components/first-build-celebration.tsx`
- Modify: `ui/v3/components/phases/ready-phase.tsx` (mount celebration on first build only)

- [ ] **Step 1: Create the celebration**

```tsx
// ui/v3/components/first-build-celebration.tsx
"use client";

/**
 * FirstBuildCelebration — confetti + upgrade-CTA shown when a free
 * user finishes their first build. The post-build dopamine spike is
 * the single highest-converting moment in the funnel — leverage it.
 *
 * Triggered by ReadyPhase when:
 *   - the just-built project is the user's first (project count == 1)
 *   - AND localStorage has NOT seen pebble.first_build_celebrated
 *
 * One-shot — sets the localStorage flag on first mount so a refresh
 * doesn't re-celebrate.
 */

import Link from "next/link";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, ArrowRight, X } from "lucide-react";
import { PebletMascot } from "@/components/peblet-mascot";

export type FirstBuildCelebrationProps = {
  open:    boolean;
  onClose: () => void;
};

export function FirstBuildCelebration({ open, onClose }: FirstBuildCelebrationProps) {
  const [showConfetti, setShowConfetti] = useState(false);

  useEffect(() => {
    if (open) {
      // Small delay so the modal animates in before confetti fires.
      const t = setTimeout(() => setShowConfetti(true), 300);
      return () => clearTimeout(t);
    }
  }, [open]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[110] bg-black/80 backdrop-blur-md flex items-center justify-center p-4"
          onClick={onClose}
        >
          {/* Confetti — pure CSS dots, 20 of them, randomized */}
          {showConfetti && (
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
              {Array.from({ length: 24 }).map((_, i) => (
                <motion.div
                  key={i}
                  initial={{ y: -20, x: `${Math.random() * 100}vw`, opacity: 0 }}
                  animate={{ y: "110vh", opacity: [0, 1, 1, 0] }}
                  transition={{ duration: 3 + Math.random() * 2, delay: Math.random() * 0.5, ease: "easeOut" }}
                  className="absolute w-3 h-3 rounded-full"
                  style={{
                    background: ["#3054ff", "#c76e3a", "#4b6548", "#5b6f4a", "#205661"][i % 5],
                  }}
                />
              ))}
            </div>
          )}

          <motion.div
            initial={{ opacity: 0, y: 16, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.98 }}
            transition={{ duration: 0.3 }}
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-md bg-card border border-border rounded-3xl shadow-2xl overflow-hidden"
          >
            <button
              type="button"
              onClick={onClose}
              className="absolute top-3 right-3 p-1.5 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground z-10"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="p-8 text-center bg-gradient-to-br from-primary/10 via-violet-500/5 to-amber-500/10">
              <PebletMascot size="lg" animate />
              <p className="text-[10px] uppercase tracking-widest font-bold text-primary mt-4">
                Built it. Shipped it.
              </p>
              <h2 className="text-3xl font-extrabold text-foreground mt-2 tracking-tight">
                Your first site is live!
              </h2>
              <p className="text-sm text-muted-foreground mt-3 max-w-sm mx-auto">
                You can keep editing this for free forever. When you're ready to make it real — custom domain, real form emails, integrations — Starter is $19.99/mo.
              </p>
            </div>

            <div className="p-6 space-y-2">
              <Link
                href="/pricing"
                className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-full bg-primary text-primary-foreground font-bold text-sm hover:opacity-95"
              >
                <Sparkles className="w-4 h-4" />
                See what Starter unlocks
                <ArrowRight className="w-4 h-4" />
              </Link>
              <button
                type="button"
                onClick={onClose}
                className="w-full py-2 text-xs font-semibold text-muted-foreground hover:text-foreground"
              >
                Keep editing
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

- [ ] **Step 2: Wire into ReadyPhase**

In `ui/v3/components/phases/ready-phase.tsx`, add at the top of the component body:

```typescript
import { FirstBuildCelebration } from "@/components/first-build-celebration";
import { listProjects } from "@/lib/api";

// ...inside component:
const [celebrating, setCelebrating] = useState(false);
useEffect(() => {
  if (typeof window === "undefined") return;
  if (localStorage.getItem("pebble.first_build_celebrated") === "1") return;
  // Only fire when this is genuinely the first build for the user.
  listProjects()
    .then((r) => {
      if (r.projects.length === 1) {
        setCelebrating(true);
        localStorage.setItem("pebble.first_build_celebrated", "1");
      }
    })
    .catch(() => { /* never block on this */ });
}, []);
```

In the JSX, at the bottom of the returned tree:

```tsx
<FirstBuildCelebration
  open={celebrating}
  onClose={() => setCelebrating(false)}
/>
```

- [ ] **Step 3: TypeScript check**

Run from `ui/v3/`: `./node_modules/.bin/tsc --noEmit`
Expected: no output

- [ ] **Step 4: Commit**

```bash
git add ui/v3/components/first-build-celebration.tsx ui/v3/components/phases/ready-phase.tsx
git commit -m "$(cat <<'EOF'
feat(v3): FirstBuildCelebration — confetti + upgrade CTA on first build

Mounts once per user (gated by both project count == 1 AND
localStorage sentinel). Confetti + Peblet mascot + "Your first
site is live!" headline + "See what Starter unlocks" primary CTA.

Highest-converting moment in any SaaS funnel is the post-success
dopamine spike — we leverage it instead of letting it pass quietly.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Final integration + push

### Task Z1: Run full test suite + commit + push to squitopest

- [ ] **Step 1: Run the full Python test suite**

Run: `python -m pytest -q`
Expected: ≥ 1998 PASS (1981 baseline + 8 from A1 + 9 from B1 + 4 from F1 = 2002 minimum), 0 FAIL

- [ ] **Step 2: TypeScript check**

Run from `ui/v3/`: `./node_modules/.bin/tsc --noEmit`
Expected: no output

- [ ] **Step 3: Push the entire branch to squitopest**

```bash
git push 2>&1 | tail -5
```

Expected: `phase56a-for-squitopest -> phase56a-for-squitopest` with the new commits enumerated.

- [ ] **Step 4: Verify on GitHub**

Open `https://github.com/squitopest/pebble-engine/commits/phase56a-for-squitopest` and confirm the funnel commits appear in order.

- [ ] **Step 5: Hand off to Marc with a manual smoke-test checklist**

Write a short message to Marc covering:
- Free user signup flow: lands on TemplateMatchModal? ✓/✗
- Free user clicks integration card: sees LockedFeature overlay? ✓/✗
- Free user finishes first build: sees confetti? ✓/✗
- Pricing page reads as credits-based + Pro card has "Most popular" ribbon? ✓/✗

---

## Self-Review

**Spec coverage check:**

| Spec item | Phase / Task | Status |
|---|---|---|
| Landing → Get Started Free → prompt | (existing) | ✓ already in welcome-phase |
| Prompt → create account | F3 (stash prompt to sessionStorage before signup redirect) | ✓ |
| Match template by industry/prompt | F1 + F2 (matcher + modal) | ✓ |
| Sophistication to reduce bounce | F1 (deterministic scorer with business_type signal) | ✓ |
| "Don't like this? More options!" | F2 (modal has "See all templates" link) | ✓ |
| Buy credits / start building | F2 (modal has "Build from scratch (10 credits)" — gated) | ✓ |
| Canva edits only if no purchase | (existing) — visual-edit endpoint is already free | ✓ no work needed |
| Free tier no integrations | A1 + B1 (PLAN_LIMITS + endpoint gate) | ✓ |
| Free is entry-level, $19.99/mo for more | A1 + E1 (tier limits + pricing UI) | ✓ |
| Move integrations to integrations page so it looks like we have more | D1 (gated cards, not hidden) | ✓ |
| "Pro Feature" / "Starter Feature" hints throughout | C1 (TierBadge) + D1 (integration cards use it) | ✓ |
| Drop 1/5/unlimited sites framing | A1 (cap → -1) + E1 (UI rewrite) | ✓ |
| Make pricing about credits | E1 (PRICING_TIERS rewrite) | ✓ |
| Make Pro the rockstar | E1 (Most popular ribbon + 1.04x scale + Stripe Checkout headline) | ✓ |
| Stripe Checkout = Pro feature | A1 (stripe_checkout: true only on pro) + E1 (listed under Pro integrations) | ✓ |
| First-build celebration | G1 | ✓ |
| Cart-abandon nudge | OUT OF SCOPE — separate plan (needs email automation infra) | deferred |
| Annual billing toggle | OUT OF SCOPE — needs Stripe annual Prices set up | deferred |

**Placeholder scan:** No TBD / TODO / "Add error handling" / "Similar to Task N" found.

**Type consistency:**
- `PlanTier` used consistently in `plan-features.ts`, `tier-badge.tsx`, `locked-feature.tsx`, `template-match-modal.tsx`, `workspace-shell.tsx` ✓
- `IntegrationId` defined once in `plan-features.ts`, imported elsewhere ✓
- `getFeature(plan, key)` signature consistent between Python and TS mirrors ✓
- Endpoint `/api/template-match` request body shape `{prompt, business_type, max_results}` matches between F1 server, F2 client ✓
- 402 envelope shape `{error, code, min_tier, message, upgrade_url}` from B1 matches what existing `CreditError` / PaywallModal expects (close — `min_tier` is new but the existing modal just shows the `message` field, so additive only) ✓

All checks pass.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-24-template-first-funnel.md`. Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Best for a 7-phase plan where each task is small and well-specified.

2. **Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints. Better if you want to watch each step.

Which approach? Or do you want me to ship a specific subset first (e.g. just Phase A+B+C for foundation, then approve before E-G UI work)?
