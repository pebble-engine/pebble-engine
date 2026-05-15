"use client";

import { WorkspaceShell } from "@/components/workspace-shell";

/**
 * /workspace — the project shell. Defaults to phase=design (resume the
 * last build) but accepts any phase via URL hash. The shell itself
 * lives in components/workspace-shell.tsx so /` (the welcome route)
 * can render the same chrome without a remount-flashing redirect.
 */
export default function WorkspacePage() {
  return <WorkspaceShell />;
}
