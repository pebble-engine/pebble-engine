/**
 * Shared interaction patterns for the v3 workspace.
 *
 * One module, one set of hover/active/focus/transition patterns — so
 * future polish becomes "import a role" instead of "remember the exact
 * mix of `hover:opacity-90 transition-opacity` from another file."
 *
 * Each role is a flat Tailwind className string anchored to the motion
 * module's duration scale (button=150ms between MICRO and SHORT, chip=100ms,
 * card=200ms, etc.). Compose with color / layout / margin utilities at the
 * call site:
 *
 *   <button className={`${interactions.button} bg-primary text-primary-foreground`}>
 *     Click me
 *   </button>
 *
 * CONTRACT — read before consuming:
 *   - Press states (`active:`) are included for tactile feedback.
 *   - Focus rings (`focus-visible:`) are universal across all roles.
 *   - `motion-reduce:` overrides collapse transforms to instant when the
 *     user prefers reduced motion. Color transitions stay (they're safe
 *     per WCAG motion guidance).
 *   - Disabled state is left to the consumer (context-dependent).
 *
 * See docs/superpowers/specs/2026-05-15-round3-microinteractions-design.md
 * for the design rationale and migration heuristic.
 */

export const interactions = {
  /** Primary / secondary buttons — pill or rounded-rect with text + bg. */
  button: [
    "transition-all duration-150 ease-out",
    "hover:opacity-90",
    "active:scale-[0.98] motion-reduce:active:scale-100",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
    "motion-reduce:transition-none",
  ].join(" "),

  /** Small pill or tag — chip-like clickables (rail items, refine buttons). */
  chip: [
    "transition-colors duration-100 ease-out",
    "hover:bg-accent",
    "active:bg-accent/80",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 focus-visible:ring-offset-background",
  ].join(" "),

  /** Clickable card or list row — gentle lift + shadow. */
  card: [
    "transition-all duration-200 ease-out",
    "hover:-translate-y-0.5 hover:shadow-md",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
    "motion-reduce:hover:translate-y-0 motion-reduce:transition-none",
  ].join(" "),

  /** Square icon-only control (close, star, delete). */
  iconButton: [
    "transition-all duration-150 ease-out",
    "hover:bg-accent",
    "active:scale-95 motion-reduce:active:scale-100",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 focus-visible:ring-offset-background",
    "motion-reduce:transition-none",
  ].join(" "),

  /** Inline text link. */
  link: [
    "transition-colors duration-100 ease-out",
    "hover:text-foreground",
    "focus-visible:outline-none focus-visible:underline focus-visible:underline-offset-2",
  ].join(" "),

  /** Standalone focus ring utility — for inputs, tab triggers, anything tabbable that doesn't otherwise need transition or hover handling. */
  focusRing: "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
} as const;
