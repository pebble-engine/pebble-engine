import * as React from "react";
import { cn } from "@/lib/cn";

type GlassCardProps = {
  children: React.ReactNode;
  className?: string;
  strong?: boolean;
};

/**
 * GlassCard — translucent surface with backdrop-blur. Used for the contact
 * info card, the floating hero badge, and any cluster that needs to sit
 * over imagery without going opaque.
 */
export function GlassCard({ children, className, strong = false }: GlassCardProps) {
  return (
    <div
      className={cn(
        strong ? "liquid-glass-strong" : "liquid-glass",
        "rounded-4xl p-6 md:p-8",
        className,
      )}
    >
      {children}
    </div>
  );
}
