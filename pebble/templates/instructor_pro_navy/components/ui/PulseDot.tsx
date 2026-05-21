import { cn } from "@/lib/cn";

/**
 * Live red status pulse dot — used inside the hero eyebrow pill and the
 * floating credentials card. The DNA notes call out this affordance by name.
 */
export function PulseDot({ className }: { className?: string }) {
  return (
    <span
      aria-hidden="true"
      className={cn("relative inline-flex h-2 w-2", className)}
    >
      <span className="absolute inset-0 rounded-full bg-accent animate-pulse-dot" />
      <span className="relative inline-flex h-2 w-2 rounded-full bg-accent" />
    </span>
  );
}
