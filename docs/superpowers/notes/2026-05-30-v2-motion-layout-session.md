# v2 Motion + Layout-Variety Session — Autonomous Work Log

**Date:** 2026-05-30
**Branch:** `claude/v2-section-files` (NOT pushed — Marc reviews + merges)
**Context:** Marc asked for the v2-generated sites to feel "alive" (motion) and
structurally varied, while staying edit-safe for the Canva-style click-to-edit
surface. Editing north star locked to **Lovable/Base44 parity** (inline edit +
prompt-to-change + section reorder), NOT free-drag Canva.

## What shipped this session (all committed on the branch)

### Sub-project A — section-files compiler  ✅
The v2 compiler now emits each block as its own `components/sections/SectionNN.tsx`
(full component body + hooks + `"use client"` preserved), with `page.tsx` a thin
import/render root. Previously every block was flattened into one `page.tsx`,
which discarded hooks — fatal for motion. This is the keystone that unblocked
everything else, and it advances the future section-reorder editor (task #232).
Commits: `a5691147` → `a92da006` (6).

### Sub-project B — motion layer  ✅
- 10 edit-safe motion primitives in `pebble/blocks/motion/` (FadeUp, Stagger/
  StaggerItem, RevealWords, Parallax, CountUp, Masonry, DragCarousel, Marquee,
  TiltCard, MagneticButton). Each: `"use client"` line 1, `prefers-reduced-motion`
  fallback, forwards `...rest` (so `data-pebble-id` rides onto the editable child),
  no hardcoded colors.
- Compiler writes the primitives into every site + adds `framer-motion` dep.
- All 49 existing blocks retrofitted to compose primitives (42 animated, 7 footers
  static). Parallel subagents, one per vibe.
Commits: `868633b5`, `ad34ea4f`, `5b91b452`, `610c59b3`.

### CRITICAL render fix — Tailwind content glob  ✅
Sub-project A moved markup from `app/` to `components/`, but the Tailwind
`content` glob still only scanned `./app/**`. Result: generated CSS shipped
nearly empty → every v2 site rendered unstyled (mashed-together headline words,
giant images, no layout). Caught by Marc's screenshot, missed by HTTP-200 +
tsc-clean checks (neither verifies CSS renders). Fixed glob to include
`./components/**` + regression test. Commit `d769dcc4`.
**Lesson: a real rendered screenshot is a required gate for visual work.**

### Sub-project C — new block types  ✅
- `gallery` (masonry image grid) + `scroll-story` (pinned step narrative).
- New `StickyStory`/`StickyStep` primitive (pure CSS sticky, no scroll-state).
- `scroll-story` added to BlockType enum; picker prompt teaches when to use each.
- 51 blocks total. Verified via `next build` (full prerender) + `next start` 200
  with 35 real Pexels images — the earlier dev-server 500 was a stale `.next`
  cache, not a code bug.
Commit `069160c9`.

### Sub-project D — click-to-edit on v2 (PARTIAL)  ⚠️
`build_v2` now calls `inject_pebble_ids` → writes `.pebble-ids.json` manifest +
tags editable elements (parity with v1). 24 ids on a 3-block site. Commit (this).

**Follow-up fix applied (autonomous):** the first D pass had `inject_pebble_ids`
walking `components/motion/` and baking ids into the SHARED primitive source —
which would give every headline the same id and route all edits to one shared
file. Fixed by excluding `components/motion/` from injection (the id rides from
the call site via `...rest`, as designed). Regression test added. Manifest now
tags only per-page section files.

**KNOWN LIMITATION — motion-wrapped headline text edits:**
Headlines compile to `<h1 ...><RevealWords>{{headline}}</RevealWords></h1>`. The
injector tags the `<h1>` (so it's selectable + color/font editable), but the text
snapshot is empty because the copy lives inside the `<RevealWords>` child, not
directly in the h1. So the *text-edit* path can't cleanly target headline copy.
- **Works today:** body `<p>`, `<a>`, `<li>`, `<button>` text edits; all color /
  font / palette edits; element selection on everything incl. headlines.
- **Needs follow-up (live-test required):** headline/stat text edits through
  RevealWords/CountUp. Options: (a) have the visual-edit text path treat a lone
  `<RevealWords>`/`<CountUp>` child as a transparent text container; or (b) emit
  the editable string as a direct child + pass it to the primitive via prop.
  Either needs the live click-to-edit flow to verify — deferred for Marc.

## Test + verification status
- Full suite: **2425 passed**, 27 failed — the SAME 27 pre-existing failures on
  `main` (repair loop / projects-api / publish), zero new regressions.
- `next build` of a motion+gallery+scroll-story site: compiles + prerenders clean.
- `tsc --noEmit` on retrofitted vibes: 0 errors.

## Open follow-ups (not blocking)
1. Motion-headline text-edit (above) — needs live edit-flow test.
2. Hero washout on light palettes — spawned as its own task (gradient overlay
   tuned for dark photos; contrast-aware overlay needed). Cosmetic.
3. Task #231 — 15 industry example templates (showcase for this work).
4. Task #232 — prompt-to-edit + drag-to-reorder (editing parity follow-up).

## Branch state
`claude/v2-section-files`, ~15 commits ahead of `main`, NOT pushed. The 27
pre-existing failures are unrelated to this work. Recommend Marc review the diff,
eyeball a live build, then merge.
