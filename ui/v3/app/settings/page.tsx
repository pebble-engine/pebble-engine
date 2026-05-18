"use client";

/**
 * /settings — profile + account + password + billing.
 *
 * Four sections:
 *   1. Profile   — display name, timezone, avatar (DiceBear initials).
 *   2. Account   — email display, deletion scheduling/cancellation.
 *   3. Password  — change password via Supabase.
 *   4. Billing   — manage subscription via Stripe Customer Portal.
 *
 * Auth: redirects to /login if no signed-in user.
 */

import { Suspense, useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  CreditCard,
  Lock,
  Settings as SettingsIcon,
  User,
} from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { useAuth } from "@/components/auth-provider";
import {
  createCheckoutSession,
  fetchSubscription,
  openBillingPortal,
  type SubscriptionState,
} from "@/lib/api";
import { createClient } from "@/lib/supabase/client";

// ── types ─────────────────────────────────────────────────────────────────────

interface ProfileState {
  first_name: string | null;
  display_name: string | null;
  timezone: string;
  deletion_scheduled_for: string | null;
}

// ── helpers ───────────────────────────────────────────────────────────────────

const PLAN_LABEL: Record<string, string> = {
  starter: "Pebble Starter",
  pro:     "Pebble Pro",
};

function planBadge(sub: SubscriptionState | null): string {
  if (!sub || !sub.plan) return "No active subscription";
  const label = PLAN_LABEL[sub.plan] ?? sub.plan;
  if (sub.status === "canceled") return `${label} (canceled)`;
  if (sub.status && sub.status !== "active") return `${label} (${sub.status})`;
  if (sub.current_period_end) {
    const renews = new Date(sub.current_period_end * 1000);
    const formatted = renews.toLocaleDateString(undefined, {
      year: "numeric", month: "short", day: "numeric",
    });
    return `${label} — renews ${formatted}`;
  }
  return label;
}

/** DiceBear avatar URL — letter-initial avatar from any email seed. */
function avatarUrl(email: string): string {
  return `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(email)}&backgroundColor=f59e0b&textColor=ffffff&fontSize=40`;
}

// Common IANA timezones for the dropdown (covers ~95% of users).
const COMMON_TIMEZONES = [
  "UTC",
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "America/Phoenix",
  "America/Anchorage",
  "Pacific/Honolulu",
  "America/Toronto",
  "America/Vancouver",
  "America/Sao_Paulo",
  "America/Argentina/Buenos_Aires",
  "America/Mexico_City",
  "Europe/London",
  "Europe/Paris",
  "Europe/Berlin",
  "Europe/Madrid",
  "Europe/Rome",
  "Europe/Amsterdam",
  "Europe/Warsaw",
  "Europe/Kiev",
  "Europe/Moscow",
  "Asia/Dubai",
  "Asia/Karachi",
  "Asia/Kolkata",
  "Asia/Dhaka",
  "Asia/Bangkok",
  "Asia/Singapore",
  "Asia/Shanghai",
  "Asia/Tokyo",
  "Asia/Seoul",
  "Australia/Sydney",
  "Australia/Melbourne",
  "Pacific/Auckland",
];

// ── main component ────────────────────────────────────────────────────────────

function SettingsPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, loading } = useAuth();
  const supabase = useMemo(() => createClient(), []);

  const justCheckedOut = searchParams?.get("billing") === "updated";
  const testMode = searchParams?.get("test") === "1";

  // ── profile state ──────────────────────────────────────────────────────────
  const [profile, setProfile]         = useState<ProfileState | null>(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [firstName, setFirstName]     = useState("");
  const [displayName, setDisplayName] = useState("");
  const [timezone, setTimezone]       = useState("UTC");
  const [profileSaving, setProfileSaving]   = useState(false);
  const [profileSuccess, setProfileSuccess] = useState(false);
  const [profileError, setProfileError]     = useState<string | null>(null);

  // ── deletion state ─────────────────────────────────────────────────────────
  const [deletionScheduled, setDeletionScheduled] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm]   = useState("");
  const [deleteSubmitting, setDeleteSubmitting] = useState(false);
  const [deleteError, setDeleteError]       = useState<string | null>(null);
  const [cancelSubmitting, setCancelSubmitting] = useState(false);

  // ── password state ─────────────────────────────────────────────────────────
  const [pw, setPw]               = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [pwError, setPwError]     = useState<string | null>(null);
  const [pwSuccess, setPwSuccess] = useState(false);
  const [pwSubmitting, setPwSubmitting] = useState(false);

  // ── billing state ──────────────────────────────────────────────────────────
  const [billingError, setBillingError]     = useState<string | null>(null);
  const [billingLoading, setBillingLoading] = useState(false);
  const [subscription, setSubscription]     = useState<SubscriptionState | null>(null);
  const [subLoading, setSubLoading]         = useState(true);

  // ── auth redirect ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (!loading && !user) router.replace("/login?next=/settings");
  }, [loading, user, router]);

  // ── load profile ───────────────────────────────────────────────────────────
  const loadProfile = useCallback(async () => {
    if (!user) return;
    try {
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (!token) return;
      const res = await fetch("/api/account/profile", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return;
      const p: ProfileState = await res.json();
      setProfile(p);
      setFirstName(p.first_name ?? "");
      setDisplayName(p.display_name ?? "");
      setTimezone(p.timezone ?? "UTC");
      setDeletionScheduled(p.deletion_scheduled_for ?? null);
    } catch {
      // non-fatal
    } finally {
      setProfileLoading(false);
    }
  }, [user, supabase]);

  useEffect(() => {
    if (!loading && user) loadProfile();
  }, [loading, user, loadProfile]);

  // ── load subscription ──────────────────────────────────────────────────────
  useEffect(() => {
    if (loading || !user) return;
    let cancelled = false;
    let timerId: ReturnType<typeof setTimeout> | null = null;
    const maxAttempts = justCheckedOut ? 8 : 1;

    function sleep(ms: number): Promise<void> {
      return new Promise((resolve) => {
        timerId = setTimeout(() => { timerId = null; resolve(); }, ms);
      });
    }

    (async () => {
      for (let attempt = 0; attempt < maxAttempts && !cancelled; attempt++) {
        try {
          const sub = await fetchSubscription();
          if (cancelled) return;
          if (sub.plan) { setSubscription(sub); setSubLoading(false); return; }
          setSubscription(sub);
        } catch {
          if (cancelled) return;
          setSubscription(null);
        }
        if (attempt < maxAttempts - 1 && !cancelled) await sleep(1500);
      }
      if (!cancelled) setSubLoading(false);
    })();
    return () => { cancelled = true; if (timerId !== null) clearTimeout(timerId); };
  }, [loading, user, justCheckedOut]);

  // ── handlers ───────────────────────────────────────────────────────────────

  async function onSaveProfile(e: React.FormEvent) {
    e.preventDefault();
    setProfileError(null);
    setProfileSuccess(false);
    setProfileSaving(true);
    try {
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (!token) { setProfileError("Not authenticated."); return; }
      const res = await fetch("/api/account/profile", {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ first_name: firstName.trim() || null, display_name: displayName.trim() || null, timezone }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        setProfileError((err as { error?: string }).error || "Profile update failed.");
        return;
      }
      setProfileSuccess(true);
    } catch (err) {
      setProfileError(err instanceof Error ? err.message : "Profile update failed.");
    } finally {
      setProfileSaving(false);
    }
  }

  async function onChangePassword(e: React.FormEvent) {
    e.preventDefault();
    setPwError(null);
    setPwSuccess(false);
    if (pw.length < 8) { setPwError("Password must be at least 8 characters."); return; }
    if (pw !== confirmPw) { setPwError("Passwords don't match."); return; }
    setPwSubmitting(true);
    try {
      const { error } = await supabase.auth.updateUser({ password: pw });
      if (error) { setPwError(error.message); return; }
      setPw(""); setConfirmPw(""); setPwSuccess(true);
    } catch (err) {
      setPwError(err instanceof Error ? err.message : "Password update failed.");
    } finally {
      setPwSubmitting(false);
    }
  }

  async function onRequestDeletion() {
    setDeleteError(null);
    if (deleteConfirm.trim().toLowerCase() !== (user?.email ?? "").toLowerCase()) {
      setDeleteError("Email doesn't match. Type your email address to confirm.");
      return;
    }
    setDeleteSubmitting(true);
    try {
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (!token) { setDeleteError("Not authenticated."); return; }
      const res = await fetch("/api/account/delete", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      const body = await res.json().catch(() => ({}));
      if (body.deleted) {
        await supabase.auth.signOut();
        router.replace("/landing");
        return;
      }
      if (body.scheduled_for) setDeletionScheduled(body.scheduled_for);
      setDeleteConfirm("");
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : "Request failed.");
    } finally {
      setDeleteSubmitting(false);
    }
  }

  async function onCancelDeletion() {
    setCancelSubmitting(true);
    try {
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (!token) return;
      await fetch("/api/account/cancel-deletion", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      setDeletionScheduled(null);
    } catch {
      // non-fatal
    } finally {
      setCancelSubmitting(false);
    }
  }

  async function onStartCheckout(plan: "starter" | "pro") {
    setBillingError(null); setBillingLoading(true);
    try {
      const { url } = await createCheckoutSession(plan);
      window.location.href = url;
    } catch (err) {
      setBillingError(err instanceof Error ? err.message : "Couldn't start checkout.");
    } finally { setBillingLoading(false); }
  }

  async function onManageBilling() {
    setBillingError(null); setBillingLoading(true);
    try {
      const { url } = await openBillingPortal();
      window.location.href = url;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Couldn't open the billing portal.";
      setBillingError(/no active subscription/i.test(msg)
        ? "You don't have an active subscription yet. Choose a plan to get started."
        : msg);
    } finally { setBillingLoading(false); }
  }

  // ── shimmer ────────────────────────────────────────────────────────────────
  if (loading || !user) {
    return (
      <div className="min-h-screen flex flex-col">
        <TopNav projectName="Settings" />
        <main className="flex-1 px-6 py-12">
          <div className="max-w-2xl mx-auto">
            <div className="h-8 w-40 bg-muted rounded animate-pulse mb-8" />
            <div className="h-32 bg-muted/50 rounded-2xl animate-pulse" />
          </div>
        </main>
      </div>
    );
  }

  const deletionDate = deletionScheduled ? deletionScheduled.slice(0, 10) : null;

  return (
    <div className="min-h-screen flex flex-col">
      <TopNav projectName="Settings" />

      <main className="flex-1 px-6 py-12 md:py-16">
        <div className="max-w-2xl mx-auto space-y-10">

          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }} className="space-y-3"
          >
            <div className="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center">
              <SettingsIcon className="w-6 h-6" />
            </div>
            <h1 className="font-display text-3xl md:text-4xl font-bold tracking-tight text-foreground">
              Settings
            </h1>
            <p className="text-muted-foreground">
              Your profile, password, and billing in one place.
            </p>
          </motion.div>

          {/* ── Profile section ─────────────────────────────────────────────── */}
          <motion.section
            initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.03 }}
            className="rounded-2xl border border-border bg-card p-6 space-y-5"
          >
            <div className="flex items-center gap-2 text-foreground">
              <User className="w-5 h-5 text-muted-foreground" />
              <h2 className="font-display text-xl font-semibold">Profile</h2>
            </div>

            {/* Avatar + email */}
            <div className="flex items-center gap-4">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={avatarUrl(user.email ?? "")}
                alt="avatar"
                width={56} height={56}
                className="rounded-full border-2 border-border bg-muted"
              />
              <div>
                <p className="font-medium text-foreground">{user.email}</p>
                <p className="text-sm text-muted-foreground">Avatar generated from your email</p>
              </div>
            </div>

            {profileLoading ? (
              <div className="h-24 bg-muted/40 rounded-lg animate-pulse" />
            ) : (
              <form onSubmit={onSaveProfile} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <label className="block">
                    <span className="text-sm text-muted-foreground">First name</span>
                    <input
                      type="text"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                      placeholder="Jane"
                      maxLength={100}
                      className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </label>
                  <label className="block">
                    <span className="text-sm text-muted-foreground">Display name</span>
                    <input
                      type="text"
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      placeholder="Jane Smith"
                      maxLength={100}
                      className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </label>
                </div>
                <label className="block">
                  <span className="text-sm text-muted-foreground">Time zone</span>
                  <select
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    {COMMON_TIMEZONES.map((tz) => (
                      <option key={tz} value={tz}>{tz.replace(/_/g, " ")}</option>
                    ))}
                  </select>
                </label>
                {profileError && (
                  <p className="text-sm text-destructive" role="alert">{profileError}</p>
                )}
                {profileSuccess && (
                  <p className="text-sm text-primary" role="status">Profile saved.</p>
                )}
                <button
                  type="submit" disabled={profileSaving}
                  className="inline-flex items-center rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {profileSaving ? "Saving…" : "Save profile"}
                </button>
              </form>
            )}
          </motion.section>

          {/* ── Account section ──────────────────────────────────────────────── */}
          <motion.section
            initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.06 }}
            className="rounded-2xl border border-border bg-card p-6 space-y-4"
          >
            <div className="flex items-center gap-2 text-foreground">
              <User className="w-5 h-5 text-muted-foreground" />
              <h2 className="font-display text-xl font-semibold">Account</h2>
            </div>

            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Signed in as</p>
              <p className="text-foreground font-medium">{user.email}</p>
            </div>

            {/* Deletion scheduled banner */}
            {deletionDate && (
              <div className="flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/5 p-4">
                <AlertTriangle className="w-5 h-5 text-destructive shrink-0 mt-0.5" />
                <div className="flex-1 space-y-2">
                  <p className="text-sm text-destructive font-medium">
                    Account scheduled for deletion on {deletionDate}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    All your sites and data will be permanently removed. You can cancel this before that date.
                  </p>
                  <button
                    type="button"
                    onClick={onCancelDeletion}
                    disabled={cancelSubmitting}
                    className="text-sm font-medium text-primary hover:underline disabled:opacity-50"
                  >
                    {cancelSubmitting ? "Cancelling…" : "Cancel deletion"}
                  </button>
                </div>
              </div>
            )}

            {/* Delete account form (only shown when no deletion is scheduled) */}
            {!deletionDate && (
              <details className="group pt-2">
                <summary className="cursor-pointer text-sm text-destructive hover:underline list-none">
                  Delete my account
                </summary>
                <div className="mt-4 space-y-3 border-t border-border pt-4">
                  <p className="text-sm text-muted-foreground">
                    Type your email address to confirm. Your account will enter a{" "}
                    <strong>14-day cooling-off period</strong> — you can cancel anytime before it expires.
                    After that, all your data is permanently deleted.
                  </p>
                  <label className="block">
                    <span className="text-sm text-muted-foreground">{user.email}</span>
                    <input
                      type="email"
                      value={deleteConfirm}
                      onChange={(e) => setDeleteConfirm(e.target.value)}
                      placeholder={user.email ?? ""}
                      autoComplete="off"
                      className="mt-1 w-full rounded-lg border border-destructive/40 bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-destructive"
                    />
                  </label>
                  {deleteError && (
                    <p className="text-sm text-destructive" role="alert">{deleteError}</p>
                  )}
                  <button
                    type="button"
                    onClick={onRequestDeletion}
                    disabled={deleteSubmitting || deleteConfirm.trim() === ""}
                    className="inline-flex items-center rounded-full bg-destructive px-4 py-2 text-sm font-medium text-white hover:bg-destructive/90 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {deleteSubmitting ? "Scheduling…" : "Schedule account deletion"}
                  </button>
                </div>
              </details>
            )}
          </motion.section>

          {/* ── Password section ─────────────────────────────────────────────── */}
          <motion.section
            initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="rounded-2xl border border-border bg-card p-6 space-y-4"
          >
            <div className="flex items-center gap-2 text-foreground">
              <Lock className="w-5 h-5 text-muted-foreground" />
              <h2 className="font-display text-xl font-semibold">Change password</h2>
            </div>
            <form onSubmit={onChangePassword} className="space-y-3">
              <label className="block">
                <span className="text-sm text-muted-foreground">New password</span>
                <input
                  type="password" value={pw} onChange={(e) => setPw(e.target.value)}
                  required minLength={8} autoComplete="new-password"
                  className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </label>
              <label className="block">
                <span className="text-sm text-muted-foreground">Confirm new password</span>
                <input
                  type="password" value={confirmPw} onChange={(e) => setConfirmPw(e.target.value)}
                  required minLength={8} autoComplete="new-password"
                  className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </label>
              {pwError && <p className="text-sm text-destructive" role="alert">{pwError}</p>}
              {pwSuccess && (
                <p className="text-sm text-primary" role="status">
                  Password updated. You can keep using Pebble — no need to sign in again.
                </p>
              )}
              <button
                type="submit" disabled={pwSubmitting}
                className="inline-flex items-center rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {pwSubmitting ? "Updating…" : "Update password"}
              </button>
            </form>
          </motion.section>

          {/* ── Billing section ──────────────────────────────────────────────── */}
          <motion.section
            initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.15 }}
            className="rounded-2xl border border-border bg-card p-6 space-y-4"
          >
            <div className="flex items-center gap-2 text-foreground">
              <CreditCard className="w-5 h-5 text-muted-foreground" />
              <h2 className="font-display text-xl font-semibold">Billing</h2>
            </div>
            {subLoading && justCheckedOut ? (
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Current plan</p>
                <p className="text-muted-foreground italic">Syncing your subscription with Stripe…</p>
              </div>
            ) : !subLoading ? (
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Current plan</p>
                <p className="text-foreground font-medium">{planBadge(subscription)}</p>
              </div>
            ) : null}
            <p className="text-sm text-muted-foreground">
              Manage your plan, payment method, and download invoices. The
              billing portal is hosted by Stripe — Pebble never sees your card number.
            </p>
            {billingError && <p className="text-sm text-destructive" role="alert">{billingError}</p>}
            <div className="flex flex-wrap items-center gap-3">
              {subscription ? (
                <button
                  type="button" onClick={onManageBilling} disabled={billingLoading}
                  className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <CreditCard className="w-4 h-4" />
                  {billingLoading ? "Opening…" : "Manage billing"}
                </button>
              ) : (
                <Link
                  href="/pricing"
                  className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
                >
                  Choose a plan →
                </Link>
              )}
              <Link href="/dashboard" className="text-sm text-muted-foreground hover:text-foreground">
                Back to dashboard
              </Link>
            </div>

            {testMode && (
              <div className="mt-4 pt-4 border-t border-border space-y-3">
                <p className="text-xs uppercase tracking-wide text-muted-foreground font-semibold">Test mode</p>
                <p className="text-sm text-muted-foreground">
                  Drive a checkout end-to-end. Use Stripe's test card
                  <code className="mx-1 px-1 py-0.5 rounded bg-muted text-xs">4242 4242 4242 4242</code>
                  with any future expiry and CVC.
                </p>
                <div className="flex flex-wrap gap-3">
                  <button
                    type="button" onClick={() => onStartCheckout("starter")} disabled={billingLoading}
                    className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-4 py-2 text-sm font-medium text-foreground hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Subscribe (test) — Starter $29/mo
                  </button>
                  <button
                    type="button" onClick={() => onStartCheckout("pro")} disabled={billingLoading}
                    className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-4 py-2 text-sm font-medium text-foreground hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Subscribe (test) — Pro $59/mo
                  </button>
                </div>
              </div>
            )}
          </motion.section>

        </div>
      </main>
    </div>
  );
}


export default function SettingsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <SettingsPageContent />
    </Suspense>
  );
}
