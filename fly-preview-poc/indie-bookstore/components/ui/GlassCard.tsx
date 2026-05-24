"use client";
import { cn } from "@/lib/utils";

type Props = {
  children: React.ReactNode;
  className?: string;
};

export function GlassCard({ children, className }: Props) {
  return (
    <div
      className={cn(
        "backdrop-blur-md bg-[var(--color-surface-2)] border border-[var(--color-border)] rounded-xl p-6 shadow-lg",
        className
      )}
    >
      {children}
    </div>
  );
}