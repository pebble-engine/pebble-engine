"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * /landing was a standalone marketing page; the marketing surface now
 * lives at / (the welcome phase of the workspace shell). Kept as a
 * redirect so legacy inbound links (footer references, signup
 * redirects, social shares) keep landing somewhere coherent.
 */
export default function LandingRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/");
  }, [router]);
  return null;
}
