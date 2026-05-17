"use client";

/**
 * /billing/success — Stripe's post-checkout return URL.
 *
 * Stripe redirects here with `?session_id=cs_...` after a successful
 * subscription Checkout. We don't need to do anything with the session_id
 * client-side — the webhook handler is authoritative for subscription
 * state — so we just bounce to /settings?billing=updated, which already
 * has the post-checkout sync-polling UX baked in.
 *
 * Kept as a thin route rather than a Stripe success_url pointing directly
 * at /settings because (a) the redirect lets us preserve the
 * session_id in browser history for support debugging if needed, and
 * (b) some browsers + ad blockers strip Stripe-attribution query params
 * on cross-origin redirects — landing here first guarantees the
 * `billing=updated` flag survives.
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function BillingSuccessPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/settings?billing=updated");
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-muted-foreground text-sm">
        Redirecting to your settings…
      </p>
    </div>
  );
}
