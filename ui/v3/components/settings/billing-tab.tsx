"use client";

/**
 * Billing tab — plan card, renewal date, invoice history, Stripe portal.
 *
 * B1: plan badge + portal button.
 * B4: enriched plan card, invoice table (last 12), "Change plan" CTA.
 */

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { CreditCard, Download } from "lucide-react";
import { type } from "@/lib/type";
import { useAuth } from "@/components/auth-provider";
import {
  createCheckoutSession,
  fetchSubscription,
  fetchInvoices,
  openBillingPortal,
  type SubscriptionState,
  type Invoice,
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

function formatAmount(cents: number, currency: string): string {
  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency: currency.toUpperCase(),
    }).format(cents / 100);
  } catch {
    return `${(cents / 100).toFixed(2)} ${currency.toUpperCase()}`;
  }
}

function formatInvoiceDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      year: "numeric", month: "short", day: "numeric",
    });
  } catch { return iso; }
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

  // ── invoice state ──────────────────────────────────────────────────────────
  const [invoices, setInvoices]           = useState<Invoice[]>([]);
  const [invoicesLoading, setInvoicesLoading] = useState(true);
  const [invoiceError, setInvoiceError]   = useState<string | null>(null);

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

  // ── load invoices ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (loading || !user) return;
    let cancelled = false;
    (async () => {
      try {
        const rows = await fetchInvoices();
        if (!cancelled) setInvoices(rows);
      } catch (err) {
        if (!cancelled) setInvoiceError(
          err instanceof Error ? err.message : "Couldn't load invoices."
        );
      } finally {
        if (!cancelled) setInvoicesLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [loading, user]);

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

      {/* ── Plan card ──────────────────────────────────────────────────────── */}
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
          {/* Change plan CTA — always visible */}
          <Link
            href="/pricing"
            className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-4 py-2 text-sm font-medium text-foreground hover:bg-accent"
          >
            {subscription ? "Change plan" : "Choose a plan →"}
          </Link>

          {/* Portal button — only for users with a subscription */}
          {subscription && (
            <button
              type="button" onClick={onManageBilling} disabled={billingLoading}
              className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <CreditCard className="w-4 h-4" />
              {billingLoading ? "Opening…" : "Manage billing"}
            </button>
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

      {/* ── Invoice history ────────────────────────────────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.04 }}
        className="rounded-2xl border border-border bg-card p-6 space-y-4"
      >
        <h2 className={`${type.dashboard.heading.l} text-foreground`}>Invoice history</h2>
        <p className={`${type.body.s} text-muted-foreground`}>
          Your last {invoices.length > 0 ? invoices.length : 12} invoices from Stripe.
          {" "}PDF links open in a new tab.
        </p>

        {invoicesLoading ? (
          <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
            Loading invoices…
          </div>
        ) : invoiceError ? (
          <div className="rounded-lg border border-destructive/40 bg-destructive/5 p-4 text-sm text-destructive">
            {invoiceError}
          </div>
        ) : invoices.length === 0 ? (
          <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
            No invoices yet. They&apos;ll appear here once you subscribe.
          </div>
        ) : (
          <div className="overflow-hidden rounded-xl border border-border">
            <table className="w-full text-sm">
              <thead className="bg-muted/40">
                <tr>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">Date</th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">Invoice #</th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">Amount</th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">Status</th>
                  <th className="px-4 py-2.5 text-right text-xs font-medium text-muted-foreground uppercase tracking-wide"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {invoices.map((inv) => (
                  <tr key={inv.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-4 py-3 text-muted-foreground whitespace-nowrap">
                      {formatInvoiceDate(inv.created_at)}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-foreground">
                      {inv.number ?? inv.id.slice(0, 12)}
                    </td>
                    <td className="px-4 py-3 font-medium text-foreground whitespace-nowrap">
                      {formatAmount(inv.amount_cents, inv.currency)}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                        inv.status === "paid"
                          ? "bg-green-500/10 text-green-700 dark:text-green-400"
                          : inv.status === "open"
                          ? "bg-yellow-500/10 text-yellow-700 dark:text-yellow-400"
                          : "bg-muted text-muted-foreground"
                      }`}>
                        {inv.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      {inv.pdf_url && (
                        <a
                          href={inv.pdf_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
                          aria-label={`Download PDF for invoice ${inv.number ?? inv.id}`}
                        >
                          <Download className="w-3.5 h-3.5" />
                          PDF
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.section>
    </div>
  );
}
