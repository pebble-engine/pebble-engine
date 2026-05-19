"use client";

/**
 * /billing/cancel — Stripe's checkout-abandoned return URL.
 *
 * Stripe sends users here if they click "back" from the Checkout page
 * without completing payment. No subscription was created; bounce them
 * to /settings so they can pick again or leave.
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { MarketingShell, MarketingCard } from "@/components/marketing-shell";

export default function BillingCancelPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/settings");
  }, [router]);

  return (
    <MarketingShell>
      <MarketingCard className="text-center">
        <Loader2 className="h-8 w-8 text-[#1a1a1a]/40 mx-auto animate-spin" />
        <h1 className="text-2xl font-semibold tracking-tight">No charge made</h1>
        <p className="text-sm text-[#1a1a1a]/65">Returning to settings…</p>
      </MarketingCard>
    </MarketingShell>
  );
}
