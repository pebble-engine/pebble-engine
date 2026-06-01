# Launch-Readiness Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the launch-readiness gaps identified in the 2026-06-01 senior-dev brief — remove the retracted $99 setup call, enforce MFA step-up on billable/destructive project routes, surface plan-usage transparency, and plan managed-secret injection at publish.

**Architecture:** The engine already has the hard parts built — `_require_aal2_if_mfa_enrolled()` (correct no-lockout step-up logic) lives in `account.py`; `get_quota_summary()` lives in `user_plan.py`. Most work is *wiring existing primitives into more places* + thin frontend surfaces, not net-new subsystems. The one genuinely new subsystem (managed secrets) is deferred to a separate plan pending an owner design decision.

**Tech Stack:** Python 3.14 stdlib HTTP server, pytest, Next.js 14 / React / TypeScript / Tailwind (ui/v3).

**Re-baseline note (2026-06-01):** Legal pages (`/privacy`, `/terms`, `/dpa`) are already complete. Multi-tab project-state clobber is already solved via per-tab `sessionStorage`. JWT revocation is bounded to the ~1h access-token TTL (standard stateless-JWT tradeoff) — documented as accepted risk, not fixed here.

---

## File Structure

**Workstream A — Remove $99 setup call (cleanup)**
- Modify: `pebble-marketing/components/sections/Pricing.tsx` (remove the "Optional add-on" $99 block)
- Modify: `pebble-marketing/README.md:135` (component inventory line)
- Modify: `CLAUDE.md` (API ref caveat about setup-call)
- Modify: `PROJECT_PLAN.md` (mark 9.7 fully removed, drop "+$99" from pricing lines)

**Workstream B — MFA step-up on project routes (security)**
- Modify: `pebble/security.py` (add shared `require_aal2_if_mfa_enrolled(handler, user)` — extracted from account.py so all routes share one implementation)
- Modify: `pebble/server/account.py` (re-point its local `_require_aal2_if_mfa_enrolled` to the shared helper to avoid drift)
- Modify: `pebble/server/build.py` (gate `/api/generate`), `pebble/server/refine.py` (gate billable refinements), `pebble/server/publish.py` (gate publish), and the rollback handler
- Test: `tests/test_mfa_stepup.py` (new)

**Workstream C — Plan-usage transparency (UX)**
- Modify: `pebble/server/billing_subscription.py` (include `quota` from `get_quota_summary`)
- Test: `tests/test_billing_subscription.py` (extend or create)
- Modify: `ui/v3/lib/api.ts` (type the new `quota` field)
- Create: `ui/v3/components/workspace/plan-usage-badge.tsx`
- Modify: `ui/v3/components/workspace/dashboard-sidebar.tsx` (mount the badge)

**Workstream D — Managed secrets at publish (DEFERRED — see end)**

---

## Workstream A: Remove the $99 setup call

### Task A1: Strip the marketing pricing add-on

**Files:**
- Modify: `pebble-marketing/components/sections/Pricing.tsx` (the "Optional add-on / $99 one-time" block, ~lines 96-98)

- [ ] **Step 1: Read the surrounding component** to find the exact JSX node wrapping the $99 copy.

Run: `grep -n "99\|setup call\|Optional add-on" pebble-marketing/components/sections/Pricing.tsx`

- [ ] **Step 2: Remove the add-on block.** Delete the JSX element (and any now-empty wrapper) that renders "$99 one-time for a 30-minute setup call." Keep the three plan cards (Free / $29 / $59) intact.

- [ ] **Step 3: Build-check the marketing app** (or typecheck) to confirm no dangling references.

Run: `cd pebble-marketing && npx tsc --noEmit` (expected: no errors referencing Pricing.tsx)

- [ ] **Step 4: Commit**

```bash
git add pebble-marketing/components/sections/Pricing.tsx
git commit -m "remove(marketing): strike retracted \$99 setup-call add-on from pricing"
```

### Task A2: Scrub the docs

**Files:**
- Modify: `pebble-marketing/README.md:135`
- Modify: `CLAUDE.md` (line ~298, the `*Setup-call ($99 one-time) flow is on the backlog*` caveat)
- Modify: `PROJECT_PLAN.md` (lines ~30, ~138, ~282-296, ~301)

- [ ] **Step 1:** In `pebble-marketing/README.md:135`, change the inventory line `Pricing.tsx  Free / $29 / $59 + $99 setup call` → `Pricing.tsx  Free / $29 / $59`.

- [ ] **Step 2:** In `CLAUDE.md`, delete the sentence `*Setup-call ($99 one-time) flow is on the backlog — not yet wired.*` (the feature is retracted, not backlogged).

- [ ] **Step 3:** In `PROJECT_PLAN.md`, update item 9.7 to state the setup-call product is fully removed (not just retracted from active surface), and drop "+ $99 setup call" from the two pricing description lines.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md PROJECT_PLAN.md pebble-marketing/README.md
git commit -m "docs: remove \$99 setup-call references (feature retracted)"
```

---

## Workstream B: MFA step-up on billable/destructive project routes

**Context:** `account.py` already has `_require_aal2_if_mfa_enrolled(handler, token, user)` (lines 115-147) with the CORRECT logic: it only requires AAL2 when the user has a *verified* MFA factor enrolled, so non-MFA users are never locked out. We extract a shared version into `security.py` and wire it into the routes a stolen AAL1 token must not reach: `/api/generate` (spends money), `/api/refine` (billable), `/api/publish` (puts a site live), `/api/rollback` (destructive).

### Task B1: Add shared step-up helper to security.py

**Files:**
- Modify: `pebble/security.py` (add `require_aal2_if_mfa_enrolled`)
- Test: `tests/test_mfa_stepup.py` (Create)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_mfa_stepup.py
import pytest
from pebble.security import require_aal2_if_mfa_enrolled


class FakeHandler:
    def __init__(self):
        self.status = None
        self.json_body = None
    def _json(self, status, payload):
        self.status = status
        self.json_body = payload


def _user(factors=None):
    return {"id": "u1", "email": "a@b.co", "factors": factors or []}


def test_no_mfa_factors_allows_aal1(monkeypatch):
    """A user with no enrolled MFA factor passes regardless of AAL."""
    monkeypatch.setattr("pebble.security.get_aal", lambda t: "aal1")
    h = FakeHandler()
    assert require_aal2_if_mfa_enrolled(h, "tok", _user(factors=[])) is True
    assert h.status is None  # no error written


def test_enrolled_mfa_with_aal2_allows(monkeypatch):
    monkeypatch.setattr("pebble.security.get_aal", lambda t: "aal2")
    h = FakeHandler()
    user = _user(factors=[{"status": "verified", "factor_type": "totp"}])
    assert require_aal2_if_mfa_enrolled(h, "tok", user) is True
    assert h.status is None


def test_enrolled_mfa_with_aal1_rejects_401(monkeypatch):
    """Stolen AAL1 token must not reach the route when MFA is enrolled."""
    monkeypatch.setattr("pebble.security.get_aal", lambda t: "aal1")
    h = FakeHandler()
    user = _user(factors=[{"status": "verified", "factor_type": "totp"}])
    assert require_aal2_if_mfa_enrolled(h, "tok", user) is False
    assert h.status == 401
    assert h.json_body.get("aal_required") == "aal2"


def test_unverified_factor_does_not_trigger_stepup(monkeypatch):
    """An unverified (pending-enrollment) factor must NOT lock out aal1."""
    monkeypatch.setattr("pebble.security.get_aal", lambda t: "aal1")
    h = FakeHandler()
    user = _user(factors=[{"status": "unverified", "factor_type": "totp"}])
    assert require_aal2_if_mfa_enrolled(h, "tok", user) is True
    assert h.status is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_mfa_stepup.py -q`
Expected: FAIL — `ImportError: cannot import name 'require_aal2_if_mfa_enrolled'`

- [ ] **Step 3: Implement in security.py**

Add near the top of `pebble/security.py` (after the imports), a module-level import of `get_aal`:

```python
# at module import section
from pebble.auth_admin import get_aal  # AAL claim reader (no network)
```

Then add the function in the "Project ownership" section:

```python
def require_aal2_if_mfa_enrolled(handler, token: str, user: dict) -> bool:
    """Step-up auth guard for billable/destructive routes.

    Returns True (allow) when the request may proceed. Writes 401 and
    returns False ONLY when the user has a verified MFA factor enrolled
    but presented an AAL1 token — i.e. a session that pre-dates MFA
    enrollment or a stolen pre-MFA token.

    Crucially, users with NO verified MFA factor always pass: AAL1 is the
    correct, maximum assurance level for them, so gating on AAL2 globally
    would lock them out. This mirrors the per-endpoint guard in
    ``pebble/server/account.py`` — kept here so generate/refine/publish/
    rollback share one implementation and can't drift.
    """
    verified_factors = [
        f for f in (user.get("factors") or [])
        if isinstance(f, dict) and f.get("status") == "verified"
    ]
    if not verified_factors:
        return True
    if get_aal(token) == "aal2":
        return True
    handler._json(401, {
        "error": (
            "This action requires multi-factor authentication. "
            "Please sign in again using your authenticator app."
        ),
        "aal_required": "aal2",
    })
    return False
```

Add `"require_aal2_if_mfa_enrolled"` to `__all__`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_mfa_stepup.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add pebble/security.py tests/test_mfa_stepup.py
git commit -m "feat(security): shared MFA step-up guard for billable/destructive routes"
```

### Task B2: Point account.py at the shared helper

**Files:**
- Modify: `pebble/server/account.py:115-147`

- [ ] **Step 1:** Replace the body of the local `_require_aal2_if_mfa_enrolled(handler, token, user)` with a delegation to the shared one, preserving the existing call signature so all call sites stay unchanged:

```python
def _require_aal2_if_mfa_enrolled(handler, token: str, user: dict) -> bool:
    """Thin wrapper — delegates to the canonical implementation in
    pebble.security so account + project routes share one guard."""
    from pebble.security import require_aal2_if_mfa_enrolled
    return require_aal2_if_mfa_enrolled(handler, token, user)
```

- [ ] **Step 2: Run the account tests to confirm no regression**

Run: `python -m pytest tests/test_account_data_export.py tests/test_account_email_change.py -q`
Expected: same pass/fail baseline as before the change (network-dependent failures unchanged; no NEW failures).

- [ ] **Step 3: Commit**

```bash
git add pebble/server/account.py
git commit -m "refactor(account): delegate MFA step-up to shared security helper"
```

### Task B3: Wire step-up into /api/generate, /api/refine, /api/publish, /api/rollback

**Files:**
- Modify: `pebble/server/build.py` (generate path — after the user is resolved)
- Modify: `pebble/server/refine.py` (billable branch only)
- Modify: `pebble/server/publish.py`
- Modify: the rollback handler (`pebble/server/projects.py` or wherever `/api/rollback` lands)

**Pattern for each route** (the user dict + bearer token must both be available; `require_user`/`require_project_owner` already resolve the user — capture the token via the existing bearer-extraction):

- [ ] **Step 1:** For each route, locate where the caller is authenticated (e.g. `require_user(handler)` or `require_project_owner(handler, slug)` returns the uid/user). Extract the bearer token (same `_bearer(handler)` pattern used in account.py — strip `Authorization: Bearer `).

- [ ] **Step 2:** Immediately after auth succeeds and BEFORE the billable/destructive work, insert:

```python
# MFA step-up: a stolen AAL1 token must not spend money / mutate a live
# site even within the access-token TTL. No-op for users without MFA.
from pebble.security import require_aal2_if_mfa_enrolled
if not require_aal2_if_mfa_enrolled(handler, token, user):
    return  # 401 already written
```

For routes that only have the uid (not the full user dict), fetch the user dict via `require_user` (which returns it) instead of `resolve_user_id`. Where a route currently uses `require_project_owner` (returns uid only), add a `require_user` call to obtain the `factors` list, or extend `require_project_owner` to return the user dict — choose the smaller diff per route.

- [ ] **Step 3: Write/extend an integration-style test** asserting that, with a mocked user carrying a verified factor + AAL1 token, each route returns 401 before doing work; with AAL2 (or no factor) it proceeds. Mirror the FakeHandler pattern from `tests/test_refine_llm.py`.

- [ ] **Step 4: Run the affected route tests**

Run: `python -m pytest tests/test_refine_llm.py tests/test_mfa_stepup.py -q`
Expected: PASS (no new failures vs baseline)

- [ ] **Step 5: Commit**

```bash
git add pebble/server/build.py pebble/server/refine.py pebble/server/publish.py pebble/server/projects.py tests/
git commit -m "feat(security): enforce MFA step-up on generate/refine/publish/rollback"
```

---

## Workstream C: Plan-usage transparency

**Context:** `get_quota_summary(user_id)` already returns `{plan, limits, usage: {ai_refinements_this_month}}`. The `/api/billing/subscription` endpoint's docstring claims it's "for the subscription response" but the handler does NOT currently include it. We add it, then surface "X of N refinements used this month" in the workspace sidebar.

### Task C1: Include quota in the subscription endpoint

**Files:**
- Modify: `pebble/server/billing_subscription.py:60-97`
- Test: `tests/test_billing_subscription.py` (Create or extend)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_billing_subscription.py
import json
from pebble.server import billing_subscription as bs


class FakeHandler:
    def __init__(self, headers=None):
        self.headers = headers or {"Authorization": "Bearer tok"}
        self.status = None
        self.json_body = None
    def _json(self, status, payload):
        self.status = status
        self.json_body = payload


def test_subscription_includes_quota(monkeypatch):
    monkeypatch.setattr(bs, "require_user", lambda h: {"id": "u1", "email": "a@b.co"})
    monkeypatch.setattr(bs, "_load_sentinel", lambda uid: {"plan": "starter", "status": "active", "current_period_end": 123})
    monkeypatch.setattr(
        "pebble.user_plan.get_quota_summary",
        lambda uid: {"plan": "starter", "limits": {"ai_refinements_per_month": 150}, "usage": {"ai_refinements_this_month": 12}},
    )
    h = FakeHandler()
    bs.run_get_subscription(h)
    assert h.status == 200
    assert h.json_body["plan"] == "starter"
    assert h.json_body["quota"]["usage"]["ai_refinements_this_month"] == 12
    assert h.json_body["quota"]["limits"]["ai_refinements_per_month"] == 150
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_billing_subscription.py::test_subscription_includes_quota -q`
Expected: FAIL — `KeyError: 'quota'`

- [ ] **Step 3: Implement** — in `run_get_subscription`, after computing `needs_pick` and before both `_json` responses, compute the quota and add it to BOTH response bodies:

```python
    quota = None
    try:
        from pebble.user_plan import get_quota_summary
        quota = get_quota_summary(user.get("id", ""))
    except Exception:
        quota = None
```

Add `"quota": quota,` to both the no-sentinel and the with-sentinel `_json` payloads.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_billing_subscription.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pebble/server/billing_subscription.py tests/test_billing_subscription.py
git commit -m "feat(billing): include plan quota + usage in /api/billing/subscription"
```

### Task C2: Type the quota field in v3 api client

**Files:**
- Modify: `ui/v3/lib/api.ts` (the subscription fetch around line 1381)

- [ ] **Step 1:** Locate the subscription response type. Add an optional `quota` field:

```typescript
export interface PlanQuota {
  plan: string;
  limits: Record<string, number | boolean | string[]>;
  usage: { ai_refinements_this_month: number };
}
// add `quota?: PlanQuota | null;` to the SubscriptionResponse interface
```

- [ ] **Step 2: Typecheck**

Run: `cd ui/v3 && npx tsc --noEmit`
Expected: no new errors.

- [ ] **Step 3: Commit**

```bash
git add ui/v3/lib/api.ts
git commit -m "feat(v3): type plan quota field on subscription response"
```

### Task C3: Build + mount the plan-usage badge

**Files:**
- Create: `ui/v3/components/workspace/plan-usage-badge.tsx`
- Modify: `ui/v3/components/workspace/dashboard-sidebar.tsx`

- [ ] **Step 1: Create the badge component.** It takes a `quota` prop and renders "N of M refinements used this month" with a thin progress bar. Free plan limit is 30; show plan name. Match the sidebar's existing Tailwind idiom (read `dashboard-sidebar.tsx:289-300` for the established style).

```tsx
"use client";
import type { PlanQuota } from "@/lib/api";

export function PlanUsageBadge({ quota }: { quota: PlanQuota | null | undefined }) {
  if (!quota) return null;
  const used = quota.usage?.ai_refinements_this_month ?? 0;
  const limitRaw = quota.limits?.ai_refinements_per_month;
  const limit = typeof limitRaw === "number" ? limitRaw : 0;
  const unlimited = limit === -1;
  const pct = unlimited || limit === 0 ? 0 : Math.min(100, Math.round((used / limit) * 100));
  return (
    <div className="px-3 py-2 text-xs text-[#1a1a1a]/70">
      <div className="flex justify-between mb-1">
        <span className="capitalize">{quota.plan} plan</span>
        <span>{unlimited ? `${used} used` : `${used} / ${limit}`}</span>
      </div>
      {!unlimited && (
        <div className="h-1 rounded bg-[#1a1a1a]/10 overflow-hidden">
          <div className="h-full bg-[#1a1a1a]/40" style={{ width: `${pct}%` }} />
        </div>
      )}
      <div className="mt-1 opacity-60">AI refinements this month</div>
    </div>
  );
}
```

- [ ] **Step 2:** In `dashboard-sidebar.tsx`, fetch the subscription (it may already fetch usage; reuse the pattern at line 110) and render `<PlanUsageBadge quota={subscription?.quota} />` near the existing usage block (~line 289).

- [ ] **Step 3: Typecheck + visually verify in the running app**

Run: `cd ui/v3 && npx tsc --noEmit`
Then load `http://127.0.0.1:3001/dashboard` and confirm the badge renders for a logged-in user.

- [ ] **Step 4: Commit**

```bash
git add ui/v3/components/workspace/plan-usage-badge.tsx ui/v3/components/workspace/dashboard-sidebar.tsx
git commit -m "feat(v3): plan-usage badge — AI refinements used this month"
```

---

## Workstream D: Managed secrets at publish (DEFERRED — owner decision required)

**Why deferred:** This is the only genuinely net-new subsystem and it stores *customer* third-party API keys (Resend) server-side. That is a security + liability decision the owner must make before any code lands. The injection point is known (`pebble/publish.py:_create_cloudflare_deployment`, ~line 493 — add an `env_vars` multipart field; Cloudflare Pages supports it). What's undecided:

1. **Storage model** — encrypted-at-rest per-project `secrets.json`, or push straight to Cloudflare and never persist locally? (Don't-persist is the lower-liability option.)
2. **Whose Resend key** — does the customer bring their own key (we just inject it), or does Pebble provide a shared/subaccount key and bill usage? (BYO-key = far less liability, matches the "no lock-in" positioning.)
3. **Where the user enters it** — a publish-time form field vs. a project settings panel.

**Recommendation to encode once decided:** BYO-key, never persisted locally — collect the Resend key in the publish modal, push it directly to the Cloudflare Pages deployment as an env var, discard from memory after the API call. This keeps Pebble out of the secret-custody business entirely. Write the full TDD plan after the owner picks.

---

## Self-Review

**Spec coverage:**
- Remove $99 → A1, A2 ✓
- MFA step-up → B1, B2, B3 ✓
- Plan-usage badge → C1, C2, C3 ✓
- Managed secrets → D (deferred with explicit decision gate) ✓
- Legal pages → already done (verify only, no task needed) ✓
- Multi-tab → already solved via sessionStorage (no task) ✓
- JWT revocation → accepted-risk, documented in re-baseline note ✓

**Placeholder scan:** B3 intentionally leaves the per-route token-extraction as "smaller diff per route" because the exact auth call differs (`require_user` vs `require_project_owner`); the pattern and the inserted guard code are fully specified. No TBDs in A or C.

**Type consistency:** `PlanQuota` interface (C2) matches the `get_quota_summary` shape (C1) — `plan`, `limits`, `usage.ai_refinements_this_month`. `require_aal2_if_mfa_enrolled(handler, token, user)` signature is identical across B1/B2/B3.
