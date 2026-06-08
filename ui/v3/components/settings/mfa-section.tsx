"use client";

/**
 * MfaSection — TOTP enrollment + verify + disable flow inside the Security
 * tab. Phase D.1 (2026-05-24).
 *
 * Architecture:
 *   - Calls Supabase MFA SDK directly from the browser
 *     (supabase.auth.mfa.enroll / challenge / verify / unenroll / listFactors)
 *   - After verify or unenroll succeeds, posts to /api/account/mfa-event so
 *     the engine writes audit_log + sends the defensive-notify email
 *
 * Why client-driven instead of an engine endpoint:
 *   - Supabase requires the user's session JWT for these calls — it's the
 *     scope key for which-user-is-enrolling. Server-side would mean
 *     forwarding the JWT through the engine which adds a hop with no
 *     security benefit (engine already trusts the JWT it forwards).
 *   - Reduces engine surface area; failure modes are localized to one tab.
 */

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle, Loader2, ShieldCheck, ShieldOff } from "lucide-react";
import { type } from "@/lib/type";
import { useAuth } from "@/components/auth-provider";
import { createClient } from "@/lib/supabase/client";
import { ENGINE_BASE } from "@/lib/engine-base";

// ── state machine ────────────────────────────────────────────────────────────
//
// Five states, one at a time:
//   loading    — listFactors() hasn't returned yet
//   idle       — no MFA enrolled, button to start
//   enrolling  — QR code + secret + code input shown
//   enabled    — MFA on, disable button shown
//   disabling  — confirm-password gate (Phase D.3 — closes Phase A pattern)
//
// Using a discriminated union keeps the JSX branches small and lets
// TypeScript verify we render the right fields per phase.

type EnrollState =
  | { phase: "loading" }
  | { phase: "idle" }
  | { phase: "enrolling"; qrCode: string; secret: string; factorId: string }
  | { phase: "enabled"; factorId: string }
  | { phase: "disabling"; factorId: string };

async function recordMfaEvent(
  token: string,
  event_type: "mfa_enabled" | "mfa_disabled",
): Promise<void> {
  // Fire-and-forget — failure to log MUST NOT break the UX. The Supabase
  // SDK call already succeeded; the audit row is best-effort.
  try {
    await fetch(`${ENGINE_BASE}/api/account/mfa-event`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ event_type }),
    });
  } catch {
    // swallow — see comment above
  }
}

export function MfaSection() {
  const { user } = useAuth();
  const supabase = useMemo(() => createClient(), []);

  const [state, setState] = useState<EnrollState>({ phase: "loading" });
  const [code, setCode] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  // On mount: check if user already has an enrolled TOTP factor.
  // The SDK returns `data.totp` which contains only verified factors
  // (Supabase auth-js 2.105.4). `data.all` includes unverified too — we
  // surface those as "idle" so a half-finished enrollment can be retried
  // from scratch rather than getting stuck.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const { data, error } = await supabase.auth.mfa.listFactors();
        if (cancelled) return;
        if (error) {
          setError(error.message);
          setState({ phase: "idle" });
          return;
        }
        const verified = (data?.totp ?? []).find((f) => f.status === "verified");
        if (verified) {
          setState({ phase: "enabled", factorId: verified.id });
        } else {
          setState({ phase: "idle" });
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Couldn't load MFA state.");
          setState({ phase: "idle" });
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [supabase]);

  async function startEnroll() {
    setBusy(true);
    setError("");
    try {
      const { data, error } = await supabase.auth.mfa.enroll({
        factorType: "totp",
        friendlyName: `Pebble (${new Date().toISOString().slice(0, 10)})`,
      });
      if (error) {
        setError(error.message);
        return;
      }
      // data shape: { id, type, totp: { qr_code, secret, uri } }
      setState({
        phase: "enrolling",
        qrCode: data.totp.qr_code,
        secret: data.totp.secret,
        factorId: data.id,
      });
    } finally {
      setBusy(false);
    }
  }

  async function verifyAndEnable() {
    if (state.phase !== "enrolling") return;
    if (code.length !== 6) {
      setError("Enter the 6-digit code from your authenticator app.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const challenge = await supabase.auth.mfa.challenge({ factorId: state.factorId });
      if (challenge.error) {
        setError(challenge.error.message);
        return;
      }
      const verify = await supabase.auth.mfa.verify({
        factorId: state.factorId,
        challengeId: challenge.data.id,
        code,
      });
      if (verify.error) {
        setError("Wrong code. Double-check your authenticator app and try again.");
        return;
      }
      setState({ phase: "enabled", factorId: state.factorId });
      setCode("");

      // Notify the engine (audit log + defensive-notify email).
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (token) await recordMfaEvent(token, "mfa_enabled");
    } finally {
      setBusy(false);
    }
  }

  async function cancelEnroll() {
    if (state.phase !== "enrolling") return;
    setBusy(true);
    setError("");
    try {
      // The factor is still unverified; clean it up so the user can
      // start fresh next time they click "Enable".
      await supabase.auth.mfa.unenroll({ factorId: state.factorId });
      setState({ phase: "idle" });
      setCode("");
    } finally {
      setBusy(false);
    }
  }

  function startDisable() {
    if (state.phase !== "enabled") return;
    // Re-auth gate: typing the current password is the same anti-stolen-
    // session check used on /api/account/change-password. A compromised
    // session can't reach the stored credential, so this defeats the
    // common attack ("attacker has cookies, wants to disable MFA").
    setState({ phase: "disabling", factorId: state.factorId });
    setError("");
    setConfirmPassword("");
  }

  async function confirmDisable() {
    if (state.phase !== "disabling") return;
    if (!confirmPassword) {
      setError("Enter your current password to disable two-factor auth.");
      return;
    }
    if (!user?.email) {
      setError("Sign in again and try once more.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      // Re-auth via Supabase signInWithPassword. If the password is wrong,
      // we abort before unenrolling.
      const reauth = await supabase.auth.signInWithPassword({
        email: user.email,
        password: confirmPassword,
      });
      if (reauth.error) {
        setError("Current password is incorrect.");
        return;
      }
      // Now safe to unenroll.
      const { error } = await supabase.auth.mfa.unenroll({ factorId: state.factorId });
      if (error) {
        setError(error.message);
        return;
      }
      setState({ phase: "idle" });
      setConfirmPassword("");

      // Audit + email notify.
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (token) await recordMfaEvent(token, "mfa_disabled");
    } finally {
      setBusy(false);
    }
  }

  function cancelDisable() {
    if (state.phase !== "disabling") return;
    setState({ phase: "enabled", factorId: state.factorId });
    setConfirmPassword("");
    setError("");
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="rounded-2xl border border-border bg-card p-6 space-y-4"
    >
      <div className="flex items-center gap-2 text-foreground">
        <ShieldCheck className="w-5 h-5 text-muted-foreground" />
        <h2 className={`${type.dashboard.heading.l}`}>Two-factor authentication</h2>
      </div>
      <p className={`${type.body.s} text-muted-foreground`}>
        Adds a second login step using an app like Google Authenticator, 1Password, or
        Authy. Strongly recommended if your account handles customer data.
      </p>

      {state.phase === "loading" && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin" />
          Checking your two-factor settings…
        </div>
      )}

      {state.phase === "idle" && (
        <button
          type="button"
          onClick={startEnroll}
          disabled={busy}
          className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
          Enable two-factor
        </button>
      )}

      {state.phase === "enrolling" && (
        <div className="space-y-4 rounded-lg border border-border bg-background/40 p-4">
          <p className={`${type.body.s}`}>Scan this QR code with your authenticator app:</p>
          <div
            className="mx-auto w-48 rounded-md bg-white p-3"
            // The qr_code field is an SVG string returned by Supabase. It's
            // generated server-side and considered safe to inject — but we
            // still scope the injection to a known container so a future
            // shape change can't escape into the rest of the page.
            dangerouslySetInnerHTML={{ __html: state.qrCode }}
          />
          <details className={`${type.body.s} text-muted-foreground`}>
            <summary className="cursor-pointer">Can't scan? Enter this code manually:</summary>
            <code className="mt-1 block break-all rounded bg-muted/50 px-2 py-1 font-mono text-xs">
              {state.secret}
            </code>
          </details>
          <label className="block">
            <span className={`${type.label} text-muted-foreground`}>
              Enter the 6-digit code from your app
            </span>
            <input
              type="text"
              inputMode="numeric"
              maxLength={6}
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
              autoComplete="one-time-code"
              className="mt-1 w-32 rounded-lg border border-border bg-background px-3 py-2 font-mono text-lg tracking-widest text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </label>
          {error && (
            <p className={`${type.body.s} text-destructive`} role="alert">
              {error}
            </p>
          )}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={verifyAndEnable}
              disabled={busy || code.length !== 6}
              className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
              Verify + enable
            </button>
            <button
              type="button"
              onClick={cancelEnroll}
              disabled={busy}
              className="rounded-full border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-muted/50 disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {state.phase === "enabled" && (
        <div className="space-y-3">
          <div className="flex items-center justify-between rounded-lg border border-border bg-green-50 p-3 dark:bg-green-950/30">
            <div className="flex items-center gap-2 text-sm text-green-900 dark:text-green-200">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>Two-factor auth is on. You'll be asked for a code at sign-in.</span>
            </div>
            <button
              type="button"
              onClick={startDisable}
              disabled={busy}
              className="inline-flex items-center gap-1 rounded-full border border-destructive/50 px-3 py-1 text-xs font-medium text-destructive hover:bg-destructive/10 disabled:opacity-50"
            >
              <ShieldOff className="w-3 h-3" /> Disable
            </button>
          </div>
        </div>
      )}

      {state.phase === "disabling" && (
        <div className="space-y-4 rounded-lg border border-destructive/30 bg-destructive/5 p-4">
          <div>
            <p className={`${type.body.s} font-medium text-foreground`}>
              Disable two-factor authentication?
            </p>
            <p className={`${type.body.s} text-muted-foreground mt-1`}>
              You'll only be protected by your password after this. Enter your current
              password to confirm.
            </p>
          </div>
          <label className="block">
            <span className={`${type.label} text-muted-foreground`}>Current password</span>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              autoComplete="current-password"
              className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-destructive"
            />
          </label>
          {error && (
            <p className={`${type.body.s} text-destructive`} role="alert">
              {error}
            </p>
          )}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={confirmDisable}
              disabled={busy || !confirmPassword}
              className="inline-flex items-center gap-2 rounded-full bg-destructive px-4 py-2 text-sm font-medium text-destructive-foreground hover:bg-destructive/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldOff className="w-4 h-4" />}
              Disable two-factor
            </button>
            <button
              type="button"
              onClick={cancelDisable}
              disabled={busy}
              className="rounded-full border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-muted/50 disabled:opacity-50"
            >
              Keep two-factor on
            </button>
          </div>
        </div>
      )}

      {/* General error display for non-flow-specific errors (e.g. listFactors failed) */}
      {(state.phase === "loading" || state.phase === "idle") && error && (
        <p className={`${type.body.s} text-destructive`} role="alert">
          {error}
        </p>
      )}
    </motion.section>
  );
}
