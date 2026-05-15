"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * Legacy /intake URL — the questionnaire now lives inside the unified
 * workspace at /workspace#phase=idea. Anyone landing here (bookmarks,
 * stale emails, prior session links) gets bounced through.
 */
export default function IntakeRedirectPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/workspace#phase=idea");
  }, [router]);
  return null;
}
