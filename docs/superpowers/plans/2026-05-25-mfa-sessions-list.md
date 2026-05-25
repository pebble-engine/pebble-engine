# Phase D — MFA + Sessions List + Global Sign-Out Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add MFA TOTP enrollment + "logged-in devices" session list + "sign out everywhere" button to the Security tab. NLM ranked sessions list as "before-2K-MRR" priority and MFA as "before-20K-MRR" — Phase D ships both since the UI surfaces share the same Security tab and the engine wiring overlaps.

**Why now:** Trust+account-surface Phase A+B shipped tonight closed the password + email + audit + billing gaps. Phase D closes the remaining two account-takeover vectors: (a) stolen session not invalidated, (b) leaked password without second factor. Both are table-stakes when agencies/business accounts start signing on — and per NLM's earlier critique, Lovable + Base44 both ship MFA.

**Tech Stack:** Supabase Auth's native MFA API (`supabase.auth.mfa.enroll/verify/unenroll/listFactors`) — no third-party TOTP library needed. Sessions list via Supabase admin API (`/auth/v1/admin/users/<id>/sessions`). Global sign-out via `supabase.auth.signOut({ scope: 'global' })`.

---

## File Structure

| Path | Purpose |
|---|---|
| `ui/v3/components/settings/security/mfa-section.tsx` | **Create.** MFA enrollment + active-factor list + disable flow with re-auth challenge |
| `ui/v3/components/settings/security/sessions-section.tsx` | **Create.** Active-sessions table (device, IP, last seen, this-device flag) + revoke + "sign out everywhere" |
| `ui/v3/components/settings/security-tab.tsx` | Modify. Compose: existing password-change + new MFA + new sessions sections |
| `pebble/server/account_sessions.py` | **Create.** GET `/api/account/sessions` (list), DELETE `/api/account/sessions/<sid>` (revoke one), POST `/api/account/sessions/revoke-all` (global sign-out + audit log) |
| `pebble/server/router.py` | Modify. Register the 3 new routes. |
| `pebble/audit_log.py` | Already exists. Add new event_type constants for `mfa_enabled`, `mfa_disabled`, `mfa_challenge_failed`, `session_revoked`, `global_signout`. (Helper accepts any string — these are just documentation. No code change needed.) |
| `pebble/email.py` | Modify. Add `send_mfa_enabled_notification`, `send_global_signout_notification`. |
| `tests/test_account_sessions.py` | **Create.** E2E tests for sessions endpoints. |
| `tests/test_mfa_flow.py` | **Create.** Integration test — mocks Supabase MFA API. |

---

## Phase D.1 — MFA TOTP enrollment + verification

**Goal:** User clicks "Enable two-factor auth" → QR code shown → scans with authenticator app → enters 6-digit code → MFA enabled.

- [ ] **Step D.1.1: New component `mfa-section.tsx`**

```tsx
"use client";

import { useState, useEffect } from "react";
import { createBrowserClient } from "@supabase/ssr";
import { Loader2, CheckCircle, ShieldOff } from "lucide-react";

type EnrollState =
  | { phase: "idle" }
  | { phase: "enrolling"; qrCode: string; secret: string; factorId: string }
  | { phase: "verifying"; factorId: string }
  | { phase: "enabled"; factorId: string };

export function MfaSection() {
  const [state, setState] = useState<EnrollState>({ phase: "idle" });
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  );

  // On mount: check if user already has an enrolled factor
  useEffect(() => {
    supabase.auth.mfa.listFactors().then(({ data }) => {
      const verified = data?.totp?.find(f => f.status === "verified");
      if (verified) setState({ phase: "enabled", factorId: verified.id });
    });
  }, []);

  async function startEnroll() {
    setBusy(true);
    setError("");
    const { data, error } = await supabase.auth.mfa.enroll({ factorType: "totp" });
    setBusy(false);
    if (error) { setError(error.message); return; }
    setState({
      phase: "enrolling",
      qrCode: data.totp.qr_code,  // SVG string from Supabase
      secret: data.totp.secret,   // manual-entry fallback
      factorId: data.id,
    });
  }

  async function verifyAndEnable() {
    if (state.phase !== "enrolling") return;
    setBusy(true);
    setError("");
    const challenge = await supabase.auth.mfa.challenge({ factorId: state.factorId });
    if (challenge.error) { setError(challenge.error.message); setBusy(false); return; }
    const verify = await supabase.auth.mfa.verify({
      factorId: state.factorId,
      challengeId: challenge.data.id,
      code,
    });
    setBusy(false);
    if (verify.error) { setError("Wrong code. Double-check your authenticator app and try again."); return; }
    setState({ phase: "enabled", factorId: state.factorId });
    setCode("");
    // Notification email is sent server-side via the audit_log webhook
  }

  async function disable() {
    if (state.phase !== "enabled") return;
    // Future: require re-auth challenge here (Marc enters password before disabling MFA)
    if (!confirm("Disable two-factor auth? You'll only be protected by your password.")) return;
    setBusy(true);
    const { error } = await supabase.auth.mfa.unenroll({ factorId: state.factorId });
    setBusy(false);
    if (error) { setError(error.message); return; }
    setState({ phase: "idle" });
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-base font-medium">Two-factor authentication</h3>
        <p className="text-sm text-muted-foreground">
          Adds a second login step using an app like Google Authenticator or 1Password.
          Strongly recommended if you handle customer data.
        </p>
      </div>

      {state.phase === "idle" && (
        <button onClick={startEnroll} disabled={busy}
                className="rounded-md border bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-60">
          {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : "Enable two-factor"}
        </button>
      )}

      {state.phase === "enrolling" && (
        <div className="space-y-4 rounded-lg border p-4">
          <div className="text-sm">Scan this QR code with your authenticator app:</div>
          <div className="mx-auto w-48" dangerouslySetInnerHTML={{ __html: state.qrCode }} />
          <details className="text-xs text-muted-foreground">
            <summary className="cursor-pointer">Can't scan? Enter this code manually:</summary>
            <code className="mt-1 block break-all font-mono">{state.secret}</code>
          </details>
          <div>
            <label className="text-sm font-medium">Enter the 6-digit code from your app</label>
            <input
              type="text" inputMode="numeric" maxLength={6}
              value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
              className="mt-1 w-32 rounded-md border px-3 py-2 font-mono text-lg tracking-widest"
              autoComplete="one-time-code"
            />
          </div>
          <button onClick={verifyAndEnable} disabled={busy || code.length !== 6}
                  className="rounded-md border bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-60">
            {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : "Verify + enable"}
          </button>
        </div>
      )}

      {state.phase === "enabled" && (
        <div className="flex items-center justify-between rounded-lg border bg-green-50 p-3 dark:bg-green-950/30">
          <div className="flex items-center gap-2 text-sm">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <span>Two-factor auth is on. You'll be asked for a code at sign-in.</span>
          </div>
          <button onClick={disable} disabled={busy}
                  className="flex items-center gap-1 rounded-md border border-destructive/50 px-3 py-1 text-xs text-destructive hover:bg-destructive/10">
            <ShieldOff className="h-3 w-3" /> Disable
          </button>
        </div>
      )}

      {error && <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-3 text-sm text-destructive">{error}</div>}
    </div>
  );
}
```

- [ ] **Step D.1.2: Wire into security-tab.tsx**

Below the existing password-change section, add `<MfaSection />`.

- [ ] **Step D.1.3: Supabase Auth dashboard config**

Marc-only (no code): enable MFA in Supabase Dashboard → Authentication → Multi-Factor → enable TOTP factor.

- [ ] **Step D.1.4: Audit-log integration**

The MFA enable/disable flow is client-driven (Supabase JS SDK), so the audit-log write needs to happen via either:
  - **Webhook** (best): Supabase Auth → custom webhook (we'd build a new endpoint) → audit_log write
  - **Client-side fetch to engine** (simpler): right after `verifyAndEnable` succeeds, call POST `/api/account/audit` with `{event_type: 'mfa_enabled'}`. Requires a new minimal endpoint.

Pick the client-side fetch — simpler, ship now, can be replaced by webhook later.

```python
# New endpoint: POST /api/account/audit — client-side audit-log trigger
def run_record_audit_event(handler):
    """Client-side hook to log MFA enable / disable from v3.
    Auth-gated; event_type allow-list prevents arbitrary log spam."""
    user = require_user(handler)
    if not user: return

    ALLOWED = {"mfa_enabled", "mfa_disabled", "global_signout"}
    body = _read_json_body(handler)
    event_type = (body.get("event_type") or "").strip()
    if event_type not in ALLOWED:
        handler._json(400, {"error": "invalid event_type"}); return

    from pebble.audit_log import log_event_for_handler
    log_event_for_handler(
        handler=handler, user_id=user["id"],
        event_type=event_type,
        metadata=body.get("metadata") or {},
    )
    handler._json(200, {"ok": True})
```

- [ ] **Step D.1.5: Tests + commit**

---

## Phase D.2 — Sessions list + revoke

**Goal:** User sees a table of active sessions (device, IP, last seen) and can revoke individual ones or "sign out everywhere".

- [ ] **Step D.2.1: `pebble/server/account_sessions.py`**

```python
"""Account sessions endpoints — list, revoke one, revoke all.

Supabase's session model is opaque; the admin API exposes:
  GET    /auth/v1/admin/users/<id>/sessions
  DELETE /auth/v1/admin/users/<id>/sessions/<sid>
  POST   /auth/v1/admin/users/<id>/sessions/sign-out-all  (or similar)

This module wraps those + adds:
  - this-device-flag detection (compare session.user_agent + ip to request)
  - audit log integration (session_revoked / global_signout events)
  - sign-out-current-too on global revoke (don't leave the user
    half-signed-out in their current tab)
"""
from __future__ import annotations
# Full implementation: ~120 lines
```

- [ ] **Step D.2.2: `sessions-section.tsx`**

UI: table with columns (Device, IP, City [via simple IP geo, optional], Last seen, [revoke button if not current]). "Sign out of all other devices" CTA below.

- [ ] **Step D.2.3: Notification on global sign-out**

When a user clicks "Sign out everywhere", we send them an email (to their primary email): "We signed out X devices on Y. If this wasn't you, change your password now." — same defensive-notify pattern as password change.

- [ ] **Step D.2.4: Tests + commit**

---

## Phase D.3 — Re-auth challenge on MFA disable

Marc's audit caught the missing-reauth-on-password-change pattern. Same risk applies to disabling MFA — a stolen session shouldn't be able to disable the second factor.

- [ ] **Step D.3.1: Add current-password input to the MFA disable flow**

When user clicks "Disable" → show current-password input + "Confirm disable" button → POST to a new `/api/account/mfa-disable-confirm` endpoint that re-auths via `_reauth_user` (already in account.py from Phase A) → on success calls Supabase admin unenroll.

- [ ] **Step D.3.2: Tests + commit**

---

## Phase D.4 — Backup codes (optional, ship-before-20K-MRR)

If a user loses their authenticator phone, they're locked out. Standard solve: backup codes generated at enrollment time, single-use, displayed once.

Supabase Auth doesn't ship backup codes natively. Two options:
- **Build our own**: generate 10 single-use 8-char codes at enrollment, store hashed in Supabase. On login flow, accept either TOTP OR backup code. Each used code is invalidated.
- **Direct user to use Supabase's recovery email**: simpler, less control.

Recommend: defer until MFA usage > 10% of paid users. Until then, the recovery path is "email support, prove identity, we unenroll for them" — which is fine at our scale.

---

## Out of scope

- **SSO (SAML / OIDC)** — enterprise-only, defer until first paying agency
- **Passkeys (WebAuthn)** — Supabase doesn't support natively yet (as of Phase D ship)
- **Device fingerprinting / risk-based MFA** — overkill
- **SCIM provisioning** — only matters for big teams; defer until first agency with 10+ seats

---

## Self-Review

**1. Spec coverage:**
- ✅ MFA TOTP enrollment + verify + disable (D.1)
- ✅ Sessions list + per-session revoke + global sign-out (D.2)
- ✅ Re-auth challenge on MFA disable (D.3 — closes Phase A pattern hole)
- ⏸️ Backup codes deferred to D.4 (acceptable — recovery via support email until usage warrants it)

**2. Dependencies:**
- D.1 must ship before D.3 (D.3 protects D.1's disable flow)
- D.2 is independent — could ship before D.1 if priorities shift

**3. Risk callouts:**
- The client-side audit-log endpoint (D.1.4) is a new attack surface — a logged-in attacker could spam fake `mfa_enabled` events. The event_type allow-list mitigates but should still be rate-limited per-user (5/min seems right).
- Sessions list shows IPs — if a user's account is compromised, the attacker can see WHERE the legitimate user usually logs in from. Acceptable trade-off (the legitimate user benefits from seeing weird IPs).
- Global sign-out doesn't sign out the CURRENT tab by default — flip Supabase's `signOut({scope:'global'})` so it also kills the current session, then redirect to /auth/login. Otherwise UX is confusing.

---

## Execution Handoff

Plan complete. Two execution options:

**1. Subagent-Driven (recommended)** — Fresh subagent per task with two-stage review. Estimated 2-3 days of wall-clock.

**2. Inline** — Bigger commits, checkpoints between phases. Slower.

Recommend D.1 → D.3 → D.2 → D.4 (defer) ordering: ship MFA's enroll first, then its protective re-auth, then sessions, defer backup codes.
