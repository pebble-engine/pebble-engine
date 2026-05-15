"use client";

import { WorkspaceShell } from "@/components/workspace-shell";

/**
 * / — the welcome route. Renders the same shell as /workspace so the
 * transition from "express your idea" into the questionnaire feels like
 * one screen instead of two. The shell reads usePathname() to know it
 * should default to phase=welcome here. Submitting the prompt then
 * router.push()es to /workspace#phase=idea — one meaningful URL change
 * at the "I've committed to building" moment.
 */
export default function HomePage() {
  return <WorkspaceShell />;
}
