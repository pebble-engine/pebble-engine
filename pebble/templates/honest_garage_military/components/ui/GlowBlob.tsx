import { cn } from "@/lib/cn";

type GlowBlobProps = {
  /** Tailwind classes for positioning + size, e.g. "top-10 -right-32 h-[700px] w-[700px]". */
  className?: string;
};

/**
 * Subtle yellow gradient-mesh corner blob. Paired in opposite corners of the
 * hero for the auto_honest_diag glow. Parent should be `relative overflow-hidden`.
 */
export function GlowBlob({ className }: GlowBlobProps) {
  return <span className={cn("glow-blob", className)} aria-hidden="true" />;
}
