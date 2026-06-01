# Trade-Pro Example Library (Wave 1) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Block-component tasks (Phase 2) additionally use the `ui-ux-pro-max` skill for layout/craft.

**Goal:** Add a `trade-pro` vibe (a set of v2 blocks) + a build→verify→promote pipeline, then ship 8 local-trade example sites to the free `/examples` gallery.

**Architecture:** New blocks live in `pebble/blocks/library/<id>.{json,tsx}` (auto-discovered by `BlockRegistry.load`). Two new `block_type`s (`trust`, `coverage`) are added to the schema. The v2 build gains an optional `vibe` filter so trade briefs deterministically draw from trade-pro blocks. A build script drives `build_v2_core` per brief; a promote script moves eval-passing builds into `pebble/examples/` + registers them in `example_gallery.json` with a Playwright thumbnail.

**Tech Stack:** Python 3.14 (stdlib HTTP engine, pytest), the v2 block engine (`pebble/blocks/*`, `pebble/sonnet_block_picker.py`, `pebble/blocks_compiler.py`, `pebble/server/build_v2.py`), Next.js 14 generated sites, Playwright (`pebble/postbuild.py`).

**Spec:** `docs/superpowers/specs/2026-06-01-trade-pro-example-library-design.md`

---

## File Structure

**Phase 1 — engine plumbing**
- Modify: `pebble/blocks/schema.py` — add `trust`, `coverage` to `BlockType`.
- Modify: `pebble/server/build_v2.py` — `_build_block_menu` (or inline menu build) gains a `vibe` filter; `build_v2_core` reads `brief["vibe"]`.
- Modify: `pebble/sonnet_block_picker.py` — only if the menu filter belongs there (decide in Task 2).
- Test: `tests/test_block_schema_types.py`, `tests/test_build_v2_vibe_pin.py`.

**Phase 2 — trade-pro blocks** (each `.json` + `.tsx` in `pebble/blocks/library/`)
- Create: `hero_trade_pro`, `trust_strip_trade`, `services_grid_trade`, `service_area_trade`, `gallery_beforeafter_trade`, `contact_quote_trade` (6 new pairs).
- Modify: `about_team_clean.json`, `testimonials_*_clean.json` (closest existing), `footer_anchored_clean.json` — add `"trade-pro"` to `vibe_tags` so the pinned menu has full section coverage without forking neutral blocks.
- Test: `tests/test_trade_pro_blocks.py` (registry loads all new blocks; metadata valid).

**Phase 3 — pipeline**
- Create: `pebble/examples_pipeline/trade_briefs.py` — the 8 Wave-1 briefs as data.
- Create: `scripts/build_trade_examples.py` — calls `build_v2_core(brief, vibe="trade-pro")` per brief.
- Create: `scripts/promote_example.py` — move `output/<slug>` → `pebble/examples/<slug>`, append `example_gallery.json` entry, capture thumbnail.
- Test: `tests/test_promote_example.py`.

**Phase 4 — execute Wave 1** (operational, no new files)

---

## Phase 1: Engine plumbing

### Task 1: Add `trust` + `coverage` block types

**Files:**
- Modify: `pebble/blocks/schema.py:21-25` (the `BlockType` Literal)
- Test: `tests/test_block_schema_types.py` (Create)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_block_schema_types.py
from pebble.blocks.schema import validate_block_metadata


def _meta(block_type):
    return {
        "block_id": f"library/x_{block_type}",
        "block_type": block_type,
        "vibe_tags": ["trade-pro"],
        "dna_tags": ["terminal_operator"],
        "slots": {"headline": {"kind": "text", "max_chars": 80}},
        "palette_slots": ["bg", "fg", "accent", "accent_fg", "muted"],
    }


def test_trust_and_coverage_types_accepted():
    for t in ("trust", "coverage"):
        m = validate_block_metadata(_meta(t))
        assert m.block_type == t


def test_existing_types_still_accepted():
    for t in ("hero", "services", "about", "testimonials", "contact", "footer", "gallery"):
        assert validate_block_metadata(_meta(t)).block_type == t
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_block_schema_types.py -q`
Expected: FAIL (trust/coverage not in Literal — or, if validate doesn't runtime-check the Literal, the test passes trivially; if so, ALSO add a runtime membership check in validate_block_metadata as part of Step 3 and assert an invalid type raises).

- [ ] **Step 3: Implement** — in `pebble/blocks/schema.py`, extend the Literal:

```python
BlockType = Literal[
    "hero", "services", "about", "testimonials",
    "contact", "pricing", "footer", "gallery", "faq",
    "scroll-story", "trust", "coverage",
]
```

If `validate_block_metadata` does NOT already runtime-check membership, add after the required-field loop:

```python
    _ALLOWED_TYPES = {
        "hero", "services", "about", "testimonials", "contact",
        "pricing", "footer", "gallery", "faq", "scroll-story",
        "trust", "coverage",
    }
    if raw["block_type"] not in _ALLOWED_TYPES:
        raise ValueError(f"unknown block_type: {raw['block_type']!r}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_block_schema_types.py -q`
Expected: PASS

- [ ] **Step 5: Confirm the existing block suite still loads**

Run: `python -m pytest tests/ -q -k "block" -p no:cacheprovider`
Expected: no new failures.

- [ ] **Step 6: Commit**

```bash
git add pebble/blocks/schema.py tests/test_block_schema_types.py
git commit -m "feat(blocks): add trust + coverage block types for trade-pro vibe"
```

### Task 2: Optional `vibe` filter on the v2 block menu

**Goal:** When `brief["vibe"]` is set, the block menu sent to Sonnet is restricted to blocks whose `vibe_tags` include that vibe — guaranteeing trade briefs draw the trade-pro set. Must NOT change behavior when `vibe` is absent (existing builds unaffected).

**Files:**
- Modify: `pebble/server/build_v2.py` (the menu-building section, ~lines 64-116)
- Test: `tests/test_build_v2_vibe_pin.py` (Create)

- [ ] **Step 1: Read `pebble/server/build_v2.py:64-120`** to find the exact menu-building code (where the registry is turned into `block_menu`). Identify the function/inline block. This step is reconnaissance — no edit.

- [ ] **Step 2: Write the failing test** (against the menu builder — adapt the import to the real symbol found in Step 1; assume a helper `_build_block_menu(registry, vibe=None)` will be extracted):

```python
# tests/test_build_v2_vibe_pin.py
from pebble.blocks.registry import BlockRegistry
from pebble.server.build_v2 import _build_block_menu  # extract in Step 3 if inline


def _registry(tmp_path):
    # minimal 2-block registry: one trade-pro, one clean
    import json
    lib = tmp_path / "library"; lib.mkdir(parents=True)
    for bid, vibe in [("hero_trade_pro", "trade-pro"), ("hero_focused_clean", "clean")]:
        (lib / f"{bid}.json").write_text(json.dumps({
            "block_id": f"library/{bid}", "block_type": "hero",
            "vibe_tags": [vibe], "dna_tags": ["x"],
            "slots": {"headline": {"kind": "text", "max_chars": 80}},
            "palette_slots": ["bg", "fg", "accent", "accent_fg", "muted"],
        }), encoding="utf-8")
        (lib / f"{bid}.tsx").write_text("export default function X(){return null;}", encoding="utf-8")
    return BlockRegistry.load(tmp_path)


def test_vibe_pin_filters_menu(tmp_path):
    reg = _registry(tmp_path)
    menu = _build_block_menu(reg, vibe="trade-pro")
    ids = {b["block_id"] for b in menu}
    assert "library/hero_trade_pro" in ids
    assert "library/hero_focused_clean" not in ids


def test_no_vibe_returns_all(tmp_path):
    reg = _registry(tmp_path)
    menu = _build_block_menu(reg, vibe=None)
    ids = {b["block_id"] for b in menu}
    assert {"library/hero_trade_pro", "library/hero_focused_clean"} <= ids
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python -m pytest tests/test_build_v2_vibe_pin.py -q`
Expected: FAIL (`_build_block_menu` missing or no `vibe` param).

- [ ] **Step 4: Implement** — extract/define `_build_block_menu(registry, vibe=None)` in `build_v2.py`. When `vibe` is truthy, include only blocks whose `metadata.vibe_tags` contains `vibe`; else include all. Then in `build_v2_core`, read `vibe = (brief.get("vibe") or "").strip() or None` and pass it to `_build_block_menu`. Preserve the existing menu-dict shape (block_id, block_type, vibe_tags, slots, palette_slots).

```python
def _build_block_menu(registry, vibe=None):
    blocks = registry.all() if hasattr(registry, "all") else list(registry._blocks.values())
    menu = []
    for blk in blocks:
        m = blk.metadata
        if vibe and vibe not in m.vibe_tags:
            continue
        menu.append({
            "block_id": m.block_id,
            "block_type": m.block_type,
            "vibe_tags": m.vibe_tags,
            "slots": {k: {"kind": s.kind, "max_chars": s.max_chars,
                          "tone": s.tone, "pexels_query_template": s.pexels_query_template}
                      for k, s in m.slots.items()},
            "palette_slots": m.palette_slots,
        })
    return menu
```

(Match the exact menu-dict shape found in Step 1 — if it differs, mirror it.)

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_build_v2_vibe_pin.py -q`
Expected: PASS

- [ ] **Step 6: Guard against an empty menu** — if `vibe` filters the menu to fewer than one block per essential type (hero, services, contact, footer), log a warning and fall back to the unfiltered menu so a build never fails for lack of blocks. Add a test `test_vibe_pin_falls_back_when_incomplete` asserting that an unknown vibe returns the full menu.

- [ ] **Step 7: Commit**

```bash
git add pebble/server/build_v2.py tests/test_build_v2_vibe_pin.py
git commit -m "feat(build_v2): optional vibe pin filters the block menu"
```

---

## Phase 2: Author the trade-pro blocks

**For each block task below:** the `.json` is given complete (the contract). The `.tsx` is authored during execution using the `ui-ux-pro-max` skill, following the exact pattern in `pebble/blocks/library/hero_focused_clean.tsx` + `services_grid_clean.tsx` (`"use client"`, motion imports from `@/components/motion/`, `{{slot}}` / `{{list_start}}…{{list_end}}` / `{{list[].field}}` placeholders, `bg-{{bg}}`/`text-{{fg}}`/`{{accent}}` palette tokens, `export default function Name()`). Acceptance for every block: `BlockRegistry.load` accepts it (sibling `.tsx` exists, metadata validates) and the placeholders resolve at compile time.

**Aesthetic intent (all trade-pro blocks):** confident, local, conversion-first. Large legible sans, strong accent CTAs, real work photos, generous tap targets (mobile-first — tradespeople's customers are on phones). NOT corporate-pastel, NOT neon. `dna_tags: ["terminal_operator", "swiss_magazine"]` as a starting affinity.

### Task 3: `hero_trade_pro`

**Files:** Create `pebble/blocks/library/hero_trade_pro.json` + `.tsx`

- [ ] **Step 1: Write the `.json`** (complete):

```json
{
  "block_id": "library/hero_trade_pro",
  "block_type": "hero",
  "vibe_tags": ["trade-pro", "local-service", "trustworthy", "practical", "no-nonsense"],
  "dna_tags": ["terminal_operator", "swiss_magazine"],
  "slots": {
    "eyebrow": {"kind": "text", "max_chars": 40, "tone": "credential-forward (Licensed & Insured · Serving <City>)"},
    "headline": {"kind": "text", "max_chars": 70, "tone": "plain, benefit-first; what you fix and for whom"},
    "subheadline": {"kind": "text", "max_chars": 160, "tone": "one sentence; reassurance + speed (same-day, upfront pricing)"},
    "phone": {"kind": "text", "max_chars": 24, "tone": "display phone number"},
    "cta_primary": {"kind": "text", "max_chars": 24, "tone": "Get a Free Estimate / Call Now"},
    "trust_line": {"kind": "text", "max_chars": 60, "tone": "Licensed • Insured • 24/7 Emergency"},
    "hero_image": {"kind": "image", "pexels_query_template": "{industry_scene} professional at work tools natural light", "aspect": "16/9"}
  },
  "palette_slots": ["bg", "fg", "accent", "accent_fg", "muted"]
}
```

- [ ] **Step 2: Author the `.tsx`** with `ui-ux-pro-max` — full-bleed `hero_image` with a left-anchored content column: eyebrow, big `headline` (RevealWords), subheadline, a primary accent button (`cta_primary`) and a tap-to-call phone link (`tel:` using `phone`), and a `trust_line` strip. Mobile: phone CTA prominent. Use the `hero_focused_clean.tsx` structure as the skeleton.

- [ ] **Step 3: Verify registry loads it**

Run: `python -c "from pebble.blocks.registry import BlockRegistry; from pathlib import Path; r=BlockRegistry.load(Path('pebble/blocks/library').parent/'library'); print('library/hero_trade_pro' in r._blocks)"`
Expected: `True`

- [ ] **Step 4: Commit**

```bash
git add pebble/blocks/library/hero_trade_pro.json pebble/blocks/library/hero_trade_pro.tsx
git commit -m "feat(blocks): hero_trade_pro (call-now + trust-line hero)"
```

### Task 4: `trust_strip_trade` (block_type: trust)

**Files:** Create `pebble/blocks/library/trust_strip_trade.json` + `.tsx`

- [ ] **Step 1: Write the `.json`** (complete):

```json
{
  "block_id": "library/trust_strip_trade",
  "block_type": "trust",
  "vibe_tags": ["trade-pro", "local-service", "trustworthy"],
  "dna_tags": ["terminal_operator", "swiss_magazine"],
  "slots": {
    "stats": {"kind": "list", "tone": "3-4 items; each {value (e.g. '15+ yrs', '4.9★', '2,000+ jobs', 'Licensed & Insured'), label (short)}"}
  },
  "palette_slots": ["bg", "fg", "accent", "accent_fg", "muted"]
}
```

- [ ] **Step 2: Author the `.tsx`** with `ui-ux-pro-max` — a horizontal stat band (3-4 cells) with `value` large in accent + `label` muted below; `Stagger` entrance. Mirror the list-iteration placeholder pattern (`{{stats_list_start}}…{{stats[].value}}…{{stats_list_end}}`).

- [ ] **Step 3: Verify registry loads it** (same one-liner as Task 3, block id `library/trust_strip_trade`). Expected `True`.

- [ ] **Step 4: Commit**

```bash
git add pebble/blocks/library/trust_strip_trade.json pebble/blocks/library/trust_strip_trade.tsx
git commit -m "feat(blocks): trust_strip_trade (credentials stat band)"
```

### Task 5: `services_grid_trade`

**Files:** Create `pebble/blocks/library/services_grid_trade.json` + `.tsx`

- [ ] **Step 1: Write the `.json`** (complete):

```json
{
  "block_id": "library/services_grid_trade",
  "block_type": "services",
  "vibe_tags": ["trade-pro", "local-service", "practical"],
  "dna_tags": ["terminal_operator", "swiss_magazine"],
  "slots": {
    "eyebrow": {"kind": "text", "max_chars": 40, "tone": "What we do / Our services"},
    "headline": {"kind": "text", "max_chars": 70, "tone": "plain scope statement"},
    "services": {"kind": "list", "tone": "4-6 items; each {title (40), body (120, outcome-focused), from_price (optional, e.g. 'from $89')}"}
  },
  "palette_slots": ["bg", "fg", "accent", "accent_fg", "muted"]
}
```

- [ ] **Step 2: Author the `.tsx`** with `ui-ux-pro-max` — responsive card grid; each card: title, body, optional `from_price` chip in accent, and a "Request Quote" link to `#contact`. Mirror `services_grid_clean.tsx` list pattern.

- [ ] **Step 3: Verify registry loads it.** Expected `True`.

- [ ] **Step 4: Commit**

```bash
git add pebble/blocks/library/services_grid_trade.json pebble/blocks/library/services_grid_trade.tsx
git commit -m "feat(blocks): services_grid_trade (service cards + from-price)"
```

### Task 6: `service_area_trade` (block_type: coverage)

**Files:** Create `pebble/blocks/library/service_area_trade.json` + `.tsx`

- [ ] **Step 1: Write the `.json`** (complete):

```json
{
  "block_id": "library/service_area_trade",
  "block_type": "coverage",
  "vibe_tags": ["trade-pro", "local-service"],
  "dna_tags": ["terminal_operator", "swiss_magazine"],
  "slots": {
    "headline": {"kind": "text", "max_chars": 60, "tone": "Proudly serving <City> & surrounding areas"},
    "areas": {"kind": "list", "tone": "6-12 neighborhood/city names served"}
  },
  "palette_slots": ["bg", "fg", "accent", "accent_fg", "muted"]
}
```

- [ ] **Step 2: Author the `.tsx`** with `ui-ux-pro-max` — `headline` + a wrap of pill chips (one per `areas[]`), accent-bordered. No live map (YAGNI; chips read as coverage). Mirror list pattern.

- [ ] **Step 3: Verify registry loads it.** Expected `True`.

- [ ] **Step 4: Commit**

```bash
git add pebble/blocks/library/service_area_trade.json pebble/blocks/library/service_area_trade.tsx
git commit -m "feat(blocks): service_area_trade (service-area chips)"
```

### Task 7: `gallery_beforeafter_trade`

**Files:** Create `pebble/blocks/library/gallery_beforeafter_trade.json` + `.tsx`

- [ ] **Step 1: Write the `.json`** (complete):

```json
{
  "block_id": "library/gallery_beforeafter_trade",
  "block_type": "gallery",
  "vibe_tags": ["trade-pro", "local-service", "practical"],
  "dna_tags": ["terminal_operator", "swiss_magazine"],
  "slots": {
    "eyebrow": {"kind": "text", "max_chars": 40, "tone": "Recent work / Our projects"},
    "headline": {"kind": "text", "max_chars": 70, "tone": "plain"},
    "projects": {"kind": "list", "tone": "3-6 items; each {caption (60), image (pexels query)}"}
  },
  "palette_slots": ["bg", "fg", "accent", "accent_fg", "muted"]
}
```

(Job-photo grid, not a true before/after slider — YAGNI; per-item images via the list image pattern. If a slot needs an image per item, follow the existing per-item image convention used by gallery blocks; verify in `pebble/blocks/library/gallery_*.json` during Step 2.)

- [ ] **Step 2: Author the `.tsx`** with `ui-ux-pro-max` — masonry/grid of project photos with captions; `Stagger` entrance. Mirror an existing `gallery_*` block's image-list pattern.

- [ ] **Step 3: Verify registry loads it.** Expected `True`.

- [ ] **Step 4: Commit**

```bash
git add pebble/blocks/library/gallery_beforeafter_trade.json pebble/blocks/library/gallery_beforeafter_trade.tsx
git commit -m "feat(blocks): gallery_beforeafter_trade (recent-work grid)"
```

### Task 8: `contact_quote_trade`

**Files:** Create `pebble/blocks/library/contact_quote_trade.json` + `.tsx`

- [ ] **Step 1: Write the `.json`** (complete):

```json
{
  "block_id": "library/contact_quote_trade",
  "block_type": "contact",
  "vibe_tags": ["trade-pro", "local-service", "trustworthy"],
  "dna_tags": ["terminal_operator", "swiss_magazine"],
  "slots": {
    "headline": {"kind": "text", "max_chars": 60, "tone": "Get a Free Quote"},
    "subheadline": {"kind": "text", "max_chars": 140, "tone": "reassurance; response-time promise"},
    "phone": {"kind": "text", "max_chars": 24, "tone": "display phone"},
    "email": {"kind": "text", "max_chars": 60, "tone": "display email"},
    "address": {"kind": "text", "max_chars": 100, "tone": "service address or 'Mobile service'"},
    "service_options": {"kind": "list", "tone": "the services list for the form dropdown (mirror services titles)"}
  },
  "palette_slots": ["bg", "fg", "accent", "accent_fg", "muted"]
}
```

- [ ] **Step 2: Author the `.tsx`** with `ui-ux-pro-max` — split layout: left = phone (tap-to-call) + email + address + hours; right = quote form (name, phone, service `<select>` from `service_options`, message, submit). The form must follow the v2 contact-block submission convention used by existing `contact_*` blocks (check `contact_split_clean.tsx` — match how it wires submission so the hosted-forms routing in `docs/superpowers/plans/2026-06-02-hosted-contact-forms.md` applies uniformly). Do NOT invent a new submission mechanism.

- [ ] **Step 3: Verify registry loads it.** Expected `True`.

- [ ] **Step 4: Commit**

```bash
git add pebble/blocks/library/contact_quote_trade.json pebble/blocks/library/contact_quote_trade.tsx
git commit -m "feat(blocks): contact_quote_trade (free-quote form)"
```

### Task 9: Tag neutral existing blocks with `trade-pro`

So the pinned menu has an `about`, `testimonials`, and `footer` option without forking neutral blocks.

**Files:** Modify `vibe_tags` in 3 existing block `.json` files.

- [ ] **Step 1: Pick the closest neutral blocks** — read `pebble/blocks/library/about_team_clean.json`, the existing `testimonials_*_clean.json` (or closest), and `footer_anchored_clean.json`. Confirm they're tonally neutral (work for trades).

- [ ] **Step 2: Add `"trade-pro"` to each one's `vibe_tags` array.** (Append only; don't remove existing tags — these blocks still serve their original vibes.)

- [ ] **Step 3: Verify all still validate**

Run: `python -m pytest tests/ -q -k "block" -p no:cacheprovider`
Expected: no new failures.

- [ ] **Step 4: Commit**

```bash
git add pebble/blocks/library/about_team_clean.json pebble/blocks/library/footer_anchored_clean.json pebble/blocks/library/testimonials_*_clean.json
git commit -m "feat(blocks): tag neutral about/testimonials/footer blocks trade-pro"
```

### Task 10: Registry coverage test for trade-pro

**Files:** Test `tests/test_trade_pro_blocks.py` (Create)

- [ ] **Step 1: Write the test**

```python
# tests/test_trade_pro_blocks.py
from pathlib import Path
from pebble.blocks.registry import BlockRegistry

LIB = Path(__file__).resolve().parent.parent / "pebble" / "blocks" / "library"


def test_trade_pro_has_every_essential_section():
    reg = BlockRegistry.load(LIB.parent)
    by_type = {}
    for blk in reg._blocks.values():
        if "trade-pro" in blk.metadata.vibe_tags:
            by_type.setdefault(blk.metadata.block_type, []).append(blk.metadata.block_id)
    # Every essential page section must have at least one trade-pro option.
    for essential in ("hero", "trust", "services", "coverage", "gallery", "contact", "about", "footer"):
        assert by_type.get(essential), f"no trade-pro block for section: {essential}"
```

- [ ] **Step 2: Run it**

Run: `python -m pytest tests/test_trade_pro_blocks.py -q`
Expected: PASS (fails loudly if any new block was missed or mistagged).

- [ ] **Step 3: Commit**

```bash
git add tests/test_trade_pro_blocks.py
git commit -m "test(blocks): trade-pro vibe covers every essential section"
```

---

## Phase 3: Build + verify + promote pipeline

### Task 11: The 8 Wave-1 briefs

**Files:** Create `pebble/examples_pipeline/__init__.py` + `pebble/examples_pipeline/trade_briefs.py`

- [ ] **Step 1: Write `trade_briefs.py`** — a list of 8 dicts, each `{business_name, industry, extra_context, vibe: "trade-pro"}`. Use the spec's lineup (Tidewater Plumbing/Portland, Brightwire Electric/Austin, Northpeak Heating & Air/Denver, Cedar & Stone Landscapes/Raleigh, Sparrow Home Cleaning/Minneapolis, Ridgeline Builders/Boise, Summit Ridge Roofing/Kansas City, Gearworks Auto Service/Columbus). `extra_context` carries services, hours, "licensed & insured", years (only if we choose to state them — to avoid invented-year eval flags, keep founding vague unless given). Complete data, no placeholders.

```python
# pebble/examples_pipeline/trade_briefs.py
TRADE_BRIEFS = [
    {
        "business_name": "Tidewater Plumbing Co.",
        "industry": "plumber",
        "vibe": "trade-pro",
        "extra_context": "Portland, OR. Services: drain cleaning, water heater install & repair, leak detection, repiping, 24/7 emergency. Licensed & insured. Upfront flat-rate pricing. Same-day service. Family-owned.",
    },
    # ... 7 more, same shape (electrician, hvac, landscaper, cleaning, contractor, roofer, auto repair)
]
```

(Fill all 8 with full `extra_context` per the spec's per-trade service lists. No "TODO".)

- [ ] **Step 2: Sanity test**

Run: `python -c "from pebble.examples_pipeline.trade_briefs import TRADE_BRIEFS; assert len(TRADE_BRIEFS)==8; assert all(b['vibe']=='trade-pro' and b['extra_context'] for b in TRADE_BRIEFS); print('ok')"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add pebble/examples_pipeline/
git commit -m "feat(examples): Wave-1 trade briefs (8 local-trade businesses)"
```

### Task 12: Build script

**Files:** Create `scripts/build_trade_examples.py`

- [ ] **Step 1: Write the script** — iterates `TRADE_BRIEFS`, calls `build_v2_core(brief, progress_cb=print)` for each, prints the resulting slug + ok status + any error. Accepts an optional `--only <industry>` to build one. Does NOT promote — just builds into `output/`.

```python
# scripts/build_trade_examples.py
import argparse, json, sys
from pebble.server.build_v2 import build_v2_core
from pebble.examples_pipeline.trade_briefs import TRADE_BRIEFS

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="industry substring to build just one")
    args = ap.parse_args()
    briefs = [b for b in TRADE_BRIEFS if not args.only or args.only in b["industry"]]
    for b in briefs:
        print(f"\n=== building {b['business_name']} ({b['industry']}) ===")
        try:
            res = build_v2_core(dict(b), progress_cb=lambda e, d: print(f"  {e}"))
            print(f"  -> slug={res.get('slug')} ok={res.get('ok')}")
        except Exception as exc:
            print(f"  BUILD FAILED: {exc}", file=sys.stderr)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-build ONE** (requires LLM key; this is the pipeline proof):

Run: `python scripts/build_trade_examples.py --only plumber`
Expected: prints SSE-style events ending in a slug; `output/<slug>/site/` exists with `app/globals.css` containing `@tailwind`.

- [ ] **Step 3: Commit**

```bash
git add scripts/build_trade_examples.py
git commit -m "feat(examples): build script for trade-pro examples (vibe-pinned)"
```

### Task 13: Eval gate

**Files:** none new — uses `python -m pebble.evals output/<slug>`.

- [ ] **Step 1: Run evals on the smoke build**

Run: `python -m pebble.evals output/<plumber-slug>`
Expected: all FOUNDATION checks pass. Record any failure; if `tailwind_directives_present` or image/contact checks fail, fix the responsible block/compiler BEFORE batch-building.

- [ ] **Step 2: Visual check** — start the engine, open `/preview/<plumber-slug>/`, confirm styled + trades-appropriate + CTA/phone/trust strip present + no invented year. (Engine proxy fix is live.)

- [ ] **Step 3: No commit** (verification only). If fixes were needed, commit them against the relevant block/compiler task.

### Task 14: Promote script

**Files:** Create `scripts/promote_example.py`; Test `tests/test_promote_example.py`

- [ ] **Step 1: Write the failing test** (the move + manifest-append logic, screenshot mocked):

```python
# tests/test_promote_example.py
import json, sys
from pathlib import Path
import scripts.promote_example as promote


def test_promote_moves_site_and_appends_manifest(tmp_path, monkeypatch):
    # Fake an output build
    out = tmp_path / "output" / "tidewater-plumbing"
    (out / "site" / "app").mkdir(parents=True)
    (out / "site" / "app" / "page.tsx").write_text("export default()=>null;", encoding="utf-8")
    (out / "brief.json").write_text(json.dumps({"business_name": "Tidewater Plumbing Co.", "industry": "plumber"}), encoding="utf-8")
    examples_dir = tmp_path / "pebble" / "examples"; examples_dir.mkdir(parents=True)
    manifest = tmp_path / "pebble" / "example_gallery.json"
    manifest.write_text(json.dumps({"schema_version": "1.0", "examples": []}), encoding="utf-8")

    monkeypatch.setattr(promote, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(promote, "EXAMPLES_DIR", examples_dir)
    monkeypatch.setattr(promote, "MANIFEST", manifest)
    monkeypatch.setattr(promote, "capture_thumbnail", lambda slug, site_dir: "templates-preview/tidewater-plumbing.png")

    promote.promote("tidewater-plumbing", vibe="trade-pro")

    assert (examples_dir / "tidewater-plumbing" / "site" / "app" / "page.tsx").exists()
    data = json.loads(manifest.read_text(encoding="utf-8"))
    slugs = {e["slug"] for e in data["examples"]}
    assert "tidewater-plumbing" in slugs
    entry = next(e for e in data["examples"] if e["slug"] == "tidewater-plumbing")
    assert entry["vibe"] == "trade-pro"
    assert entry["source_dir"] == "pebble/examples/tidewater-plumbing"
    assert entry["kind"] == "example_build"
```

- [ ] **Step 2: Run it**

Run: `python -m pytest tests/test_promote_example.py -q`
Expected: FAIL (module missing).

- [ ] **Step 3: Implement `scripts/promote_example.py`** — module-level constants `OUTPUT_DIR`, `EXAMPLES_DIR`, `MANIFEST` (real repo paths); `capture_thumbnail(slug, site_dir)` (runs `post_build_run_dev_server` + a single full-page Playwright screenshot to `ui/v3/public/templates-preview/<slug>.png`, returns the relative path; degrades to `""` if Playwright unavailable); `promote(slug, vibe)` which: copies `output/<slug>/site` → `pebble/examples/<slug>/site` (skip node_modules/.next via the same exclude set as `pebble/server/examples.py::_copy_site`), copies `brief.json`, reads the brief for `name`/`industry`, derives `sections` from `build_meta.json` block_picks count (fallback to counting `components/sections/Section*.tsx`), calls `capture_thumbnail`, and appends a manifest entry `{slug, name, industry, vibe, hero_image, sections, source_dir, kind:"example_build"}` (idempotent — replace if slug already present). `hero_image` defaults to the thumbnail path or the build's resolved hero Pexels URL.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_promote_example.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/promote_example.py tests/test_promote_example.py
git commit -m "feat(examples): promote script (move + manifest + thumbnail)"
```

---

## Phase 4: Build Wave 1 + promote

### Task 15: Run the wave

- [ ] **Step 1: Build all 8** — `python scripts/build_trade_examples.py` (LLM key required). Capture each slug.
- [ ] **Step 2: Eval-gate each** — `python -m pebble.evals output/<slug>` for all 8. List passers/failers.
- [ ] **Step 3: Visual-check each** passer at `/preview/<slug>/`. Note any that are tonally off or have wiring issues.
- [ ] **Step 4: Fix-or-drop** — for failures, fix the responsible block/brief and rebuild that one; or drop it from Wave 1 and log why (no silent truncation).
- [ ] **Step 5: Promote passers** — `python scripts/promote_example.py <slug> --vibe trade-pro` for each that cleared both gates.
- [ ] **Step 6: Verify the gallery** — `GET /api/examples` lists the new entries; clone one (`POST /api/examples/clone`) and confirm it lands in `output/` and renders.
- [ ] **Step 7: Commit the promoted examples + manifest**

```bash
git add pebble/examples/ pebble/example_gallery.json ui/v3/public/templates-preview/
git commit -m "feat(examples): Wave 1 trade-pro example sites (N shipped)"
```

---

## Self-Review

**Spec coverage:**
- 8 trade examples → Tasks 11, 15 ✓
- trade-pro vibe (blocks) → Tasks 3-9 ✓
- new block_types trust/coverage → Task 1 ✓
- v2 build path + vibe determinism → Task 2 ✓
- eval gate + visual check → Tasks 13, 15 ✓
- promote (move + manifest + Playwright thumbnail) → Task 14, 15 ✓
- quote form → /api/forms → Task 8 (follows existing contact-block convention; depends on hosted-forms plan) ✓
- per-trade accent palettes → handled by Sonnet's palette pick per brief (sonnet_block_picker returns `palette`); blocks read tokens ✓

**Placeholder scan:** Block `.tsx` bodies are intentionally authored during execution via `ui-ux-pro-max` (design work, not logic) — every such task gives the complete `.json` contract + exact pattern reference + acceptance check, which is the correct granularity for visual components. Task 11 must be filled with all 8 full briefs (no "..."). No TBDs in logic tasks.

**Type/name consistency:** `_build_block_menu(registry, vibe=None)` (Task 2) used consistently; block_ids (`hero_trade_pro`, `trust_strip_trade`, `services_grid_trade`, `service_area_trade`, `gallery_beforeafter_trade`, `contact_quote_trade`) consistent across Tasks 3-10; `promote(slug, vibe)` + constants consistent across Task 14-15; manifest entry shape matches `pebble/example_gallery.json` (slug, name, industry, vibe, hero_image, sections, source_dir, kind).

**Risk carried from spec:** if Sonnet still mixes vibes despite the pin (Task 2 filters the menu, which should prevent it), Task 13's visual check catches it before promotion.
