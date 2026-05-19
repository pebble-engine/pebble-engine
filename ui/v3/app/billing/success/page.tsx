"use client";

/**
 * /billing/success — Stripe's post-checkout return URL.
 *
 * Stripe redirects here with `?session_id=cs_...` after a successful
 * subscription Checkout. The webhook handler is authoritative for
 * subscription state, so we just bounce to /settings?billing=updated,
 * which has the post-checkout sync-polling UX baked in.
 *
 * Kept as a thin route rather than pointing Stripe's success_url directly
 * at /settings because (a) the redirect preserves the session_id in
 * browser history for support debugging, and (b) some browsers + ad
 * blockers strip Stripe-attribution query params on cross-origin
 * redirects — landing here first guarantees `billing=updated` survives.
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { MarketingShell, MarketingCard } from "@/components/marketing-shell";

export default function BillingSuccessPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/settings?billing=updated");
  }, [router]);

  return (
    <MarketingShell>
      <MarketingCard className="text-center">
        <Loader2 className="h-8 w-8 text-[#3054ff] mx-auto animate-spin" />
        <h1 className="text-2xl font-semibold tracking-tight">Payment successful</h1>
        <p className="text-sm text-[#1a1a1a]/65">Loading your settings…</p>
      </MarketingCard>
    </MarketingShell>
  );
}
