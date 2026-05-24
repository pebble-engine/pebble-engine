"use client";

/**
 * Billing tab — plan display, next charge date, Stripe portal link.
 * Reads existing /api/billing/subscription via fetchSubscription helper.
 * Invoice history is a B4 placeholder.
 */

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { CreditCard } from "lucide-react";
import { type } from "@/lib/type";
import { useAuth } from "@/components/auth-provider";
import {
  createCheckoutSession,
  fetchSubscription,
  openBillingPortal,
  type SubscriptionState,
} from "@/lib/api";
import { useSearchParams } from "next/navigation";

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

// ── component ─────────────────────────────────────────────────────────────────

export function BillingTab() {
  const { user, loading } = useAuth();
  const searchParams = useSearchParams();

  const justCheckedOut = searchParams?.get("billing") === "updated";
  const testMode = searchParams?.get("test") === "1";

  // ── billing state ──────────────────────────────────────────────────────────
  const [billingError, setBillingError]     = useState<string | null>(null);
  const [billingLoading, setBillingLoading] = useState(false);
  const [subscription, setSubscription]     = useState<SubscriptionState | null>(null);
  const [subLoading, setSubLoading]         = useState(true);

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

  if (!user) return null;

  return (
    <div className="space-y-8">
      <motion.section
        initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="rounded-2xl border border-border bg-card p-6 space-y-4"
      >
        <div className="flex items-center gap-2 text-foreground">
          <CreditCard className="w-5 h-5 text-muted-foreground" />
          <h2 className={`${type.dashboard.heading.l}`}>Billing</h2>
        </div>

        {subLoading && justCheckedOut ? (
          <div className="space-y-1">
            <p className={type.caption}>Current plan</p>
            <p className="text-muted-foreground italic">Syncing your subscription with Stripe…</p>
          </div>
        ) : !subLoading ? (
          <div className="space-y-1">
            <p className={type.caption}>Current plan</p>
            <p className="text-foreground font-medium">{planBadge(subscription)}</p>
          </div>
        ) : null}

        <p className={`${type.body.s} text-muted-foreground`}>
          Manage your plan, payment method, and download invoices. The
          billing portal is hosted by Stripe — Pebble never sees your card number.
        </p>

        {!subscription && !subLoading && (
          <p className={`${type.caption} text-muted-foreground mt-1`}>
            Upgrade to unlock unlimited builds and publishing.
          </p>
        )}

        {billingError && <p className={`${type.body.s} text-destructive`} role="alert">{billingError}</p>}

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
            <p className={type.eyebrow}>Test mode</p>
            <p className={`${type.body.s} text-muted-foreground`}>
              Drive a checkout end-to-end. Use Stripe&apos;s test card
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

      {/* ── Invoice history placeholder (B4) ─────────────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.04 }}
        className="rounded-2xl border border-border bg-card p-6 space-y-3"
      >
        <h2 className={`${type.dashboard.heading.l} text-foreground`}>Usage history</h2>
        <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
          Usage history coming soon
        </div>
      </motion.section>
    </div>
  );
}
