"use client";

/**
 * PlanPickerModal — Phase 54c (2026-05-23).
 *
 * The "offer wall" that mounts on top of the workspace shell whenever
 * the current user's needs_plan_selection flag is true (Phase 54b).
 * Marc's UX vision: the picker shows DURING the build (which is
 * already streaming in the background), so the time spent reading
 * tiers doubles as a perceived-speed boost. By the time the user
 * picks Free (the path of least resistance), the build is partially
 * or fully done.
 *
 * Design rules
 * ------------
 * - No dismiss without picking. The user must click a plan card.
 *   Otherwise the gate's "intentional" semantics are undermined.
 * - Free is the path of least resistance. It's the primary, largest,
 *   most-emphasized CTA. Starter / Pro are clearly available as
 *   upgrades but don't pressure the user.
 * - Mounts on top of the workspace shell so the build progress is
 *   visible UNDER the backdrop — the user sees something is happening.
 * - Closes only when /api/account/select-plan succeeds.
 *
 * Failure modes
 * -------------
 * - If select-plan fails (network, 500), shows an inline error and
 *   lets the user retry. Never closes silently.
 * - If checkout-redirect (Starter/Pro) fails, falls back to Free so
 *   the user isn't stuck in the picker forever.
 */

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Check, Loader2, Sparkles } from "lucide-react";
import { selectPlan, createCheckoutSession } from "@/lib/api";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

type PlanId = "free" | "starter" | "pro";

const TIERS: ReadonlyArray<{
  id:           PlanId;
  name:         string;
  price:        string;
  tagline:      string;
  highlights:   readonly string[];
  cta:          string;
  featured?:    boolean;
}> = [
  {
    id:    "free",
    name:  "Free",
    price: "$0",
    tagline: "Test drive Pebble. No card needed.",
    highlights: [
      "1 live site",
      "30 AI refinements/mo",
      "pebble.app subdomain",
      "Unlimited cosmetic edits",
    ],
    cta:      "Start with Free",
    featured: true,
  },
  {
    id:    "starter",
    name:  "Starter",
    price: "$19/mo",
    tagline: "For one real business that needs a real site.",
    highlights: [
      "5 live sites",
      "150 AI refinements/mo (rollover)",
      "1 custom domain",
      "Email forms (Resend-backed)",
    ],
    cta: "Try Starter",
  },
  {
    id:    "pro",
    name:  "Pro",
    price: "$49/mo",
    tagline: "For agencies + serial builders.",
    highlights: [
      "Unlimited sites",
      "400 AI refinements/mo (rollover)",
      "5 custom domains + analytics",
      "Drop-in section library",
    ],
    cta: "Try Pro",
  },
];

export function PlanPickerModal({
  onPlanSelected,
  firstName,
}: {
  /** Called after the plan is successfully persisted server-side. The
      parent should dismiss the modal AND continue with whatever flow
      was paused (typically the build is already running underneath). */
  onPlanSelected: (plan: PlanId) => void;
  /** Optional — personalises the headline ("Marc, while we build…"). */
  firstName?: string | null;
}) {
  const [busyPlan, setBusyPlan] = useState<PlanId | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handlePick(plan: PlanId) {
    if (busyPlan) return;
    setBusyPlan(plan);
    setError(null);
    try {
      const res = await selectPlan(plan);
      if (res.next === "checkout" && (plan === "starter" || plan === "pro")) {
        // Paid pick — open Stripe checkout. We don't dismiss the modal
        // first because the Stripe redirect navigates the whole tab;
        // dismissing would cause a flash of unstable workspace UI.
        try {
          const checkout = await createCheckoutSession(plan);
          window.location.href = checkout.url;
          return;
        } catch (e) {
          // Checkout failed — the plan flag is already cleared
          // server-side, so the user is technically on Free now. Show
          // them the error and let them retry from /settings.
          setError(
            e instanceof Error
              ? `Couldn't open checkout: ${e.message}. You're on Free for now — upgrade anytime from Settings.`
              : "Couldn't open checkout. You're on Free for now — upgrade anytime from Settings.",
          );
          // Still close the modal — the gate is cleared.
          onPlanSelected("free");
          return;
        }
      }
      // Free pick (or any other branch where next === "build")
      onPlanSelected(plan);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't save your plan choice. Try again?");
      setBusyPlan(null);
    }
  }

  return (
    <motion.div
      role="dialog"
      aria-modal="true"
      aria-labelledby="plan-picker-title"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-8 bg-black/60 backdrop-blur-sm overflow-y-auto"
    >
      <motion.div
        initial={{ opacity: 0, y: 24, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
        className="bg-card border border-border rounded-3xl shadow-[0_20px_80px_rgba(0,0,0,0.35)] p-6 sm:p-10 w-full max-w-4xl my-auto"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <p className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-[0.25em] text-muted-foreground mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            Your site is building
          </p>
          <h2 id="plan-picker-title" className={`${type.display.l} text-foreground`}>
            {firstName ? `${firstName}, p` : "P"}ick a plan while we work.
          </h2>
          <p className={`${type.body.m} text-muted-foreground mt-2 max-w-xl mx-auto`}>
            Take 30 seconds to glance at the tiers. Most people start on Free
            and upgrade if and when they need more — that&apos;s totally fine.
          </p>
        </div>

        {/* Tier grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {TIERS.map((tier) => {
            const isBusy = busyPlan === tier.id;
            const isDisabled = busyPlan !== null && busyPlan !== tier.id;
            return (
              <motion.button
                key={tier.id}
                onClick={() => handlePick(tier.id)}
                disabled={isDisabled}
                whileHover={{ y: -3 }}
                whileTap={{ scale: 0.98 }}
                className={`relative flex flex-col text-left p-5 rounded-2xl border-2 transition-colors disabled:opacity-50 disabled:cursor-wait ${
                  tier.featured
                    ? "border-primary bg-primary/5 hover:bg-primary/10"
                    : "border-border bg-background hover:border-foreground/40"
                }`}
              >
                {tier.featured && (
                  <span className="absolute -top-2 left-5 inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-primary text-primary-foreground text-[9px] font-bold uppercase tracking-widest">
                    Recommended
                  </span>
                )}

                <h3 className={`${type.heading.m} text-foreground`}>{tier.name}</h3>
                <p className={`${type.heading.l} text-foreground mt-1`}>{tier.price}</p>
                <p className={`${type.body.s} text-muted-foreground mt-1 mb-4`}>{tier.tagline}</p>

                <ul className="space-y-1.5 mb-5 flex-1">
                  {tier.highlights.map((h) => (
                    <li key={h} className="flex items-start gap-2 text-xs text-foreground/80">
                      <Check className="w-3.5 h-3.5 text-primary mt-0.5 shrink-0" />
                      <span>{h}</span>
                    </li>
                  ))}
                </ul>

                <div
                  className={`mt-auto inline-flex items-center justify-center gap-2 w-full px-4 py-2.5 rounded-full text-sm font-bold transition-colors ${
                    tier.featured
                      ? "bg-primary text-primary-foreground"
                      : "bg-foreground text-background"
                  }`}
                >
                  {isBusy && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  {isBusy ? "Saving…" : tier.cta}
                </div>
              </motion.button>
            );
          })}
        </div>

        {/* Reassurance row */}
        <p className={`${type.caption} text-center mt-6`}>
          Switch plans anytime. No long-term contracts. Cancel from Settings.
        </p>

        {error && (
          <motion.p
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 text-center text-sm text-destructive"
          >
            {error}
          </motion.p>
        )}
      </motion.div>
    </motion.div>
  );
}
