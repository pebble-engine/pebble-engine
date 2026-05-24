"use client";

/**
 * TierBadge — small "Pro" / "Starter" pill shown on locked features.
 *
 * 2026-05-24 funnel restructure: hints throughout the workspace tell
 * users WHICH tier unlocks a feature instead of hiding the feature
 * (which would make the app feel small). Renders inline next to the
 * locked feature's label — never blocks interaction, just signals.
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
