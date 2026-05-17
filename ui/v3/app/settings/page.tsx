"use client";

/**
 * /settings — account + password + billing.
 *
 * Three small sections. Stays deliberately spare: this is Pebble, not a
 * SaaS admin console, so we don't surface dozens of toggles. Only the
 * things a real customer needs to do day-to-day.
 *
 *   1. Account — email display, GDPR delete link.
 *   2. Password — change password via Supabase.
 *   3. Billing — manage subscription via Stripe Customer Portal.
 *
 * Auth: redirects to /login if no signed-in user. The portal endpoint
 * itself is auth-gated server-side (require_user), but bouncing
 * unauthenticated visitors here avoids the embarrassing "click 'Manage
 * billing' → Not signed in" round trip.
 */

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { CreditCard, Lock, Settings as SettingsIcon, User } from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { useAuth } from "@/components/auth-provider";
import { fetchSubscription, openBillingPortal, type SubscriptionState } from "@/lib/api";
import { createClient } from "@/lib/supabase/client";


const PLAN_LABEL: Record<string, string> = {
  starter: "Pebble Starter",
  pro:     "Pebble Pro",
};


function planBadge(sub: SubscriptionState | null): string {
  if (!sub || !sub.plan) {
    return "No active subscription";
  }
  const label = PLAN_LABEL[sub.plan] ?? sub.plan;
  if (sub.status === "canceled") {
    return `${label} (canceled)`;
  }
  if (sub.status && sub.status !== "active") {
    return `${label} (${sub.status})`;
  }
  if (sub.current_period_end) {
    const renews = new Date(sub.current_period_end * 1000);
    const formatted = renews.toLocaleDateString(undefined, {
      year:  "numeric",
      month: "short",
      day:   "numeric",
    });
    return `${label} — renews ${formatted}`;
  }
  return label;
}


export default function SettingsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, loading } = useAuth();
  const supabase = useMemo(() => createClient(), []);

  // When Stripe redirects the user back after Checkout
  // (`/settings?billing=updated`), the webhook may not have fired yet —
  // it's async and can take 5-30 seconds. Without this flag the page
  // would render "No active subscription" for a user who literally just
  // paid. NLM round 3 R3.A1.
  const justCheckedOut = searchParams?.get("billing") === "updated";

  // ---- Password change state -----------------------------------------
  const [pw, setPw]               = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [pwError, setPwError]     = useState<string | null>(null);
  const [pwSuccess, setPwSuccess] = useState(false);
  const [pwSubmitting, setPwSubmitting] = useState(false);

  // ---- Billing portal state ------------------------------------------
  const [billingError, setBillingError]   = useState<string | null>(null);
  const [billingLoading, setBillingLoading] = useState(false);

  // ---- Current-plan badge --------------------------------------------
  const [subscription, setSubscription] = useState<SubscriptionState | null>(null);
  const [subLoading, setSubLoading]     = useState(true);

  // Bounce unauthenticated visitors to /login. Wait for the auth state
  // to finish loading so we don't redirect during the brief flicker
  // before the session hydrates.
  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login?next=/settings");
    }
  }, [loading, user, router]);

  // Fetch the current subscription state once we know who the user is.
  // Failures (network, 503) degrade gracefully to "no subscription" — the
  // portal button still works for users who have one.
  //
  // Post-checkout polling (justCheckedOut): the Stripe webhook is async.
  // If the user just paid, the sentinel may not exist yet when this page
  // mounts. Poll briefly with a "syncing" message rather than flashing
  // "No active subscription" at someone who literally just gave us money.
  //
  // NLM round 4 R4.1: the cleanup must actually CLEAR the pending
  // setTimeout, not just set a flag the loop will eventually notice.
  // StrictMode mounts the component twice in dev; without clearTimeout
  // both poll loops would run to completion in the background, leaking
  // a few network requests + timers per visit.
  useEffect(() => {
    if (loading || !user) return;
    let cancelled = false;
    let timerId: ReturnType<typeof setTimeout> | null = null;
    const maxAttempts = justCheckedOut ? 8 : 1;  // ~12s total when polling
    const intervalMs = 1500;

    function sleep(ms: number): Promise<void> {
      return new Promise((resolve) => {
        timerId = setTimeout(() => {
          timerId = null;
          resolve();
        }, ms);
      });
    }

    (async () => {
      for (let attempt = 0; attempt < maxAttempts && !cancelled; attempt++) {
        try {
          const sub = await fetchSubscription();
          if (cancelled) return;
          if (sub.plan) {
            setSubscription(sub);
            setSubLoading(false);
            return;
          }
          setSubscription(sub);
        } catch {
          if (cancelled) return;
          setSubscription(null);
        }
        if (attempt < maxAttempts - 1 && !cancelled) {
          await sleep(intervalMs);
        }
      }
      if (!cancelled) setSubLoading(false);
    })();
    return () => {
      cancelled = true;
      if (timerId !== null) clearTimeout(timerId);
    };
  }, [loading, user, justCheckedOut]);

  async function onChangePassword(e: React.FormEvent) {
    e.preventDefault();
    setPwError(null);
    setPwSuccess(false);
    if (pw.length < 8) {
      setPwError("Password must be at least 8 characters.");
      return;
    }
    if (pw !== confirmPw) {
      setPwError("Passwords don't match.");
      return;
    }
    setPwSubmitting(true);
    try {
      const { error } = await supabase.auth.updateUser({ password: pw });
      if (error) {
        setPwError(error.message);
        return;
      }
      setPw("");
      setConfirmPw("");
      setPwSuccess(true);
    } catch (err) {
      setPwError(err instanceof Error ? err.message : "Password update failed.");
    } finally {
      setPwSubmitting(false);
    }
  }

  async function onManageBilling() {
    setBillingError(null);
    setBillingLoading(true);
    try {
      const { url } = await openBillingPortal();
      // Redirect into Stripe's hosted portal. They'll bounce the user
      // back to /settings?billing=updated when they're done.
      window.location.href = url;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Couldn't open the billing portal.";
      // The most common reason is "No active subscription" (404) — surface
      // a friendlier message with a path forward.
      if (/no active subscription/i.test(msg)) {
        setBillingError(
          "You don't have an active subscription yet. Choose a plan to get started.",
        );
      } else {
        setBillingError(msg);
      }
    } finally {
      setBillingLoading(false);
    }
  }

  // Initial loading shimmer — keeps the page from flashing the form
  // before we know who the user is.
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

  return (
    <div className="min-h-screen flex flex-col">
      <TopNav projectName="Settings" />

      <main className="flex-1 px-6 py-12 md:py-16">
        <div className="max-w-2xl mx-auto space-y-10">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="space-y-3"
          >
            <div className="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center">
              <SettingsIcon className="w-6 h-6" />
            </div>
            <h1 className="font-display text-3xl md:text-4xl font-bold tracking-tight text-foreground">
              Settings
            </h1>
            <p className="text-muted-foreground">
              Your account, password, and billing in one place.
            </p>
          </motion.div>

          {/* Account section */}
          <motion.section
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.05 }}
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
            <div className="pt-2 text-sm text-muted-foreground">
              Need to delete your account? Visit{" "}
              <Link href="/help#delete-account" className="text-primary hover:underline">
                Help → Delete account
              </Link>
              .
            </div>
          </motion.section>

          {/* Password section */}
          <motion.section
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
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
                  type="password"
                  value={pw}
                  onChange={(e) => setPw(e.target.value)}
                  required
                  minLength={8}
                  autoComplete="new-password"
                  className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </label>
              <label className="block">
                <span className="text-sm text-muted-foreground">Confirm new password</span>
                <input
                  type="password"
                  value={confirmPw}
                  onChange={(e) => setConfirmPw(e.target.value)}
                  required
                  minLength={8}
                  autoComplete="new-password"
                  className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </label>
              {pwError && (
                <p className="text-sm text-destructive" role="alert">{pwError}</p>
              )}
              {pwSuccess && (
                <p className="text-sm text-primary" role="status">
                  Password updated. You can keep using Pebble — no need to sign in again.
                </p>
              )}
              <button
                type="submit"
                disabled={pwSubmitting}
                className="inline-flex items-center rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {pwSubmitting ? "Updating…" : "Update password"}
              </button>
            </form>
          </motion.section>

          {/* Billing section */}
          <motion.section
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.15 }}
            className="rounded-2xl border border-border bg-card p-6 space-y-4"
          >
            <div className="flex items-center gap-2 text-foreground">
              <CreditCard className="w-5 h-5 text-muted-foreground" />
              <h2 className="font-display text-xl font-semibold">Billing</h2>
            </div>
            {/* Current-plan badge — driven by the webhook-written sentinel.
                Hidden while loading to avoid flashing "No active subscription"
                for users who do have one. Post-checkout (?billing=updated)
                shows a friendly "syncing" message during the brief webhook-
                lag window instead of the misleading "No active subscription"
                badge. */}
            {subLoading && justCheckedOut ? (
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Current plan</p>
                <p className="text-muted-foreground italic">
                  Syncing your subscription with Stripe…
                </p>
              </div>
            ) : !subLoading ? (
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Current plan</p>
                <p className="text-foreground font-medium">{planBadge(subscription)}</p>
              </div>
            ) : null}
            <p className="text-sm text-muted-foreground">
              Manage your plan, payment method, and download invoices. The
              billing portal is hosted by Stripe — Pebble never sees your
              card number.
            </p>
            {billingError && (
              <p className="text-sm text-destructive" role="alert">{billingError}</p>
            )}
            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={onManageBilling}
                disabled={billingLoading}
                className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <CreditCard className="w-4 h-4" />
                {billingLoading ? "Opening…" : "Manage billing"}
              </button>
              <Link
                href="/dashboard"
                className="text-sm text-muted-foreground hover:text-foreground"
              >
                Back to dashboard
              </Link>
            </div>
          </motion.section>
        </div>
      </main>
    </div>
  );
}
