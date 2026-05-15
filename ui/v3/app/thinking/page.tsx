"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * Legacy /thinking URL — the build animation now lives inside the
 * unified workspace at /workspace#phase=draft. The shell drives the
 * actual /api/generate call, so direct hits here can't continue an
 * in-flight build; we send them back to the questionnaire so they can
 * start fresh.
 */
export default function ThinkingRedirectPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/workspace#phase=idea");
  }, [router]);
  return null;
}
