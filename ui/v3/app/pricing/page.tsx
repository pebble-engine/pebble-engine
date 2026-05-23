"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/auth-provider";

/**
 * `/pricing` was a standalone page; it now redirects to the in-landing
 * pricing section for anonymous visitors, OR to /settings (the in-app
 * upgrade surface) for signed-in users.
 *
 * Kept as a redirect (rather than deleted) so existing inbound links —
 * signup `?redirect=/pricing`, dashboard "Upgrade" links, external shares,
 * email footers — keep working for both audiences.
 *
 * Why the auth-aware split (2026-05-23):
 *   Old code sent everyone to `/#pricing`. For authed users that becomes
 *   `/` which middleware bounces to `/dashboard` (GUEST_ONLY_ROUTES),
 *   leaving them stranded with no way to see pricing — a real upgrade
 *   blocker. Routing authed users to `/settings` (which already houses
 *   the current-plan badge + Manage Billing button) gives them a working
 *   upgrade path; anonymous visitors still see the marketing pricing.
 */
export default function PricingRedirect() {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (loading) return; // wait for auth state to resolve before deciding
    if (user) {
      router.replace("/settings#plan");
    } else {
      router.replace("/#pricing");
    }
  }, [router, user, loading]);

  return null;
}
