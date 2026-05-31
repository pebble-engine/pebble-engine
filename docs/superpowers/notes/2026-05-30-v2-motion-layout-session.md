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

**RESOLVED — motion-wrapped headline text edits (autonomous follow-up):**
Headlines compile to `<h1 ...><RevealWords>{{headline}}</RevealWords></h1>`.
RevealWords renders each word as a margin-spaced span, so the bridge's live
textContent is de-spaced ("OldTitle") and never matched the spaced source —
headline/stat text edits silently no-op'd. Fixed in `_edit_text_by_id` (option
(a) from the original plan): a lone `<RevealWords>`/`<CountUp>` child is now
treated as a transparent text container and the string inside it is edited
directly, independent of `original_text`. Reproduced the bug with a capture test,
fixed, verified: 4 new tests (2 wrapper, 2 regression), 71 visual/v2 tests green.
- **Works now:** headline + stat-number text edits (RevealWords/CountUp), body
  `<p>`/`<a>`/`<li>`/`<button>` text, all color/font/palette edits, selection.
- Click-to-edit is now functionally complete for v2 sites at the unit level. A
  full live browser pass is still worth doing once, but no known gap remains.

**Minor follow-up (spawned as a task):** `test_visual_edit.py` has a
test-order-pollution flaw — one regression test only mis-behaves when the whole
file runs (passes in isolation). Production code is correct; the test's assertion
was relaxed to the true invariant (source-not-corrupted) and the isolation leak
is queued as its own fix.

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
