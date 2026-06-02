# Image-Forward Templates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Block-component tasks (Phase 2) additionally use the `ui-ux-pro-max` skill for layout/craft.

**Goal:** Make Pebble's generated sites visibly image-rich — fix the preview proxy that hides existing hero/about/testimonial photos, add photo-top imagery to service cards, and refresh the 8 live trade examples.

**Architecture:** A pure `preview_forward_path` helper (new `pebble/server/preview_paths.py`) lets `_handle_preview` forward the query string to the Next dev server, so `/_next/image?url=…` resolves instead of 400-ing. Two services blocks gain a per-item `image` field rendered photo-top, reusing the per-item-image + Pexels-resolution pattern the gallery block already proves. The 8 trade examples are rebuilt and re-promoted.

**Tech Stack:** Python 3.14 (stdlib HTTP engine, pytest), the v2 block engine (`pebble/blocks/*`, `pebble/pexels_resolver.py`, `pebble/server/build_v2.py`), Next.js 14 generated sites, Playwright.

**Spec:** `docs/superpowers/specs/2026-06-01-image-forward-templates-design.md`

---

## File Structure

**Phase 1 — preview proxy fix**
- Create: `pebble/server/preview_paths.py` — pure `preview_forward_path(raw_path, slug_prefix)`.
- Modify: `pebble_engine.py` — import the helper; use it at both proxy call-sites in `_handle_preview` (dev-registry ~line 1820, Fly ~line 1792).
- Test: `tests/test_preview_forward_path.py`.

**Phase 2 — photo-top service cards**
- Modify: `pebble/blocks/library/services_grid_trade.{json,tsx}` — add per-item `image`, render photo-top.
- Create: `pebble/blocks/library/services_photo_grid.{json,tsx}` — reusable photo-top services block.
- Test: `tests/test_services_photo_blocks.py`.

**Phase 3 — rebuild + re-promote** (operational, no new files)

---

## Phase 1: Preview image proxy fix

### Task 1: `preview_forward_path` helper (TDD)

**Files:**
- Create: `pebble/server/preview_paths.py`
- Test: `tests/test_preview_forward_path.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_preview_forward_path.py
from pebble.server.preview_paths import preview_forward_path


def test_preserves_next_image_query():
    raw = "/preview/foo/_next/image?url=https%3A%2F%2Fx.jpg&w=1920&q=75"
    assert preview_forward_path(raw, "/preview/foo") == \
        "/_next/image?url=https%3A%2F%2Fx.jpg&w=1920&q=75"


def test_trailing_slash_root():
    assert preview_forward_path("/preview/foo/", "/preview/foo") == "/"


def test_bare_slug_becomes_root():
    assert preview_forward_path("/preview/foo", "/preview/foo") == "/"


def test_sub_route():
    assert preview_forward_path("/preview/foo/about", "/preview/foo") == "/about"


def test_query_on_bare_slug_gets_root_prefix():
    assert preview_forward_path("/preview/foo?t=1", "/preview/foo") == "/?t=1"


def test_prefix_mismatch_returns_input():
    # Defensive: if the prefix isn't present, return the path unchanged.
    assert preview_forward_path("/other/path", "/preview/foo") == "/other/path"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_preview_forward_path.py -q`
Expected: FAIL (module `pebble.server.preview_paths` does not exist).

- [ ] **Step 3: Implement the helper**

```python
# pebble/server/preview_paths.py
"""Pure path helper for the /preview/<slug>/ dev-server proxy.

The router strips the query string off ``handler.path`` for route matching
and stashes the original on ``handler._raw_path``. When proxying to a live
``next dev`` server we must forward the ORIGINAL path (query intact) — Next's
image optimizer (/_next/image?url=...&w=...&q=...) 400s without its query.
Isolated here so it is unit-testable without booting the engine.
"""
from __future__ import annotations


def preview_forward_path(raw_path: str, slug_prefix: str) -> str:
    """Strip ``slug_prefix`` from ``raw_path``, preserving the query string.

    ``raw_path``    — original request path WITH query (handler._raw_path),
                      e.g. ``/preview/foo/_next/image?url=X&w=1920&q=75``.
    ``slug_prefix`` — ``/preview/<raw-slug>`` (no trailing slash).

    Returns the path to send to the dev server. Empty remainder and
    query-only remainder both normalize to a leading ``/`` so the dev
    server always receives an absolute path.
    """
    if not raw_path.startswith(slug_prefix):
        return raw_path  # defensive: nothing to strip
    rest = raw_path[len(slug_prefix):]
    if not rest or rest.startswith("?"):
        rest = "/" + rest
    return rest
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_preview_forward_path.py -q`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add pebble/server/preview_paths.py tests/test_preview_forward_path.py
git commit -m "feat(preview): pure preview_forward_path helper (preserves query string)"
```

### Task 2: Wire the helper into `_handle_preview`

**Goal:** Both proxy call-sites in `_handle_preview` forward the query-preserving path so `/_next/image?...` resolves. No behavior change for static-file fallback.

**Files:**
- Modify: `pebble_engine.py` (import + two call-sites in `_handle_preview`, ~lines 1786-1822)

- [ ] **Step 1: Read `pebble_engine.py:1748-1840`** to confirm the two call-sites still read `forward_path = self.path[len(slug_prefix):] or "/"` (one in the Fly branch, one in the dev-registry branch). Reconnaissance — no edit.

- [ ] **Step 2: Add the import** near the other `pebble.server` imports at the top of `pebble_engine.py`. Search for an existing `from pebble.server` import and add beside it:

```python
from pebble.server.preview_paths import preview_forward_path
```

(If no top-level `pebble.server` import exists, add the line in the same import block as the other `from pebble.` imports.)

- [ ] **Step 3: Replace BOTH proxy call-sites.** Each currently reads:

```python
                slug_prefix = "/preview/" + parts[0]
                forward_path = self.path[len(slug_prefix):] or "/"
```

Replace each occurrence with:

```python
                slug_prefix = "/preview/" + parts[0]
                forward_path = preview_forward_path(
                    getattr(self, "_raw_path", self.path), slug_prefix
                )
```

There are exactly two occurrences (Fly branch ~line 1792, dev-registry branch ~line 1820). Replace both. Leave the surrounding `_proxy_to_dev(...)` calls and the static-file fallback (which uses `rest`/`self.path` for on-disk lookup) untouched.

- [ ] **Step 4: Verify the engine still imports cleanly**

Run: `python -c "import pebble_engine; print('import ok')"`
Expected: `import ok` (no ImportError / SyntaxError).

- [ ] **Step 5: Confirm both call-sites changed**

Run: `python -c "import re,io; s=open('pebble_engine.py',encoding='utf-8').read(); print('old call-sites remaining:', s.count('self.path[len(slug_prefix):] or'))"`
Expected: `old call-sites remaining: 0`

- [ ] **Step 6: Commit**

```bash
git add pebble_engine.py
git commit -m "fix(preview): forward query string to dev server so /_next/image resolves"
```

(End-to-end verification — image bytes returned, not 400 — happens in Phase 3 Task 6 against a live rebuild.)

---

## Phase 2: Photo-top service cards

**For each block task:** the `.json` is the contract (given complete). The `.tsx` is authored with the `ui-ux-pro-max` skill following the established library conventions: `"use client"`, named `import { Stagger, StaggerItem } from "@/components/motion/Stagger"`, `RevealWords` default import, `{{slot}}` / `{{list_start}}…{{list_end}}` / `{{list[].field}}` placeholders, `bg-{{bg}}`/`text-{{fg}}`/`{{accent}}` palette tokens, hardcoded `text-slate-600` for muted body text (the palette `muted` token is a surface tint, NOT text), `min-h-[44px]` + `focus-visible:` on the CTA. Per-item images use a plain-text Pexels query in `src="{{services[].image}}"` — `pebble/pexels_resolver.py` resolves it (proven by `gallery_beforeafter_trade`). **Acceptance:** `BlockRegistry.load` accepts the block, placeholders resolve at compile, every declared `palette_slot` appears in the `.tsx` (no contract drift).

### Task 3: Make `services_grid_trade` photo-top

**Files:**
- Modify: `pebble/blocks/library/services_grid_trade.json`
- Modify: `pebble/blocks/library/services_grid_trade.tsx`

- [ ] **Step 1: Update the `services` slot tone in the JSON** to add the per-item `image` query. Replace the `services` slot line with:

```json
    "services": {"kind": "list", "tone": "4-6 items; each {title (40), body (110, outcome-focused), from_price (optional, e.g. 'from $89'), image (a Pexels search query for THIS specific service so each card photo is distinct, e.g. 'water heater installation plumber', 'drain cleaning pipe wrench')}"}
```

Leave `block_id`, `block_type`, `vibe_tags`, `dna_tags`, the `eyebrow`/`headline` slots, and `palette_slots` (`["bg", "fg", "accent"]`) unchanged.

- [ ] **Step 2: Author the photo-top `.tsx`** with `ui-ux-pro-max`. Replace the body of `services_grid_trade.tsx` so each card leads with the photo. The grid stays `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-slate-200`; each `StaggerItem` becomes `overflow-hidden` with a fixed-aspect photo on top, then the existing title / body / from_price chip / "Request a quote →" CTA in a padded body. Exact structure:

```tsx
"use client";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridTrade() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="max-w-6xl mx-auto">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-{{accent}} text-xs font-semibold uppercase tracking-[0.2em] mb-4">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-4xl md:text-5xl font-semibold leading-tight max-w-xl tracking-tight">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        {/* Services grid — photo-top cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-slate-200">
          {/* {{services_list_start}} */}
          <StaggerItem className="bg-{{bg}} flex flex-col overflow-hidden">
            <div className="aspect-[4/3] overflow-hidden bg-slate-100">
              <img
                src="{{services[].image}}"
                alt="{{services[].title}}"
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-{{fg}} text-lg font-semibold leading-snug">
                {{services[].title}}
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1">
                {{services[].body}}
              </p>
              <span className="inline-block self-start bg-{{accent}}/10 text-{{accent}} text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded">
                {{services[].from_price}}
              </span>
              <a
                href="#contact"
                className="text-{{accent}} text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-{{accent}}/50 rounded"
              >
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          {/* {{services_list_end}} */}
        </Stagger>

      </div>
    </section>
  );
}
```

- [ ] **Step 3: Verify the registry loads it and the image placeholder is present**

Run:
```bash
python -c "from pathlib import Path; from pebble.blocks.registry import BlockRegistry; r=BlockRegistry.load(Path('pebble/blocks/library').parent); b=r._blocks['library/services_grid_trade']; src=b.template_source; print('img_placeholder', '{{services[].image}}' in src); print('palette_slots', b.metadata.palette_slots)"
```
Expected: `img_placeholder True` and `palette_slots ['bg', 'fg', 'accent']`. (Confirm every token in `palette_slots` still appears in the `.tsx`; the photo-top edit adds no new tokens.)

- [ ] **Step 4: Run the block suite**

Run: `python -m pytest tests/ -q -k "block or trade" --no-header -p no:cacheprovider 2>&1 | tail -5`
Expected: no new failures.

- [ ] **Step 5: Commit**

```bash
git add pebble/blocks/library/services_grid_trade.json pebble/blocks/library/services_grid_trade.tsx
git commit -m "feat(blocks): services_grid_trade photo-top cards (per-service photo)"
```

### Task 4: New reusable `services_photo_grid`

**Files:**
- Create: `pebble/blocks/library/services_photo_grid.json`
- Create: `pebble/blocks/library/services_photo_grid.tsx`

- [ ] **Step 1: Write the `.json`** (complete):

```json
{
  "block_id": "library/services_photo_grid",
  "block_type": "services",
  "vibe_tags": ["clean", "professional", "bold", "editorial", "modern", "versatile", "trust-building"],
  "dna_tags": ["swiss_magazine", "boutique_brokerage", "terminal_operator"],
  "slots": {
    "eyebrow": {"kind": "text", "max_chars": 40, "tone": "What we offer / Our services"},
    "headline": {"kind": "text", "max_chars": 70, "tone": "plain scope statement"},
    "services": {"kind": "list", "tone": "3-6 items; each {title (40), body (120, outcome-focused), image (a Pexels search query for THIS specific service so each card photo is distinct)}"}
  },
  "palette_slots": ["bg", "fg", "accent"]
}
```

- [ ] **Step 2: Author the `.tsx`** with `ui-ux-pro-max` — a vibe-neutral photo-top services grid (more universal feel than the trade block: rounded cards on a clean background, photo-top, title + body). Use the same placeholder conventions and the per-item image pattern. Skeleton:

```tsx
"use client";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesPhotoGrid() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-14 max-w-2xl">
          <p className="text-{{accent}} text-xs font-semibold uppercase tracking-[0.2em] mb-4">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-4xl md:text-5xl font-semibold leading-tight tracking-tight">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        <Stagger className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* {{services_list_start}} */}
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-{{bg}}">
            <div className="aspect-[4/3] overflow-hidden bg-slate-100">
              <img
                src="{{services[].image}}"
                alt="{{services[].title}}"
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-{{fg}} text-lg font-semibold leading-snug">
                {{services[].title}}
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1">
                {{services[].body}}
              </p>
            </div>
          </StaggerItem>
          {/* {{services_list_end}} */}
        </Stagger>
      </div>
    </section>
  );
}
```

- [ ] **Step 3: Verify the registry loads it**

Run:
```bash
python -c "from pathlib import Path; from pebble.blocks.registry import BlockRegistry; r=BlockRegistry.load(Path('pebble/blocks/library').parent); b=r._blocks['library/services_photo_grid']; print('loaded', b.metadata.block_type, b.metadata.palette_slots, '{{services[].image}}' in b.template_source)"
```
Expected: `loaded services ['bg', 'fg', 'accent'] True`.

- [ ] **Step 4: Commit**

```bash
git add pebble/blocks/library/services_photo_grid.json pebble/blocks/library/services_photo_grid.tsx
git commit -m "feat(blocks): services_photo_grid (reusable photo-top services block)"
```

### Task 5: Regression test for photo-top services blocks

**Files:**
- Create: `tests/test_services_photo_blocks.py`

- [ ] **Step 1: Write the test**

```python
# tests/test_services_photo_blocks.py
from pathlib import Path

from pebble.blocks.registry import BlockRegistry

LIB_ROOT = Path(__file__).resolve().parent.parent / "pebble" / "blocks"

PHOTO_SERVICES = ("library/services_grid_trade", "library/services_photo_grid")


def test_photo_services_blocks_declare_per_item_image():
    reg = BlockRegistry.load(LIB_ROOT)
    for bid in PHOTO_SERVICES:
        blk = reg._blocks[bid]
        # services block type
        assert blk.metadata.block_type == "services", bid
        # the template renders a per-item image
        assert "{{services[].image}}" in blk.template_source, bid


def test_photo_services_palette_parity():
    """Every declared palette_slot must appear in the template (no drift)."""
    reg = BlockRegistry.load(LIB_ROOT)
    for bid in PHOTO_SERVICES:
        blk = reg._blocks[bid]
        for slot in blk.metadata.palette_slots:
            token = "{{" + slot + "}}"
            assert token in blk.template_source, f"{bid}: declared palette slot {slot!r} unused in template"
```

- [ ] **Step 2: Run it**

Run: `python -m pytest tests/test_services_photo_blocks.py -q`
Expected: PASS (2 passed).

- [ ] **Step 3: Run the full block suite**

Run: `python -m pytest tests/ -q -k "block or trade or services or preview" --no-header -p no:cacheprovider 2>&1 | tail -5`
Expected: no new failures.

- [ ] **Step 4: Commit**

```bash
git add tests/test_services_photo_blocks.py
git commit -m "test(blocks): photo-top services blocks declare per-item image + palette parity"
```

---

## Phase 3: Rebuild + re-promote the 8 trade examples

### Task 6: Verify one build end-to-end (proxy + photos)

**Files:** none new — uses `scripts/build_trade_examples.py`, the live engine, `python -m pebble.evals`.

- [ ] **Step 1: Rebuild the plumber** (LLM key required; engine must be running for the preview check):

Run: `python scripts/build_trade_examples.py --only plumber`
Expected: ends with `1/1 succeeded` and a slug.

- [ ] **Step 2: Confirm the services section renders per-service photos in source**

Run:
```bash
python -c "import glob,re; f=[p for p in glob.glob('output/tidewater-plumbing-co/site/components/sections/Section*.tsx')]; hits=[p for p in f if 'object-cover' in open(p,encoding='utf-8').read() and 'Request a quote' in open(p,encoding='utf-8').read()]; print('services-with-photo section:', hits)"
```
Expected: one Section file path printed (the services grid now has `<img ... object-cover>` per card).

- [ ] **Step 2b: Confirm distinct per-service Pexels URLs resolved**

Run:
```bash
python -c "import glob,re; f=[p for p in glob.glob('output/tidewater-plumbing-co/site/components/sections/Section*.tsx') if 'Request a quote' in open(p,encoding='utf-8').read()][0]; urls=re.findall(r'images\.pexels\.com/[^\" ]+', open(f,encoding='utf-8').read()); print('count', len(urls), 'distinct', len(set(urls)))"
```
Expected: `count` ≥ 3 and `distinct` > 1 (photos are not all identical). If `distinct == 1`, the per-service image queries collapsed — treat as a slot-tone/resolver issue and fix before proceeding.

- [ ] **Step 3: Confirm the preview proxy now serves image bytes (not 400).** Wait for the dev server to warm (poll until the page is >30KB), then hit the optimizer URL for the hero image. First grab a real `_next/image` URL from the rendered page, then fetch it:

Run:
```bash
python -X utf8 - <<'PY'
import time, re, urllib.request
base = "http://127.0.0.1:8000/preview/tidewater-plumbing-co/"
# warm
for _ in range(18):
    try:
        html = urllib.request.urlopen(base, timeout=12).read().decode("utf-8", "replace")
    except Exception:
        html = ""
    if len(html) > 30000 and "Starting preview" not in html:
        break
    time.sleep(7)
m = re.search(r'/preview/tidewater-plumbing-co/_next/image\?[^"\\\s]+', html)
print("found optimizer url:", bool(m))
if m:
    url = "http://127.0.0.1:8000" + m.group(0).replace("&amp;", "&")
    req = urllib.request.urlopen(url, timeout=20)
    data = req.read()
    print("status", req.status, "content_type", req.headers.get("Content-Type"), "bytes", len(data))
PY
```
Expected: `found optimizer url: True`, `status 200`, a `content_type` of `image/*` (webp/jpeg), and `bytes` in the tens of thousands. (Before the Phase 1 fix this returned `400`.)

- [ ] **Step 4: Eval-gate the rebuild**

Run: `python -m pebble.evals tidewater-plumbing-co --skip-compile 2>&1 | grep -E "(no_invented_time|Score)"`
Expected: `no_invented_time_markers` passes; score at or above the prior 50%.

- [ ] **Step 5: Visual check** — capture a homepage screenshot via Playwright (engine running) and eyeball the services section for real, distinct per-service photos. No commit (verification only). If photos are wrong/repetitive, fix the responsible block/slot-tone and re-run this task before the batch.

### Task 7: Rebuild all 8, review, re-promote

**Files:** `pebble/examples/<slug>/`, `pebble/example_gallery.json`, `ui/v3/public/templates-preview/` (if thumbnails captured).

- [ ] **Step 1: Build all 8**

Run: `python scripts/build_trade_examples.py`
Expected: `8/8 succeeded`. Capture each slug.

- [ ] **Step 2: Eval-gate each**

Run: `for s in tidewater-plumbing-co brightwire-electric northpeak-heating-air cedar-stone-landscapes sparrow-home-cleaning ridgeline-builders summit-ridge-roofing gearworks-auto-service; do echo "== $s =="; python -m pebble.evals "$s" --skip-compile 2>&1 | grep -E "(no_invented_time|Score)"; done`
Expected: all pass `no_invented_time_markers`; record scores.

- [ ] **Step 3: Capture fresh screenshots** of all 8 (Playwright, full page, scroll to trigger Stagger). Save under `docs/superpowers/wave1-screenshots/imgfwd_<slug>.png`.

- [ ] **Step 4: STOP — owner review.** Present the 8 new renders to the owner (copy was regenerated; this is the re-approval gate from the spec). Do NOT re-promote until the owner approves. Note any that are tonally off or have repetitive photos; fix-or-drop per the owner's call.

- [ ] **Step 5: Re-promote each approved example**

Run: `for s in <approved-slugs>; do python scripts/promote_example.py "$s" --vibe trade-pro; done`
Expected: each prints an `entry` with a `hero_image` Pexels URL; the script replaces the existing `pebble/examples/<slug>/` + manifest entry in place (idempotent).

- [ ] **Step 6: Verify the gallery + clone round-trip**

Run: `curl -s http://127.0.0.1:8000/api/examples | python -c "import sys,json; d=json.load(sys.stdin); print('trade-pro:', len([e for e in d['examples'] if e.get('vibe')=='trade-pro']))"`
Expected: `trade-pro: 8` (or the approved count). Then clone one and confirm it lands in `output/` and renders.

- [ ] **Step 7: Commit the refreshed examples + manifest**

```bash
git add pebble/examples/ pebble/example_gallery.json ui/v3/public/templates-preview/
git commit -m "feat(examples): refresh Wave 1 trade examples with photo-top service cards"
```

---

## Self-Review

**Spec coverage:**
- Part 1 preview proxy fix → Tasks 1-2 ✓ (pure helper + both call-sites + end-to-end check in Task 6 Step 3)
- Part 2a modify services_grid_trade photo-top → Task 3 ✓
- Part 2b new reusable services_photo_grid → Task 4 ✓
- Part 2 image resolution via existing pexels_resolver → verified in Task 6 Step 2b (distinct URLs) ✓
- Part 3 rebuild + re-promote with owner re-approval → Tasks 6-7 ✓ (review gate is Task 7 Step 4)
- Testing (helper unit test; block load/parity; manual proxy + photo check) → Tasks 1, 5, 6 ✓
- Risks: per-service photo relevance → Task 6 Step 2b guard; rebuild re-approval → Task 7 Step 4; reusable block additive tags → Task 4 JSON (no trade-pro tag, additive vibes only) ✓

**Placeholder scan:** Block `.tsx` for `services_grid_trade` is given complete; `services_photo_grid.tsx` is given as a concrete skeleton authored via `ui-ux-pro-max` (design work) with a full contract + acceptance check — correct granularity for a visual component. No TBDs in logic tasks. `<approved-slugs>` / `<slug>` in Task 7 are intentional runtime values gated by the owner-review step, not placeholders for unknown logic.

**Type/name consistency:** `preview_forward_path(raw_path, slug_prefix)` used identically in Task 1 (def + tests) and Task 2 (call-sites). Block ids `services_grid_trade` / `services_photo_grid` consistent across Tasks 3-7. Per-item placeholder `{{services[].image}}` consistent across Tasks 3, 4, 5. palette_slots `["bg","fg","accent"]` consistent for both blocks. Manifest re-promote uses the existing `promote_example.py promote(slug, vibe)` contract unchanged.
