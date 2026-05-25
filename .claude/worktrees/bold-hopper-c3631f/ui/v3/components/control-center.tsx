"use client";

/**
 * ControlCenter — two-pane shell for the Pebble app (2026-05-25 rev 3).
 *
 * Peblet moved from a fixed 340px right rail to a draggable floating
 * widget (FloatingPeblet). The shell now has two panes only:
 *
 *   [ DashboardSidebar (240px) ] [ canvas (flex-1) ]
 *
 * FloatingPeblet mounts via React portal to document.body so it floats
 * freely across the full viewport. The external prop API is unchanged —
 * no page-level edits needed.
 */

import type { ReactNode } from "react";
import { FloatingPeblet } from "@/components/floating-peblet";
import { type ChatProjectContext } from "@/lib/api";

export type ControlCenterProps = {
  /** Middle column — the actual route content. */
  children: ReactNode;
  /** Optional left sidebar slot (DashboardSidebar, or omit). */
  leftSidebar?: ReactNode;
  /** Opening line spoken by Peblet on mount. */
  greeting?: string;
  /** Optional project context for chat dispatch. */
  projectContext?: ChatProjectContext | null;
};

export function ControlCenter({
  children,
  leftSidebar,
  greeting,
  projectContext,
}: ControlCenterProps) {
  return (
    <div className="flex h-full w-full overflow-hidden bg-transparent">
      {/* LEFT — workspace sidebar. Hidden under lg. */}
      {leftSidebar && (
        <aside className="hidden lg:flex shrink-0 h-full">
          {leftSidebar}
        </aside>
      )}

      {/* MIDDLE — canvas. Scrolls independently. Transparent bg so pages
          that paint their own fixed background (e.g. /community with the
          architectural Unsplash photo) show through. The body/html layer
          provides the default bg-background for pages that don't override. */}
      <section className="flex-1 h-full overflow-y-auto bg-transparent min-w-0">
        {children}
      </section>

      {/* Floating Peblet — portal-mounted to document.body */}
      <FloatingPeblet greeting={greeting} projectContext={projectContext} />
    </div>
  );
}
