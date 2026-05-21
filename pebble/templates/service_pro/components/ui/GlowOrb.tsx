import { cn } from "@/lib/cn";

type GlowOrbProps = {
  /** Tailwind classes for absolute positioning + size, e.g. "top-10 -left-20 w-[600px] h-[600px]". */
  className?: string;
  /** Color HSL token name — primary / accent / secondary. */
  color?: "primary" | "accent" | "secondary";
};

/**
 * Reusable absolutely-positioned blurred glow. Stays inside its parent (parent
 * should be `relative overflow-hidden`). Auto-hidden on mobile via `.glow-orb`.
 */
export function GlowOrb({ className, color = "primary" }: GlowOrbProps) {
  const colorVar = `hsl(var(--${color}) / 0.55)`;
  return (
    <span
      className={cn("glow-orb", className)}
      style={{ background: colorVar }}
      aria-hidden="true"
    />
  );
}
