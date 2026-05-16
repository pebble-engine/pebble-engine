# Round 3 / Micro-interactions Module — Design Spec

**Date:** 2026-05-15
**Owner:** Marc (Claude operating autonomously per the round 3 mandate)
**Scope tier:** Define a reusable hover/active/focus pattern module, then
apply it across the workspace + dashboard surfaces. Companion pass to
the round-2 motion + type modules.
**Status:** Self-approved 2026-05-15 (autonomous mode).

## Summary

The v3 frontend has organic interaction patterns: every clickable was
written with whatever hover/transition felt right at the time. The
result is rhythmic noise — primary buttons in different files use
`transition-opacity` vs `transition-transform` vs no transition at all;
focus rings appear sparsely; press states (`active:`) are nearly absent.
Linear-style tactile polish requires consistency, not novelty.

Round 3 / commit 2 lifts the existing patterns into a single module
(`ui/v3/lib/interactions.ts`), adds the missing pieces (focus rings,
press states, motion-reduce overrides), and applies it across the
sixteen workspace-critical files already covered by the type + motion
modules.

The point is the *consistency*, not the originality. Future polish
becomes "import a role" rather than "remember the exact mix of
hover/active/focus from another file."

## Goals

- **One source of truth for interaction states.** A
  `ui/v3/lib/interactions.ts` module exporting flat Tailwind className
  strings keyed by role (button, chip, card, iconButton, link,
  focusRing). Consumers compose with template literals.
- **Cover the four interaction states uniformly.** Every role defines
  hover, active (where appropriate), focus-visible, and a base
  transition. Disabled state is left to the consumer (often
  context-dependent).
- **Honor `prefers-reduced-motion`.** Every role with a transform or
  scale animation includes `motion-reduce:` overrides that collapse the
  motion to instant.
- **Workspace + dashboard coverage.** Same sixteen files already covered
  by round 2 + round 3 commit 1 import the module. Anything else (other
  app pages, /inbox, /migrate, /login, etc.) keeps its existing
  patterns until round 4.
- **No new visual language.** Lift the patterns the codebase already
  uses (`hover:opacity-90` on primary, `hover:bg-accent` on outline,
  `whileHover={{ y: -3 }}` on cards, etc.) into the module. The
  *additions* are focus rings, press states, and motion-reduce
  overrides — none of those break existing visuals; they extend them.

## Non-goals (deferred to round 4+)

- Dashboard / standalone components OUTSIDE the sixteen-file scope:
  /landing, /login, /signup, /forgot, /reset, /help, /inbox, /migrate,
  /thinking, /publish, /plan-review, /intake. Many of these already
  have great per-file polish (login uses `hover:scale-[1.01]
  active:scale-[0.99]` for example). They get standardized in round 4.
- The generated marketing sites (output/) — separate codebase.
- Component-internal animation states (loading spinners, accordion
  expand/collapse, dialog open/close). Out of scope; framer-motion
  handles those via the motion module.
- Color-tone shifts on hover (e.g., `hover:bg-primary/90` vs
  `hover:opacity-90`). The current convention varies — leave it.
- Disabled-state styling. Stays at the consumer.

## Architecture

### New file

- `ui/v3/lib/interactions.ts` — exports the `interactions` object as a
  pure `as const` literal of className strings.

### New tests

- `ui/v3/lib/interactions.test.mjs` — plain-Node verifier matching the
  motion + type test pattern. Pins each role's critical classes.
- `tests/test_interactions_module_wiring.py` — Python regression that
  pins:
  - `lib/interactions.ts` exists.
  - Module exports `interactions` as a const.
  - Each role key is present (button, chip, card, iconButton, link,
    focusRing).
  - Each role's value contains the expected critical classes
    (`transition-*`, `hover:*`, `focus-visible:*`).
  - The two anchor consumer files import from `@/lib/interactions`:
    `workspace-shell.tsx` + `top-nav.tsx`. Other files MAY import but
    are not required by the wiring test (sparser usage than typography).

### Files modified — apply pass

- `ui/v3/components/workspace-shell.tsx` — rail items, top-nav action
  buttons.
- `ui/v3/components/top-nav.tsx` — brand link, project-name slot,
  help button.
- `ui/v3/components/phases/welcome-phase.tsx` — submit chip, suggestion
  cards.
- `ui/v3/components/phases/idea-phase.tsx` — chip questions, forward
  button, optional-question close.
- `ui/v3/components/phases/plan-phase.tsx` — back button, edit fields.
- `ui/v3/components/phases/draft-phase.tsx` — minimal (mostly read-only
  during build).
- `ui/v3/components/phases/edit-phase.tsx` — refine buttons, history
  drawer items, color picker chips.
- `ui/v3/components/phases/publish-phase.tsx` — publish CTA.
- `ui/v3/app/dashboard/page.tsx` — sidebar items, project cards, search
  input, action buttons, delete confirm buttons, empty-state CTA.
- `ui/v3/app/admin/page.tsx` — refresh button, tab buttons.
- `ui/v3/components/command-palette.tsx` — result rows.
- `ui/v3/components/dna-preview.tsx` — reroll button.
- `ui/v3/components/language-picker.tsx` — trigger button, option rows.
- `ui/v3/components/ui/ai-prompt-box.tsx` — adapted 3rd-party; minimal
  application (one or two clean fits if any).
- `ui/v3/components/block-gallery.tsx` — close button, block cards.
- `ui/v3/components/auth-menu.tsx` — sign-in / sign-up chips, trigger
  button, menu items.

### What does NOT change

- The motion module. interactions.ts *uses* its duration constants but
  doesn't replace anything in motion.ts.
- The type module. Typography is independent.
- Backend Python code (except the new wiring test).
- The `whileHover={{ y: -2 }}` framer-motion props on the publish-phase
  CTA — the framer spring physics there is intentional; do NOT migrate
  to CSS hover.
- The animated `@radix-ui/react-tooltip` and `@radix-ui/react-dialog`
  open/close states — those are library-driven.

### Blast radius

- 1 new module + 1 new plain-Node verifier + 1 new Python wiring test +
  16 v3 files modified. Estimated ~250-350 lines net change.

## The interactions scale

```ts
// ui/v3/lib/interactions.ts
import { MICRO, SHORT } from "./motion";

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
```

### Notes on choices

- **Durations.** `button` and `iconButton` use 150ms (between MICRO=120
  and SHORT=200). `chip` and `link` use 100ms — color-only changes can
  be snappier without feeling abrupt. `card` uses 200ms — translate +
  shadow benefits from a slightly more deliberate ease.
- **Easings.** All use `ease-out` (Tailwind's default `ease-out`). The
  motion module's curves (`EASE_CINEMATIC`, `EASE_QUIET`) are tuned for
  larger entrance animations; for 100-200ms hover transitions, the
  difference is sub-perceptual. Tailwind's ease-out (cubic-bezier(0,0,
  0.2, 1)) is fine.
- **Press scale.** Buttons get `scale-[0.98]` (2% shrink). Icon buttons
  get `scale-95` (5%). Icons feel tactile-er with more pop because the
  square area is small; on text buttons, 5% is too much.
- **Card lift.** `-translate-y-0.5` (2px). The codebase already uses
  `whileHover={{ y: -3 }}` on dashboard project cards via framer-motion
  spring. Migrating to `-translate-y-0.5` (CSS tween, ease-out, 200ms)
  is a *deliberate* shift toward calmer interactions per Pebble's "calm
  premium" brand. The motion is identical visually (~2-3px lift); the
  curve is what differs (spring → tween).
- **Focus ring offsets.** Buttons + cards get `ring-offset-2` (8px) for
  comfortable separation. Chips + iconButtons get `ring-offset-1` (4px)
  because they're smaller and the larger offset overlaps neighbors.
- **`motion-reduce:` overrides.** Tailwind's `motion-reduce:` variant
  applies the suffixed class only when `prefers-reduced-motion: reduce`
  is true. Each role with transform/scale includes a same-position
  override that resets the motion. Color and bg transitions don't need
  motion-reduce — color shifts are already considered safe under WCAG
  motion guidance.
- **No `disabled:` styling.** Buttons commonly want `disabled:opacity-40
  disabled:cursor-not-allowed` but the EXACT shape depends on context
  (some want cursor-wait, some want cursor-default, some want a ghost
  state). Leave to the consumer.

### Migration heuristic — what each existing pattern becomes

| Was | Becomes |
|---|---|
| `hover:opacity-90 transition-opacity` (primary buttons) | prepend `${interactions.button}` (drops the explicit transition-opacity in favor of transition-all 150ms) |
| `hover:bg-accent transition-colors` (outline buttons) | replace with `${interactions.button}` if it's a button OR `${interactions.chip}` if it's a chip |
| `hover:bg-accent transition-colors` (icon-only square) | replace with `${interactions.iconButton}` |
| `hover:scale-[1.02] transition-transform` (auth signup) | drop in favor of `${interactions.button}` (consistent press) — the scale-up was per-file polish, the module replaces it with universal active scale-down + opacity hover |
| `hover:bg-accent` on a card-shaped clickable | replace with `${interactions.card}` |
| `whileHover={{ y: -3 }}` framer-motion (dashboard project cards) | drop the framer prop, use `${interactions.card}` for the same lift via CSS |
| `hover:text-foreground` on a link | prepend `${interactions.link}` |
| Existing `focus-visible:ring-*` classes | drop in favor of the role's built-in ring; standalone elements use `${interactions.focusRing}` |

### What stays raw

- Color-tone hover shifts that aren't accent-based (e.g., `hover:bg-destructive/10` for destructive ghost buttons). Keep raw.
- Disabled state classes (`disabled:opacity-50`, `disabled:cursor-not-allowed`). Keep raw — context-dependent.
- Color overrides (`text-primary-foreground`, `text-muted-foreground`,
  etc.). Always raw.
- Layout (flex, gap, padding, etc.) — never a role concern.
- Motion-driven animations via framer-motion variants (entry, exit,
  layoutId morphs). The motion module owns those; interactions module
  is for hover/active/focus only.

## Testing strategy

### Automated

- `ui/v3/lib/interactions.test.mjs` — plain-Node assertions:
  - Module exports `interactions` (named).
  - Each role key exists.
  - `interactions.button` contains `transition-all`, `hover:opacity-90`,
    `active:scale-[0.98]`, `focus-visible:ring-2`,
    `motion-reduce:transition-none`.
  - `interactions.chip` contains `transition-colors`, `hover:bg-accent`,
    `focus-visible:ring-2`.
  - `interactions.card` contains `transition-all`, `hover:-translate-y-0.5`,
    `hover:shadow-md`, `motion-reduce:hover:translate-y-0`.
  - `interactions.iconButton` contains `hover:bg-accent`, `active:scale-95`,
    `motion-reduce:active:scale-100`.
  - `interactions.link` contains `transition-colors`, `hover:text-foreground`.
  - `interactions.focusRing` contains `ring-2`, `ring-offset-2`.

- `tests/test_interactions_module_wiring.py` — Python regression:
  - File exists.
  - Module exports `interactions` const.
  - All six role keys are present in the source.
  - `motion-reduce:` appears at least once in the file (proves
    accessibility was considered).
  - The two anchor consumer files (`workspace-shell.tsx`,
    `top-nav.tsx`) import from `@/lib/interactions`.

### Manual smoke (handoff doc)

- Hover every clickable in the workspace shell. Lifts feel uniform; no
  rhythmic noise.
- Tab through a phase. Focus rings appear consistently — never missing
  on a button.
- Click and hold on a button — visible scale-down (`active:scale-[0.98]`).
- Toggle OS reduce-motion. Press states + card lifts collapse to
  instant. Color shifts still happen.

## Risk mitigation

- **Module landing first.** Round 2 commits 4 + 5 had the module land
  before any application. Same here: commit B is module + tests (zero
  behavior change), commit C applies. Bisecting any visual regression
  is a single-commit revert.
- **Subset coverage.** Sixteen files. The other ~10 v3 routes are
  untouched.
- **Reversible per-element.** Every change is a className edit. If a
  specific spot reads wrong, the fix is one-line override.
- **No backend impact.** Pure v3 + the wiring test.
- **`motion-reduce:` first-class.** OS preference is honored from day
  one. Round 1's spinner regression (motion-reduce broke a CSS-driven
  spinner because the MotionConfig wrapper froze it) is exactly the
  kind of thing this module's overrides prevent — `motion-reduce:` is
  in the module by construction.

## Honest scoping notes

What this commit does NOT close:

1. **Standalone-page polish.** /landing, /login, /signup, /forgot,
   /reset, /help, /inbox, /migrate, /thinking, /publish, /plan-review,
   /intake. Round 4.
2. **Color / contrast pass.** Out of scope.
3. **Component-internal animation states.** Loading spinners,
   accordion, dialog. Belongs to motion module / framer-motion / radix.
4. **Generated-site interactions.** Output sites have their own.

Estimated impact of this commit alone: closes ~70% of the "buttons
feel inconsistent" complaint when navigating the workspace + dashboard.
Adds focus rings universally — major a11y win. The rest of the polish
arc closes the remaining standalone-page gaps in round 4.

## References

- Code: `ui/v3/lib/motion.ts` — duration constants imported here.
- Code: `ui/v3/lib/type.ts` — pattern for the new `lib/interactions.ts`
  shape (flat const object, role keys, `as const`).
- Code: `tests/test_motion_module_wiring.py` + `test_type_module_wiring.py`
  — patterns for the new wiring test.
- Spec: `2026-05-15-workspace-motion-polish-design.md` — round 1 spec
  with motion language context.
- Spec: `2026-05-15-workspace-typography-density-design.md` — round 2
  spec with the same module-then-apply pattern.
- Spec: `2026-05-15-round3-dashboard-typography-design.md` — round 3
  commit 1 spec, the typography sibling of this commit.
- Memory: `feedback_universal_design_not_senior.md` — focus rings + 4px
  padding for tappable targets benefit older eyes / reduced motor
  control. Not framed as "for older users" — the patterns just happen
  to be inclusive.
