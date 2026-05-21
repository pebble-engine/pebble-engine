# Phase 31 hand-off — Templates are live

_Autonomous evening session — went dark after your "OK", came back with a working template-instantiation pipeline. Everything below shipped + validated end-to-end._

## TL;DR

You can now do this:

1. POST a brief to `http://localhost:8000/api/instantiate-template` with `{template_id, brief}`
2. Engine clones a designer-curated Next.js project
3. A focused LLM call (~$0.003 — three-tenths of a cent) rewrites only `content/site.ts` with the customer's brand
4. Result is a real Next.js project at `output/<slug>/site/`, deployable like any other Pebble build

**Live proof:** http://localhost:3062 — "Hudson Valley Pest & Lawn" — instantiated from `service_pro` template with a real brief. Took ~30 seconds end-to-end. Cost $0.003.

Compare that to:
- Qwen Flash full generation: $0.02, 187s, dashboard-feeling output
- Claude Sonnet full generation: $0.58, 437s, slightly more polished dashboard
- **Template instantiation: $0.003, 30s, designer-curated visual baseline**

## What landed tonight

### 31a — Design DNA extracted from your 7 client HTMLs

Read every byte of every file in `C:/Users/marci/Qwen 3.6/`, wrote a structured JSON spec for each at `pebble/templates/dna/<slug>.json`. **All 7 DNAs are reusable foundation specs — vibe labels, palettes with hex values, font stacks, section flows, motion vocabularies, applicable-industry lists (5-15 industries each).**

| DNA spec file | Vibe label | Source brand (your client work) | Industries it'd suit as a template |
|---|---|---|---|
| `tattoo_studio.json` | Gothic Blackletter Gold-Glow | Bound By Flesh | tattoo, barber, personal brand, music artist |
| `bakery_warm.json` | Tactile Y2K Warm-Cream | Angie's Bakery | bakery, café, restaurant, deli, ice cream |
| `training_authority.json` | Tactical Crimson Gold-Gradient | Pestana Firearms | trainer, dojo, coach, security, fitness instructor |
| `pest_clean_safe.json` | Glow Emerald Dual-Theme | Squito Pest Control | pest, lawn, HVAC, plumbing, electrician, cleaning |
| `beauty_ethereal.json` | Editorial Mint Ethereal-Cloud | Rich Queen Beauty | beauty, cosmetics, spa, wellness, fragrance, jewelry |
| `real_estate_luxury.json` | Cinematic IMAX Vermilion-Slab | Onyx Properties | real estate, architect, interior design, luxury sales |
| `auto_honest_diag.json` | Industrial Hazard-Stripe Stencil | Iron Cesspool Auto | mechanic, tow, body shop, motorcycle, towing |

Plus PIO.html (Pebble brand site) — skipped per your instructions, that's a different bucket (might become the Pebble marketing site).

### 31b — Service Pro template (DNA from Pest)

Built at `pebble/templates/service_pro/` — full Next.js 14 App Router project, 43 source files. **Brand placeholder: "Coastal Pro Services"** (not Squito). Honors all the Pest design moves: dual light/dark theme + toggle, glass-morphism navbar, 3 blurred glow orbs, shimmer-sweep "Call Now" pill, infinite marquee ticker, 5-star rating chip + 3 trust badges, SVG fractalNoise grain overlay, Inter + Outfit font stack via `next/font/google`. **`npx tsc --noEmit` zero errors. `npx next build` clean. 9 static pages.**

### 31c — Luxe Beauty template (DNA from RQB)

Built at `pebble/templates/luxe_beauty/` — full Next.js project. **Brand placeholder: "Maison Lume"** (not Rich Queen). Honors all the RQB editorial moves: Bodoni Moda italic display + Manrope body + Pinyon Script cursive accent via `next/font/google`, Material Design 3 surface tokens, glass-cards with backdrop-blur, vapor-shadow utility, light-mode cream/mint palette, generous editorial whitespace. **The one non-dark template in the set.** Intentionally simplified two RQB features (Three.js 3D carousel → static 4-tile grid; SPA cart/product detail → static `/shop` page). Both punted as Phase 32+ enhancements. **Validations clean.**

### 31d — Backend infrastructure

- `pebble/templates/registry.json` — template catalog with metadata
- `pebble/server/templates_api.py` — `load_registry()`, `get_template()`, `run_list_templates()`, `run_instantiate_template()`. The instantiator copies template files, runs a focused content-swap LLM call (~3K input / ~3K output tokens), validates the response preserved every exported constant, falls back to template defaults if the LLM dropped any exports.
- Routes wired in `pebble/server/router.py`: GET `/api/templates`, POST `/api/instantiate-template`
- **21 unit tests in `tests/test_templates_api.py`** — registry contract, validation logic, prompt construction, anti-slop guards. All passing.

Full suite: **1737 tests passing**.

### 31e — v3 gallery UI

`ui/v3/app/templates/page.tsx` — gallery grid, click → instantiation modal with business name / industry / location / notes fields → POST to `/api/instantiate-template` → navigate to workspace with new slug.

`ui/v3/lib/api.ts` — added `listTemplates()` + `instantiateTemplate()` + types. **`npx tsc --noEmit` zero errors.**

## What's running for you to look at

| URL | What |
|---|---|
| **http://localhost:8000/api/templates** | Raw JSON from the new endpoint — confirms both templates registered |
| **http://localhost:3062** | "Hudson Valley Pest & Lawn" — a fully instantiated Service Pro template. **Hit this first.** Same design language as Pest.html, completely new brand, fully populated with content-swap output. |
| http://localhost:3060 | OLD Terminal mechanic (this morning's bad render — for comparison) |
| http://localhost:3061 | OLD Weather Report mechanic w/ photo overlay (this evening's "still slop" attempt) |
| http://localhost:3001 | v3 workspace — `/templates` route now exists (you may need to start v3 if it died) |

## What I need from you (the explicit asks)

### Critical / must-decide

1. **Look at http://localhost:3062 first.** Then read `output/hudson-valley-pest-lawn/site/content/site.ts` to see the swapped content. **Is this the quality bar?** If yes, we scale. If no, tell me what's missing and I iterate.
2. **Look at the v3 `/templates` route** (start v3 with `cd ui/v3 && npm run dev` if needed). Tell me if the gallery card design / instantiation dialog feel right.
3. **Confirm the IP/licensing approach.** I structured these templates with placeholder brands ("Coastal Pro Services", "Maison Lume") that share design DNA with your client work but don't reproduce any of their content or brand identity. **Verify this matches what you intended.** If you want even more separation (different fonts, different palette tones from the source DNA), say the word.

### Important / nice-to-decide

4. **Greenlight the remaining 5 templates?** Same pattern as Service Pro + Luxe Beauty:
   - `ink_studio` (from `tattoo_studio` DNA)
   - `instructor_pro` (from `training_authority` DNA)
   - `artisan_kitchen` (from `bakery_warm` DNA)
   - `boutique_brokerage` (from `real_estate_luxury` DNA)
   - `honest_garage` (from `auto_honest_diag` DNA)
   - Each takes ~30 min of agent time. Could be done by tomorrow evening.
5. **Pricing model decision.** Right now `service_pro` and `luxe_beauty` are both `tier: "free"` in the registry. Webild-style framing is "templates free, AI custom paid". You comfortable with that, or do you want a different breakdown (free vs Pro templates)?
6. **Screenshots for the gallery.** Each template needs a hero screenshot at `ui/v3/public/templates-preview/<id>.png`. I can generate these from headless Chrome against the running next dev, or you can take them yourself (might prefer your taste). Currently the gallery shows a swatch-gradient placeholder.

### Optional / future

7. **PIO.html** — your Pebble brand site. Want me to ingest that separately as the foundation for the new Pebble marketing site? Different track from the customer-template gallery.
8. **Phase 30 — cinematic DNA rebrand of the existing /api/generate path** — is that still on the table, or do templates make it moot? My honest take: templates make full-AI-gen the *upgrade* path, not the default. We can still refactor the DNAs later but it's lower priority now.

## What's NOT done (deliberately deferred)

- **Template screenshots** — see ask #6 above
- **The other 5 templates** — see ask #4 above
- **Phase 25b bot persona** — still queued (cheap GPT-4o-mini chat narration during builds)
- **Phase 27 cloud sandbox previews** — still queued (the architectural one; biggest investment)
- **Phase 28 hybrid model routing** — validated tonight ($0.58 Sonnet vs $0.02 Qwen, Sonnet meaningfully more polished). Worth wiring as paid-tier. Independent of templates.

## File map of tonight's work

```
pebble-engine/
├── pebble/
│   ├── templates/               # NEW
│   │   ├── registry.json
│   │   ├── dna/                 # 7 DNA spec files
│   │   ├── service_pro/         # NEW Next.js template (43 files)
│   │   └── luxe_beauty/         # NEW Next.js template (44 files)
│   └── server/
│       ├── templates_api.py     # NEW — list + instantiate handlers
│       └── router.py            # MODIFIED — wired 2 new routes
├── tests/
│   └── test_templates_api.py    # NEW — 21 tests
├── ui/v3/
│   ├── app/templates/page.tsx   # NEW — gallery + instantiate dialog
│   └── lib/api.ts               # MODIFIED — added listTemplates + instantiateTemplate
└── PHASE_31_HANDOFF.md          # NEW — this file
```

## Working tree state

`git status` will show ~20 new + modified files. **Nothing committed** per CLAUDE.md "only commit when requested". Your call.

Tests: **1737 passing** (+21 new from `test_templates_api.py`).

## How to do the verification I'm asking for

```bash
# 1. Look at the instantiated Hudson Valley site
open http://localhost:3062

# 2. Read what the LLM swapped in
cat output/hudson-valley-pest-lawn/site/content/site.ts

# 3. Test another instantiation yourself with a different brief
curl -X POST http://127.0.0.1:8000/api/instantiate-template \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "luxe_beauty",
    "brief": {
      "business_name": "Saffron & Smoke Apothecary",
      "business_type": "skincare brand",
      "location": "Brooklyn, NY",
      "notes_freeform": "Small-batch botanical skincare. Cruelty-free. We source from regenerative farms in upstate NY."
    }
  }'
# ~30 seconds later — preview at: cd output/saffron-and-smoke-apothecary/site && npm install && npx next dev -p 3063

# 4. Look at the gallery
cd ui/v3 && npm run dev
# then open http://localhost:3001/templates
```

---

This is the path forward. The LLM is no longer being asked to design — it's being asked to do one narrow, high-quality task it's reliably good at: rewriting content values inside a curated structure.

You proved tonight that you had the design ceiling solved already (your client HTMLs are the proof). All we needed was to operationalize that ceiling into a templating system that anybody can use. That's what shipped.

---

## Addendum — additional autonomous work after Phase 31

You said "is there anything else you can do autonomously" — three more pieces landed:

### Luxe Beauty instantiation validated end-to-end

Triggered `luxe_beauty` instantiation with a "Saffron & Smoke Apothecary" botanical-skincare brief. **Cost $0.005, ~60s, swap_ok: true.** Qwen wrote "Where Botanicals Meet Ritual" + "rooted in brooklyn" — poetic, on-brand, captured the location.

**Live preview:** http://localhost:3063 — both templates now have a real instantiation to compare:
- **3062** Hudson Valley Pest & Lawn (Service Pro template)
- **3063** Saffron & Smoke Apothecary (Luxe Beauty template)

### Phase 29 — `next_js_static_check` extended with SSR-ref detection

Added the 6th gotcha to the existing eval — `document.` / `window.` references inside JSX expressions, which crash SSR even in "use client" files. Caught the exact pattern from this evening's Footer.tsx bug. **6 new tests pinning the behavior**, including the safe cases (useEffect bodies, typeof guards, onClick arrow handlers). Total `test_next_js_static_check.py` now 22 tests.

### Phase 25b — `/api/bot-message` endpoint shipped

The Webild-Bob narration pattern. Backend-only for now; v3 integration is a frontend slice you can decide when to schedule.

- **POST /api/bot-message** with `{intent: "greeting" | "status" | "chips", context: {...}}`
- Returns `{message: str}` for greeting/status, `{chips: str[]}` for chips
- Uses **GPT-4o-mini via OpenRouter** (~$0.0001/call, ~$2/month at 1000 builds × 20 calls each)
- Independent of PEBBLE_MODEL — never accidentally routes through the expensive build model
- **Graceful fallback**: if the LLM call fails, returns a safe canned message instead of 500'ing. The whole point is making the UI feel alive; a fallback beats no message.
- **16 unit tests** in `tests/test_bot_message.py`

Tested all three intents live, all return real LLM-generated content. Examples:

| Intent | Real response |
|---|---|
| greeting | "Hi there. I'll help you create a website for Hudson Valley Pest & Lawn, focusing on your pest control services. Let's get started." |
| status (phase="writing pages") | "I just finished writing the pages for Hudson Valley Pest & Lawn." |
| chips | ["Enhance Service Descriptions", "Add Customer Testimonials", "Create Seasonal Promotions Page"] |

When you want v3 to use it, drop `fetchBotMessage()` into the workspace draft phase and replace the static "Hang out while Pebble builds…" copy with the dynamic greeting + status updates.

### Updated test count

**1759 tests passing** (was 1716 before Phase 25b + 29). +43 net additions tonight.

### Updated file map

```
pebble-engine/
├── pebble/
│   ├── server/
│   │   ├── bot_message.py             # NEW — Phase 25b endpoint
│   │   ├── templates_api.py           # Phase 31d
│   │   └── router.py                  # MODIFIED — wired bot-message + templates routes
│   ├── evals/checks.py                # MODIFIED — Phase 29 (gotcha #6)
│   └── templates/                     # Phase 31a/b/c (DNAs + 2 templates)
├── tests/
│   ├── test_bot_message.py            # NEW — 16 tests
│   ├── test_next_js_static_check.py   # MODIFIED — +6 tests for gotcha #6
│   ├── test_templates_api.py          # Phase 31d
│   └── ...
└── ui/v3/
    ├── app/templates/page.tsx         # Phase 31e
    └── lib/api.ts                     # MODIFIED — added listTemplates + instantiateTemplate
```

### Updated "what I need from you" list

Original asks unchanged (look at 3062, look at /templates gallery, confirm IP/licensing). Plus optional follow-ups:

- **Phase 25c — bot greeting wired into v3** (DONE while you were away). Draft-phase headline now fetches a warm greeting from `/api/bot-message` on the `started` SSE event. Static fallback if LLM fails. Visible next time anyone triggers a build via v3.
- **Phase 31f — 3 more templates building NOW** (in progress as of this update). `ink_studio` (tattoo), `artisan_kitchen` (bakery), `instructor_pro` (training). Same pattern as service_pro + luxe_beauty. ~10 more minutes.
- **Gallery preview screenshots captured** at `ui/v3/public/templates-preview/service_pro.png` + `luxe_beauty.png` — gallery now shows real previews instead of swatch gradients.
- **/templates added to v3 top nav** — Sparkles icon next to Help, visible from every authenticated page.

### Latest autonomous additions (after the "is there anything else autonomously" check)

- Bot-message v3 wire-up (greeting in draft-phase) ✓
- **3 additional templates BUILT, INSTANTIATED, AND SCREENSHOT-CAPTURED** ✓
- Gallery preview screenshots captured for all 5 templates ✓
- /templates link added to top-nav ✓
- `scripts/capture_template_previews.py` + `scripts/preview_new_template.sh` — reusable scripts ✓
- TypeScript clean throughout, **1759 tests passing**

---

## FINAL state — 5 templates live in the gallery

| Template ID | Brand placeholder | Vibe | Instantiated as | Live at |
|---|---|---|---|---|
| `service_pro` | Coastal Pro Services | Glow Emerald Dual-Theme | **Hudson Valley Pest & Lawn** | http://localhost:3062 |
| `luxe_beauty` | Maison Lume | Editorial Mint Ethereal-Cloud | **Saffron & Smoke Apothecary** | http://localhost:3063 |
| `ink_studio` | Inkhouse Atelier | Gothic Blackletter Gold-Glow | **Vermilion Ink Atelier** | http://localhost:3064 |
| `artisan_kitchen` | Maple & Hearth | Tactile Y2K Warm-Cream | **Hayfield Bakery** | http://localhost:3065 |
| `instructor_pro` | Stratford Tactical Academy | Tactical Crimson Gold-Gradient | **Brookline Fitness Academy** | http://localhost:3066 |

**Combined cost of 5 instantiations: ~$0.022** (each was $0.003-0.007 on Qwen 3.6 Plus content-swap). Compare to ~$2.50 if all five had been full AI generations.

**Gallery at http://localhost:3001/templates now shows all 5 with real preview screenshots** (not the swatch-gradient placeholders).

### Final ask priority for when you check in

1. **Hit http://localhost:3001/templates** — confirm the gallery feels right.
2. **Visit each of the 5 instantiated previews** (3062-3066) — confirm they each clear your quality bar.
3. **Read each `output/<slug>/site/content/site.ts`** — confirm the LLM content swaps produced acceptable copy (none of the prior anti-slop patterns like "since 2015" or "15+ Years Experience" should appear).
4. **Then decide pricing/positioning**: templates default for free tier? Custom AI gen as paid upgrade?

If everything passes, the remaining 2 DNAs (`real_estate_luxury`, `auto_honest_diag`) can be built next session with the same agent pattern — another ~$0.01 of LLM cost and ~30 minutes of agent time.

Sleep well when you do. Tomorrow's first decision is whether `http://localhost:3062` clears the quality bar.

— Claude

---

## Phase 32 update — 21 templates now in the gallery

_Continuation session after your "shoot for 21" go-ahead. All 14 color variants + 2 new bases landed and shipped._

### What got built

**Two new bases** (real DNAs that were sitting in `_planned_next`):
- `boutique_brokerage` → **Beacon & Bay Realty** — Cinematic IMAX Vermilion-Slab — for luxury real estate / boutique brokerage / urban high-end developers
- `honest_garage` → **Honest Axle Auto** — Industrial Hazard-Stripe Stencil — for mechanic / tire / fleet / motorcycle / brake shop

**14 color variants** (2 per base, layered on top of the existing 7 bases):

| Base DNA | Variant | Brand placeholder | Vibe |
|---|---|---|---|
| service_pro | navy | Meridian Service Co | Corporate Navy + Slate (B2B / bonded white-collar trades) |
| service_pro | cream | Magnolia Home & Garden | Warm Cream + Forest Emerald (landscape / lawn / garden) |
| luxe_beauty | rose | Rose & Veil Apothecary | Warm Rose + Lavender (intimate feminine luxury) |
| luxe_beauty | aubergine | Atelier Vesper | Deep Aubergine + Champagne (evening luxury / perfume / jewelry) |
| ink_studio | oxblood | Cathedral Ink Society | Warm Gothic Oxblood + Parchment (leather / whiskey / vintage) |
| ink_studio | steel | Vault Iron Studio | Cold Steel + Aged Brass (workshop / fabrication / metal craft) |
| artisan_kitchen | navy | Harbor Light Coffee | Coastal Navy + Amber (coastal cafés / cream + warm amber) |
| artisan_kitchen | olive | Olive Tree Trattoria | Deep Olive + Honey + Terracotta (Mediterranean / trattoria) |
| instructor_pro | navy | Veridian Executive Coaching | Authority Navy + Gold (executive / leadership / pro services) |
| instructor_pro | forest | Northbound Guide Co | Wilderness Forest + Bronze (guiding / outdoor / eco-lodges) |
| boutique_brokerage | sage | Willow & Slate Estates | Sage Countryside + Bronze (Hudson Valley / rural luxury) |
| boutique_brokerage | navy | Harbor Stone Holdings | Marine Navy + Brass (Greenwich / Newport yacht-club RE) |
| honest_garage | rust | Rust Belt Garage | Vintage Americana Rust + Bone (classic-car / restoration) |
| honest_garage | military | Foxtrot Motor Works | Olive Drab + Safety Orange (diesel / fleet / heavy-duty) |

Every variant was built by a dedicated agent: clean palette + tonal voice swap, **structure identical to parent**, `npm install` + `tsc --noEmit` + `next build` all green per agent report. Fonts kept identical to parent base.

### How the gallery behaves with 21

- **7 bases** keep their dev servers running on **ports 3062-3068** so the iframe preview pane works (Home / About / Services / Contact tabs).
- **14 variants** are screenshot-only — the card click goes straight to the instantiate dialog. **The screenshot IS the preview.** Avoids running 21 dev servers continuously.
- Screenshot capture: `python scripts/boot_variant_previews.py --kill-after` (boots each on 3070-3083 just long enough to capture, then frees RAM).

### Files added / changed this session

- `pebble/templates/registry.json` — 21 entries (was 5). Added 2 base entries (boutique_brokerage + honest_garage with preview_url 3067/3068) + 14 variant entries (no preview_url, screenshot-only).
- `pebble/templates/<variant>/` × 14 new directories (full Next.js project copies with palette swaps in `tailwind.config.ts`, `app/globals.css`, `app/icon.svg`, and brand swaps in `content/site.ts`).
- `ui/v3/public/templates-preview/<variant>.png` × 14 new screenshots + 2 base screenshots.
- `scripts/register_variants.py` — one-shot to batch-add 14 variants to registry. Idempotent (skips if already registered).
- `scripts/boot_variant_previews.py` — boot 14 dev servers on 3070-3083, wait for ready, Playwright screenshot batch, optional `--kill-after` to free RAM.
- `scripts/boot_new_bases.py` — companion for capturing the 2 new bases on 3067/3068.

### Cost

- Per-variant agent build: ~$0.20-0.40 (sonnet-tier, 100k tokens each). 14 variants ≈ **$3-5 total** in agent cost.
- Zero LLM cost at user runtime — variants are baked Next.js projects, identical to base templates from the instantiation pipeline's perspective.

### What's not committed

Per your standing instruction, **nothing was committed or pushed**. All 21 templates + 14 screenshots + 3 helper scripts are sitting clean in the worktree. When you're ready:

```bash
git add pebble/templates/registry.json pebble/templates/*_*/ ui/v3/public/templates-preview/ scripts/register_variants.py scripts/boot_variant_previews.py scripts/boot_new_bases.py
git commit -m "Phase 32: 14 color variants + 2 new bases — 21 templates total"
```

### Verification checklist for when you come back

1. **Hit http://localhost:3001/templates** — should now show **21** cards (was 5). Variants appear without preview iframes; bases get full iframe + page-tab preview.
2. **Click each of the 14 variants** — instantiate dialog should fire (uses parent's `preview_image` as the card thumb).
3. **Confirm brand swaps** — open any 3 random variants' `content/site.ts` and verify the SITE_TITLE matches the table above (no client brand leaks).
4. **Spot-check a base preview** — http://127.0.0.1:3067/ should show Beacon & Bay Realty; http://127.0.0.1:3068/ should show Honest Axle Auto.

### Known caveats

- **honest_garage_rust + honest_garage_military screenshot sizes are small** (~165 KB vs 3-5 MB for others). **This is correct** — the hazard-stripe stencil aesthetic uses solid colors and minimal photography vs the photo-heavy beauty/RE templates. Verified the render visually: FOXTROT MOTOR WORKS, hazard stripe, full hero — clean.
- The `_planned_next` array in registry.json is now empty (both planned templates shipped).
- READMEs in variant directories still credit "Rich Queen Beauty Supply" etc. as design lineage — same as the existing pattern in `pebble/templates/dna/*.json`. **Internal documentation only**, not shipped to instantiated customer sites.

— Claude (Phase 32 continuation)
