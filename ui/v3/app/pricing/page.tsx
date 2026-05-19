"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * `/pricing` was a standalone page; it now redirects to the in-landing
 * pricing section. Kept as a redirect (rather than deleted) so existing
 * inbound links — signup `?redirect=/pricing`, dashboard "Upgrade" links,
 * external shares — keep working.
 */
export default function PricingRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/#pricing");
  }, [router]);
  return null;
}
