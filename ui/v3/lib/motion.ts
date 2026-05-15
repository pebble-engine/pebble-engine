/**
 * Shared motion language for the v3 workspace.
 *
 * One module, one set of curves, one source of truth — so future
 * polish becomes "import a constant" instead of "rewrite the curve in
 * 14 places."
 *
 * CONTRACT — read before consuming:
 *   - The exported `Variants` objects (`fadeUp`, `phaseEnter`, etc.) are
 *     bare framer-motion Variants. They do NOT automatically adapt to the
 *     OS reduced-motion preference.
 *   - `prefersReducedMotion()` — call at render time to check the preference.
 *   - `withReducedMotion(variant)` — wraps any variant so every state
 *     collapses to an instant transition when the preference is active.
 *     Consumers must call this themselves, typically inside a `useMemo`:
 *
 *       const safeVariant = useMemo(() => withReducedMotion(fadeUp), []);
 *
 * See docs/superpowers/specs/2026-05-15-workspace-motion-polish-design.md
 * for the design rationale.
 */
import type { Variants } from "framer-motion";

// ---- Durations (milliseconds) ---------------------------------------------
export const MICRO    = 120;
export const SHORT    = 200;
export const STANDARD = 480;
export const SLOW     = 700;

// Framer-motion takes durations in seconds. Pre-converted for convenience.
export const MICRO_S    = MICRO    / 1000;
export const SHORT_S    = SHORT    / 1000;
export const STANDARD_S = STANDARD / 1000;
export const SLOW_S     = SLOW     / 1000;

// ---- Easings (cubic-bezier control points) --------------------------------
export const EASE_CINEMATIC: [number, number, number, number] = [0.22, 1, 0.36, 1];
export const EASE_QUIET:     [number, number, number, number] = [0.4, 0, 0.2, 1];

// ---- Accessibility: reduced motion ----------------------------------------
/** True when the user has the OS-level "reduce motion" preference enabled.
 *  Safe to call on the server (returns false). */
export function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/** Wrap any variant so it collapses to an instant transition when the
 *  user prefers reduced motion. Variants pass through unchanged
 *  otherwise. */
export function withReducedMotion<V extends Variants>(variant: V): V {
  if (!prefersReducedMotion()) return variant;
  // Reduce motion: keep the visual end-state, drop the animation.
  const collapsed: Variants = {};
  for (const [name, def] of Object.entries(variant)) {
    if (typeof def === "object" && def !== null) {
      collapsed[name] = { ...def, transition: { duration: 0 } };
    } else {
      collapsed[name] = def;
    }
  }
  return collapsed as V;
}

// ---- Variants -------------------------------------------------------------

/** Soft fade-up. Default for "thing entered" announcements. */
export const fadeUp: Variants = {
  hidden:  { opacity: 0, y: 8 },
  visible: { opacity: 1, y: 0, transition: { duration: STANDARD_S, ease: EASE_CINEMATIC } },
};

/** Phase entry — slightly larger movement than fadeUp because phase
 *  changes are the dominant motion in the app. */
export const phaseEnter: Variants = {
  hidden:  { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: STANDARD_S, ease: EASE_CINEMATIC } },
};

export const phaseExit: Variants = {
  visible: { opacity: 1, y: 0 },
  exit:    { opacity: 0, y: -8, transition: { duration: SHORT_S, ease: EASE_QUIET } },
};

/** Staggered fade-in for rail items. Use as the parent variant; child
 *  rail items get `fadeUp` via inherited transition. */
export const railStep: Variants = {
  hidden:  {},
  visible: { transition: { staggerChildren: 0.06, delayChildren: 0.04 } },
};

/** Staggered slide-in for action chips/buttons. Used by TopNav's
 *  right-slot when the design phase activates. */
export const chipDeck: Variants = {
  hidden:  {},
  visible: { transition: { staggerChildren: 0.06 } },
};

/** Default hover lift for clickable cards. Pure transform — no layout
 *  shift. Use as `initial='rest' whileHover='hover'`. */
export const cardHover: Variants = {
  rest:  { y: 0, transition: { duration: SHORT_S, ease: EASE_CINEMATIC } },
  hover: { y: -2, transition: { duration: SHORT_S, ease: EASE_CINEMATIC } },
};

/** Pebble droplet pulse used on the draft phase. SLOW + infinite.
 *  Use as `animate='rest'`; no hidden/visible states. */
export const dropletPulse: Variants = {
  rest: {
    scale: [1, 1.06, 1],
    transition: { duration: SLOW_S * 3.4, repeat: Infinity, ease: "easeInOut" },
  },
};


