# 15-Template Gallery — Build Results (2026-05-31)

Task #231: build 15 industry example sites through the v2 motion engine as free pick-from templates.

## What shipped

All 15 briefs (drafted by a 15-agent workflow, deliberately conversational —
"a starter my grandmother kept alive for thirty years") were built through the
**real `build_v2_core`** pipeline: Sonnet block-pick + copy → section-file
compile with motion primitives → Pexels resolution → click-to-edit id injection.

| # | Vibe | Business | Slug | Sections |
|---|------|----------|------|----------|
| 1 | warm-craft | Flour & Fern (bakery) | `flour-fern` | 8 |
| 2 | warm-craft | Marigold Lane (salon) | `marigold-lane` | 8 |
| 3 | clean-trust | Willow Creek Dental | `willow-creek-dental` | 7 |
| 4 | clean-trust | Maple & Hart Law | `maple-hart-law` | 8 |
| 5 | clean-trust | Maple & Ledger (CPA) | `maple-ledger` | 8 |
| 6 | bold-energetic | Iron Anvil CrossFit | `iron-anvil-cross-fit` | 7 |
| 7 | bold-energetic | Static Vanguard (esports) | `static-vanguard` | 7 |
| 8 | editorial-minimal | Linen & Light (wedding photo) | `linen-light` | 8 |
| 9 | editorial-minimal | Field & Frame (architecture) | `field-frame` | 8 |
| 10 | appetizing-rich | Maple & Furrow (restaurant) | `maple-furrow` | 8 |
| 11 | appetizing-rich | Ember & Oak Roasters (coffee) | `ember-oak-roasters` | 8 |
| 12 | luxurious-spa | Marrow & Mist (day spa) | `marrow-mist` | 8 |
| 13 | luxurious-spa | Maren & Vale (fine jewelry) | `maren-vale` | 7 |
| 14 | playful-illustrated | Scribble Sprouts (kids art) | `scribble-sprouts` | 8 |
| 15 | playful-illustrated | Pocket & Pinecone (toy shop) | `pocket-pinecone` | 7 |

Output: `output/<slug>/site/` — full Next.js 14 projects. Manifest: `_template_results.json`.

## Verification (programmatic — all green)

- **15/15 built clean** — zero `{{placeholder}}` leaks anywhere.
- **48 of 51 library blocks** exercised across the gallery → real layout variety,
  not "same page every time." Each site is vibe-matched: galleries on
  image-heavy businesses (photo/restaurant/salon/art), scroll-story process
  sections on service businesses (dental/spa/bakery).
- **15/15 Pexels images fully resolved** — no leftover `[pexels:]` tags.
- **Motion present everywhere** — FadeUp, Stagger, RevealWords, Parallax,
  MagneticButton on all 15; Masonry on the 6 image-heavy ones; TiltCard on 2.
- **`linen-light` production build = clean** — `npx next build` → ✓ Compiled
  successfully, type-checks pass, all 4 routes prerendered, no SSR errors,
  137 kB First Load JS. Proves no `document`/`window` SSR crashes, no
  framer-motion hydration breakage, no type errors.
- Copy quality is genuinely good and slop-free — e.g. linen-light hero:
  *"35mm and medium-format film, shot and hand-developed by Nora."* Straight
  from the brief, no invented facts.

Cost: ~$0.75–1.20 total (15 × ~$0.05–0.08 Sonnet calls).

## Bug found + fixed: hero headline could render invisible

While verifying `linen-light` I found the hero h1 sat at `opacity:0`. Root cause:
`RevealWords` (the headline primitive) used `whileInView` — so the headline's
visibility depended on **IntersectionObserver** firing. A hero h1 is always above
the fold and is the highest-stakes text on the page; gating it behind IO means it
can render invisible if IO is delayed/absent or during the hydration window.

**Fix (committed to working tree, NOT yet committed to git):**
`pebble/blocks/motion/RevealWords.tsx` now fires on **mount** (`animate`) instead
of on scroll (`whileInView`). FadeUp/Stagger keep `whileInView` intentionally —
those are genuine below-the-fold scroll reveals you asked for. Regression test
added: `tests/test_motion_library.py::test_revealwords_fires_on_mount_not_on_scroll`.
The fixed primitive was copied into all 15 built templates. 67 related tests green.

## ✅ Visual QA — PASSED in real Chrome (4 vibes screenshotted)

Once Chrome reconnected, I production-built + served + screenshotted four
deliberately distinct vibes. All render beautifully and completely differently:

- **`linen-light` (editorial)** — full-bleed B&W film hero, headline visible,
  masonry gallery of six on-theme wedding photos ("photographs from barns,
  vineyards, and backyards").
- **`static-vanguard` (bold)** — dark esports-arena hero, lime-400 accent,
  heavy display "THE STATIC VANGUARD", lime + outline CTAs.
- **`scribble-sprouts` (playful)** — pink gradient, rounded purple display
  "Where every kid is already an artist", kids-painting photo in a rounded card.
- **`maple-furrow` (appetizing)** — candlelit farm-table hero, warm orange
  accent, "Every plate names the farm it came from — most within 30 miles."

Headlines render visible in all four → **confirms the RevealWords mount-fire fix
works in real browsers** (the earlier opacity:0 was purely the Preview renderer,
which lacks IntersectionObserver and doesn't advance framer-motion's loop — a
tooling limitation, not a product bug). Real on-theme Pexels images, correct
palettes/fonts/CTAs throughout.

### New finding (not yet fixed): hero headline contrast over bright photos
`maple-furrow`'s "Rooted" headline is **low-contrast** — light serif over the
busy mid-tone wood-table photo, with no scrim (the VEX hero spec forbids a dark
overlay). Legible but faint. `linen-light`/`static-vanguard` had darker image
regions so were fine. Recommend a subtle hero-headline `text-shadow` or a soft
bottom-gradient scrim (NOT a full dark overlay) for legibility over bright
images. Touches the hero foundation across the 8 hero block variants — flagged
for your decision rather than restyled unilaterally.

**Re-serve any template yourself (paste-ready):**
```bash
cd C:\Users\marci\pebble-engine\output\linen-light\site && npx next start -p 4319
# open http://localhost:4319
```
(`linen-light`, `static-vanguard`, `scribble-sprouts`, `maple-furrow` are
already built. For the other 11, run `npm install && npx next build` in their
`site/` dir first.)

## Shipped this session (both decisions actioned)

1. ✅ **Hero contrast fix.** Light-text-over-photo heroes (`hero_fullbleed_editorial`,
   `hero_plate_appetizing`) now carry a soft bottom scrim + headline text-shadow so
   the headline never washes out over bright images (the dark-text / strong-scrim /
   solid-bg heroes were correctly left alone). Fixed at source in
   `pebble/blocks/library/` AND patched into the 3 affected built artifacts
   (linen-light, field-frame, maple-furrow). **Visually re-verified** in Chrome —
   maple-furrow's "Rooted in season. Cooked for the table." is now crisp.
2. ✅ **"Clone this example" gallery path.** Free pick-from gallery wired end-to-end:
   - `pebble/example_gallery.json` — committed manifest of all 15 (name, industry,
     vibe, hero preview image, source).
   - `pebble/server/examples.py` — `GET /api/examples` (public list) +
     `POST /api/examples/clone {example_slug, business_name?}` → pure filesystem
     copy of a built v2 site into the user's account. No LLM, instant,
     `billable: false`. Motion + click-to-edit ids carried intact.
   - Routes registered in `pebble/server/router.py`.
   - `tests/test_examples.py` (6 tests) + **live smoke confirmed**: listed 15,
     cloned linen-light → new project (30 files, billable:false, contrast fix carried).

## Open follow-ups

1. **Production: example sources must ship with the server.** The clone reads from
   `output/<slug>/` (gitignored — present in dev, absent on a fresh deploy). For prod,
   relocate the 15 built `site/` dirs (minus `node_modules`/`.next`) into a committed
   `pebble/examples/<slug>/` and repoint `source_dir` in the manifest — same precedent
   as `pebble/templates/`. ~600 small files; your call on committing them vs seeding at
   deploy. Mechanism is done; only the source location needs finalizing.
2. **v3 UI for the gallery** — a `/examples` (or tab) page calling `GET /api/examples`
   with a "Use this template" button → `POST /api/examples/clone` → route to
   `/workspace/<slug>`. Frontend-only; backend is ready.
3. **`next@14.2.5` security advisory.** The v2 compiler pins `next@14.2.5`, which npm
   now flags (patched in a later 14.2.x). Affects *every* v2 build — one-line bump in
   `pebble/blocks_compiler.py` `_PACKAGE_JSON`.
4. **framer-motion `initial:{opacity:0}` + no-JS.** Inherent tradeoff: if JS never runs,
   hidden content stays hidden. Fine for normal browsers; note for SEO/no-JS.
5. **Editing parity (#232)** — prompt-to-edit + drag-to-reorder sections — still open.

## Uncommitted changes in `main` working tree (for your review)
- `pebble/blocks/motion/RevealWords.tsx` — mount-fire fix
- `tests/test_motion_library.py` — regression test
- `_build_templates.py`, `_template_briefs.json`, `_template_results.json` — build harness + artifacts (scratch)
- (`ui/v3/lib/plan-features.ts` was already modified before this session — not mine.)
