"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * Legacy /publish URL — the publish flow now lives inside the unified
 * workspace at /workspace#phase=publish. The shell drives the actual
 * publishSite() call.
 */
export default function PublishRedirectPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/workspace#phase=publish");
  }, [router]);
  return null;
}
