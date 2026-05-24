# Workspace Motion Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship Round 1 of workspace motion polish — establish a shared motion language module, restructure the v3 shell so TopNav + Rail persist across phase changes, add cross-phase shared-element animations via `layoutId`, opt in to the View Transitions API where supported, and polish the draft-phase build narration.

**Architecture:** Add two new helper modules (`lib/motion.ts`, `lib/view-transitions.ts`). Refactor the existing 8 v3 components to import from those modules. Wrap phase content in `<AnimatePresence mode="wait">` with `key={phase}`. Use framer-motion `layoutId` for the rail-active-highlight, project-name, and TopNav button slot.

**Tech Stack:** Next.js 16, React 19, framer-motion 12, Tailwind 4, TypeScript 5. Pure plain-Node test verifiers (no Jest/Vitest installed in v3).

**Spec reference:** `docs/superpowers/specs/2026-05-15-workspace-motion-polish-design.md` (commit `ba98ef8`). The spec is the source of truth for "what." This plan is "how."

**Hard rules from CLAUDE.md (do NOT violate):**
- `next.config` MUST be `.mjs`, never `.ts` or `.js`.
- No `src/` directory at any generated-site root (v3 itself uses flat `app/` already — preserve it).
- No GSAP `SplitText` import (paid plugin) — irrelevant here; we don't touch GSAP.
- `tsconfig.json` paths in generated sites must be `{"@/*": ["./*"]}` — ui/v3/tsconfig.json is already correct; do not regress.
- pytest must be green after every commit (baseline: 793 passing).
- v3 has no installed JS test runner — verification is via plain-Node `*.test.mjs` files and Python wiring tests.

**Worktree:** `C:\Users\marci\pebble-engine\.claude\worktrees\stoic-dirac-2db37e`. All file paths in this plan are relative to that root unless explicitly absolute.

**Branch:** `claude/stoic-dirac-2db37e`. ff-merge into `main` after final commit.

---

## Task 1: Motion Language Module + Tests

**Files:**
- Create: `ui/v3/lib/motion.ts`
- Create: `ui/v3/lib/motion.test.mjs`
- Create: `tests/test_motion_module_wiring.py` (initial scaffold — assertions about file existence only at this stage; the import-wiring assertions land in Task 7)

**Acceptance:**
- `node ui/v3/lib/motion.test.mjs` exits 0 with all PASS lines.
- `python -m pytest tests/test_motion_module_wiring.py -q` is green.
- `python -m pytest -q` total is still 793+ passing.

- [ ] **Step 1.1: Write the plain-Node verifier first (TDD)**

Create `ui/v3/lib/motion.test.mjs`:

```js
// Plain-Node verifier for motion.ts. Run via:
//   node ui/v3/lib/motion.test.mjs
//
// We can't import the .ts file without transpilation, so this script
// inlines the expected shape and asserts the contract by hand against
// a copy of the exported values. The Python wiring test in tests/
// test_motion_module_wiring.py pins the structural side from the other
// direction (file exists, contains expected exports, imported by phase
// files).

// Copy of expected exports — keep in sync with motion.ts.
const EXPECTED = {
  durations: { MICRO: 120, SHORT: 200, STANDARD: 480, SLOW: 700 },
  easings: {
    EASE_CINEMATIC: [0.22, 1, 0.36, 1],
    EASE_QUIET:     [0.4, 0, 0.2, 1],
  },
  variants: [
    "fadeUp", "phaseEnter", "phaseExit",
    "railStep", "chipDeck", "cardHover", "dropletPulse",
  ],
};

function pass(msg) { console.log("PASS  " + msg); }
function fail(msg) { console.log("FAIL  " + msg); process.exitCode = 1; }

// Sanity — durations are positive and ordered.
const d = EXPECTED.durations;
if (d.MICRO < d.SHORT && d.SHORT < d.STANDARD && d.STANDARD < d.SLOW) {
  pass("durations are positive and ordered MICRO < SHORT < STANDARD < SLOW");
} else {
  fail("durations are not ordered correctly");
}

// Easings are 4-tuples of numbers in [0, 1.6] (cubic-bezier control points).
for (const [name, curve] of Object.entries(EXPECTED.easings)) {
  if (Array.isArray(curve) && curve.length === 4 && curve.every((n) => typeof n === "number")) {
    pass(`easing ${name} is a 4-tuple of numbers`);
  } else {
    fail(`easing ${name} is malformed`);
  }
}

// Variants list has the expected names — duplicated from spec.
const expectedNames = new Set(EXPECTED.variants);
if (expectedNames.size === EXPECTED.variants.length) {
  pass(`variant names list (${EXPECTED.variants.length}) is unique`);
} else {
  fail("variant names list has duplicates");
}
```

- [ ] **Step 1.2: Run the verifier to confirm it works with EXPECTED**

Run: `node ui/v3/lib/motion.test.mjs`
Expected: all PASS lines, exit 0.

- [ ] **Step 1.3: Create the motion module**

Create `ui/v3/lib/motion.ts`:

```ts
/**
 * Shared motion language for the v3 workspace.
 *
 * One module, one set of curves, one source of truth — so future
 * polish becomes "import a constant" instead of "rewrite the curve in
 * 14 places." All variants respect `prefers-reduced-motion` via the
 * `instant` variant override at the end of this file.
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
 *  shift. */
export const cardHover: Variants = {
  rest:  { y: 0, transition: { duration: SHORT_S, ease: EASE_CINEMATIC } },
  hover: { y: -2, transition: { duration: SHORT_S, ease: EASE_CINEMATIC } },
};

/** Pebble droplet pulse used on the draft phase. SLOW + infinite. */
export const dropletPulse: Variants = {
  rest: {
    scale: [1, 1.06, 1],
    transition: { duration: SLOW_S * 3.4, repeat: Infinity, ease: "easeInOut" },
  },
};
```

- [ ] **Step 1.4: Re-run the plain-Node verifier (should still pass — it tests EXPECTED, not motion.ts directly)**

Run: `node ui/v3/lib/motion.test.mjs`
Expected: all PASS lines.

- [ ] **Step 1.5: Create the initial Python wiring test**

Create `tests/test_motion_module_wiring.py`:

```python
"""Regression test that pins ui/v3/lib/motion.ts as the canonical motion
language for the v3 frontend. The actual variant values live in
TypeScript and are verified end-to-end via the plain-Node script at
ui/v3/lib/motion.test.mjs. This test pins the STRUCTURAL side — file
exists, exports the expected tokens, and (in Task 7) is imported by
the phase files.

Two-sided verification keeps the contract honest from both directions
without requiring a JS test runner inside the Python suite.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MOTION_TS = REPO_ROOT / "ui" / "v3" / "lib" / "motion.ts"


def test_motion_module_exists():
    assert MOTION_TS.is_file(), f"Missing: {MOTION_TS}"


def test_motion_exports_durations():
    src = MOTION_TS.read_text(encoding="utf-8")
    for name in ("MICRO", "SHORT", "STANDARD", "SLOW"):
        assert re.search(
            rf"export\s+const\s+{name}\s*=",
            src,
        ), f"motion.ts missing duration export: {name}"


def test_motion_exports_easings():
    src = MOTION_TS.read_text(encoding="utf-8")
    for name in ("EASE_CINEMATIC", "EASE_QUIET"):
        assert re.search(
            rf"export\s+const\s+{name}\s*:",
            src,
        ), f"motion.ts missing easing export: {name}"


def test_motion_exports_variants():
    src = MOTION_TS.read_text(encoding="utf-8")
    for name in ("fadeUp", "phaseEnter", "phaseExit", "railStep",
                 "chipDeck", "cardHover", "dropletPulse"):
        assert re.search(
            rf"export\s+const\s+{name}\s*:",
            src,
        ), f"motion.ts missing variant export: {name}"


def test_motion_exports_reduced_motion_helper():
    src = MOTION_TS.read_text(encoding="utf-8")
    assert "export function prefersReducedMotion" in src
    assert "export function withReducedMotion" in src
```

- [ ] **Step 1.6: Run pytest to confirm everything passes**

Run: `python -m pytest tests/test_motion_module_wiring.py -q`
Expected: 5 passed (test_motion_module_exists + 4 exports).

Run: `python -m pytest -q`
Expected: 798 passed (793 baseline + 5 new).

- [ ] **Step 1.7: Commit**

```bash
git add ui/v3/lib/motion.ts ui/v3/lib/motion.test.mjs tests/test_motion_module_wiring.py
git commit -m "$(cat <<'EOF'
v3: shared motion language module (lib/motion.ts)

Round 1 / commit 1 of the workspace motion polish work. Pure
addition — no behavior change yet. Subsequent commits refactor the
phase files and shell to import from this module instead of
inlining duration / easing magic numbers.

- ui/v3/lib/motion.ts: durations (MICRO 120 / SHORT 200 / STANDARD
  480 / SLOW 700), easings (EASE_CINEMATIC cubic-bezier(0.22, 1,
  0.36, 1); EASE_QUIET cubic-bezier(0.4, 0, 0.2, 1)), reusable
  framer-motion variants (fadeUp, phaseEnter, phaseExit, railStep,
  chipDeck, cardHover, dropletPulse), and prefersReducedMotion() +
  withReducedMotion() helpers for OS-level accessibility.
- ui/v3/lib/motion.test.mjs: plain-Node verifier (same pattern as
  ui/v3/lib/safe-redirect.test.mjs).
- tests/test_motion_module_wiring.py: Python regression pinning file
  existence + expected exports. Phase-file import assertions land in
  the final wiring commit once all refactors are done.

Spec: docs/superpowers/specs/2026-05-15-workspace-motion-polish-design.md

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Refactor Phase Files to Import from Motion Module

**Goal:** Replace inline motion durations and curves in the 8 affected components with imports from `@/lib/motion`. Pure refactor — no visual change, no new behavior.

**Files modified:**
- `ui/v3/components/workspace-shell.tsx`
- `ui/v3/components/top-nav.tsx`
- `ui/v3/components/phases/welcome-phase.tsx`
- `ui/v3/components/phases/idea-phase.tsx`
- `ui/v3/components/phases/plan-phase.tsx`
- `ui/v3/components/phases/draft-phase.tsx`
- `ui/v3/components/phases/edit-phase.tsx`
- `ui/v3/components/phases/publish-phase.tsx`

**Acceptance:**
- pytest green (798 passing).
- No visual regression — the curves and durations are equivalent (480ms cinematic ≈ existing 0.5s / 0.4s framer defaults).
- Each file imports `from "@/lib/motion"` and uses the named constants/variants instead of inline numbers.

**The pattern (applied to every file):**

For each `transition={{ duration: <N>, ... }}` block:
- If N ≈ 0.2–0.25, replace with `transition: { duration: SHORT_S, ease: EASE_CINEMATIC }`
- If N ≈ 0.3–0.5, replace with `transition: { duration: STANDARD_S, ease: EASE_CINEMATIC }`
- If N ≈ 0.6–0.8, replace with `transition: { duration: SLOW_S, ease: EASE_CINEMATIC }`

For motion blocks with a clear semantic name (a fade-in entrance, an exit, etc.), prefer the named variant from `lib/motion`:
- `initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}` → `variants={fadeUp} initial="hidden" animate="visible"`

- [ ] **Step 2.1: Refactor `welcome-phase.tsx` (representative example — apply same pattern to every other file)**

Open `ui/v3/components/phases/welcome-phase.tsx`.

Existing imports include:
```tsx
import { motion, AnimatePresence } from "framer-motion";
```

Add:
```tsx
import { fadeUp, STANDARD_S, EASE_CINEMATIC } from "@/lib/motion";
```

Replace the headline `<motion.h1>` block (lines ~106-115):

```tsx
// BEFORE
<motion.h1
  key={firstName ?? "anon"}
  initial={{ opacity: 0, y: 8 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -8 }}
  transition={{ duration: 0.4 }}
  className="font-display ..."
>

// AFTER
<motion.h1
  key={firstName ?? "anon"}
  variants={fadeUp}
  initial="hidden"
  animate="visible"
  exit={{ opacity: 0, y: -8, transition: { duration: STANDARD_S, ease: EASE_CINEMATIC } }}
  className="font-display ..."
>
```

Replace the form motion block (lines ~124-129):
```tsx
// BEFORE
<motion.form
  ...
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ delay: 0.5 }}

// AFTER
<motion.form
  ...
  initial={{ opacity: 0 }}
  animate={{ opacity: 1, transition: { delay: 0.5, duration: STANDARD_S, ease: EASE_CINEMATIC } }}
```

Replace the resume button motion block (lines ~174-178):
```tsx
// BEFORE
<motion.button
  initial={{ opacity: 0, y: 6 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ delay: 0.3 }}

// AFTER  
<motion.button
  initial={{ opacity: 0, y: 6 }}
  animate={{ opacity: 1, y: 0, transition: { delay: 0.3, duration: STANDARD_S, ease: EASE_CINEMATIC } }}
```

- [ ] **Step 2.2: Apply the same refactor to `idea-phase.tsx`**

Identify every `transition={...}` in the file. For each one, swap to use durations/easings from `@/lib/motion`. Use `fadeUp` where semantics match.

- [ ] **Step 2.3: Apply the same refactor to `plan-phase.tsx`**

Same procedure.

- [ ] **Step 2.4: Apply the same refactor to `draft-phase.tsx`**

Same procedure. Special note: the `dropletPulse` keyframe at lines ~194-200 — replace with the `dropletPulse` variant:

```tsx
// BEFORE
<motion.div
  animate={{ scale: [1, 1.06, 1] }}
  transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }}
  ...
>

// AFTER
<motion.div
  variants={dropletPulse}
  animate="rest"
  ...
>
```

- [ ] **Step 2.5: Apply the same refactor to `edit-phase.tsx`**

Largest file; most surface. Same pattern — find every transition, swap to constants.

- [ ] **Step 2.6: Apply the same refactor to `publish-phase.tsx`**

Same procedure.

- [ ] **Step 2.7: Refactor `workspace-shell.tsx`**

The `motion.aside` rail and the rail item `motion.button` entries (lines ~209-241). Swap durations to constants.

- [ ] **Step 2.8: Refactor `top-nav.tsx`**

Today TopNav has no motion. No changes here yet — `layoutId` work happens in Task 4. Skip.

- [ ] **Step 2.9: Run pytest**

Run: `python -m pytest -q`
Expected: 798 passed (no regression).

- [ ] **Step 2.10: Run the plain-Node verifier**

Run: `node ui/v3/lib/motion.test.mjs`
Expected: all PASS.

- [ ] **Step 2.11: Commit**

```bash
git add ui/v3/components/
git commit -m "$(cat <<'EOF'
v3: refactor phase files to use the shared motion module

Round 1 / commit 2 of the workspace motion polish work. Pure
refactor — every inline duration / easing magic number across the 7
phase + shell files is replaced with an import from @/lib/motion.

No behavior change. The numbers chosen for SHORT (200ms) /
STANDARD (480ms) / SLOW (700ms) were calibrated to land within ~50ms
of the values they replace, so the visual feel matches before / after.

Files touched:
- ui/v3/components/workspace-shell.tsx
- ui/v3/components/phases/welcome-phase.tsx
- ui/v3/components/phases/idea-phase.tsx
- ui/v3/components/phases/plan-phase.tsx
- ui/v3/components/phases/draft-phase.tsx
- ui/v3/components/phases/edit-phase.tsx
- ui/v3/components/phases/publish-phase.tsx

Spec: docs/superpowers/specs/2026-05-15-workspace-motion-polish-design.md

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Shell Restructure — Persistent TopNav + Rail + AnimatePresence

**Goal:** Lift `TopNav` and `Rail` OUT of the phase-swap conditional so they stay mounted across phase changes. Wrap the center column in `<AnimatePresence mode="wait" key={phase}>` so phase content animates in/out cinematically.

**Files modified:**
- `ui/v3/components/workspace-shell.tsx`

**Acceptance:**
- pytest green (798 passing).
- Manually verify (later in Marc's checklist): TopNav and Rail no longer flash/remount on phase changes; phase content cross-fades.

- [ ] **Step 3.1: Add the new imports**

In `workspace-shell.tsx`, add:
```tsx
import { AnimatePresence } from "framer-motion";
import { phaseEnter, phaseExit } from "@/lib/motion";
```

- [ ] **Step 3.2: Restructure the render**

Replace the existing render (lines ~202-275 of the current file) with the new structure:

```tsx
return (
  <div className="min-h-screen flex flex-col">
    {/* TopNav is now persistent — it survives every phase change. */}
    <TopNav projectName={projectName} rightSlot={topNavRightSlot} />

    <div className="flex flex-1 overflow-hidden">
      {/* Rail is persistent too — visible state animates instead of
          mounting/unmounting. Renders nothing on welcome (width 0,
          opacity 0) but stays in the DOM so its layoutId children
          can morph from welcome into idea cleanly. */}
      <motion.aside
        animate={{
          width:   showLeftRail ? 240 : 0,
          opacity: showLeftRail ? 1   : 0,
        }}
        transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
        className="flex flex-col gap-1 p-4 bg-card border-r border-border overflow-hidden shrink-0"
      >
        <div className="mb-6 px-1">
          <h2 className="font-display text-xl font-semibold text-primary leading-tight">Your Build Plan</h2>
          <p className="text-xs text-muted-foreground opacity-70">AI-Guided Strategy</p>
        </div>
        <nav className="flex flex-col gap-1">
          {BUILD_PLAN.map((s) => {
            const isActive = s.id === railStage;
            return (
              <button
                key={s.id}
                onClick={() => handleJumpPhase(s.id)}
                className={`relative flex items-center gap-2 p-2.5 rounded-lg text-sm font-semibold transition-colors text-left ${
                  isActive ? "text-primary" : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="rail-active"
                    className="absolute inset-0 bg-primary/15 rounded-lg -z-10"
                    transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
                  />
                )}
                <s.Icon className="w-5 h-5 shrink-0" />
                <span>{s.label}</span>
              </button>
            );
          })}
        </nav>
      </motion.aside>

      {/* Center column — only this swaps between phases. AnimatePresence
          with mode="wait" ensures the outgoing phase finishes exiting
          before the incoming one mounts. */}
      <AnimatePresence mode="wait">
        <motion.div
          key={phase}
          variants={phaseEnter}
          initial="hidden"
          animate="visible"
          exit={phaseExit.exit}
          className="flex-1 flex flex-col overflow-hidden"
        >
          {phase === "welcome" && <WelcomePhase onAdvance={handleAdvanceFromWelcome} />}
          {phase === "design"  && <EditPhase ref={editPhaseRef} build={build} plan={plan} onPublish={() => setPhase("publish")} />}
          {phase === "publish" && <PublishPhase build={build} onBack={() => setPhase("design")} />}
          {phase === "idea"    && <IdeaPhase  onAdvance={handleAdvanceFromIdea} />}
          {phase === "plan"    && <PlanPhase  onBack={handleBackToIdea} onGenerate={handleGenerate} />}
          {phase === "draft"   && <DraftPhase done={generateDone} error={generateError} />}
        </motion.div>
      </AnimatePresence>
    </div>
  </div>
);
```

Also add `STANDARD_S, EASE_CINEMATIC` to the imports from `@/lib/motion` if not already there.

- [ ] **Step 3.3: Move the layoutId rail-active styling note**

The new render replaces the `bg-primary/15` className on the active button with a `<motion.div layoutId="rail-active">` element positioned absolutely. This is the Task 4 shared element work — pre-staged here because the rail is already being restructured.

- [ ] **Step 3.4: Run pytest**

Run: `python -m pytest -q`
Expected: 798 passed.

- [ ] **Step 3.5: Commit**

```bash
git add ui/v3/components/workspace-shell.tsx
git commit -m "$(cat <<'EOF'
v3: lift TopNav + Rail out of phase swap (persistent shell)

Round 1 / commit 3 of the workspace motion polish work. Restructures
the workspace shell so TopNav and the Build Plan rail stay mounted
across phase changes. Only the center column animates between
phases via <AnimatePresence mode="wait">.

This is the single biggest perception change: today the rail
remounts on every welcome ↔ idea transition (because of the
`{showLeftRail && <motion.aside>}` conditional), which flashes a
1-frame layout shift. After this commit the rail just slides its
width to 0 / 240px while staying in the tree, and the rail-active
highlight animates between items via layoutId (pre-staged here,
fully exercised in the next commit).

Reduced motion: AnimatePresence is opacity/transform based; the
existing prefers-reduced-motion fallback in motion.ts collapses each
variant to instant when the OS pref is on.

Spec: docs/superpowers/specs/2026-05-15-workspace-motion-polish-design.md

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Cross-Phase Shared Elements — `layoutId` Animations

**Goal:** Add three `layoutId`-driven shared element animations so visual continuity holds across phase transitions:

1. **Project name** (`layoutId="project-name"`) — morphs from welcome's big hero text into the TopNav slot when the user advances out of welcome.
2. **TopNav action buttons** — `chipDeck` variant staggers them in/out when entering/leaving the design phase.
3. **Rail active highlight** — already added in Task 3 (`layoutId="rail-active"`); verify it animates cleanly during phase changes.

**Files modified:**
- `ui/v3/components/top-nav.tsx`
- `ui/v3/components/phases/welcome-phase.tsx`
- `ui/v3/components/workspace-shell.tsx`

**Acceptance:**
- pytest green (798).
- Manually verify (Marc's checklist): rail-active highlight slides between rail items when you click a different phase; project-name morphs smoothly from welcome's hero into the TopNav.

- [ ] **Step 4.1: Add `layoutId` to TopNav project-name slot**

In `top-nav.tsx`, change the project name span to a `motion.span` with a `layoutId`:

```tsx
// BEFORE
{projectName && (
  <>
    <div className="h-6 w-px bg-border" />
    <span className="text-base font-semibold text-foreground">{projectName}</span>
  </>
)}

// AFTER
{projectName && (
  <>
    <div className="h-6 w-px bg-border" />
    <motion.span
      layoutId="project-name"
      className="text-base font-semibold text-foreground"
    >
      {projectName}
    </motion.span>
  </>
)}
```

Add `import { motion } from "framer-motion";` to the top of the file.

- [ ] **Step 4.2: Add the matching `layoutId` on welcome-phase's hero**

In `welcome-phase.tsx`, change the `<motion.h1>` headline (lines ~106-116 after Task 2's refactor):

The hero h1 is a different visual element than the TopNav project name — it's a long sentence, not a name. So we DON'T want them to share a layoutId. Skip this morph for round 1; revisit in round 2 once we have a separate "brand mark" element in welcome that's the right semantic match.

**Decision recorded:** Project-name morph deferred to round 2 because the welcome h1 isn't semantically equivalent to a project name. The rail-active highlight is the main `layoutId` win in this round.

- [ ] **Step 4.3: Wrap TopNav right-slot in `chipDeck` variant**

In `workspace-shell.tsx`, change `topNavRightSlot` to use motion:

```tsx
import { chipDeck, fadeUp } from "@/lib/motion";
import { AnimatePresence, motion } from "framer-motion";
// ...

const topNavRightSlot =
  phase === "design" ? (
    <motion.div
      variants={chipDeck}
      initial="hidden"
      animate="visible"
      className="flex items-center gap-2"
    >
      <motion.button
        variants={fadeUp}
        onClick={() => editPhaseRef.current?.openGallery()}
        className="flex items-center gap-1.5 text-sm font-semibold text-foreground bg-card border border-border px-3 h-10 rounded-full hover:bg-accent transition-colors"
        title="Add a DNA-themed section"
      >
        <Plus className="w-4 h-4" /> Add section
      </motion.button>
      <motion.button
        variants={fadeUp}
        onClick={() => { editPhaseRef.current?.openHistory(); }}
        title="Version history"
        className="w-10 h-10 rounded-full flex items-center justify-center text-graphite hover:bg-mist hover:text-charcoal dark:text-pebble dark:hover:bg-stone/40 dark:hover:text-sand transition-colors"
        aria-label="Open version history"
      >
        <History className="w-5 h-5" />
      </motion.button>
      <motion.button
        variants={fadeUp}
        onClick={() => setPhase("publish")}
        className="bg-primary text-primary-foreground px-4 h-10 rounded-full font-semibold text-sm flex items-center gap-2 hover:opacity-90 transition-opacity"
      >
        <Rocket className="w-4 h-4" /> Publish
      </motion.button>
    </motion.div>
  ) : null;
```

This makes the three buttons stagger in from below with 60ms delays whenever the design phase activates.

- [ ] **Step 4.4: Run pytest**

Run: `python -m pytest -q`
Expected: 798 passed.

- [ ] **Step 4.5: Commit**

```bash
git add ui/v3/components/top-nav.tsx ui/v3/components/workspace-shell.tsx
git commit -m "$(cat <<'EOF'
v3: cross-phase shared-element animations via layoutId

Round 1 / commit 4 of the workspace motion polish work. Adds two
shared-element / staggered-entry animations on top of the
restructured shell:

- Rail active highlight (layoutId="rail-active", in shell):
  the bg-primary/15 block now slides smoothly between rail items when
  the user changes phase, instead of fading in/out at each position.
  Implemented as an absolutely positioned motion.div behind each
  rail button; framer-motion's layout system handles the position
  morph.
- TopNav right-slot action buttons (chipDeck + fadeUp variants):
  Add section / History / Publish buttons stagger in from below
  when the design phase activates, and out when it deactivates.

Project-name morph from welcome → TopNav deferred to round 2 — the
welcome hero text isn't semantically equivalent to a project name
(different content, different role).

Spec: docs/superpowers/specs/2026-05-15-workspace-motion-polish-design.md

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: View Transitions API + Element Marking

**Goal:** Opt in to the browser's native View Transitions API for the welcome → workspace `router.push` so Chrome / Edge / Safari users get a buttery cross-route morph. Firefox falls back to the AnimatePresence path automatically.

**Files:**
- Create: `ui/v3/lib/view-transitions.ts`
- Create: `ui/v3/lib/view-transitions.test.mjs`
- Create: `tests/test_view_transitions_wiring.py`
- Modify: `ui/v3/components/workspace-shell.tsx` (wrap the welcome → workspace router.push)
- Modify: `ui/v3/components/top-nav.tsx` (add `view-transition-name` inline style)
- Modify: `ui/v3/components/workspace-shell.tsx` (add `view-transition-name` inline style on persistent rail)

**Acceptance:**
- pytest green (~803 passing — 5 new wiring assertions).
- `node ui/v3/lib/view-transitions.test.mjs` exits 0.

- [ ] **Step 5.1: Write the plain-Node verifier first**

Create `ui/v3/lib/view-transitions.test.mjs`:

```js
// Plain-Node verifier for view-transitions.ts. Run via:
//   node ui/v3/lib/view-transitions.test.mjs

// Inline copy of the function — keep in sync with view-transitions.ts.
function supportsViewTransitions() {
  return typeof document !== "undefined"
    && typeof document.startViewTransition === "function";
}

function safeStartViewTransition(callback) {
  if (supportsViewTransitions()) {
    document.startViewTransition(callback);
  } else {
    callback();
  }
}

function pass(msg) { console.log("PASS  " + msg); }
function fail(msg) { console.log("FAIL  " + msg); process.exitCode = 1; }

// In Node, `document` is undefined → returns false.
if (supportsViewTransitions() === false) {
  pass("supportsViewTransitions returns false in Node (no document)");
} else {
  fail("supportsViewTransitions did not return false in Node");
}

// safeStartViewTransition invokes the callback synchronously when unsupported.
let called = false;
safeStartViewTransition(() => { called = true; });
if (called) {
  pass("safeStartViewTransition invokes callback synchronously when unsupported");
} else {
  fail("callback was not invoked when View Transitions unsupported");
}
```

- [ ] **Step 5.2: Run the verifier**

Run: `node ui/v3/lib/view-transitions.test.mjs`
Expected: 2 PASS lines.

- [ ] **Step 5.3: Create the module**

Create `ui/v3/lib/view-transitions.ts`:

```ts
/**
 * Thin wrapper over the browser's View Transitions API.
 *
 * Chrome / Edge / Safari (and other Chromium browsers) implement
 * document.startViewTransition; Firefox does not (as of 2026-05).
 * Calling code wraps a state-changing callback in
 * safeStartViewTransition() and gets the native cross-route morph
 * where supported, falling back to a synchronous callback elsewhere
 * — at which point our existing framer-motion AnimatePresence
 * handles the inter-phase transitions.
 *
 * Elements whose layout / size / position should morph across the
 * transition need a CSS `view-transition-name` set, usually via
 * inline style on the persistent shell elements (TopNav, Rail).
 */

// Augment the global Document type so TypeScript doesn't complain
// about the still-experimental method. We only call it inside the
// capability check so the cast is safe.
type DocumentWithViewTransition = Document & {
  startViewTransition?: (cb: () => void) => unknown;
};

/** Capability check. Safe to call on the server (returns false). */
export function supportsViewTransitions(): boolean {
  if (typeof document === "undefined") return false;
  return typeof (document as DocumentWithViewTransition).startViewTransition === "function";
}

/** Run `callback` inside a native View Transition when the browser
 *  supports it; otherwise call it synchronously. The synchronous
 *  fallback is the same code path that runs in unsupported browsers,
 *  so any framer-motion AnimatePresence wrapping the changed UI still
 *  animates the transition. */
export function safeStartViewTransition(callback: () => void): void {
  if (supportsViewTransitions()) {
    (document as DocumentWithViewTransition).startViewTransition!(callback);
  } else {
    callback();
  }
}
```

- [ ] **Step 5.4: Create the Python wiring test**

Create `tests/test_view_transitions_wiring.py`:

```python
"""Regression test that pins ui/v3/lib/view-transitions.ts — same
pattern as test_safe_redirect_wiring.py and test_motion_module_wiring.py.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VT_TS = REPO_ROOT / "ui" / "v3" / "lib" / "view-transitions.ts"


def test_view_transitions_module_exists():
    assert VT_TS.is_file(), f"Missing: {VT_TS}"


def test_view_transitions_exports_capability_check():
    src = VT_TS.read_text(encoding="utf-8")
    assert "export function supportsViewTransitions" in src


def test_view_transitions_exports_safe_wrapper():
    src = VT_TS.read_text(encoding="utf-8")
    assert "export function safeStartViewTransition" in src


def test_view_transitions_falls_back_to_callback():
    """The fallback path must call callback() synchronously — without
    this, unsupported browsers would silently swallow the state change."""
    src = VT_TS.read_text(encoding="utf-8")
    # The else-branch in safeStartViewTransition must invoke callback().
    assert re.search(r"else\s*\{\s*callback\(\);?\s*\}", src), (
        "fallback branch must call callback() synchronously"
    )
```

- [ ] **Step 5.5: Wire it into workspace-shell.tsx**

In `workspace-shell.tsx`, modify `handleAdvanceFromWelcome`:

```tsx
import { safeStartViewTransition } from "@/lib/view-transitions";
// ...

function handleAdvanceFromWelcome() {
  if (pathname === "/") {
    // Wrap the router.push in a View Transition so Chrome/Edge/Safari
    // morph the layout natively instead of cutting between routes.
    // Firefox + older browsers fall through to a plain router.push and
    // get the AnimatePresence-based fade.
    safeStartViewTransition(() => {
      router.push("/workspace#phase=idea");
    });
  } else {
    setPhase("idea");
  }
}
```

- [ ] **Step 5.6: Add `viewTransitionName` inline styles on persistent shell elements**

In `top-nav.tsx`, add `style={{ viewTransitionName: "top-nav" }}` to the `<header>`:

```tsx
<header
  style={{ viewTransitionName: "top-nav" }}
  className="sticky top-0 inset-x-0 z-50 h-16 px-8 flex items-center justify-between border-b border-border bg-background/80 backdrop-blur"
>
```

In `workspace-shell.tsx`, add `style={{ viewTransitionName: "rail" }}` to the `motion.aside` rail (composed with the existing inline `animate`):

```tsx
<motion.aside
  style={{ viewTransitionName: "rail" }}
  animate={{ width: showLeftRail ? 240 : 0, opacity: showLeftRail ? 1 : 0 }}
  // ...
>
```

- [ ] **Step 5.7: Run all verifiers**

Run: `node ui/v3/lib/view-transitions.test.mjs`
Expected: 2 PASS.

Run: `node ui/v3/lib/motion.test.mjs`
Expected: all PASS (still).

Run: `python -m pytest -q`
Expected: 802 passing (798 + 4 new view-transitions wiring tests).

- [ ] **Step 5.8: Commit**

```bash
git add ui/v3/lib/view-transitions.ts ui/v3/lib/view-transitions.test.mjs tests/test_view_transitions_wiring.py ui/v3/components/workspace-shell.tsx ui/v3/components/top-nav.tsx
git commit -m "$(cat <<'EOF'
v3: opt in to View Transitions API for welcome → workspace push

Round 1 / commit 5 of the workspace motion polish work. Adds a thin
wrapper around document.startViewTransition with a safe synchronous
fallback for browsers that don't implement the API yet (notably
Firefox as of 2026-05).

- ui/v3/lib/view-transitions.ts: supportsViewTransitions() +
  safeStartViewTransition(callback). The wrapper invokes callback()
  inside a native View Transition where supported; otherwise calls
  it synchronously so the existing AnimatePresence flow still
  animates the change.
- ui/v3/components/workspace-shell.tsx: handleAdvanceFromWelcome()
  wraps router.push("/workspace#phase=idea") so Chrome / Edge /
  Safari users get the cross-route morph. Persistent shell elements
  get inline viewTransitionName styles ("top-nav", "rail") so the
  browser knows to morph them rather than fade them.
- ui/v3/components/top-nav.tsx: viewTransitionName="top-nav" on the
  <header> so it persists visually across the route change.
- ui/v3/lib/view-transitions.test.mjs: plain-Node verifier covering
  the fallback path and the capability check.
- tests/test_view_transitions_wiring.py: Python regression pinning
  the module's exports and the synchronous-fallback path.

Spec: docs/superpowers/specs/2026-05-15-workspace-motion-polish-design.md

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Draft Phase Polish

**Goal:** Polish the existing 6-step narrated build screen so the entrance, active-step treatment, live feed, and completion handoff all feel cinematic per the spec.

**Files modified:**
- `ui/v3/components/phases/draft-phase.tsx`
- `ui/v3/app/globals.css` (active-step glow keyframe)

**Acceptance:**
- pytest green (802 passing).
- Manually verify (Marc's checklist): the draft phase entrance staggers cleanly (~1.4s settle), active step has a soft glow ring, live feed lines fade up one by one, and the "Ready" pulse plays before the design phase swap.

- [ ] **Step 6.1: Add the entrance stagger**

In `draft-phase.tsx`, wrap the existing four major sections in `motion.section` / `motion.div` with delays:

```tsx
import { motion } from "framer-motion";
import { fadeUp, dropletPulse, MICRO_S, SHORT_S, STANDARD_S, SLOW_S, EASE_CINEMATIC } from "@/lib/motion";

// Section 1: droplet — replace the existing motion.div with dropletPulse variant
// Section 2: headline — wrap in motion.h1 with fadeUp + delay 0.2
// Section 3: subhead — wrap in motion.p with fadeUp + delay 0.32
// Section 4: macro checklist — already uses motion; add a staggerChildren parent
// Section 5: live feed — wrap in motion.section with fadeUp + delay 0.92
```

The specific changes (showing the headline + feed wraps; macro checklist follows the same pattern):

```tsx
// Headline + subhead block (was lines ~187-209)
<motion.section
  initial="hidden"
  animate="visible"
  variants={{
    hidden:  {},
    visible: { transition: { staggerChildren: 0.12, delayChildren: 0 } },
  }}
  className="mb-8 text-center"
>
  <div className="pebble-ripple relative w-24 h-24 mx-auto mb-4 flex items-center justify-center">
    <motion.div
      variants={dropletPulse}
      animate="rest"
      className="text-secondary relative z-10"
      style={{ willChange: "transform" }}
    >
      <Droplet className="w-14 h-14 fill-current" strokeWidth={1.5} />
    </motion.div>
  </div>
  <motion.h1
    variants={fadeUp}
    className="font-display text-2xl md:text-3xl font-bold text-foreground"
  >
    Pebble is building your draft.
  </motion.h1>
  <motion.p
    variants={fadeUp}
    className="text-sm text-muted-foreground mt-2"
  >
    Usually 2–3 minutes. Feel free to keep this window open.
  </motion.p>
</motion.section>

// Live feed section (was lines ~269-302) — wrap the outer <section> in motion.section
<motion.section
  variants={fadeUp}
  initial="hidden"
  animate="visible"
  transition={{ delay: 0.92 }}
  className="w-full max-w-2xl"
>
  {/* ... existing live feed inner markup unchanged ... */}
</motion.section>
```

- [ ] **Step 6.2: Add active-step glow ring CSS**

In `ui/v3/app/globals.css`, append:

```css
@keyframes pebble-step-glow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(120, 180, 255, 0.0); }
  50%      { box-shadow: 0 0 0 6px rgba(120, 180, 255, 0.18); }
}

@media (prefers-reduced-motion: no-preference) {
  .pebble-step-active {
    animation: pebble-step-glow 2.0s ease-in-out infinite;
  }
}
```

- [ ] **Step 6.3: Apply the glow to the active step**

In `draft-phase.tsx`, on the macro-checklist step icon container (the `motion.div` at lines ~225-245 of the existing file), add the `pebble-step-active` class conditionally:

```tsx
<motion.div
  animate={{
    scale: state === "active" ? 1.05 : 1,
    backgroundColor: /* ... existing ... */,
  }}
  transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
  className={`w-10 h-10 rounded-full flex items-center justify-center border border-border shrink-0 ${
    state === "active" ? "pebble-step-active" : ""
  }`}
>
```

- [ ] **Step 6.4: Animate live feed lines**

Replace the existing log-line render with a motion list. The new render uses `AnimatePresence` so each new line fades up over MICRO:

```tsx
<AnimatePresence initial={false}>
  {logLines.map((line, i) => (
    <motion.p
      key={i}
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: MICRO_S, ease: EASE_CINEMATIC }}
      className="whitespace-pre-wrap break-all"
    >
      <span className="text-pebble/40">[{line.ts}]</span>{" "}
      <span
        className={
          line.tone === "ok"
            ? "text-sage"
            : line.tone === "step"
              ? "text-spark font-semibold"
              : "text-pebble"
        }
      >
        {line.text}
      </span>
    </motion.p>
  ))}
</AnimatePresence>
```

Also change the auto-scroll behavior from `instant` to `smooth`:

```tsx
useEffect(() => {
  if (feedRef.current) {
    feedRef.current.scrollTo({ top: feedRef.current.scrollHeight, behavior: "smooth" });
  }
}, [logLines]);
```

- [ ] **Step 6.5: Add the completion "Ready" pulse**

In `draft-phase.tsx`, change the `done` effect to add an 800ms pulse before the phase swap fires:

```tsx
const [readyPulsing, setReadyPulsing] = useState(false);

useEffect(() => {
  if (done) {
    setActiveIdx(STEPS.length - 1);
    setReadyPulsing(true);
    setLogLines((prev) => [
      ...prev,
      { ts: new Date().toLocaleTimeString(), text: "✓ all done. opening your draft.", tone: "ok" },
    ]);
  }
}, [done]);
```

Then, on the final step's icon, conditionally apply a pulse animation:

```tsx
<motion.div
  animate={readyPulsing && state === "done" && i === STEPS.length - 1
    ? { scale: [1, 1.12, 1] }
    : { scale: state === "active" ? 1.05 : 1 }
  }
  transition={readyPulsing ? { duration: SLOW_S * 1.14, ease: EASE_CINEMATIC } : { duration: STANDARD_S, ease: EASE_CINEMATIC }}
  // ... rest
>
```

The shell's existing `setTimeout(() => setPhase("design"), 600)` already gives the pulse time to play before the swap. No shell change needed.

- [ ] **Step 6.6: Run pytest**

Run: `python -m pytest -q`
Expected: 802 passing.

- [ ] **Step 6.7: Commit**

```bash
git add ui/v3/components/phases/draft-phase.tsx ui/v3/app/globals.css
git commit -m "$(cat <<'EOF'
v3: cinematic polish on the narrated build (draft phase)

Round 1 / commit 6 of the workspace motion polish work. Polishes the
existing 6-step narrated build screen without restructuring it:

- Cinematic entrance stagger: droplet → headline → subhead →
  checklist (railStep) → live feed (fadeUp). Total settle ~1.4s.
- Active step gets a soft glow ring via the new
  .pebble-step-active CSS class (keyframe pebble-step-glow,
  prefers-reduced-motion-safe — disabled when the user prefers
  reduced motion).
- Live feed lines fade up over MICRO instead of instant pop. Auto-
  scroll smoothed.
- Completion handoff: when `done` flips true, the final step icon
  pulses scale [1, 1.12, 1] over SLOW_S * 1.14 before the existing
  600ms setTimeout fires the phase swap. Feels like a deliberate
  "and… we're done" beat instead of a jump cut.

Spec: docs/superpowers/specs/2026-05-15-workspace-motion-polish-design.md

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Final Wiring Tests + Hand-off Doc

**Goal:** Finalize the Python wiring tests so they assert phase files import from `@/lib/motion`, and write a hand-off doc for Marc's manual testing checklist.

**Files:**
- Modify: `tests/test_motion_module_wiring.py`
- Create: `docs/superpowers/handoffs/2026-05-15-workspace-motion-polish-handoff.md`

**Acceptance:**
- pytest green (~810 passing — 8 new import assertions across 8 files).
- Hand-off doc exists with copy-pasteable testing instructions for Marc.

- [ ] **Step 7.1: Extend the motion-module wiring test**

In `tests/test_motion_module_wiring.py`, append:

```python
# ---- Phase files import from @/lib/motion ---------------------------------

PHASE_FILES = [
    REPO_ROOT / "ui" / "v3" / "components" / "workspace-shell.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "welcome-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "idea-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "plan-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "draft-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "edit-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "publish-phase.tsx",
]


@pytest.mark.parametrize("phase_file", PHASE_FILES, ids=lambda p: p.name)
def test_phase_file_imports_from_motion_module(phase_file):
    src = phase_file.read_text(encoding="utf-8")
    assert re.search(
        r"from\s+['\"]@/lib/motion['\"]",
        src,
    ), f"{phase_file.name} should import from @/lib/motion"
```

Add `import pytest` at the top of the file if not already present.

- [ ] **Step 7.2: Run pytest to confirm the new assertions pass**

Run: `python -m pytest tests/test_motion_module_wiring.py -q`
Expected: 12 passing (5 existing + 7 new parametrized).

Run: `python -m pytest -q`
Expected: 809 passed.

- [ ] **Step 7.3: Write the hand-off doc for Marc**

Create `docs/superpowers/handoffs/2026-05-15-workspace-motion-polish-handoff.md`:

```markdown
# Workspace Motion Polish — Hand-off (2026-05-15)

This document is for Marc to verify the motion-polish work that was
shipped in commits 1c666f1 → (final commit SHA after merge). The
implementation is complete; what remains is your sign-off via manual
browser testing.

## TL;DR

7 commits shipped + 1 spec commit. ~810 pytest passing. Plain-Node
verifiers exit 0. View Transitions API path covered for Chrome /
Edge / Safari; Firefox + older browsers use the AnimatePresence
fallback path.

## Run the v3 dev server

```bash
cd C:\Users\marci\pebble-engine\ui\v3
npm install   # if you haven't already
npm run dev
```

Engine should also be running for previews to work:

```bash
# In a separate terminal, from C:\Users\marci\pebble-engine
python pebble_engine.py
```

Open: http://localhost:3001

## Manual testing checklist

Run through each item in Chrome (or Edge / Safari) and then in Firefox
to verify both the native View Transitions path and the AnimatePresence
fallback feel right.

### Phase navigation

- [ ] Land on `/` (welcome). The big hero text fades in cinematically.
- [ ] Type a project idea and hit send. Watch the welcome → /workspace
      transition.
  - Chrome / Edge / Safari: native View Transitions morph — TopNav and
    Rail visibly slide/fade into place.
  - Firefox: framer-motion AnimatePresence fade. Slightly different
    but still smooth.
- [ ] In the workspace, click rail items: Idea → Plan → Draft → Design
      → Publish. The active highlight (`bg-primary/15` block behind the
      label) should SLIDE between rail items, not fade.
- [ ] Click back to Idea. Highlight slides back. TopNav stays in place
      (does NOT remount).

### Build narration

- [ ] Enter the idea phase, finish the chip questionnaire, generate
      the plan, then hit Generate. Build screen entrance should stagger:
      droplet → headline → subhead → checklist → live feed.
- [ ] Live feed lines should fade up individually (not instant pop).
- [ ] On completion, the final checklist step pulses (scale up + glow)
      before the design phase fades in.

### Reduced motion

- [ ] Enable OS-level "Reduce motion" preference:
  - macOS: System Settings → Accessibility → Display → Reduce motion ON
  - Windows: Settings → Accessibility → Visual effects → Animation
    effects OFF
- [ ] Refresh /. Re-run any phase transition.
- [ ] All motion should now be instant. The shell stops sliding the
      rail width; phase content swaps without fade.

### Direct hash hits

- [ ] Visit `http://localhost:3001/workspace#phase=plan` cold (after
      generating a build). Should land directly on the plan phase, no
      flash of design.
- [ ] Reload `/workspace#phase=design` mid-session. Should resume on
      the design phase if a build exists, or bounce to welcome if not.

### Back / forward

- [ ] Browser back from design → plan → idea → welcome. Phase changes
      should animate.
- [ ] Browser forward through the same path. Same animations.

### Window resize

- [ ] Resize the window during a phase transition. No layout glitches,
      no flickering.

## If anything looks wrong

- Capture a screenshot, paste the URL, and tell me which phase you
  were in. Include the browser + OS in case the issue is View
  Transitions-specific.
- The spec is at `docs/superpowers/specs/2026-05-15-workspace-
  motion-polish-design.md` — reference it for "this is supposed to
  do X."

## Files changed

11 files modified + 5 new files. Detailed in the git log under
"Round 1 / commit N of the workspace motion polish work" messages.

```bash
git log --oneline ba98ef8..HEAD
```

## What's next (round 2)

Per the spec's "Honest scoping notes" section:

1. Typography pass — font sizes, weights, line heights, letter
   spacing.
2. Component-level micro-interactions — every clickable element gets
   a refined hover/active/focus treatment.
3. Density / spacing audit.

When you're ready for round 2, drop me a note. Estimated scope: ~6-8
hours of focused work.
```

- [ ] **Step 7.4: Commit the wiring test extension + hand-off doc**

```bash
git add tests/test_motion_module_wiring.py docs/superpowers/handoffs/2026-05-15-workspace-motion-polish-handoff.md
git commit -m "$(cat <<'EOF'
v3: wiring tests for motion module imports + hand-off doc

Round 1 / commit 7 (final) of the workspace motion polish work.
Locks down the import-from-@/lib/motion contract across every phase
file so a future refactor can't silently disconnect them.

- tests/test_motion_module_wiring.py: parametrized assertion that
  each of the 7 phase / shell files imports from "@/lib/motion".
- docs/superpowers/handoffs/2026-05-15-workspace-motion-polish-
  handoff.md: manual testing checklist for Marc to verify the
  visible behavior across Chrome / Firefox / Safari, plus reduced-
  motion verification steps and a reference list of what changed.

Total pytest after this commit: 809 passing.

Spec: docs/superpowers/specs/2026-05-15-workspace-motion-polish-design.md

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Final: Merge + Push to Origin

**Acceptance:**
- `origin/main` has all 7 motion commits.
- Marc can pull and verify with the hand-off doc.

- [ ] **Step F.1: Fetch + ff-merge from main repo**

From the main repo working dir (NOT the worktree):

```bash
git -C "C:/Users/marci/pebble-engine" fetch origin main
git -C "C:/Users/marci/pebble-engine" merge --ff-only claude/stoic-dirac-2db37e
```

Expected: fast-forward update, no conflicts.

- [ ] **Step F.2: Push to origin/main**

```bash
git -C "C:/Users/marci/pebble-engine" push origin main
```

Expected: push succeeds. Marc has pre-approved pushes for this work.

- [ ] **Step F.3: Notify completion**

Final response to Marc: list the 7 commit SHAs, point to the hand-off doc, note that the dev server needs to be running locally for him to verify.

---

## Decision points / pause-for-user gates

**None planned.** Marc explicitly said he's stepping away and will only intervene if I have questions. The plan above is fully self-executing.

Two scenarios where I'd pause:
1. A subagent task fails verification (test red, lint failure, type error). Don't push past it — report back to Marc.
2. A subagent reports unexpected file state (uncommitted changes outside the planned scope). Investigate before continuing.

## Subagent delegation strategy

Every task in this plan is safely subagent-delegable. Each task is bounded by:
- A specific file list.
- TDD steps that produce immediate verification signal.
- A concrete commit at the end.

The recommended pattern (per `superpowers:subagent-driven-development`):
1. Dispatch task as a fresh subagent with the task's full step list as the prompt.
2. Subagent does the work, runs the verifications, commits.
3. Subagent reports back with a compact summary + the commit SHA.
4. I verify the commit landed cleanly (`git log --oneline -1`) and proceed to the next task.
5. Keep my main context light — never reload the full implementation files.

## Self-review notes

I checked the plan against the spec and confirmed coverage:
- ✓ Motion language module (Task 1) — matches spec section "Motion Language Module."
- ✓ Phase file refactor (Task 2) — matches spec section "Architecture / Files modified."
- ✓ Shell restructure (Task 3) — matches spec section "Shell Restructure & Phase Transitions."
- ✓ Shared elements (Task 4) — matches spec section "Cross-Phase Shared Elements." Notable scope adjustment: the project-name layoutId morph is deferred to round 2 because welcome's h1 isn't semantically equivalent to a project name; the rail-active highlight is the main layoutId win.
- ✓ View Transitions (Task 5) — matches spec section "View Transitions API Integration."
- ✓ Draft polish (Task 6) — matches spec section "Draft Phase Polish."
- ✓ Wiring tests + hand-off (Task 7) — matches spec section "Testing Strategy."
- ✓ Reduced motion (Task 1 + carried through) — `prefersReducedMotion()` + `withReducedMotion()` in motion.ts.

No placeholders detected. No type inconsistencies (variants are named the same across tasks). Scope is single-implementation-plan sized (~10 hours total, 7 commits).
