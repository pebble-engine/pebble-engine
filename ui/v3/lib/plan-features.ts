/**
 * plan-features.ts — Tier definitions + feature gates.
 *
 * 2026-05-24: Canonical source for the four tiers (free, starter, pro, enterprise)
 * and which subscription status maps to which tier.
 */

export type PlanTier = "free" | "starter" | "pro" | "enterprise";

export type SubscriptionStatus = "active" | "past_due" | "canceled" | "incomplete" | "trialing" | "unpaid";

/**
 * Map Stripe subscription status to our internal tier.
 * For users without a subscription, they're "free".
 * For users with an active/trialing subscription, they're paid (tier determined by price_id).
 */
export function subscriptionStatusToTier(
  status: SubscriptionStatus | null | undefined,
  plan?: string | null,
): PlanTier {
  if (!status || status === "canceled") {
    return "free";
  }
  // For now, any active/trialing/past_due/incomplete subscription defaults to "pro".
  // In the future, the plan string (price_id or product slug) will determine
  // whether this is "starter" or "pro".
  if (status === "active" || status === "trialing" || status === "past_due" || status === "incomplete") {
    return "pro";
  }
  return "free";
}


// ---------- Integration tier gates ----------
//
// 2026-05-26: integrations-phase.tsx imports canUseIntegration() and
// minTierFor() but the helpers were missing from this file (task #146
// was marked completed but the diff didn't include them — drift). v3
// dev server crashed with "Export minTierFor doesn't exist" on every
// page load that touches integrations. Stubs below restore startup;
// real per-integration gating can replace these later.
//
// Current policy:
//   - free: NO third-party integrations (forces upgrade prompt)
//   - starter: basic ones (whatsapp, booking, maps)
//   - pro / enterprise: everything
// The minTierFor() return type is widened to PlanTier but consumers
// cast it down to "starter" | "pro" — that cast stays safe because
// we never return "free" or "enterprise" from this helper.

const _STARTER_INTEGRATIONS = new Set(["whatsapp", "booking", "maps"]);

export function minTierFor(integrationId: string): PlanTier {
  return _STARTER_INTEGRATIONS.has(integrationId) ? "starter" : "pro";
}

export function canUseIntegration(tier: PlanTier, integrationId: string): boolean {
  if (tier === "pro" || tier === "enterprise") return true;
  if (tier === "starter") return _STARTER_INTEGRATIONS.has(integrationId);
  return false;
}
