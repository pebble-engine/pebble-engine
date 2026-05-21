import * as React from "react";
import { cn } from "@/lib/cn";

type SectionDividerProps = {
  index: string;
  label?: string;
  className?: string;
};

/**
 * SectionDivider — numbered slab divider used between major sections.
 * Renders as: thin rule | "01 — LABEL" | thin rule. The number is the
 * cinematic signature for ordering sections without leaning on icons.
 */
export function SectionDivider({ index, label, className }: SectionDividerProps) {
  return (
    <div
      role="separator"
      aria-hidden={!label}
      className={cn("slab-divider py-12 md:py-16", className)}
    >
      <span className="text-accent font-display font-black text-xs">{index}</span>
      {label && <span className="text-eyebrow">{label}</span>}
    </div>
  );
}
