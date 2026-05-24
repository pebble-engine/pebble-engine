/**
 * TypeScript mirror of pebble/user_plan.py PLAN_LIMITS.
 *
 * 2026-05-24 funnel restructure. Keep IN SYNC with the Python source —
 * if either copy drifts, every gated UI will lie to the user about
 * what they can / can't do.
 *
 * Why a mirror (not a fetch): client-side gates (lock overlays, "Pro
 * Feature" badges, integration card states) need to render synchronously
 * during the first paint. A fetch would force a loading flash. The
 * authoritative server-side check still runs on every gated API call,
 * so a drifted client only annoys, never breaks security.
 */

export type PlanTier = "free" | "starter" | "pro" | "enterprise";

export type IntegrationId =
  | "whatsapp" | "booking" | "google-maps" | "cookie-consent"
  | "stripe"   | "custom-code" | "social";

export type PlanFeatures = {
  published_sites:           number;   // -1 = unlimited
  ai_refinements_per_month:  number;
  custom_domains:            number;
  drop_in_sections_allowed:  boolean;
  resend_email_forms:        boolean;
  site_analytics:            boolean;
  multi_page_sites:          boolean;
  white_label:               boolean;
  integrations_allowed:      IntegrationId[];
  stripe_checkout:           boolean;
  api_access:                boolean;
  money_back_days:           number;
  priority_support:          boolean;
  remove_pebble_badge:       boolean;
  lead_inbox:                boolean;
  form_autoresponder:        boolean;
};

export const PLAN_LIMITS: Record<PlanTier, PlanFeatures> = {
  free: {
    published_sites:           -1,
    ai_refinements_per_month:  30,
    custom_domains:            0,
    drop_in_sections_allowed:  false,
    resend_email_forms:        false,
    site_analytics:            false,
    multi_page_sites:          true,
    white_label:               false,
    integrations_allowed:      [],
    stripe_checkout:           false,
    api_access:                false,
    money_back_days:           0,
    priority_support:          false,
    remove_pebble_badge:       false,
    lead_inbox:                false,
    form_autoresponder:        false,
  },
  starter: {
    published_sites:           -1,
    ai_refinements_per_month:  150,
    custom_domains:            1,
    drop_in_sections_allowed:  false,
    resend_email_forms:        true,
    site_analytics:            false,
    multi_page_sites:          true,
    white_label:               false,
    integrations_allowed:      ["whatsapp", "booking", "google-maps", "cookie-consent"],
    stripe_checkout:           false,
    api_access:                false,
    money_back_days:           7,
    priority_support:          false,
    remove_pebble_badge:       true,
    lead_inbox:                true,
    form_autoresponder:        true,
  },
  pro: {
    published_sites:           -1,
    ai_refinements_per_month:  400,
    custom_domains:            5,
    drop_in_sections_allowed:  true,
    resend_email_forms:        true,
    site_analytics:            true,
    multi_page_sites:          true,
    white_label:               true,
    integrations_allowed:      ["whatsapp", "booking", "google-maps", "cookie-consent",
                                "stripe", "custom-code", "social"],
    stripe_checkout:           true,
    api_access:                true,
    money_back_days:           14,
    priority_support:          true,
    remove_pebble_badge:       true,
    lead_inbox:                true,
    form_autoresponder:        true,
  },
  enterprise: {
    published_sites:           -1,
    ai_refinements_per_month:  -1,
    custom_domains:            -1,
    drop_in_sections_allowed:  true,
    resend_email_forms:        true,
    site_analytics:            true,
    multi_page_sites:          true,
    white_label:               true,
    integrations_allowed:      ["whatsapp", "booking", "google-maps", "cookie-consent",
                                "stripe", "custom-code", "social"],
    stripe_checkout:           true,
    api_access:                true,
    money_back_days:           30,
    priority_support:          true,
    remove_pebble_badge:       true,
    lead_inbox:                true,
    form_autoresponder:        true,
  },
};

/** Look up a feature flag for a plan tier. Mirror of user_plan.get_feature(). */
export function getFeature<K extends keyof PlanFeatures>(
  plan: PlanTier | string | null | undefined,
  key:  K,
): PlanFeatures[K] {
  const tier = (plan && plan in PLAN_LIMITS ? plan : "free") as PlanTier;
  return PLAN_LIMITS[tier][key];
}

/** True when the given tier is allowed to use the given integration. */
export function canUseIntegration(plan: PlanTier | string | null, id: IntegrationId): boolean {
  return (getFeature(plan, "integrations_allowed") as IntegrationId[]).includes(id);
}

/** Cheapest tier that unlocks the given integration. "starter" or "pro". */
export function minTierFor(id: IntegrationId): PlanTier {
  if (canUseIntegration("starter", id)) return "starter";
  return "pro";
}
