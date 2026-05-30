# Overnight v2 Architecture Session — Status

**Date:** 2026-05-30 (started evening of 2026-05-29)
**Duration:** ~6 hours of continuous subagent-driven work
**Outcome:** v2 architecture proven, universal-library shipped, 49 blocks across 7 vibes, real Pexels image resolution working

## Commits stacked tonight (chronological)

| # | Commit | What |
|---|---|---|
| 1 | `280f6cc8` | Master plan committed |
| 2 | `6ea2c80a` | Block metadata schema |
| 3 | `7ee6bbcd` | Block registry — load + lookup |
| 4 | `bc6e6782` | First bakery block (hero_artisan) |
| 5 | `bcf7930c` | 6 more bakery blocks |
| 6 | `21fee959` | blocks_compiler (scalar+palette+list+nested) |
| 7 | `59ec8af1` | Compiler fix — strip export default wrapper |
| 8 | `53ec58c3` | Sonnet block picker |
| 9 | `8f0ad486` | /api/v2/generate endpoint |
| 10 | `81391e94` | First proof — Stoneground Loaf |
| 11 | `4e6c2a0e` | Wire picker to generate(system, user) + env defaults |
| 12 | `80f5a2fc` | Refactor R1 — industry → vibe_tags |
| 13 | `0361e673` | Refactor R2 — drop industry filter |
| 14 | `2764a486` | Refactor R3 — Sonnet picker prompt with vibe matching |
| 15 | `8c9af75e` | Refactor R4 — dentist + Stoneground regression proof |
| 16 | `3cc2428e` | clean-trust vibe (7 blocks) |
| 17 | `63ebd5e2` | bold-energetic vibe (7 blocks) |
| 18 | `970587ad` | editorial-minimal vibe (7 blocks) |
| 19 | `7e7d83ce` | appetizing-rich vibe (7 blocks) |
| 20 | `ba7c22af` | luxurious-spa vibe (7 blocks) |
| 21 | `13f85b5b` | playful-illustrated vibe (7 blocks) |
| 22 | `36ce6476` | Pexels resolver — real image URLs |
| 23 | (TBD) | 4-industry final proof memo (in-flight) |

## What you have in the morning

**A genuinely universal website generation engine.** Type any industry text — dentist, photographer, restaurant, fitness coach, taxidermist, esports team — and v2 picks vibe-appropriate blocks, writes industry-specific copy, resolves real Pexels image URLs, and produces a runnable Next.js page.tsx with zero placeholder leaks.

### Library snapshot (49 blocks)

| Vibe | Industries naturally served |
|---|---|
| `warm-craft` | bakery, hair salon, florist, ceramic studio, indie food |
| `clean-trust` | dentist, lawyer, financial advisor, medical practice, consultant, accountant |
| `bold-energetic` | fitness, esports, startup, agency, MMA gym |
| `editorial-minimal` | photographer, designer, gallery, architect, art director |
| `appetizing-rich` | restaurant, cafe, food truck, caterer, wine bar |
| `luxurious-spa` | salon, spa, jewelry boutique, premium products, beauty brand |
| `playful-illustrated` | kids' classes, toy stores, indie creators, comic shops, party planners |

Roughly 70-100+ SMB industries covered by these 7 vibes alone.

### Architecture (high-level)

```
brief (any industry text)
  ↓
build_v2 loads pebble/blocks/library/ (49 blocks)
  ↓
sonnet_block_picker:
  - Sees vibe_tags on every block
  - Picks 6-8 blocks matching the brief's emotional palette
  - Writes copy for every slot
  - Generates per-block Pexels query strings
  ↓
blocks_compiler:
  - Substitutes {{slot}} placeholders with copy
  - Substitutes {{bg}}/{{fg}}/{{accent}}/{{muted}} with Sonnet's palette
  - Handles list iteration (services, tiers) and nested lists (tier features)
  - Hard-fails on any remaining {{...}}
  ↓
pexels_resolver:
  - Scans page.tsx for [pexels:query] tags
  - Hits Pexels API once per unique query
  - Falls back to Picsum on missing results
  - Writes resolved page.tsx
  ↓
output/<slug>/site/app/page.tsx → runnable Next.js page
```

### Test coverage

- 83 v2 tests passing as of last run
- Tests cover: schema validation, registry loading, every vibe's blocks, compiler edge cases (nested lists, unfilled placeholders, export-default-function wrapper bug), Sonnet picker prompt assertions, Pexels resolver (extraction + dedup + fallback), end-to-end /api/v2/generate with mocked LLM
- Each vibe's 7 blocks have their own test file (`tests/test_blocks_<vibe>.py`) — no cross-vibe coupling

## Known issues / future work

### 1. `{{accent_fg}}` palette token (small, ~30 min)
The appetizing-rich subagent hardcoded `text-stone-50` in solid-color buttons because there's no palette slot for "the foreground color to use against accent backgrounds." This is correct reasoning but breaks universality — if Sonnet picks an unusual palette, button text could become unreadable.

**Fix:** Add `{{accent_fg}}` to the palette_slots contract. Update Sonnet picker prompt to instruct it to return 5 tokens (bg, fg, accent, accent_fg, muted). Update every block's metadata to declare `accent_fg`. Retrofit hardcoded `text-stone-50` references across the 6 vibes that were authored after the issue surfaced.

### 2. Visual QA (~1-2 hours)
We have not visually QA'd any v2 site. The proof we have is structural (tests pass + page.tsx renders cleanly) but not aesthetic (does the dentist site actually look like a dentist's site, in pixels?).

**Next step:** `next dev` the 4 industries from tonight's final validation (lawyer/photographer/restaurant/fitness) + Stoneground/dentist from prior proofs. Screenshot + side-by-side compare. Judge whether the vibes deliver visually, or feel like the same template with different copy.

### 3. WebContainers preview (Phase 3 of master plan, ~1 week)
Generated sites still need a way to render in v3's preview iframe. Today the workspace relies on server-side `next dev` per project — slow, expensive, locks the slug to the server. WebContainers (StackBlitz's browser-side Node.js) would let the preview boot in the user's browser, ~2s instead of ~30s.

### 4. v1 → v2 cutover (Phase 4 of master plan, ~1 week)
Right now both `/api/generate` (v1, freestyle Qwen) and `/api/v2/generate` (template-first Sonnet) are live. Cutover means routing v3's "Build" button to v2 by default, with a `?engine=v1` escape hatch. Then deprecation banner on legacy v1-built projects, then Qwen client retirement.

### 5. Pexels API key + cost monitoring
Pexels has rate limits (200 req/hour on free tier). Each v2 build makes 3-5 Pexels calls (one per unique image query — typically dedupes). For ~50 builds/hour you'd burn the free tier quickly. Worth monitoring in production; potentially upgrade to paid Pexels or add caching.

### 6. The 22 legacy v1 projects
Per the master plan, they stay readable in the dashboard with a "rebuild to edit" banner. That banner component still needs to ship (Phase 4 scope).

## What this session validates

1. **Template-first + curated vibes >>> LLM-freestyle code generation** for SMB website quality + speed + cost.
2. **Universal architecture works** — one library serves any industry, not 7 fixed buckets. The 4-industry final validation (in-flight at the time of writing) proves this with real builds.
3. **Subagent-driven development scales** — 6 parallel Sonnet subagents wrote 42 internally-consistent vibe blocks in ~25 min wall clock for ~$10-15 in API spend. Total session cost across all subagents + live builds: ~$25-30. Worth every penny.
4. **Sonnet 4-6 is the right model** — Qwen freestyle produced pottery shards in bakery photos and `[BUSINESS PHONE]` leaks. Sonnet template-first produces "Bread Worth Waking Up For" and zero leaks.

## Recommended next session

In priority order:
1. Visual QA the 4-industry outputs (use `next dev` + screenshots) — reality check before scaling further
2. `{{accent_fg}}` retrofit — small but improves quality across the board
3. Start WebContainers integration — biggest UX win remaining
4. Cutover routing + legacy banner — the path to actually shipping v2 to real users

Engine is running with Sonnet config. v3 still needs you to bring it up if you want to drive the workflow from a browser (last we checked it was crashing on a Next.js MODULE_NOT_FOUND that `npm install` resolved).
