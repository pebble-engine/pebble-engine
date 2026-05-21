import * as React from "react";
import { cn } from "@/lib/cn";

type StatCardProps = {
  value: string;
  label: string;
  className?: string;
};

/**
 * StatCard — dark surface card with thin border + uppercase label.
 * Used in the 2x2 intro grid and the principal section's Years/Awards pair.
 */
export function StatCard({ value, label, className }: StatCardProps) {
  return (
    <div
      className={cn(
        "bg-surface border border-border cinematic-radius p-6 md:p-8 flex flex-col gap-2",
        className,
      )}
    >
      <span className="font-display font-black text-4xl md:text-5xl text-fg leading-none tracking-tighter">
        {value}
      </span>
      <span className="text-eyebrow">{label}</span>
    </div>
  );
}
