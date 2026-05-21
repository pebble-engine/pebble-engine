import * as React from "react";
import { cn } from "@/lib/cn";

type GlassCardProps = {
  children: React.ReactNode;
  className?: string;
  strong?: boolean;
};

/**
 * GlassCard — translucent card with backdrop-blur. Used for product cards,
 * testimonials, the navbar chip, and any floating UI that needs to sit over
 * imagery without going opaque.
 */
export function GlassCard({ children, className, strong = false }: GlassCardProps) {
  return (
    <div
      className={cn(
        strong ? "glass-card-strong" : "glass-card",
        "rounded-2xl p-6 md:p-8 transition-all duration-300",
        className,
      )}
    >
      {children}
    </div>
  );
}
