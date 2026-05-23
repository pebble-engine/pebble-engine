"use client";

import { use } from "react";
import { WorkspaceShell } from "@/components/workspace-shell";

/**
 * /workspace/<slug> — open an existing project by slug.
 *
 * Next.js 16 App Router passes route params as a Promise — `use()`
 * unwraps it synchronously inside a client component. Then we hand
 * the slug to the shell, which fetches the project state via the
 * /api/projects/<slug> endpoint.
 *
 * Sibling /workspace (no slug) still handles the fresh-build entry —
 * see app/workspace/page.tsx.
 */
export default function WorkspaceSlugPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  return <WorkspaceShell slug={slug} />;
}
