import * as React from "react";
import { cn } from "@/lib/cn";

/**
 * GoldWavyDivider — decorative double-stroke wavy SVG line in gold + dark
 * gold. Lifts the "hand-drawn" texture between sections.
 */
export function GoldWavyDivider({ className }: { className?: string }) {
  return (
    <div
      className={cn("flex items-center justify-center py-12 md:py-16", className)}
      aria-hidden="true"
    >
      <svg
        width="240"
        height="32"
        viewBox="0 0 240 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="opacity-80"
      >
        <path
          d="M2 12 Q30 2, 60 12 T120 12 T180 12 T238 12"
          stroke="#b8924a"
          strokeWidth="1.4"
          strokeLinecap="round"
          fill="none"
        />
        <path
          d="M2 22 Q30 32, 60 22 T120 22 T180 22 T238 22"
          stroke="#967438"
          strokeWidth="1.1"
          strokeLinecap="round"
          fill="none"
        />
      </svg>
    </div>
  );
}
