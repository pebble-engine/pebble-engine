import * as React from "react";
import { cn } from "@/lib/cn";

type EyebrowChipProps = {
  children: React.ReactNode;
  className?: string;
};

/**
 * EyebrowChip — small uppercase pill that sits above section headlines.
 * The DNA pattern: tracked uppercase label inside a soft cream-alt pill
 * with a 1px edge border. Provides rhythm across every section.
 */
export function EyebrowChip({ children, className }: EyebrowChipProps) {
  return <span className={cn("eyebrow-chip", className)}>{children}</span>;
}
