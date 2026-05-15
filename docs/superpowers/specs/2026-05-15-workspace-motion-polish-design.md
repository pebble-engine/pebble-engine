# Workspace Motion Polish — Round 1 Design Spec

**Date:** 2026-05-15
**Owner:** Marc (with Claude pair-implementation)
**Scope tier:** Option 3 (full motion-first refactor, ~10 hours)
**Status:** Approved 2026-05-15, ready for implementation plan

## Summary

Make Pebble's v3 frontend feel like *one premium app* rather than a stack of
phase-routed pages. Establish a shared motion language module so every future
motion decision becomes "import a constant," not "rewrite the curve in 14
places." Restructure the workspace shell so top nav + left rail persist across
phase changes. Use framer-motion `layoutId` for shared-element animations
(rail highlight slides, project name morphs in). Opt in to the View
Transitions API on supporting browsers for the welcome → workspace
cross-route transition. Polish the build narration on the draft phase.

This is round 1 of a 3-round premium-polish arc. It closes ~60-70% of the
perceived gap to Lovable / Base44. Rounds 2-3 will address typography,
component-level micro-interactions, and density/spacing.

## Goals

- **Motion language.** A single canonical curve (Cinematic — `cubic-bezier(0.22, 1, 0.36, 1)` at 480ms) applied consistently. Reusable framer-motion variants exported from one module.
- **Persistent shell.** Top nav and left rail stay mounted across phase changes. Only the center column animates between phases.
- **Cross-phase choreography.** The rail's active-step highlight slides between rail items via `layoutId`. The project name morphs from welcome's hero into the top-nav slot. Top-nav action buttons (Publish / Add section / History) enter/exit with staggered cinematic timing.
- **Native View Transitions.** Chrome / Edge / Safari get `document.startViewTransition` on the welcome → workspace route push. Firefox + older browsers get the AnimatePresence fallback path.
- **Draft phase entrance + completion.** Existing 6-step narration + live build feed get a cinematic entrance, soft-glow active step, smooth auto-scroll on the feed, and a deliberate "Ready → opening your draft" arrival before the draft → design phase swap.
- **Accessibility.** All motion respects `prefers-reduced-motion: reduce` — variants collapse to instant when the OS pref is on.

## Non-goals (out of scope, deferred to rounds 2-3)

- Typography at rest — font sizes, weights, letter spacing across v3.
- Component-level micro-interactions on every button/input (only the ones we touch this round get polished).
- Density / spacing / whitespace audit across phases.
- Color palette refinement.
- /landing, /dashboard, /admin, /help motion polish.
- Sound design.
- /api/refine UI polish.
- The narrated-build "stages" tied to real backend progress (we keep the existing pre-timed client-side narration).
- Folding /migrate and /inbox into the workspace shell as drawers — deliberately deferred per scope decision on 2026-05-15.

## Architecture

### New files

- `ui/v3/lib/motion.ts` — motion tokens + reusable framer-motion variants.
- `ui/v3/lib/motion.test.mjs` — plain-Node verifier (same pattern as `lib/safe-redirect.test.mjs`).
- `ui/v3/lib/view-transitions.ts` — capability check + `safeStartViewTransition(callback)` wrapper.
- `ui/v3/lib/view-transitions.test.mjs` — plain-Node verifier.
- `tests/test_motion_module_wiring.py` — Python regression test pinning that phase files import from `@/lib/motion`.

### Files modified

- `ui/v3/components/workspace-shell.tsx` — restructure to lift TopNav + Rail OUT of the phase-swap; wrap phase content in `<AnimatePresence mode="wait">`.
- `ui/v3/components/phases/welcome-phase.tsx` — refactor inline motion to use `lib/motion`.
- `ui/v3/components/phases/idea-phase.tsx` — same refactor.
- `ui/v3/components/phases/plan-phase.tsx` — same refactor.
- `ui/v3/components/phases/draft-phase.tsx` — cinematic entrance, glow on active step, smooth feed scroll, deliberate "Ready" arrival.
- `ui/v3/components/phases/edit-phase.tsx` — refactor to motion module.
- `ui/v3/components/phases/publish-phase.tsx` — refactor to motion module.
- `ui/v3/components/top-nav.tsx` — `layoutId` on project name + action button slot; staggered button entry on phase change.
- `ui/v3/app/globals.css` — `view-transition-name` declarations on persistent shell elements.

### What does NOT change

- Phase routing model (still hash-based via `usePhase` hook).
- Component boundaries (still 6 phase files + shell).
- Backend engine (no Python changes).
- Auth, supabase, webhook, RLS (independent surfaces).

### Blast radius estimate

8 v3 files touched + 5 new files. ~400-500 lines net change.

## Motion language module (`lib/motion.ts`)

```ts
// Durations (ms)
export const MICRO    = 120;
export const SHORT    = 200;
export const STANDARD = 480;
export const SLOW     = 700;

// Easings
export const EASE_CINEMATIC: [number, number, number, number] =
  [0.22, 1, 0.36, 1];
export const EASE_QUIET: [number, number, number, number] =
  [0.4, 0, 0.2, 1];

// Reusable variants — concrete shapes are an implementation detail; the
// plan fills in the exact `initial` / `animate` / `exit` keyframes.
export const fadeUp:       Variants;   // opacity 0→1, y 8→0, STANDARD, EASE_CINEMATIC
export const phaseEnter:   Variants;   // opacity 0→1, y 12→0, STANDARD, EASE_CINEMATIC
export const phaseExit:    Variants;   // opacity 1→0, y 0→-8, SHORT
export const railStep:     Variants;   // staggered fadeUp for rail items
export const chipDeck:     Variants;   // staggered slide-in from right for action chips
export const cardHover:    Variants;   // y -2, shadow lift, SHORT
export const dropletPulse: Variants;   // scale 1→1.06→1, SLOW, infinite

// Accessibility
export function prefersReducedMotion(): boolean { ... }
export function withReducedMotion<V>(variant: V): V { ... } // returns instant if user prefers reduced motion
```

Every motion in the v3 app becomes `<motion.div variants={fadeUp}>` instead of inline durations. Future polish becomes "add a variant" rather than "rewrite the curve."

## Shell restructure & phase transitions

### Today

`workspace-shell.tsx` renders:
- `<TopNav>` inside the flex container
- `{showLeftRail && <motion.aside>` (conditional — remounts on every welcome ↔ idea transition)
- Phase content rendered as sibling `<div>`s with `{phase === "idea" && ...}` guards (instant swap, no exit animation)

### After

```
<flex-container>
  <TopNav projectName={projectName} rightSlot={topNavRightSlot} />  // persists
  <flex>
    <Rail visible={phase !== "welcome"} />  // persists; opacity/width animates on welcome-toggle
    <AnimatePresence mode="wait">
      <motion.div key={phase} variants={phaseEnter} initial="hidden" animate="visible" exit="exit">
        {renderPhase(phase)}
      </motion.div>
    </AnimatePresence>
  </flex>
</flex-container>
```

`mode="wait"` ensures the outgoing phase finishes its exit before the incoming phase mounts — no overlap. Reduced-motion path bypasses AnimatePresence so phases swap instantly.

### State preservation

AnimatePresence with `mode="wait"` unmounts the outgoing phase. Phase-local state (form fields, in-progress brief) MUST live in the shell or in `sessionStorage` so it survives the unmount. The current codebase already follows this pattern (state.ts is the source of truth — verified by reading `ui/v3/lib/state.ts`). No state-lift work needed.

## Cross-phase shared elements (the "wow" pieces)

Framer-motion's `layoutId` and `layout` props animate elements between positions when they re-mount with the same id.

### Rail active highlight

The `bg-primary/15` block on the active rail item gets `layoutId="rail-active"`. When `phase` changes, framer animates the highlight from its old position to its new position rather than fading in/out.

### Project name in TopNav

The `<h1>Pebble.</h1>` element on the welcome phase gets `layoutId="project-name"`. The project-name slot in TopNav uses the same `layoutId`. On welcome → idea transition, framer morphs the big hero text into the TopNav slot.

### TopNav action buttons

`<motion.div variants={chipDeck}>` wraps the right-slot button cluster. On phase change to `design`, the buttons stagger in from the right with 60ms delays. On phase change away from `design`, they exit back to the right.

## View Transitions API integration

```ts
// ui/v3/lib/view-transitions.ts
export function supportsViewTransitions(): boolean {
  return typeof document !== "undefined"
    && typeof (document as any).startViewTransition === "function";
}

export function safeStartViewTransition(callback: () => void): void {
  if (supportsViewTransitions()) {
    (document as any).startViewTransition(callback);
  } else {
    callback();
  }
}
```

### Applied in

- `workspace-shell.tsx`'s `handleAdvanceFromWelcome()` wraps the `router.push("/workspace#phase=idea")` call in `safeStartViewTransition`. Chrome / Edge / Safari morph the welcome layout into the workspace layout natively; Firefox just navigates.

### Element marking

The codebase uses Tailwind utility classes, not semantic class names, so the
`view-transition-name` declarations go on the persistent shell elements via
inline `style`:

```tsx
<header style={{ viewTransitionName: "top-nav" }}>…</header>
<aside  style={{ viewTransitionName: "rail" }}>…</aside>
```

The brand-text `view-transition-name: "brand"` is set on the welcome-phase
hero text AND on the TopNav project-name slot — same name on both sides of
the route change means the browser's native engine morphs between layouts.

### Fallback

Firefox (no View Transitions support as of 2026-05) and older Safari go through `cb()` directly — the existing framer-motion AnimatePresence handles the inter-phase transitions. Firefox users see the Option 2 path; same code, same components, just no native cross-route morph.

## Draft phase polish

### Entrance

Current: instant render.
New cinematic stagger (delays from mount, ms):
1. **0ms** — Pebble droplet: scale 0 → 1 + opacity 0 → 1 over STANDARD (480ms)
2. **200ms** — Headline ("Pebble is building your draft."): fadeUp
3. **320ms** — Subhead ("Usually 2-3 minutes…"): fadeUp
4. **480ms** — Macro checklist starts: railStep stagger, 60ms per item (6 items → 360ms total)
5. **920ms** — Live build feed: fadeUp

Total entrance settles around 1.4s; the feed is already fading in while
the checklist items finish staggering so it feels continuous rather than
phased.

### Active step polish

Current: scale 1.05 + bg color swap.
New: same scale + a soft glow ring (`box-shadow: 0 0 0 4px var(--accent-1) / 0.18`), pulses with the 1.4s interval already in place. The active step's label gets a subtle weight bump (font-weight 500 → 600).

### Live feed

Current: instant text append, `behavior: "instant"` auto-scroll.
New: each new line wrapped in a framer-motion variant — MICRO (120ms) fade + 4px translate. Auto-scroll uses `behavior: "smooth"` with a per-line debounce so the user can scroll up to read older lines without being yanked back.

### Completion handoff (draft → design)

Current: `setTimeout(() => setPhase("design"), 600)` — instant phase swap.
New:
1. The shell sets `generateDone = true`.
2. Draft phase's `done` effect pulses the final macro-checklist step (scale 1 → 1.06 → 1) with the cinematic curve for 800ms.
3. Phase swap fires via AnimatePresence. Draft's exit variant fades the central content over STANDARD; design's enter variant slides the preview iframe in from below over STANDARD.
4. Total handoff feels like a deliberate "and… we're done" beat, not a jump cut.

## Testing strategy

### New automated tests

- `ui/v3/lib/motion.test.mjs` (plain Node, no test runner needed):
  - All exported constants exist with right type
  - Variants are valid framer-motion shape (have `initial`, `animate` keys)
  - `prefersReducedMotion()` returns boolean
- `ui/v3/lib/view-transitions.test.mjs` (plain Node):
  - `supportsViewTransitions()` returns `false` in Node (no `document`)
  - `safeStartViewTransition(cb)` invokes `cb` synchronously when unsupported
- `tests/test_motion_module_wiring.py` (Python regression — same pattern as `test_safe_redirect_wiring.py`):
  - `ui/v3/lib/motion.ts` exists and exports expected tokens
  - Every phase file under `ui/v3/components/phases/` imports from `@/lib/motion`
  - `workspace-shell.tsx` imports from `@/lib/motion` and `@/lib/view-transitions`

### Manual testing checklist

Documented in this spec; reviewed before merge:

- [ ] Tab through every phase: welcome → idea → plan → draft → design → publish
- [ ] Back navigation: design → plan → idea → welcome
- [ ] Direct hash hit: load `/workspace#phase=plan` cold
- [ ] Direct hash hit: load `/workspace#phase=design` cold (no build → bounces to welcome/idea)
- [ ] Reduced motion: enable OS pref → all motion collapses to instant
- [ ] Chrome: View Transitions visibly fire on welcome → workspace push
- [ ] Firefox: same transition uses AnimatePresence fallback, still smooth
- [ ] Safari: View Transitions fire
- [ ] Reload mid-build: state persists, phase resumes correctly
- [ ] Resize window during transition: no layout glitches
- [ ] Live feed: scroll up during build, new lines don't yank scroll back
- [ ] Completion handoff: "Ready" pulse visible before phase swap

## Risk mitigation

- **Commits land in 6-7 logical chunks** so bisecting a regression is fast:
  1. `lib/motion.ts` module + tests (zero behavior change yet — pure addition)
  2. Phase files refactored to import from motion module (behavior preserved)
  3. Shell restructure (rail/nav persistence) + AnimatePresence wrap
  4. Cross-phase shared elements (`layoutId` work)
  5. View Transitions API + element marking
  6. Draft phase entrance + completion polish
  7. Wiring tests + manual-checklist doc

- **No backend changes** — engine, auth, RLS, webhooks all untouched. If something breaks, the blast radius is contained to v3.

- **Reduced motion fallback** is the FIRST thing tested in each new motion path, not last. A `prefersReducedMotion()` returning true should short-circuit every animation to instant.

- **Manual cross-browser smoke** before merge. Chrome + Firefox at minimum; Safari if Marc has access.

## Honest scoping notes

This spec is round 1 of 3. What it does not fix, in order of next-round priority:

1. **Typography pass** — font sizes, weights, line heights, letter spacing across the v3 design system. Lovable's premium feel is ~30% typography; this round doesn't touch it.
2. **Component-level micro-interactions** — every clickable element gets a refined hover/active/focus treatment. Some lands here via `cardHover` variant, but a full pass requires its own session.
3. **Density / spacing audit** — Lovable is more breathable than Pebble in places; rebalancing whitespace is its own pass.

Estimated impact of this spec alone: ~60-70% of the perceived gap to Lovable closes. Rounds 2-3 close the rest.

## References

- Memory: `feedback_too_many_pages_study_lovable.md` — Marc's 2026-05-15 feedback that drove this work.
- Memory: `project_lovable_parity_backlog.md` — items deliberately NOT copied from Lovable (persistent chat, code mode).
- Memory: `project_pebble_product_vision.md` — visual direction (soft warm white, stone gray, charcoal text, calm premium).
- Code: `ui/v3/components/workspace-shell.tsx` — current shell.
- Code: `ui/v3/components/phases/use-phase.ts` — phase routing model that's preserved.
- Code: `ui/v3/lib/safe-redirect.ts` + `ui/v3/lib/safe-redirect.test.mjs` — pattern for the new `lib/motion.ts` + test harness.
- Code: `tests/test_safe_redirect_wiring.py` — pattern for `tests/test_motion_module_wiring.py`.
- W3C: [View Transitions API spec](https://www.w3.org/TR/css-view-transitions-1/).
