# Round 2 Workspace Polish — Hand-off (2026-05-15)

This document hands round 2 of the premium-polish arc back to Marc. Six
commits landed on top of round 1's tip (`1b23bf1`). Pytest is at 836
green on the latest commit (was 809 baseline + new wiring tests).

## TL;DR

Three "safe pile" cleanups from round 1's review process + the round 2
main work (typography + density pass) + a follow-up addressing the
Sonnet review's two findings. Ships in 6 functional commits + 1 spec
commit:

```
a6b1f6c v3: round 2 / commit 5 follow-up — review fixes
266d868 v3: round 2 / commit 5 — apply type scale + density to 8 workspace files
222045c v3: round 2 / commit 4 — typography scale module
10fc9ef docs: spec for round 2 typography + density pass
b246721 v3: round 2 / commit 3 — project-name layoutId morph + MotionConfig
c146ac3 v3: round 2 / commit 2 — apply withReducedMotion consumer-side
683990c v3: round 2 / commit 1 — consolidate phase variants
```

All wiring tests + plain-Node verifiers pass (836 pytest green). ~200
lines net change across 14 files (8 v3 files + 4 lib/test files + 2
docs).

## Commits in detail

### Commit 1 — `683990c` Consolidate phase variants

`phaseEnter` + `phaseExit` were near-duplicates that the shell had to
stitch back together via `variants={phaseEnter} exit={phaseExit.exit}`.
Merged into one `phaseVariants` export with hidden/visible/exit keys so
the shell can use canonical string variant names:

```tsx
<motion.div
  variants={phaseVariants}
  initial="hidden"
  animate="visible"
  exit="exit"
/>
```

Wiring tests on both sides pin the shape (Python parametrized + plain
Node). +2 pytest tests; legacy names cannot regress.

### Commit 2 — `c146ac3` Apply withReducedMotion consumer-side

Round 1 exported `withReducedMotion()` from the motion module but never
called it. Bare variants meant the OS reduced-motion preference was
ignored everywhere. Wraps every named-variant consumer at component
scope via `useMemo`:

```tsx
const safeFadeUp = useMemo(() => withReducedMotion(fadeUp), []);
// …
<motion.div variants={safeFadeUp}>
```

Coverage: workspace-shell (3 vars), welcome-phase (1), draft-phase (2),
plan-phase (Card component's local cardVariants). The other phase files
use only inline variants — out of scope this pass.

New parametrized wiring test forbids regression: any phase file using
`variants={someConst}` must call `withReducedMotion()` somewhere. +7
pytest tests.

### Commit 3 — `b246721` Project-name layoutId morph + MotionConfig

Welcome's hero gets a small "Untitled Project" kicker above the headline
sharing `layoutId="project-name"` with the persistent TopNav slot. When
the user advances, framer-motion morphs the kicker up into the TopNav
position; on the / → /workspace push, the View Transitions API does
the same morph natively via matching `viewTransitionName`.

Hardcoded "Untitled Project" so the morph is text-identical regardless
of any stale `brief.business_name`. The welcome label is `aria-hidden` —
purely presentational; the H1 below is what screen readers announce.

Wraps the shell in `<MotionConfig reducedMotion="user">` so layoutId /
shared-element animations also honor the OS preference. The
`withReducedMotion()` helper from commit 2 only operates on Variants —
layoutId animations bypass it, so MotionConfig is the right knob.

Wiring tests pin both endpoints + the MotionConfig wrapper. +2 pytest
tests.

**Manual-test note:** Two paths for the morph:

1. `/` → `/workspace#phase=idea` (the typical home-page flow): View
   Transitions API handles it on Chrome / Edge / Safari. Firefox falls
   through to plain `router.push` with no morph.
2. Cold-load `/workspace#phase=welcome` → submit: framer's layoutId
   takes over. Both endpoints exist briefly during the welcome exit
   (TopNav re-renders synchronously when `phase` flips); framer should
   detect the layoutId match and animate.

If the morph doesn't fire visibly on path 2, the conservative fallback
is to render the TopNav project-name slot unconditionally (with empty
text on welcome) so framer always sees both endpoints. We left the
conditional render in place because the dominant path uses native View
Transitions and the conditional is what hides the TopNav project-name
on welcome (visual intent).

### Commit 4 — `222045c` Typography scale module

New `ui/v3/lib/type.ts`. Role-keyed Tailwind className strings:
display.{xl,l,m}, heading.{l,m,s}, body.{l,m,s}, label, caption,
eyebrow, mono. Sizes anchor to Tailwind defaults (text-xs=12 →
text-6xl=60); only `eyebrow` uses an arbitrary `text-[11px]` (the
conventional uppercase-label size with no Tailwind equivalent).

`font-display` (Literata) is reserved for `display.*` only. Headings +
body use Inter Variable. JetBrains Mono only via `mono`.

Two-sided wiring tests: Python pins structure + role keys, plain-Node
verifier pins per-role family rules (display.* uses font-display,
heading.* doesn't, mono uses font-mono, eyebrow has the
arbitrary-size + uppercase + tracking attributes). +7 pytest tests.

Spec at
`docs/superpowers/specs/2026-05-15-workspace-typography-density-design.md`.

### Commit 5 — `266d868` Apply type scale + density to 8 files

Migrates workspace-shell + top-nav + 6 phase files (welcome, idea,
plan, draft, edit, publish) from ad-hoc Tailwind type combinations to
the role-keyed module. ~60 typography swaps + 10 density swaps; net
+26 lines.

Density: `py-1.5`/`py-2.5` → `py-2`/`py-3`, `gap-1.5` → `gap-2`,
`p-2.5` → `p-3`, `mt-0.5` → `mt-1`. Spacing in the 8 files now snaps to
the 4px/8px grid; 2px tweaks (`p-0.5`, `gap-0.5`) stay only where
they're optical.

Notable mapping decisions (for later regression debugging):

- Rail step labels → `type.label` (text-sm font-medium); they're nav
  controls, not section headers.
- Plan card titles → `type.heading.m` (sans semibold); structural
  labels, not narrative moments — losing the serif (`font-display`) is
  intentional per the spec.
- Welcome H1, draft H1, publish H1 → `type.display.{xl,m}`; these are
  the few "narrative" moments where the serif gravitas earns its place.
- VisualEditorPanel section labels → `type.eyebrow`; exact semantic
  match (text-[11px] uppercase + tracking).

Adds the parametrized consumer-import wiring test (deferred from commit
4 for green-commit discipline). All 8 phase + shell files must import
from `@/lib/type` or pytest fails. +8 pytest tests.

**Out of scope:** Dashboard, admin, command-palette, dna-preview,
language-picker, ai-prompt-box, the-infinite-grid, block-gallery,
auth-menu — these still use ad-hoc Tailwind type. Round 3.

### Commit 6 — `a6b1f6c` Review fixes follow-up

Two findings from a Sonnet code review on commits 1-5:

- **Publishing-panel spinner.** The MotionConfig wrapper from commit 3
  halts framer's rotate animation under reduced-motion. The visual was
  a `border-t-transparent` ring whose gap rotated — frozen, that reads
  as a broken UI element. Replaced with a CSS-driven spinner using
  Tailwind `animate-spin motion-reduce:animate-none
  motion-reduce:border-t-primary` so the gap fills when motion is off.
  Also added `role="status" aria-label="Packaging your site"` for
  screen reader users who wouldn't see any indicator otherwise.
- **Version history drawer h2.** Commit 5 mapped `font-display
  text-2xl font-semibold` → `type.heading.l` (sans). The drawer is a
  modal-like aside that benefits from serif weight. Switched to
  `type.display.m`, the spec's primary suggestion for that pattern.

## Manual testing checklist

Run the v3 dev server:

```powershell
cd C:\Users\marci\pebble-engine\ui\v3
npm install     # if you haven't already
npm run dev
```

Engine on the side for previews:

```powershell
# In a separate terminal, from C:\Users\marci\pebble-engine
python pebble_engine.py
```

Then open http://localhost:3001 and walk through:

### Phase navigation (sanity)

- [ ] `/` (welcome) renders. The big H1 is visible. A small
      "Untitled Project" eyebrow sits above it (slightly muted).
- [ ] Submit a project idea. Watch the welcome → /workspace transition.
  - Chrome / Edge / Safari: native View Transition fires. Look for the
    "Untitled Project" label morphing up into the TopNav slot.
  - Firefox: framer-motion AnimatePresence fade. Same end state, less
    polish on the morph.
- [ ] In the workspace, click rail items. Active highlight slides; rail
      labels read as `text-sm font-medium`. TopNav doesn't remount.
- [ ] Open the design phase. The Add section / History / Publish cluster
      reads tight + rhythmic.

### Typography (the new pass)

- [ ] Welcome H1 still dominates the screen (text-5xl/6xl serif bold).
- [ ] Welcome subtitle ("Tell me in your own words…") reads as relaxed
      body (text-lg).
- [ ] Idea phase question heading is large + serif.
- [ ] Plan card titles read as semibold sans (NOT serif). This is
      intentional per the spec.
- [ ] Draft phase: H1 ("Pebble is building your draft.") is serif
      gravitas; subhead is small body; live-feed labels are mono +
      uppercase.
- [ ] Edit phase Visual Editor section labels are tiny uppercase
      (text-[11px] + tracking) — the eyebrow role.

### Density

- [ ] Buttons / chips have breathing room (`py-2` vs the old cramped
      `py-1.5`).
- [ ] Cards feel deliberate — no spots where the padding screams
      "off-grid" (no 2.5 / 1.5 increments visible).
- [ ] Compare to dashboard (out of scope for this pass) — dashboard will
      look slightly noisier; that's expected and is round 3.

### Reduced motion

- [ ] Enable OS-level "Reduce motion":
  - macOS: System Settings → Accessibility → Display → Reduce motion
  - Windows: Settings → Accessibility → Visual effects → Animation
    effects OFF
- [ ] Reload `/`. Re-run any phase transition.
- [ ] Phase content swaps without the cinematic fade. The shell rail
      animation collapses to instant. Layout-id morphs also instant
      (the new MotionConfig wrapper).
- [ ] Active-step glow on draft is disabled (CSS `@media reduced-motion:
      no-preference` gate, unchanged from round 1).

### Direct hash hits (regression)

- [ ] `http://localhost:3001/workspace#phase=plan` cold load lands
      directly on plan (after generating a build).
- [ ] `http://localhost:3001/workspace#phase=design` cold load lands on
      design if a build exists, otherwise bounces to welcome.

### Window resize / accessibility

- [ ] Resize the window during a phase transition. No layout glitches.
- [ ] On welcome, Tab through. Focus skips the (collapsed) rail (round
      1's a11y fix). Focus DOES NOT land on the new "Untitled Project"
      kicker (it's `aria-hidden`).

## Known concerns

1. **TypeScript keyword shadowing.** Eight files now do
   `import { type } from "@/lib/type";`. `type` is also a TS contextual
   keyword (in `import { type Foo }` for type-only imports, and in
   `type Alias = ...` declarations). The grammar disambiguates by
   position — `{ type }` with no following identifier is interpreted as
   importing the value `type` — but the worktree has no node_modules so
   I couldn't compile-check. If TS complains on `npm run build`, the
   fix is one find-replace: `import { type as t }` everywhere, then
   `type.X` → `t.X`. Pyret pytest still passes regardless.

2. **layoutId morph on path 2.** As noted in commit 3 above. Path 1
   (homepage) uses native View Transitions and works deterministically.
   Path 2 (deep-link to `#phase=welcome` then submit) relies on
   framer-motion seeing both endpoints during the brief overlap when
   TopNav re-renders. If you don't see the morph in Path 2 testing,
   that's the symptom — fix is unconditional rendering of the TopNav
   slot (commented in the spec).

3. **Pre-existing flake.** `tests/test_auth.py::test_revoke_all_falls_back_when_index_missing`
   intermittently fails in the full suite due to test-ordering
   sensitivity. Passes in isolation. NOT introduced by round 2; flagged
   in round 1's hand-off.

## Files changed

```
14 files modified across 6 commits:

ui/v3/lib/motion.ts                       (commit 1: phase-variant consolidation)
ui/v3/lib/motion.test.mjs                 (commit 1)
tests/test_motion_module_wiring.py        (commits 1, 2, 3)
ui/v3/components/workspace-shell.tsx      (commits 1, 2, 3, 5)
ui/v3/components/phases/welcome-phase.tsx (commits 2, 3, 5)
ui/v3/components/phases/draft-phase.tsx   (commits 2, 5)
ui/v3/components/phases/plan-phase.tsx    (commits 2, 5)
ui/v3/components/top-nav.tsx              (commits 3, 5)
ui/v3/lib/type.ts                         (new, commit 4)
ui/v3/lib/type.test.mjs                   (new, commit 4)
tests/test_type_module_wiring.py          (new, commits 4, 5)
ui/v3/components/phases/idea-phase.tsx    (commit 5)
ui/v3/components/phases/edit-phase.tsx    (commit 5)
ui/v3/components/phases/publish-phase.tsx (commit 5)
docs/superpowers/specs/2026-05-15-workspace-typography-density-design.md (new)
docs/superpowers/handoffs/2026-05-15-round2-handoff.md                   (this file)
```

## What's next (round 3)

Per round 1's spec + the round 2 typography spec's "honest scoping
notes":

1. **Component-level micro-interactions.** Hover / active / focus polish
   on every clickable element. Linear has obsessive transition timing on
   every button — Pebble does not. ~3-5 hours.
2. **Dashboard / admin standardization.** Apply the type module + 4px
   density to dashboard, admin, command-palette, dna-preview,
   language-picker, ai-prompt-box, block-gallery, auth-menu. ~2 hours.
3. **Color / contrast pass.** The current palette works; this is
   structural rhythm only. ~2 hours.
4. **Marketing page polish.** /landing typography + motion. ~2 hours.

Estimated round 3 scope: ~8-12 hours of focused work. Round 4 (if
needed) closes the long tail of edge cases discovered during use.

## If anything looks wrong

- Capture a screenshot, paste the URL, and tell Claude which phase you
  were in + the browser + OS.
- The specs at `docs/superpowers/specs/` are the reference for "this is
  supposed to do X."
- The wiring tests are the safety net — `python -m pytest -q` after any
  edit and watch for new red.
