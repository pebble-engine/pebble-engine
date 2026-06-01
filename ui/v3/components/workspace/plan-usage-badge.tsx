"use client";

/**
 * PlanUsageBadge — "12 of 150 AI refinements used this month".
 *
 * Reads the `quota` block now returned by /api/billing/subscription
 * (see pebble/server/billing_subscription.py). Presentational only — the
 * parent (dashboard-sidebar) fetches the subscription and passes quota in.
 *
 * Matches the sidebar's design idiom: theme tokens (bg-background,
 * border-border, text-muted-foreground) + the shared `type` scale.
 */
import { Sparkles } from "lucide-react";
import { type } from "@/lib/type";
import type { PlanQuota } from "@/lib/api";

export function PlanUsageBadge({ quota }: { quota: PlanQuota | null | undefined }) {
  if (!quota) return null;

  const used = quota.usage?.ai_refinements_this_month ?? 0;
  const limitRaw = quota.limits?.ai_refinements_per_month;
  const limit = typeof limitRaw === "number" ? limitRaw : 0;
  const unlimited = limit === -1;
  const pct =
    unlimited || limit <= 0 ? 0 : Math.min(100, Math.round((used / limit) * 100));
  const near = !unlimited && pct >= 80;

  return (
    <div className="px-3 py-2 bg-background border border-border rounded-lg">
      <div className="flex items-center gap-2 mb-1">
        <Sparkles className="w-3.5 h-3.5 text-muted-foreground" />
        <p className={type.eyebrow}>
          <span className="capitalize">{quota.plan}</span> plan
        </p>
      </div>
      <p className={`${type.body.s} text-foreground`}>
        {unlimited ? `${used} used` : `${used} of ${limit}`}
      </p>
      {!unlimited && limit > 0 && (
        <div className="h-1 mt-1.5 rounded-full bg-muted overflow-hidden">
          <div
            className={`h-full rounded-full ${near ? "bg-amber-500" : "bg-primary"}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
      <p className={`${type.caption} mt-1`}>AI refinements this month</p>
    </div>
  );
}
