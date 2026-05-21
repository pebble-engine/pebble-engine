import { cn } from "@/lib/cn";

/**
 * The parts-catalog ref-code label. Every section is stamped with one of
 * these (`REF-XXX`, `SVC-XXX`, `BADGE-0X`, etc.) per the auto_honest_diag DNA.
 * Defaults to the muted body color; pass `accent` for yellow.
 */
export function RefCode({
  children,
  accent = false,
  className,
}: {
  children: React.ReactNode;
  accent?: boolean;
  className?: string;
}) {
  return (
    <span className={cn(accent ? "ref-code-accent" : "ref-code", className)}>
      {children}
    </span>
  );
}
