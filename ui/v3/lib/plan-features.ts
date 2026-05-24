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
