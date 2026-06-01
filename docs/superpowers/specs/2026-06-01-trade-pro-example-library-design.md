# Trade-Pro Example Library — Design Spec (Wave 1)

**Date:** 2026-06-01
**Status:** Approved direction; pending spec review → implementation plan.

## Goal

Grow the free `/examples` clone-this gallery with **8 local/home-trade starter sites** so polished that a tradesperson picks one over building their own. Each must clear an automated eval gate + a visual check before it ships. Wave 1 (trades) proves the pipeline; later waves (health/wellness, professional/B2B, food/retail/events) reuse it.

**Success criteria**
- 8 trade example sites live in `pebble/examples/<slug>/` and registered in `pebble/example_gallery.json`.
- Each passes `pebble.evals` (esp. `tailwind_directives_present`, `no_invented_time_markers`, image wiring, `contact_form_uses_server_action`/forms wiring, a11y checks).
- Each has a real Playwright homepage screenshot thumbnail.
- Each is visually reviewed (renders styled, on-brand, tonally a trades site).
- A user can clone any of them from `/examples` (instant, free, `billable:false`) and edit in the workspace.

## Background / why this shape

- **Two systems exist.** Templates (`pebble/templates/`, registry-driven, LLM swaps only `content/site.ts`) vs **Examples** (`pebble/examples/`, full v2 block-engine builds, cloned verbatim). The owner chose the **examples** path.
- **Build via the v2 block engine**, not `/api/generate`. Evidence: existing examples (e.g. `pebble/examples/flour-fern`) are v2 builds — they carry `.pebble-ids.json`, motion primitives, and `globals.css` WITH `@tailwind` directives scaffolded by the compiler. The v2 compiler scaffolds `package.json`/config/`globals.css` deterministically, making the `@tailwind`-missing defect class (which broke the deleted Qwen `mechanic` build) **structurally impossible**.
- **A "vibe" = a set of blocks.** Blocks live in `pebble/blocks/library/` as `<block_id>.json` (block_type, vibe_tags, dna_tags, slots) + `<block_id>.tsx`. Naming: `<type>_<style>_<vibe>`. None of the 7 existing vibes (warm-craft, clean-trust, bold-energetic, editorial-minimal, appetizing-rich, luxurious-spa, playful-illustrated) fits trades conversion patterns — hence a new `trade-pro` vibe.

## The `trade-pro` vibe (new block set)

New blocks in `pebble/blocks/library/`, each `vibe_tags: ["trade-pro", "local-service", "trustworthy"]`, with appropriate `dna_tags`. Aesthetic: confident, local, conversion-first — strong CTAs, trust signals, real work photos; NOT corporate-soft, NOT loud-neon.

| block_id | block_type | Purpose / key slots |
|---|---|---|
| `library/hero_trade_pro` | hero | Full-bleed work photo; headline; subhead; **tap-to-call phone**; "Free Estimate" CTA; trust line (Licensed • Insured • 24/7). Slots: eyebrow, headline, subhead, phone, cta_label, trust_line, hero_image (pexels query template). |
| `library/trust_strip_trade` | trust (new type) | Stat band: years_in_business, jobs_completed, licensed_insured, rating. Slots: 3–4 stat {value,label}. |
| `library/services_grid_trade` | services | Service cards: icon, name, blurb, optional `from_price`. Slots: list of {name, blurb, price?}. |
| `library/service_area_trade` | coverage (new type) | Neighborhoods/cities served (local SEO + reassurance). Slots: area headline + list of place names. |
| `library/gallery_beforeafter_trade` | gallery | Before/after (or job) photo pairs. Slots: list of {before_img, after_img, caption} OR job photo grid. |
| `library/testimonials_trade` | testimonial | Review cards: stars, quote, name, neighborhood. Slots: list of {quote, name, locale, stars}. |
| `library/about_trade` | about | Owner/crew story + credentials, family-owned angle. Slots: headline, story_paragraphs, credentials list, portrait_image. |
| `library/quote_form_trade` | contact | "Get a Free Quote" form → posts to `/api/forms/<slug>` (works on static publish). Slots: headline, fields (name, phone, service select, message), phone/email/address. |
| `library/footer_trade` | footer | Hours, service area, license #, phone, quick links. Slots: hours, license_no, phone, links. |

**New block_types** introduced: `trust`, `coverage`. Must be registered wherever block types are enumerated (`pebble/blocks/schema.py` / `catalog.py` / the sonnet_block_picker's slot map). Verify the picker can place new types or treat them as optional sections.

**Per-trade accent palette** via existing ThemeTokens (no per-trade block forks): plumber→blue, electrician→amber, HVAC→teal/red, landscaper→green, cleaning→fresh-cyan, contractor→slate/orange, roofer→charcoal/red, auto→steel/red. The DNA/theme layer supplies the accent; blocks read tokens.

**Implementation note:** block component authoring leans on the `ui-ux-pro-max` skill for layout/craft. Each `.tsx` is a real client/server component using ThemeTokens + motion primitives, mirroring existing `*_clean`/`*_bold` blocks.

## Build → verify → promote pipeline

1. **Author 8 briefs** (below) — realistic business name, city, services, hours, license #, tone. Quality starts here.
2. **Build** each via `build_v2_core` (vibe = trade-pro). Use the existing v2 path (`POST /api/v2/generate` / `run_build_v2`). Sonnet for copy.
3. **Eval gate** — run `python -m pebble.evals output/<slug>`; must pass FOUNDATION checks.
4. **Visual check** — render `/preview/<slug>/` (proxy fix is live) and eyeball: styled, on-brand, trades tone, images wired, no invented data.
5. **Promote passers**:
   - Move `output/<slug>` → `pebble/examples/<slug>/` (site + brief.json + build_meta.json).
   - Add an entry to `pebble/example_gallery.json` (slug, name, industry, vibe="trade-pro", thumbnail path).
   - Capture a Playwright homepage screenshot → `ui/v3/public/templates-preview/<slug>.png` (or the gallery's image dir) via the existing postbuild screenshot path.
6. Failures → fix the block/brief, rebuild; or drop from the wave. Only passers reach the gallery.

## Wave-1 trades + draft briefs

(Names are illustrative, locally-grounded, non-trademarked. Final copy is LLM-generated per brief; no invented founding years unless supplied.)

1. **Plumber** — "Tidewater Plumbing Co.", Portland OR. Services: drain cleaning, water heaters, leak repair, repiping, emergency. Licensed & insured, 24/7. Accent: blue.
2. **Electrician** — "Brightwire Electric", Austin TX. Panel upgrades, EV chargers, lighting, troubleshooting, generators. Accent: amber.
3. **HVAC** — "Northpeak Heating & Air", Denver CO. AC install/repair, furnace, tune-ups, indoor air quality, emergency. Accent: teal/red.
4. **Landscaper** — "Cedar & Stone Landscapes", Raleigh NC. Design/build, lawn care, hardscape, irrigation, seasonal cleanup. Accent: green.
5. **Cleaning service** — "Sparrow Home Cleaning", Minneapolis MN. Recurring, deep clean, move-in/out, office. Accent: fresh-cyan.
6. **General contractor** — "Ridgeline Builders", Boise ID. Remodels, additions, kitchens, baths, decks. Accent: slate/orange.
7. **Roofer** — "Summit Ridge Roofing", Kansas City MO. Replacement, repair, storm/insurance, inspections, gutters. Accent: charcoal/red.
8. **Auto repair** — "Gearworks Auto Service", Columbus OH. Diagnostics, brakes, oil, AC, tires, fleet. Accent: steel/red. (Replaces the deleted broken Mechanic — done right this time.)

## Quality gate (definition of done per example)

- `pebble.evals` passes (no failures on FOUNDATION checks).
- Renders styled in `/preview/<slug>/`; trades-appropriate tone; CTA/phone/trust strip present; no `[BUSINESS PHONE]`-style leftover placeholders unless intentional; no invented founding year/metrics.
- Quote form wired to `/api/forms/<slug>`.
- Playwright thumbnail captured.
- Registered in `example_gallery.json`; clone flow (`POST /api/examples/clone`) produces a working copy.

## Out of scope (this spec)

- Waves 2–4 (health/wellness, professional/B2B, food/retail/events) — same pipeline, future specs.
- Template-skeleton (registry) path — not this effort.
- New publish/hosting work — the quote form relies on the existing/planned `/api/forms` routing (see `docs/superpowers/plans/2026-06-02-hosted-contact-forms.md`).

## Risks / open items

- **New block_types (`trust`, `coverage`)** — confirm the v2 block picker + schema accept new types or treat them as optional sections; otherwise model them as `services`/`about` variants.
- **v2 engine health** — block registry imports clean now; confirm `run_build_v2` produces a full styled site end-to-end before batch-building all 8.
- **8 accent palettes from one block set** — verify blocks read Themetokens cleanly so the 8 look distinct, not cloned.
- **Playwright path** — confirm the postbuild screenshot path works headless for thumbnail capture.

## Key files

- Blocks: `pebble/blocks/library/` (+ `schema.py`, `catalog.py`, `registry.py`, the sonnet block picker).
- v2 build: `pebble/server/build_v2.py` (`run_build_v2`), `build_v2_core`.
- Examples: `pebble/examples/<slug>/`, `pebble/example_gallery.json`, `pebble/server/examples.py`.
- Gallery UI: `ui/v3/app/examples/page.tsx`.
- Evals: `pebble/evals/` (`python -m pebble.evals output/<slug>`).
- Screenshots: `pebble/postbuild.py` (Playwright path).
