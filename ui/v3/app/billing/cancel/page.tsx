"use client";

/**
 * /billing/cancel — Stripe's checkout-abandoned return URL.
 *
 * Stripe sends users here if they click "back" from the Checkout
 * page without completing payment. No subscription was created;
 * just bounce them back to /settings so they can pick again or
 * leave.
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function BillingCancelPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/settings");
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-muted-foreground text-sm">Returning to settings…</p>
    </div>
  );
}
