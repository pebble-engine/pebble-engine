# Pebble Engine

A local website-generation engine for sites that don't look generated. Answer a short business-intake quiz; the engine resolves an industry DNA, picks a per-build aesthetic personality, fetches industry-relevant photos and a hero video, runs an anti-slop audit, calls an LLM, and writes a working Next.js site to disk. Optional post-build steps generate AI hero images, install dependencies, start `next dev`, and capture screenshots.

The engine is a single-process Python HTTP server. No framework, no cloud, no auth — runs entirely on `localhost:8000`.

---

## Quick start

```bash
git clone <repo>
cd pebble-engine
pip install -r requirements.txt
cp .env.example .env          # then fill in keys, see "Configuration"
cd ui && npm install && npm run build && cd ..
python pebble_engine.py
```

The browser opens at `http://localhost:8000`. If port 8000 is taken: `python pebble_engine.py --port 8765`.

For quick iteration without auto-build or images, only `GOOGLE_API_KEY` (or `ANTHROPIC_API_KEY`) needs to be set.

---

## Pipeline

Each `/api/generate` call runs this sequence:

```
intake quiz (ui/index.html)
     │
     ▼
slug + brief
     │
     ▼
design-system search (ui-ux-pro-max BM25 over CSV data)
     │
     ▼
industry intelligence (industries.json → LLM fallback → cache)
     │
     ▼
industry research (long-form text via LLM)
     │
     ▼
hero imagery (Pexels photos + Pexels Video API when hero_type=video)
     │
     ▼
design reference (optional Figma + uploaded screenshots)
     │
     ▼
Style DNA pick (random aesthetic personality from style_dna.py)
     │
     ▼
anti-slop audit (CONVERGENCE_FONTS, ACCEPTABLE_DISPLAY_PAIRS, WATCH_STYLES)
     │
     ▼
PROMPT.md assembled from skills/prompt_template.md
     │
     ▼
LLM call → response parsed → files written to output/<slug>/site/
     │
     ▼
[PEBBLE_USE_IMAGEN=true]  Imagen 4 generates hero/section images,
                          replaces Pexels URLs in generated .tsx/.ts/.js/.html
     │
     ▼
[PEBBLE_AUTO_RUN=true]    npm install → next dev → Playwright screenshots
```

Mode A (prompt only) stops after `PROMPT.md` is written and returns it to the UI. Mode B (full build) runs the rest.

---

## Style DNA

`style_dna.py` ships 10 over-specified visual identities (Swiss Magazine, Brutalist Editorial, Terminal Operator, etc.). One is picked at random per build and injected at the top of `PROMPT.md` with override-priority framing so it contradicts the default Fraunces/Inter pairing baked into the template. Same business inputs produce visibly different sites across runs because the DNA dictates display/body/mono fonts, hero structure, motion intensity, layout grid, and a list of signature moves the LLM must include.

The skill files (Stack, iOS, No-Slop, BI) still apply for code correctness and conversion patterns. DNA only governs visual surface.

The chosen DNA id is saved in each build's `brief.json` under `_design_dna`.

---

## Industry intelligence

`industries.json` is a curated database of 52 industries. Each entry drives palette, hero type, Three.js variant, video keyword, copy tone, trust signals, and section order.

Lookup is fuzzy (`exact key → substring → word overlap`). When a business type doesn't match any entry, the engine asks the LLM to fill in a new entry, validates the shape, and writes it back to `industries.json` so the next build for that industry is fast.

Key matched + entry are surfaced to `brief.json` as `_industry_intel_key` and injected into `PROMPT.md` as an `## INDUSTRY INTELLIGENCE` block.

---

## Configuration

`.env` is loaded at startup. Required keys depend on which features are turned on.

| Variable | Purpose |
|---|---|
| `PEBBLE_PROVIDER` | `gemini` (default) or `anthropic` |
| `PEBBLE_MODEL` | Optional override. Defaults: `gemini-2.5-flash`, `claude-opus-4-7`. |
| `GOOGLE_API_KEY` | Required when provider is gemini. [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `ANTHROPIC_API_KEY` | Required when provider is anthropic. [console.anthropic.com](https://console.anthropic.com/settings/keys) |
| `PEXELS_API_KEY` | Hero photos + Pexels Video API. Falls back to Picsum if missing. |
| `FIGMA_ACCESS_TOKEN` | Optional. Pulls metadata when the brief includes a Figma URL. |
| `PEBBLE_USE_IMAGEN` | `true` to swap Pexels stills with Imagen 4 generations after the LLM call. |
| `PEBBLE_AUTO_RUN` | `true` to run `npm install`, `next dev`, and Playwright screenshots after build. |

If both `PEBBLE_USE_IMAGEN` and `PEBBLE_AUTO_RUN` are off, a build takes 60–120 s end-to-end. With both on, expect 3–5 minutes (Imagen calls + npm install dominate).

---

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET  | `/`                         | The intake quiz UI |
| GET  | `/api/health`               | Engine + LLM readiness, provider + model |
| GET  | `/api/industries`           | Flat list from `industries.json` for the typeahead |
| GET  | `/api/briefs`               | All saved briefs in `output/` |
| GET  | `/api/briefs/<slug>`        | One brief: answers, prompt, file tree |
| POST | `/api/build`                | Generate prompt only, save to `output/<slug>/`, return JSON |
| POST | `/api/generate`             | Generate prompt **and** call LLM, write site files |
| POST | `/api/setup`                | Save API key + provider to `.env`, reload, return new health |
| GET  | `/preview/<slug>/...`       | Serve files from the generated site |
| GET  | `/static/...`               | Built Tailwind CSS, fonts, demo videos for the quiz UI |

---

## Project structure

```
pebble-engine/
├── pebble_engine.py             ← HTTP server + build orchestration
├── pebble/                      ← package extracted from pebble_engine.py
│   ├── llm.py                   ← Gemini / Anthropic clients + vision support
│   ├── industry.py              ← lookup_industry_intel, research_new_industry, resolve_industry_intel
│   └── postbuild.py             ← Imagen, post-build npm + next dev + Playwright
├── style_dna.py                 ← DNA cards + pick_random_dna + build_dna_block
├── industries.json              ← 52-industry design DNA database
├── skills/
│   ├── prompt_template.md       ← Master prompt template, str.format() rendered
│   ├── no-slop-web/             ← anti-slop doctrine
│   ├── ui-ux-pro-max/           ← BM25 design system search
│   ├── stack/                   ← Next.js + motion stack rules
│   ├── ios/                     ← iOS Safari constraints
│   ├── business-intelligence/   ← industry-aware copy direction
│   ├── visitor-experience/      ← UX patterns
│   ├── code-reviewer/           ← post-build review (still manual)
│   ├── readme-generator/        ← project README writer
│   ├── git-commit-writer/       ← clean commits
│   └── software-architect/      ← architecture artifacts
├── ui/
│   ├── index.html               ← single-file quiz (no build step)
│   ├── input.css                ← Tailwind source
│   ├── tailwind.config.js
│   ├── package.json             ← Tailwind CLI only — `npm run build` → ui/style.css
│   └── style.css                ← prebuilt Tailwind output (the CDN is gone)
├── tests/
│   ├── test_smoke.py            ← 14 smoke tests, ~2.5 s, no network
│   └── conftest.py
├── pyproject.toml               ← pytest config
├── requirements.txt
├── .env.example
└── output/
    └── <slug>/
        ├── brief.json           ← saved answers + _design_dna + _industry_intel_key
        ├── PROMPT.md            ← full assembled prompt
        ├── llm_response_raw.txt ← raw response (full builds only)
        ├── build_meta.json      ← provider + model + elapsed time
        └── site/                ← generated Next.js project
```

---

## Tests

```bash
pytest
```

14 smoke tests, ~2.5 s, no network. They exercise prompt rendering, DNA card shape, industry-intel resolution, the slugifier, and the audit. Treat them as the floor — anything that touches `build_prompt`, `pick_random_dna`, `resolve_industry_intel`, or `audit_design_system` should leave them green.

The most likely regression they catch: a literal `{` or `}` slipped into `skills/prompt_template.md` without doubling, which silently breaks `str.format()` at build time.

---

## UI build

`ui/style.css` is committed prebuilt — the page loads instantly without a Tailwind CDN. To change classes used in `ui/index.html`:

```bash
cd ui
npm install              # first time only
npm run build            # one-shot
# or: npm run watch      # rebuild on save while iterating
```

`tailwind.config.js` scans `index.html` for class names. Nothing else triggers a rebuild.

---

## Iterating

The highest-leverage edit points:

- `ui/index.html` — `QUESTIONS` array at the top of the `<script>` tag controls intake. Intake quality compounds.
- `skills/prompt_template.md` — the master prompt. Edit and every future site inherits the change. Double literal `{` `}` — `str.format()` renders this file. The smoke tests catch brace regressions.
- `style_dna.py` — add a new DNA card to widen the visual range. Each card is intentionally over-specified.
- `industries.json` — add or refine an industry entry. The LLM fallback writes new ones automatically; hand-curating them is just higher quality.
- `pebble_engine.py` — `CONVERGENCE_FONTS`, `ACCEPTABLE_DISPLAY_PAIRS`, `WATCH_STYLES` at the top tune what the anti-slop audit flags.

---

## Antigravity workflow (optional)

The engine works standalone, but if you open `pebble-engine/` as a workspace in Antigravity, the `skills/` directory becomes available to the agent automatically. The original Mode-A flow — take the quiz, download `PROMPT.md`, paste into Antigravity — still works as a fallback when `PEBBLE_PROVIDER` is unconfigured.

---

## Provider notes

- **Gemini** is the default. `gemini-2.5-flash` is fast and free-tier friendly. Google AI Ultra subscribers get higher rate limits.
- **Anthropic** is the second-opinion / premium path. `claude-opus-4-7` produces the highest-quality builds; switch with `PEBBLE_PROVIDER=anthropic`. Both clients accept image attachments (Figma screenshots, reference uploads) as vision input.

Imagen 4 (`imagen-4.0-generate-001`) is hard-coded for image generation regardless of provider; it requires a Google key.
