# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Pebble Engine — a local Python HTTP server that generates production Next.js 14 marketing sites from a short intake quiz. Strategic direction (May 2026): pivoting from generator-only to a hosted SaaS targeting non-technical small-business owners. See `.claude/SENIOR_LEVEL_ROADMAP.md` for the multi-phase plan.

## Common commands

```bash
# Run the engine (port 8000)
python pebble_engine.py

# Override port if 8000 is taken
python pebble_engine.py --port 8765

# Test suite — 206 passing as of ce909b0
python -m pytest -q

# Run a single test file
python -m pytest tests/test_evals.py -q

# Run a single test by name
python -m pytest tests/test_evals.py::test_no_src_directory_passes_when_absent -q

# Rebuild the quiz UI Tailwind (only if changing ui/index.html classes)
cd ui && npm run build

# Run the eval suite manually against a generated build
python -m pebble.evals output/<slug>

# Run the repair loop manually (requires LLM key in .env)
python -m pebble.repair <slug> --max-rounds 2

# Live engine health check
curl -s http://127.0.0.1:8000/api/health
```

Environment flags that change behavior (see `.env`):

- `PEBBLE_PROVIDER=gemini|anthropic`
- `PEBBLE_MODEL=<model-id>` — provider default if unset
- `PEBBLE_USE_IMAGEN=true` — replace Pexels stills with Imagen 4 (Google key required)
- `PEBBLE_AUTO_RUN=true` — npm install + next dev + Playwright screenshots after build
- `PEBBLE_AUTO_REPAIR=true` — run evals + repair loop after every full build

## Architecture in 60 seconds

`pebble_engine.py` (~1800 lines) is the HTTP server + build orchestrator. Most of the build pipeline has been carved out into the `pebble/` package:

- `pebble.llm` — Gemini + Anthropic clients with vision support
- `pebble.industry` — 52-industry lookup with LLM fallback for new industries, fuzzy matching, writes new entries back to `industries.json`
- `pebble.postbuild` — Imagen image generation, npm install, `next dev`, Playwright screenshots
- `pebble.repair` — critique-and-fix loop wired in via `PEBBLE_AUTO_REPAIR`
- `pebble.evals` — 27 FOUNDATION checks + repair-corpus harness
- `pebble.server.build` — the actual `/api/generate` request body

`/api/generate` runs this sequence for each build:

```
quiz → slug + brief
  → design-system search (BM25 over CSV in skills/ui-ux-pro-max/data)
  → industry intelligence (industries.json → LLM fallback → cache)
  → hero imagery (Pexels photos + Pexels Video API)
  → Style DNA pick (random one of 10 cards in style_dna.py)
  → anti-slop audit (CONVERGENCE_FONTS, ACCEPTABLE_DISPLAY_PAIRS, WATCH_STYLES)
  → PROMPT.md assembled from skills/prompt_template.md
  → LLM call → response parsed → files written to output/<slug>/site/
  → [if PEBBLE_USE_IMAGEN] Imagen 4 swaps Pexels stills
  → [if PEBBLE_AUTO_RUN] npm install → next dev → screenshots
  → [if PEBBLE_AUTO_REPAIR] eval suite → focused repair prompt → re-eval (up to 2 rounds)
```

## What every generated site includes (the foundation)

VEX-spec hero is MANDATORY for every build. The Style DNA system layers accent decoration on top — DNA does NOT override the foundation. Inverted hierarchy as of `cc3ed96` (May 2026 overhaul).

Foundation artifacts the eval suite enforces:

- `app/layout.tsx` — Inter via `next/font/google` (weights 300/400/500/600), `<html lang="...">` mandatory
- `components/ui/AnimatedHeading.tsx` — per-character entrance with sr-only span (a11y) + aria-hidden char wrapper + built-in textShadow
- `components/ui/FadeIn.tsx` — opacity wrapper with `prefers-reduced-motion` bypass
- `components/sections/Hero.tsx` — full-bleed `<video autoPlay muted loop playsInline poster=...>` with NO dark overlay
- `components/layout/Navbar.tsx` — liquid-glass rounded chip pattern with `focus-visible:` rings
- `components/forms/ContactForm.tsx` + `app/actions/contact.ts` + `lib/email.ts` — real Resend Server Action, NOT a fake onSubmit
- `app/globals.css` — `.liquid-glass` utility, `@media (prefers-reduced-motion: reduce)`, Inter body
- `vercel.json` + README `## Deploy` section
- `.env.example` with `RESEND_API_KEY`, `CONTACT_FROM_EMAIL`, `CONTACT_TO_EMAIL`

Style DNA (`style_dna.py`) holds 10 over-specified personalities (Swiss Magazine, Brutalist Editorial, Terminal Operator, Cinematic IMAX, etc.). One is picked at random per build. DNA contributes: palette, copy voice, signature moves, accent font for pull-quotes / drop-caps / stat numbers / optional right-column hero tag. NEVER the h1 (Inter wins) or body.

## Hard rules — the gotchas that bite

1. **`skills/prompt_template.md` is rendered via Python `str.format()`.** Every literal `{` and `}` in code samples must be doubled (`{{`, `}}`). The smoke tests catch regressions but only after the build fails. When editing, search for new single-brace occurrences.

2. **`next/image` does NOT forward refs.** Attaching a `ref` directly to `<Image>` crashes at runtime. The fix is always: wrap in `<div ref={...}>` and animate the wrapper. This is in the prompt template, but worth knowing.

3. **`ScrollTrigger.normalizeScroll` and `.config` MUST be inside `useEffect`.** Module-level call = Next.js SSR crash. Eval check `scroll_trigger_ssr_safe` catches this.

4. **`gsap/SplitText` is a paid Club plugin.** Never import it. The hero h1 uses `AnimatedHeading` instead (Code Pattern 1 in prompt_template).

5. **`next.config` MUST be `.mjs` with plain JS body.** Not `.ts`, not `.js`. Use `/** @type {import('next').NextConfig} */` JSDoc, never `import type`.

6. **`tsconfig.json` paths MUST be exactly `{"@/*": ["./*"]}`.** No `./src/*`. The `no_src_directory` eval enforces no `site/src/` folder.

7. **Secrets never go in chat.** The `.env` file is the secret channel. To take a new key from the user, add a labeled section to `.env` with a placeholder, link them to it, they paste and save. Pattern in use since 2026-05-14.

8. **Live engine logs are at `engine.log` / `engine.err.log` in repo root.** They're gitignored. If `python -m pytest` complains about port 8000, the engine is already running.

## Skills to invoke at specific triggers (Pebble-specific reminder system)

This project uses Claude Code skills as part of the workflow. Invoke these when their trigger fires — don't wait to be asked.

| Trigger | Skill to invoke |
|---|---|
| Before any release / before launching the SaaS | `security-review` |
| When designing a new pebble-specific helper (e.g. pebble-launch-check, pebble-customer-debug) | `skill-creator` |
| When editing code that touches the Anthropic SDK or prompt-caching | `claude-api` |
| After non-trivial edits, before commit | `simplify` |
| When the user opens a PR or asks for review | `review` |
| When user needs spreadsheets / decks / PDFs / docs (e.g. revenue projections, pitch deck) | `xlsx` / `pptx` / `pdf` / `docx` |
| Memory feels stale (~quarterly) | `consolidate-memory` |
| User reports a setting issue or wants hooks | `update-config` |

These are skills available in the session — invoke via the Skill tool. Don't propose them; just use them when the trigger matches.

## The three-tool workflow

This project runs on a triangle:

- **Claude Code** (this) — writes code, makes architecture calls, enforces quality. The builder.
- **Hermes Agent** — installed locally, Telegram-gateway, scheduled tasks (cron), capture-and-monitor. The watcher. Config keys are in `.env` (`OPENROUTER_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_CHAT_ID`).
- **NotebookLM** (via `notebooklm-mcp`) — adversarial critique, deep research, source-grounded review. The critic. Used heavily for strategic decisions; tends to overshoot for code-level questions.

See `.claude/UNSUPERVISED_SESSION_SUMMARY.md` for the full workflow patterns and `.claude/SENIOR_LEVEL_ROADMAP.md` for the strategic frame.

## Strategic context files (gitignored, but load them when relevant)

- `.claude/SENIOR_LEVEL_ROADMAP.md` — the multi-phase plan (foundation → SaaS → ops scale)
- `.claude/UNSUPERVISED_SESSION_SUMMARY.md` — most recent hand-off summary
- `.claude/OVERNIGHT_OVERHAUL_SUMMARY.md` — the May 14 foundation overhaul narrative
- User memory at `~/.claude/projects/C--Users-marci-pebble-engine/memory/` — persistent across sessions, auto-loaded
