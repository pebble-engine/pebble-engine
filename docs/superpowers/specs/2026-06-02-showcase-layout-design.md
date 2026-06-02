# Showcase Layout — Design Spec

**Date:** 2026-06-02
**Status:** Approved direction; pending spec review → implementation plan.
**Branch:** claude/launch-readiness-2026-06-01

## Goal

Add a second, visibly distinct template style to the free `/examples` gallery. Today all 8 trade examples draw from the single `trade-pro` vibe, which has ~one block per section, so Sonnet assembles the same blocks in the same order every time — the gallery looks like one template repeated across eight industries.

The new **`showcase`** style is image-dominant, light on words, and CTA-forward: big work photos do the talking, with a call-to-action at every scroll-stop. It gives the gallery two clearly different looks side by side.

## Background / why this shape

- **A "vibe" = a set of blocks** in `pebble/blocks/library/`. The v2 build pins the block menu to a brief's `vibe` (`_build_block_menu(registry, vibe=…)` in `pebble/server/build_v2.py`), so a `showcase` brief draws only from showcase-tagged blocks. This is the same mechanism `trade-pro` already uses.
- **Reuse the image-forward work just shipped.** The 2026-06-01 image-forward pass made `services_*` and `gallery_beforeafter_trade` photo-led with `next/image`, fixed the preview proxy, and added per-build photo dedup. Showcase reuses those blocks where it can; only the genuinely-different sections are new.

## The `showcase` vibe (new block set)

**Aesthetic:** confident, image-dominant, minimal copy, conversion-first. Large edge-to-edge photography, short headlines, repeated strong CTAs. NOT text-heavy, NOT corporate-soft.

### 3 new blocks

| block_id | block_type | Purpose / key slots |
|---|---|---|
| `library/hero_showcase` | hero | Full-bleed work photo; **centered** short headline (distinct from the left-column `hero_trade_pro`); eyebrow; one big primary CTA ("Get a Free Quote") + tap-to-call phone; thin trust line. Slots: eyebrow, headline, subheadline (short), phone, cta_primary, trust_line, hero_image. |
| `library/gallery_showcase` | gallery | The centerpiece: large edge-to-edge work-photo masonry/grid, bigger tiles than `gallery_beforeafter_trade`, hover-zoom, minimal captions. Slots: eyebrow, headline (short), projects list of {caption, image}. Uses `next/image` per item. |
| `library/cta_banner_showcase` | contact | Full-width image band with a single bold CTA + phone — a mid-page conversion prompt. block_type `contact` so it satisfies the picker's contact slot if needed and links to `#contact`. Slots: headline (short), cta_primary, phone, bg_image. |

All three: `vibe_tags` include `"showcase"`; `next/image` for photos; named `Stagger` import; `min-h-[44px]` + `focus-visible:` on CTAs; declare only palette_slots the `.tsx` uses; mobile-first.

### Reused blocks (add `"showcase"` to their `vibe_tags`)

- `trust_strip_trade` (compact credentials band)
- `services_photo_grid` (reusable photo-top services — built 2026-06-01)
- `contact_quote_trade` (quote form)
- `footer_anchored_clean` (footer)

This gives the showcase vibe full essential-section coverage (hero, services, gallery, contact, footer) so the menu pin never falls back. Deliberately **excluded**: the long `about_team_clean` and the text-heavy `service_area_trade` chips — omitting them is what keeps showcase light on words.

### Section rhythm (the showcase look)

`hero_showcase` → `trust_strip_trade` (thin) → **`gallery_showcase` (big centerpiece)** → `services_photo_grid` → `cta_banner_showcase` → `contact_quote_trade` → `footer_anchored_clean`.

The new hero + promoted big gallery + dropped text sections are what make it read as a different template, even though several mid-page blocks are shared.

## Rollout

- **Convert the 4 visual trades to showcase:** stamp `vibe: "showcase"` on the Cedar & Stone Landscapes (landscaper), Summit Ridge Roofing (roofer), Ridgeline Builders (general contractor), and Gearworks Auto Service (auto repair) briefs in `pebble/examples_pipeline/trade_briefs.py`.
- **Keep the other 4 as trade-pro:** Tidewater Plumbing, Brightwire Electric, Northpeak Heating & Air, Sparrow Home Cleaning.
- Rebuild all 8 (4 showcase + 4 trade-pro), eval-gate, visual-check, **owner reviews the new renders**, then re-promote all 8 (idempotent `scripts/promote_example.py`). The manifest records each example's `vibe` (`"showcase"` or `"trade-pro"`).
- This also completes the still-pending promotion of the image-forward 8 — they ship together, as one varied gallery.

## Quality gate (per example)

- `pebble.evals` passes FOUNDATION checks (esp. `no_invented_time_markers`, `images_use_next_image`, `tailwind_directives_present`).
- Renders styled in `/preview/<slug>/`; correct tone; images display; CTAs present; no invented data.
- Showcase examples read as visibly distinct from the trade-pro ones (the whole point) — owner confirms at the review gate.
- Clone flow (`POST /api/examples/clone`) produces a working copy.

## Testing

- Registry-load + placeholder-resolution + palette-parity for the 3 new blocks.
- `showcase` essential-section coverage test (hero/services/gallery/contact/footer each have ≥1 showcase block) — mirrors `tests/test_trade_pro_blocks.py`.
- Existing block suite stays green; per-build photo dedup still holds (no repeated photos in the bigger gallery).

## Risks / mitigations

- **Showcase not distinct enough** (shares mid-page blocks) — the new hero, big gallery centerpiece, and dropped text sections carry the difference; owner confirms at the review gate; if still too similar, add a distinct services treatment.
- **Bigger gallery exhausts distinct photos** — `gallery_showcase` requests more images; the 2026-06-01 dedup picks distinct Pexels results per build, but a large grid may repeat if Pexels returns few results for a niche query. Cap the gallery item count (e.g. ≤6) and rely on the dedup fallback.
- **`cta_banner_showcase` as block_type `contact`** could collide with the real quote form in the picker — keep its slots minimal and ensure both can coexist; if the picker treats two `contact` blocks as mutually exclusive, model the banner as a `hero`/`scroll-story` type instead. Verify during implementation.
- **Rebuild regenerates copy** — owner re-approves the 8 before re-promote.

## Out of scope

- The other archetypes (Bold Conversion, Split-Screen, Editorial) — future waves if wanted.
- New verticals beyond the existing 8 trades.
- Any publish/hosting changes.

## Key files

- Blocks: `pebble/blocks/library/{hero_showcase,gallery_showcase,cta_banner_showcase}.{json,tsx}` (new); `vibe_tags` edits to `trust_strip_trade.json`, `services_photo_grid.json`, `contact_quote_trade.json`, `footer_anchored_clean.json`.
- Vibe pin: `pebble/server/build_v2.py` (`_build_block_menu` — already supports `vibe`; no change expected).
- Briefs: `pebble/examples_pipeline/trade_briefs.py` (4 briefs → `vibe: "showcase"`).
- Pipeline: `scripts/build_trade_examples.py`, `scripts/promote_example.py`, `pebble/example_gallery.json`, `pebble/examples/<slug>/`.
- Tests: `tests/test_showcase_blocks.py` (new).
- Evals: `python -m pebble.evals <slug>`.
