# Pebble v2 — Motion + Layout Variety (Edit-Safe) Design

**Date:** 2026-05-30
**Status:** Approved direction (Marc, 2026-05-30) — pending spec review before plan.
**Author:** Claude (brainstorming session)

## Goal

Make v2-generated sites feel *alive* and *structurally varied* — without reopening the
LLM-freestyle failure mode (broken animations, SSR crashes, paid-plugin imports) and
without breaking the click-to-edit ("Canva-style") editing system.

## Problem

Today every v2 site shares:

1. **No motion.** All 49 blocks are static JSX. `grep` for `framer-motion`/`gsap`/`whileInView`
   across the library returns 0. Only CSS `hover:` transitions exist.
2. **One skeleton.** Every site is `hero → services → about → testimonials → pricing → contact → footer`.
   The picker swaps which *vibe-variant* fills each slot, but the section *shapes* never change
   (services is always a 3-col grid; there is no gallery section type at all).

The vibes change the skin (color, copy, fonts); the bones are identical. That is why distinct
industries still feel related.

## Cross-cutting constraint: everything stays editable

Pebble's product promise is "everything editable later" — a Canva-style surface where users
move, recolor, retype, and swap any part of the page. The current visual-edit system
(`pebble/server/visual_edit.py`) implements a deterministic subset of that:

- Editable elements are tagged with **`data-pebble-id`**.
- The injected bridge walks up to the nearest `data-pebble-id` ancestor on click and posts
  element metadata to the parent workspace.
- Edits are **surgical source edits** via a manifest mapping `data-pebble-id → (file, element span)`.
  - **text**: replaces an element's inner text. If the element has child elements, it only
    succeeds when `original_text` appears **verbatim** in the inner source.
  - **color / font-size / font-family**: upsert a style on the tag near a selector hint or by id.
  - **palette swap**: rewrites palette tokens site-wide.

**The hard rule this imposes on motion:** a motion primitive may transform *presentation*
(opacity, transform, splitting text into animated spans **at render time**) but the **source
representation of every editable slot must remain a single string / single tagged element**.
Animation never fragments the editable source.

## Architecture

### 1. Motion primitives library (`components/motion/`)

The 10 lab-approved effects become ~11 small, tested components the compiler writes into every
generated project — the same mechanism that already writes `app/layout.tsx` and `app/globals.css`.

| Component | Effect | Edit-safety note |
|---|---|---|
| `RevealWords` | per-word headline reveal | takes plain-string `children`; splits at render only; root carries the `data-pebble-id` |
| `Parallax` | scroll-driven image translate | wraps an `<img>`/child that keeps its own id; wrapper holds no editable slot |
| `FadeUp` | fade + rise on view | transparent wrapper; child keeps id |
| `Stagger` | cascade children on view | wraps a list container; each child keeps its id |
| `CountUp` | animated number | takes a numeric prop + plain children fallback; renders the final number as text |
| `StickyStory` | pinned scroll narrative | step content are plain editable nodes; ids preserved per step |
| `Masonry` | CSS-column gallery | each image keeps its id/src for swap |
| `DragCarousel` | drag/swipe row | each card keeps its ids |
| `Marquee` | infinite CSS strip | decorative; not an editable region |
| `TiltCard` | hover 3D tilt | wraps a card whose inner nodes keep ids |
| `MagneticButton` | cursor-follow CTA | renders an `<a>`/`<button>` that keeps its id + editable label |

Requirements for **every** primitive:
- `"use client"`.
- `prefers-reduced-motion` honored internally (one place, once) — falls back to a static render.
- No hardcoded colors — visual styling comes from the child / palette tokens, never baked in.
- Accepts and forwards `data-pebble-id` and arbitrary props to the editable child/root so the
  manifest tagging survives.
- SSR-safe: no module-level browser access; GSAP/ScrollTrigger registered inside `useEffect`
  and guarded by `typeof window`.

### 2. Tech choice: Framer Motion primary, GSAP for one effect

Framer Motion is the default (declarative, React-native, SSR-safe, reduced-motion in one line,
already used by v3). GSAP is included **only** for `StickyStory`/pinned-horizontal-class effects
where ScrollTrigger is materially better. GSAP rules from CLAUDE.md are mandatory: register
plugins inside `useEffect`, never import `SplitText` (paid), use `gsap/dist/ScrollTrigger`.

### 3. Blocks compose primitives (motion pass on all 49)

Each of the 49 existing block `.tsx` files is rewritten to wrap its key elements in primitives
(hero → `Parallax` + `RevealWords`; services → `Stagger` + `FadeUp`; stats → `CountUp`; CTA →
`MagneticButton`; etc.). The motion choice per block is **authored, not generated** — the LLM
still only picks blocks and writes copy. One big pass via parallel subagents, one per vibe
(the proven overnight pattern). Decision (Marc): **all 49 at once.**

### 4. Two new block *types* (ship in the same project)

Add to the `BlockType` enum in `pebble/blocks/schema.py` and to the picker menu:

- **`gallery`** — `masonry` and `drag-carousel` variants. Natural for photographer, restaurant,
  portfolio, salon. Image-list slot.
- **`scroll-story`** — the sticky-pin narrative. Natural for service businesses ("how it works"),
  processes, before/after. Ordered step slots (image + heading + body per step).

Author at least one variant of each per relevant vibe (start with the vibes where they matter
most; the picker only offers what exists). Decision (Marc): **same project as the motion pass.**

### 5. Compiler upgrade: section files instead of inline page.tsx

Today `blocks_compiler` flattens every block into one `page.tsx`, keeping only the JSX body
(`_extract_jsx_body` strips the function wrapper). That **discards any hooks** a block declares
before its `return` — fatal for motion blocks that need `useScroll`/`useRef`.

New behavior:
- Each picked block is written as its **own section file** under `components/sections/<Name>.tsx`,
  preserving its full function body (hooks + return) and its `"use client"` directive.
- `page.tsx` imports and renders the section files in pick order.
- Section order lives in one place (the import/render list) — which **directly enables the
  Canva "move section" capability** later: reordering sections is reordering that list.
- The placeholder-leak hard-fail and palette/slot substitution stay exactly as they are, applied
  per section file.
- Pexels resolution runs across all section files (today it runs on page.tsx).

### 6. Picker prompt update

Teach `sonnet_block_picker` that `gallery` and `scroll-story` block types exist and when to
reach for them (gallery for visual/portfolio industries; scroll-story for
process/service industries). No motion instructions to the LLM — motion is invisible to it.

### 7. Editability integration (must not regress)

- The compiler's existing `data-pebble-id` tagging pass runs **after** motion wrapping, tagging
  the editable child/root inside each primitive — never the decorative wrapper.
- `RevealWords` and `CountUp` keep their editable content as a **single plain-string** in source
  (e.g. `<RevealWords>{{headline}}</RevealWords>`), so the text-edit verbatim check still matches.
- The bridge's "current text" read may need to reconstruct spaced text from split spans for
  display only (cosmetic; does not affect the source edit). Note for implementation.
- Color edits and palette swap are unaffected — primitives introduce no hardcoded colors.

## Data flow

```
brief → sonnet_block_picker (picks blocks incl. gallery/scroll-story + copy + palette)
  → blocks_compiler:
      • write components/motion/*.tsx  (fixed primitive library)
      • write components/sections/<Name>.tsx per pick (full body, "use client", hooks intact)
      • substitute slots + palette tokens; hard-fail on leaks
      • tag editable nodes with data-pebble-id (after motion wrap) + build manifest
      • write page.tsx importing sections in order
  → pexels_resolver across section files
  → runnable Next.js site: alive, varied, fully edit-safe
```

## Testing

- Unit: each motion primitive renders static markup under reduced-motion; forwards `data-pebble-id`.
- Compiler: section-file emission preserves hooks + `"use client"`; page.tsx imports in order;
  leak hard-fail still triggers; manifest still maps every editable id to a section file + span.
- Edit-safety regression: for a compiled motion site, run a text edit on a `RevealWords` headline,
  a color edit on a button, an image swap in a `gallery` — all must succeed via the existing
  `_edit_*_by_id` paths.
- E2E: build one site per vibe; assert HTTP 200, no `Module not found`, image URLs resolved,
  zero `{{...}}` leaks.

## Risks

- **Edit-safety regressions** (highest). Mitigation: the regression tests above are mandatory in
  the plan; motion wrapping rule is "wrapper outside, id on the editable child."
- **Compiler refactor scope.** Section-files is the one structural change; isolate it as its own
  task with its own tests before the motion pass depends on it.
- **GSAP SSR.** Mitigated by the CLAUDE.md rules + one-effect-only containment.
- **Bundle size / perf.** Framer Motion is tree-shakeable; primitives are small. Watch CWV after.

## Editing north star (decided 2026-05-30)

The target is **Lovable / Base44 parity**, NOT a Canva free-drag canvas:

1. **Inline click-to-edit** — click any element, change text / color / font / size / image. ✅ exists today.
2. **Prompt-to-change** — natural-language edits ("move the gallery up", "make the hero bolder"). *Follow-up.*
3. **Drag-to-reorder whole sections** — rearrange section order like Lego blocks; responsive-safe. *Follow-up, unlocked by section-files.*

Explicitly **not** in the product target: free-pixel dragging of individual elements, handle-resize,
or arbitrary per-element absolute positioning. This is rarer than it looks in this category
(Lovable/Base44 don't do it) because it fights responsive design.

**This project's job toward that north star:** deliver #1's continued correctness through the motion
changes, and lay the section-files foundation that #3 needs. #2 and #3 themselves are tracked as a
separate follow-up (see task backlog), built on top of this.

## Out of scope (separate future projects)

- **Prompt-to-edit engine + drag-to-reorder UI** (the parity follow-up) — tracked separately; this
  project only guarantees it isn't blocked and that section-files advance it.
- **Free-drag/Canva-style per-element positioning** — not a product goal (see north star above).
- The **15-industry free template gallery** (task #231) — built *after* this lands, as its showcase.
- WebContainers preview (Phase 3 plan already written) — independent track.
