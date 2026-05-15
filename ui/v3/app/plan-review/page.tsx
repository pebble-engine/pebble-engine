"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * Legacy /plan-review URL — the Pebble Plan review now lives inside
 * the unified workspace at /workspace#phase=plan.
 */
export default function PlanReviewRedirectPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/workspace#phase=plan");
  }, [router]);
  return null;
}
