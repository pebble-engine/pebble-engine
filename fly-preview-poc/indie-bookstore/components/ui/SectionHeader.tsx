"use client";
import { cn } from "@/lib/utils";

type Props = {
  eyebrow: string;
  title: string;
  description?: string;
  className?: string;
};

export function SectionHeader({ eyebrow, title, description, className }: Props) {
  return (
    <div className={cn("space-y-4 mb-12", className)}>
      <p className="text-sm font-medium tracking-wider uppercase text-[var(--color-accent)]" data-pebble-id="pb-c39b21">
        {eyebrow}
      </p>
      <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-text-primary)]" data-pebble-id="pb-2870f3">
        {title}
      </h2>
      {description && (
        <p className="text-lg text-[var(--color-text-secondary)] max-w-2xl" data-pebble-id="pb-f6054e">
          {description}
        </p>
      )}
    </div>
  );
}