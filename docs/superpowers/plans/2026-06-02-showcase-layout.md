# Showcase Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Block-component tasks (Phase 1) additionally use the `ui-ux-pro-max` skill for layout/craft.

**Goal:** Add a second, image-dominant `showcase` template style to the `/examples` gallery and convert the 4 visual trades to it, so the gallery shows two visibly different looks.

**Architecture:** A "vibe" is a set of blocks; the v2 build pins the block menu to `brief["vibe"]` (already supported). The new `showcase` vibe = 3 new image-forward blocks + 4 existing image-forward blocks re-tagged `showcase`. The 4 visual-trade briefs get `vibe: "showcase"`; all 8 examples are rebuilt and re-promoted together.

**Tech Stack:** Python 3.14 (stdlib HTTP engine, pytest), the v2 block engine (`pebble/blocks/*`, `pebble/sonnet_block_picker.py`, `pebble/server/build_v2.py`), Next.js 14 generated sites, Playwright.

**Spec:** `docs/superpowers/specs/2026-06-02-showcase-layout-design.md`

---

## File Structure

**Phase 1 — 3 new showcase blocks** (each `.json` + `.tsx` in `pebble/blocks/library/`)
- Create: `hero_showcase`, `gallery_showcase`, `cta_banner_showcase`.

**Phase 2 — tag reused blocks + coverage test**
- Modify `vibe_tags`: `trust_strip_trade.json`, `services_photo_grid.json`, `contact_quote_trade.json`, `footer_anchored_clean.json`.
- Test: `tests/test_showcase_blocks.py`.

**Phase 3 — rollout** (convert 4 briefs, rebuild 8, re-promote)
- Modify: `pebble/examples_pipeline/trade_briefs.py`.

---

## Conventions for all new blocks (read once)

`"use client"`; `import Image from "next/image"` for photos; `import { Stagger, StaggerItem } from "@/components/motion/Stagger"` (NAMED import); `RevealWords` default import. Placeholders: `{{slot}}`, list iteration `{/* {{list_list_start}} */} … {/* {{list_list_end}} */}` with `{{list[].field}}`. Per-item photos use `<Image src="{{list[].image}}" alt=… fill sizes=… className="object-cover">` inside a `relative aspect-[…]` wrapper (the resolver swaps the plain-text query for a real Pexels URL; build_v2 dedups photos across the page). Palette tokens `bg-{{bg}}`/`text-{{fg}}`/`{{accent}}`/`text-{{accent_fg}}`; muted body text is hardcoded `text-slate-600`/`text-white/70` (the `muted` palette token is a surface tint, not text). Declare ONLY palette_slots the `.tsx` actually references. CTAs: `min-h-[44px]` + `focus-visible:ring-2`. Mobile-first. NO emoji icons (inline SVG only). Acceptance for every block: `BlockRegistry.load` accepts it, placeholders resolve, palette parity holds.

---

## Phase 1: New showcase blocks

### Task 1: `hero_showcase`

**Files:** Create `pebble/blocks/library/hero_showcase.json` + `.tsx`

- [ ] **Step 1: Write the `.json`** (complete):

```json
{
  "block_id": "library/hero_showcase",
  "block_type": "hero",
  "vibe_tags": ["showcase", "visual", "image-led", "local-service", "conversion-first"],
  "dna_tags": ["cinematic_imax", "swiss_magazine", "terminal_operator"],
  "slots": {
    "eyebrow": {"kind": "text", "max_chars": 40, "tone": "credential-forward (Licensed & Insured · Serving <City>)"},
    "headline": {"kind": "text", "max_chars": 60, "tone": "short, punchy, benefit-first — 3 to 6 words"},
    "subheadline": {"kind": "text", "max_chars": 110, "tone": "one short line; outcome + reassurance"},
    "phone": {"kind": "text", "max_chars": 24, "tone": "display phone number"},
    "cta_primary": {"kind": "text", "max_chars": 24, "tone": "Get a Free Quote / See Our Work"},
    "trust_line": {"kind": "text", "max_chars": 60, "tone": "Licensed • Insured • Free Estimates"},
    "hero_image": {"kind": "image", "pexels_query_template": "{industry_scene} professional finished work wide shot natural light", "aspect": "16/9"}
  },
  "palette_slots": ["accent", "accent_fg"]
}
```

- [ ] **Step 2: Author the `.tsx`** with `ui-ux-pro-max` — full-bleed `hero_image` (next/image `fill`, `priority`) with a dark gradient overlay for legibility, and a **CENTER-anchored** content column (distinct from the left-column `hero_trade_pro`): eyebrow, big `{{headline}}` in `<RevealWords>` (`text-white`), short `{{subheadline}}` (`text-white/80`), a CTA row with a primary `MagneticButton` (`bg-{{accent}} text-{{accent_fg}}`, href `#contact`, label `{{cta_primary}}`) + a tap-to-call `<a href="tel:{{phone}}">` (inline SVG phone icon), and a `{{trust_line}}` strip below. Use `min-h-[100dvh] md:min-h-screen`. Centered text → `text-center items-center`. Reference `hero_trade_pro.tsx` for the overlay + CTA + phone-icon patterns; differ by centering and shorter copy. (`MagneticButton` is a default import from `@/components/motion/MagneticButton`; `Parallax` from `@/components/motion/Parallax` optional for the bg.)

- [ ] **Step 3: Verify registry + parity**

Run:
```bash
python -c "from pathlib import Path; from pebble.blocks.registry import BlockRegistry; r=BlockRegistry.load(Path('pebble/blocks/library').parent); b=r._blocks['library/hero_showcase']; s=b.template_source; print('type',b.metadata.block_type,'palette',b.metadata.palette_slots,'parity',all(('{{'+x+'}}') in s for x in b.metadata.palette_slots))"
```
Expected: `type hero palette ['accent', 'accent_fg'] parity True`. (If the `.tsx` references more/fewer palette tokens, make the JSON match.)

- [ ] **Step 4: Block suite**

Run: `python -m pytest tests/ -q -k "block or trade or showcase" --no-header -p no:cacheprovider 2>&1 | tail -5`
Expected: no new failures.

- [ ] **Step 5: Commit**

```bash
git add pebble/blocks/library/hero_showcase.json pebble/blocks/library/hero_showcase.tsx
git commit -m "feat(blocks): hero_showcase (full-bleed centered image hero)"
```

### Task 2: `gallery_showcase` (the centerpiece)

**Files:** Create `pebble/blocks/library/gallery_showcase.json` + `.tsx`

- [ ] **Step 1: Write the `.json`** (complete):

```json
{
  "block_id": "library/gallery_showcase",
  "block_type": "gallery",
  "vibe_tags": ["showcase", "visual", "image-led", "local-service"],
  "dna_tags": ["cinematic_imax", "swiss_magazine"],
  "slots": {
    "eyebrow": {"kind": "text", "max_chars": 40, "tone": "Our work / Recent projects"},
    "headline": {"kind": "text", "max_chars": 50, "tone": "short — 2 to 5 words"},
    "projects": {"kind": "list", "tone": "5-6 items; each {caption (50), image (a Pexels query for THIS specific finished job so each photo is distinct)}"}
  },
  "palette_slots": ["bg", "fg", "accent"]
}
```

(Cap at 5-6 items so the per-build photo dedup can supply distinct images.)

- [ ] **Step 2: Author the `.tsx`** with `ui-ux-pro-max` — a LARGE, near-edge-to-edge work-photo grid that reads as the page centerpiece: wider container than the trade gallery (e.g. `max-w-7xl`), bigger tiles, a 2–3 column grid with one feature tile spanning 2 columns/rows for visual rhythm, hover-zoom, minimal caption overlaid or beneath. Use `next/image` `fill` per item inside `relative aspect-[…]` wrappers, `Stagger` entrance. Reference `gallery_beforeafter_trade.tsx` (per-item `<Image fill>` pattern) and `gallery_masonry_editorial.tsx` (`Masonry` from `@/components/motion/Masonry`) — pick grid OR masonry, whichever reads bigger. Short header (`{{eyebrow}}` + `{{headline}}`).

- [ ] **Step 3: Verify registry + parity** (same one-liner as Task 1 Step 3, block id `library/gallery_showcase`). Expected `type gallery`, parity True, and `{{projects[].image}}` present:
```bash
python -c "from pathlib import Path; from pebble.blocks.registry import BlockRegistry; r=BlockRegistry.load(Path('pebble/blocks/library').parent); b=r._blocks['library/gallery_showcase']; s=b.template_source; print('img','{{projects[].image}}' in s,'parity',all(('{{'+x+'}}') in s for x in b.metadata.palette_slots))"
```
Expected: `img True parity True`.

- [ ] **Step 4: Commit**

```bash
git add pebble/blocks/library/gallery_showcase.json pebble/blocks/library/gallery_showcase.tsx
git commit -m "feat(blocks): gallery_showcase (edge-to-edge work-photo centerpiece)"
```

### Task 3: `cta_banner_showcase`

**Note on block_type:** the Sonnet picker "prefers one block of each core block_type", so typing this `contact` would make the picker choose EITHER it OR the quote form. To guarantee BOTH appear, type it `scroll-story` (an OPTIONAL type the picker reaches for with service/contractor businesses — exactly the showcase trades). Verified in Phase 3 Task 7.

**Files:** Create `pebble/blocks/library/cta_banner_showcase.json` + `.tsx`

- [ ] **Step 1: Write the `.json`** (complete):

```json
{
  "block_id": "library/cta_banner_showcase",
  "block_type": "scroll-story",
  "vibe_tags": ["showcase", "visual", "conversion-first", "local-service"],
  "dna_tags": ["cinematic_imax", "terminal_operator"],
  "slots": {
    "headline": {"kind": "text", "max_chars": 60, "tone": "short, action-oriented — Ready to start? / Let's build something"},
    "subheadline": {"kind": "text", "max_chars": 90, "tone": "one short reassurance line (optional)"},
    "cta_primary": {"kind": "text", "max_chars": 24, "tone": "Get a Free Quote / Call Now"},
    "phone": {"kind": "text", "max_chars": 24, "tone": "display phone number"},
    "bg_image": {"kind": "image", "pexels_query_template": "{industry_scene} professional team at work wide dramatic", "aspect": "21/9"}
  },
  "palette_slots": ["accent", "accent_fg"]
}
```

- [ ] **Step 2: Author the `.tsx`** with `ui-ux-pro-max` — a full-width image band (`bg_image` via next/image `fill` + dark overlay), centered `{{headline}}` (`text-white`, large), optional `{{subheadline}}` (`text-white/80`), and a CTA row: primary `MagneticButton` (`bg-{{accent}} text-{{accent_fg}}`, href `#contact`, `{{cta_primary}}`) + tap-to-call `<a href="tel:{{phone}}">` with inline SVG phone icon. Fixed band height (`min-h-[420px]` / `py-28`). `min-h-[44px]` + `focus-visible:` on both CTAs.

- [ ] **Step 3: Verify registry + parity** (one-liner, block id `library/cta_banner_showcase`). Expected `type scroll-story`, parity True.

- [ ] **Step 4: Commit**

```bash
git add pebble/blocks/library/cta_banner_showcase.json pebble/blocks/library/cta_banner_showcase.tsx
git commit -m "feat(blocks): cta_banner_showcase (full-width image CTA band)"
```

---

## Phase 2: Tag reused blocks + coverage test

### Task 4: Tag 4 existing blocks `showcase`

So the showcase menu has full essential-section coverage (hero, services, gallery, contact, footer) and the pin never falls back.

**Files:** Modify `vibe_tags` in 4 existing `.json` files.

- [ ] **Step 1: Append `"showcase"`** to the `vibe_tags` array (append only; keep existing tags) in each of:
  - `pebble/blocks/library/trust_strip_trade.json`
  - `pebble/blocks/library/services_photo_grid.json`
  - `pebble/blocks/library/contact_quote_trade.json`
  - `pebble/blocks/library/footer_anchored_clean.json`

  Read each file first; edit the `vibe_tags` list carefully (valid JSON).

- [ ] **Step 2: Verify all still validate + showcase coverage**

Run:
```bash
python -c "
from pathlib import Path
from pebble.blocks.registry import BlockRegistry
reg = BlockRegistry.load(Path('pebble/blocks/library').parent)
by_type = {}
for b in reg._blocks.values():
    if 'showcase' in b.metadata.vibe_tags:
        by_type.setdefault(b.metadata.block_type, []).append(b.metadata.block_id)
for t in ('hero','services','gallery','contact','footer','trust','scroll-story'):
    print(t, by_type.get(t, ['MISSING']))
"
```
Expected: every line prints at least one block_id, no MISSING (hero=hero_showcase, services=services_photo_grid, gallery=gallery_showcase, contact=contact_quote_trade, footer=footer_anchored_clean, trust=trust_strip_trade, scroll-story=cta_banner_showcase).

- [ ] **Step 3: Commit**

```bash
git add pebble/blocks/library/trust_strip_trade.json pebble/blocks/library/services_photo_grid.json pebble/blocks/library/contact_quote_trade.json pebble/blocks/library/footer_anchored_clean.json
git commit -m "feat(blocks): tag trust/services/contact/footer for the showcase vibe"
```

### Task 5: Showcase coverage test

**Files:** Create `tests/test_showcase_blocks.py`

- [ ] **Step 1: Write the test**

```python
# tests/test_showcase_blocks.py
from pathlib import Path

from pebble.blocks.registry import BlockRegistry

LIB_ROOT = Path(__file__).resolve().parent.parent / "pebble" / "blocks"


def test_showcase_has_every_essential_section():
    reg = BlockRegistry.load(LIB_ROOT)
    by_type: dict[str, list[str]] = {}
    for blk in reg._blocks.values():
        if "showcase" in blk.metadata.vibe_tags:
            by_type.setdefault(blk.metadata.block_type, []).append(blk.metadata.block_id)
    # The showcase menu must cover every section its template uses.
    for section in ("hero", "services", "gallery", "contact", "footer"):
        assert by_type.get(section), f"no showcase block for essential section: {section}"


def test_showcase_new_blocks_use_next_image():
    """The 3 new showcase blocks are image-forward — they must use next/image,
    not raw <img> (Core Web Vitals + the images_use_next_image eval)."""
    reg = BlockRegistry.load(LIB_ROOT)
    for bid in ("library/hero_showcase", "library/gallery_showcase", "library/cta_banner_showcase"):
        src = reg._blocks[bid].template_source
        assert "next/image" in src, f"{bid} must import next/image"
        assert "<img" not in src, f"{bid} must not use raw <img>"
```

- [ ] **Step 2: Run it**

Run: `python -m pytest tests/test_showcase_blocks.py -q`
Expected: PASS (2 passed).

- [ ] **Step 3: Commit**

```bash
git add tests/test_showcase_blocks.py
git commit -m "test(blocks): showcase vibe covers every essential section + uses next/image"
```

---

## Phase 3: Rollout — convert 4 briefs, rebuild 8, re-promote

### Task 6: Convert the 4 visual-trade briefs to `showcase`

**Files:** Modify `pebble/examples_pipeline/trade_briefs.py`

- [ ] **Step 1: Change the `vibe` field** from `"trade-pro"` to `"showcase"` for exactly these 4 briefs (match on `industry`): `landscaper`, `roofer`, `general contractor`, `auto repair`. Leave `plumber`, `electrician`, `hvac`, `cleaning service` as `"trade-pro"`. Change ONLY the `vibe` value; leave `business_name`, `industry`, `extra_context` untouched.

- [ ] **Step 2: Sanity test**

Run:
```bash
python -c "from pebble.examples_pipeline.trade_briefs import TRADE_BRIEFS as T; import collections; c=collections.Counter(b['vibe'] for b in T); print(c); show=[b['industry'] for b in T if b['vibe']=='showcase']; print('showcase:', sorted(show))"
```
Expected: `Counter({'trade-pro': 4, 'showcase': 4})` and `showcase: ['auto repair', 'general contractor', 'landscaper', 'roofer']`.

- [ ] **Step 3: Commit**

```bash
git add pebble/examples_pipeline/trade_briefs.py
git commit -m "feat(examples): convert the 4 visual trades to the showcase vibe"
```

### Task 7: Build one showcase example + verify the layout

**Files:** none new — uses `scripts/build_trade_examples.py`, the live engine, `python -m pebble.evals`.

- [ ] **Step 1: Build the landscaper** (LLM key required; engine running for the preview check):

Run: `python scripts/build_trade_examples.py --only landscaper`
Expected: `1/1 succeeded` + a slug.

- [ ] **Step 2: Confirm the showcase blocks were picked AND both the CTA banner and the quote form appear**

Run:
```bash
python -c "import json; p=json.load(open('output/cedar-stone-landscapes/build_meta.json'))['block_picks']; print(p); assert 'library/hero_showcase' in p, 'hero_showcase missing'; assert 'library/gallery_showcase' in p, 'gallery_showcase missing'; assert 'library/cta_banner_showcase' in p, 'cta banner missing (picker may have dropped scroll-story)'; assert 'library/contact_quote_trade' in p, 'quote form missing'; print('OK both banner + form present')"
```
Expected: `OK both banner + form present`. If the banner is missing, the picker dropped the `scroll-story` block — fix by strengthening the block's vibe_tags / picker guidance, OR (fallback) bake the CTA band into the bottom of `gallery_showcase` and drop the standalone block. Do NOT proceed to the batch until a showcase build reliably includes the banner.

- [ ] **Step 3: Eval-gate**

Run: `python -m pebble.evals cedar-stone-landscapes --skip-compile 2>&1 | grep -E "(no_invented_time|images_use_next|Score)"`
Expected: `no_invented_time_markers` + `images_use_next_image` pass.

- [ ] **Step 4: Visual check** — start/confirm the engine, warm `/preview/cedar-stone-landscapes/`, screenshot full-page (scroll to trigger Stagger). Confirm: full-bleed centered hero, BIG gallery centerpiece, photo services, the CTA banner band, quote form — and that it reads as clearly DIFFERENT from the trade-pro plumber. No commit (verification only). If the layout isn't distinct enough or photos repeat, fix the responsible block before the batch.

### Task 8: Rebuild all 8, review gate, re-promote

**Files:** `pebble/examples/<slug>/`, `pebble/example_gallery.json`, `ui/v3/public/templates-preview/` (if thumbnails captured).

- [ ] **Step 1: Build all 8** — `python scripts/build_trade_examples.py`. Expected `8/8 succeeded`.

- [ ] **Step 2: Eval-gate each** — for all 8, `python -m pebble.evals <slug> --skip-compile` and confirm `no_invented_time_markers` + `images_use_next_image` pass. Fix-or-rebuild any failure (per the image-forward lessons: a stray invented time-marker usually clears on rebuild; a raw `<img>` means a block needs `next/image`).

- [ ] **Step 3: Capture fresh screenshots** of all 8 (Playwright, full-page, scroll). Save `docs/superpowers/wave1-screenshots/showcase_<slug>.png`.

- [ ] **Step 4: STOP — owner review.** Present the 8 renders (4 showcase + 4 trade-pro) to the owner. Confirm the two styles look clearly distinct and on-brand. Do NOT re-promote until the owner approves. Fix-or-drop per their call.

- [ ] **Step 5: Re-promote all 8** — for each approved slug, `python scripts/promote_example.py <slug> --vibe <showcase|trade-pro>` (pass the slug's actual vibe). The script replaces each `pebble/examples/<slug>/` + manifest entry in place (idempotent); the manifest records the per-example `vibe`.

- [ ] **Step 6: Verify the gallery** — `GET /api/examples` lists 8 with a mix of `vibe: "showcase"` (4) and `vibe: "trade-pro"` (4); clone one showcase example and confirm it lands in `output/` and renders.

- [ ] **Step 7: Commit the promoted examples + manifest**

```bash
git add pebble/examples/ pebble/example_gallery.json ui/v3/public/templates-preview/
git commit -m "feat(examples): ship showcase style — 4 visual trades converted, gallery now 2 looks"
```

---

## Self-Review

**Spec coverage:**
- New showcase vibe + 3 new blocks → Tasks 1-3 ✓
- Reuse 4 image-forward blocks via vibe_tags → Task 4 ✓
- Section rhythm (hero → trust → gallery → services → cta banner → quote → footer) → emerges from the showcase menu + picker's one-per-type preference; verified in Task 7 ✓
- cta_banner block_type collision risk → resolved (typed `scroll-story`) + verified both banner+form appear (Task 7 Step 2) ✓
- Convert 4 visual trades, keep 4 trade-pro → Task 6 ✓
- Rebuild + re-promote all 8 with owner review → Task 8 (gate is Step 4) ✓; also lands the pending image-forward promotion ✓
- Testing (registry/parity/coverage/next-image; build/eval/visual gate) → Tasks 1-3, 5, 7-8 ✓

**Placeholder scan:** The 3 new `.tsx` are authored during execution via `ui-ux-pro-max` with complete `.json` contracts + concrete structural direction + acceptance checks (correct granularity for visual components). No TBDs in logic/config tasks. `<showcase|trade-pro>` / `<slug>` in Task 8 are runtime values gated by the owner-review step, not placeholders.

**Type/name consistency:** block ids `hero_showcase` / `gallery_showcase` / `cta_banner_showcase` consistent across Tasks 1-3, 5, 7. `cta_banner_showcase` block_type `scroll-story` consistent (Task 3 JSON + Task 4 coverage + Task 7 verify). Per-item placeholder `{{projects[].image}}` (gallery) and `{{services[].image}}` (reused services) consistent. `promote_example.py promote(slug, vibe)` unchanged. Manifest `vibe` field records `showcase`/`trade-pro` per example.
