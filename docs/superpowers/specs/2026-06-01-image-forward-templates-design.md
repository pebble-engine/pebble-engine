# Image-Forward Templates — Design Spec

**Date:** 2026-06-01
**Status:** Approved direction; pending spec review → implementation plan.
**Branch:** claude/launch-readiness-2026-06-01

## Goal

Make Pebble's generated sites visibly image-rich. The trigger: the owner observed that many templates "aren't sourcing images or using photos somewhere either in the hero or completely in the background of the hero" — *people understand images faster than words.*

Investigation reframed the problem into two distinct parts:

1. **A preview bug hides imagery that already exists.** Every `hero`, `about`, and `testimonials` block in `pebble/blocks/library/` already declares an image slot (full-bleed/split backgrounds, portraits, headshots). They render **blank in the workspace/gallery preview** because the engine's `/preview/<slug>/_next/image` proxy drops the query string. Clone-and-run-locally renders correctly — it is preview-only — but the workspace iframe and Playwright thumbnails look imageless.
2. **`services` blocks are genuinely text-only.** Across the whole library (`services_grid_*`, `services_cards_*`, `services_menu_luxe`) there is no per-service imagery. This is the real "more imagery" gap.

## Scope (agreed)

- **Fix the preview image proxy** (Part 1).
- **Add photo-top imagery to service cards** (Part 2): modify `services_grid_trade` + add one reusable photo-top block.
- **Rebuild + re-promote the 8 Wave-1 trade examples** so the live gallery is image-rich (Part 3).

**Out of scope:** retrofitting the entire `services_*` family across all vibes; redesigning hero/about/testimonial layouts (the proxy fix makes their existing imagery render); any new publish/hosting work.

## Part 1 — Preview image proxy fix

**Root cause.** `pebble/server/router.py` strips the query string for route matching (`handler.path = path_only`) and stashes the original on `handler._raw_path` (router.py:79-82). `pebble_engine.py::_handle_preview` then builds the proxy `forward_path` from `self.path` (engine ~line 1820 for the dev-registry proxy; ~line 1792 for the Fly proxy). Because `self.path` no longer has `?url=…&w=…&q=…`, Next's image optimizer receives a bare `/_next/image` and returns `400 "url parameter is required"`.

**Fix.** Introduce a pure helper:

```python
def _preview_forward_path(raw_path: str, slug_prefix: str) -> str:
    """Return the path to forward to the dev server, query string intact.

    raw_path is the original request path WITH query (handler._raw_path);
    slug_prefix is '/preview/<raw-slug>'. Strips the prefix, preserves the
    rest + query, defaults to '/' when empty.
    """
```

Behavior:
- `_preview_forward_path("/preview/foo/_next/image?url=X&w=1920&q=75", "/preview/foo")` → `"/_next/image?url=X&w=1920&q=75"`
- `_preview_forward_path("/preview/foo/", "/preview/foo")` → `"/"`
- `_preview_forward_path("/preview/foo", "/preview/foo")` → `"/"`
- `_preview_forward_path("/preview/foo/about", "/preview/foo")` → `"/about"`

Both proxy call-sites in `_handle_preview` (dev-registry and Fly) compute `forward_path` via this helper using `getattr(self, "_raw_path", self.path)` as the source, instead of `self.path`. Static-file fallback continues to use the query-stripped `self.path`/`rest` for on-disk lookups (correct — files have no query).

**Why a helper:** `_handle_preview` is hard to unit-test (needs a live socket + dev server). The path computation is the only logic that changed, so isolating it into a pure function makes it unit-testable and documents the contract.

**Impact:** every hero/about/testimonial photo across the entire gallery renders in the workspace preview; Playwright thumbnails become real (which also means `promote_example.py --thumbnail` becomes viable later, though still opt-in).

## Part 2 — Photo-top service cards

Chosen card style (visual companion, option A): a real work photo fills the **top** of each card, then title / blurb / optional `from_price` chip / "Request a quote →" CTA.

### 2a. Modify `services_grid_trade`

- **JSON:** the `services` list item tone gains an `image` field — a per-service Pexels query. The slot tone must steer Sonnet to a query for *that specific service* (e.g. "water heater installation plumber", "electrical panel upgrade") so cards are visually distinct, not repetitive stock.
- **TSX:** each `StaggerItem` renders the photo at the top inside a fixed-aspect wrapper (`aspect-[4/3]` or `aspect-video`, `object-cover`, `loading="lazy"`), then the existing title/blurb/price/CTA below. Reuses the proven per-item-image pattern from `gallery_beforeafter_trade` (`{{services[].image}}` resolved by `pebble/pexels_resolver.py`).
- Keep Wave-1 lessons: named `import { Stagger, StaggerItem }`; declare only palette_slots the TSX uses; hardcode mid-gray for muted text; CTA `min-h-[44px]` + `focus-visible:` ring; mobile-first 1→2→3 col grid.

### 2b. New reusable block `services_photo_grid`

- A vibe-neutral photo-top services grid for non-trade builds, so any future industry gets image-rich service cards.
- `vibe_tags`: additive set covering common non-trade vibes (e.g. `clean`, `professional`, `trust-building`, `bold-energetic`, `editorial-minimal`) — chosen so it *adds* an option to those vibes' menus without removing any. Not tagged `trade-pro` (trade already has its own photo-top services block).
- Same slot contract as 2a (`services` list with `title`, `body`, optional `from_price`, `image`), same craft rules. Layout may differ slightly from the trade block (it serves a broader aesthetic), but the slot names match so copy is portable.
- Acceptance: `BlockRegistry.load` accepts it; placeholders resolve at compile; palette parity holds.

### Image resolution note

`pebble/pexels_resolver.py` already resolves `{{list[].image}}` queries inside section files (the gallery block depends on this). No resolver change expected; the implementation plan must verify a services build actually resolves distinct photos per card and, if not, treat it as a resolver/compiler bug to fix before Part 3.

## Part 3 — Rebuild + re-promote the 8 trade examples

1. After Parts 1-2 land, rebuild **one** example (plumber) and verify: `/preview/.../_next/image?...` returns image bytes (not 400); the service grid shows distinct per-service photos; evals still pass `no_invented_time_markers`.
2. Rebuild all 8 via `scripts/build_trade_examples.py`.
3. Eval-gate each (same bar as Wave 1).
4. Capture fresh screenshots; **owner reviews the new renders** (copy is regenerated, so re-approval is required).
5. Re-promote each via `scripts/promote_example.py <slug> --vibe trade-pro` (idempotent — replaces the existing `pebble/examples/<slug>/` + manifest entry in place).
6. Commit the refreshed examples + manifest.

## Testing

- **Unit:** `_preview_forward_path` — query preserved, prefix stripped, empty/trailing-slash/sub-route cases.
- **Block:** registry-load + placeholder-resolution + palette-parity for `services_grid_trade` (modified) and `services_photo_grid` (new); existing block suite stays green; the trade-pro essential-section coverage test still passes.
- **Manual/integration:** rebuilt plumber renders service photos in the live preview; `_next/image` returns 200 with image bytes.

## Risks / mitigations

- **Per-service photo relevance.** Mitigate with a tight `image` slot-tone instructing a query for the specific service; the manual check in Part 3 step 1 catches repetitive/irrelevant photos before the batch.
- **Rebuild regenerates copy (non-deterministic).** Owner re-approves the 8 renders before re-promote (Part 3 step 4).
- **Reusable block starving other vibes' menus.** Tags are additive only; the existing empty-menu fallback + coverage test guard against a vibe losing an essential section.
- **Proxy fix regressions.** The helper is pure + unit-tested; static-file fallback path is untouched; both proxy call-sites switch to the same helper so behavior stays consistent between local-dev and Fly backends.

## Key files

- Proxy: `pebble_engine.py` (`_handle_preview`, new `_preview_forward_path`), `pebble/server/router.py` (`_raw_path` source), test under `tests/`.
- Blocks: `pebble/blocks/library/services_grid_trade.{json,tsx}` (modify), `pebble/blocks/library/services_photo_grid.{json,tsx}` (new), `pebble/pexels_resolver.py` (verify only).
- Pipeline: `scripts/build_trade_examples.py`, `scripts/promote_example.py`, `pebble/example_gallery.json`, `pebble/examples/<slug>/`.
- Eval gate: `python -m pebble.evals <slug>`.
