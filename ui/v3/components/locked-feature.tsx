"use client";

/**
 * LockedFeature — ghost-state overlay that wraps a feature surface.
 *
 * 2026-05-24 funnel restructure: making the gap concrete (Pro features
 * are visible, just locked) converts ~3x better than hiding them
 * altogether (free users don't know what they're missing).
 *
 * Behavior:
 *   - If currentPlan tier is >= requires tier → render children as-is
 *   - Otherwise → render children in opacity-40 blurred container, with
 *     a centered absolute overlay showing the feature label + tier badge
 *     + an Upgrade CTA routing to /pricing.
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
  const callerTier: PlanTier = (plan && (plan as PlanTier) in TIER_RANK ? (plan as PlanTier) : "free");
  const callerRank   = TIER_RANK[callerTier];
  const requiredRank = TIER_RANK[requires];

  if (callerRank >= requiredRank) {
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
