import * as React from "react";
import { cn } from "@/lib/cn";

/**
 * ScratchyDivider — 12-stop linear-gradient simulating uneven hand-inked ink.
 * Used between major sections to add the "drawn" feel called out by the
 * tattoo_studio DNA `notable_features`.
 */
export function ScratchyDivider({ className }: { className?: string }) {
  return (
    <div
      className={cn("page-container", className)}
      role="presentation"
      aria-hidden="true"
    >
      <div className="scratchy-divider" />
    </div>
  );
}
