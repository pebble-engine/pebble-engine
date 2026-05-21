/**
 * Shared typography scale for the v3 workspace.
 *
 * One module, one set of size/weight/leading/tracking combinations — so
 * future copy work becomes "import a role" instead of "remember the
 * exact mix of `text-sm font-medium leading-snug` from another file."
 *
 * CONTRACT — read before consuming:
 *   - Each value is a Tailwind className string. Compose with color /
 *     layout / margin utilities at the call site:
 *
 *       <h1 className={`${type.display.l} text-foreground drop-shadow-sm`}>
 *         {headline}
 *       </h1>
 *
 *   - `font-display` (Cormorant) is reserved for the `display.*` roles.
 *     Headings and body use Plus Jakarta Sans (`font-sans`).
 *     `font-mono` (JetBrains Mono) only via the `mono` role.
 *
 *   - Sizes anchor to Tailwind defaults (text-xs=12 → text-6xl=60).
 *     Only `eyebrow` uses an arbitrary value (text-[11px]) because
 *     11px is the conventional uppercase-label size and Tailwind has
 *     no utility for it.
 *
 * See docs/superpowers/specs/2026-05-15-workspace-typography-density-design.md
 * for the design rationale + migration heuristic.
 */
export const type = {
  display: {
    xl: "font-display text-5xl md:text-6xl font-bold tracking-tight leading-[1.05]",
    l:  "font-display text-4xl md:text-5xl font-bold tracking-tight leading-[1.1]",
    m:  "font-display text-2xl md:text-3xl font-semibold tracking-tight leading-[1.2]",
  },
  heading: {
    l: "text-xl md:text-2xl font-semibold tracking-tight leading-snug",
    m: "text-lg font-semibold leading-snug",
    s: "text-base font-semibold leading-snug",
  },
  body: {
    l: "text-lg leading-relaxed",
    m: "text-base leading-relaxed",
    s: "text-sm leading-normal",
  },
  label:   "text-sm font-medium leading-snug",
  caption: "text-xs leading-normal text-muted-foreground",
  eyebrow: "text-[11px] font-semibold uppercase tracking-[0.08em] text-muted-foreground",
  badge:   "text-[11px] font-bold uppercase tracking-wider",
  mono:    "font-mono text-xs uppercase tracking-widest",
} as const;
