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

# Test suite — 1981 passing as of 2026-05-21 (incl. 15 e2e HTTP tests + 21 brand-extract multipart cases)
python -m pytest -q

# Run only the e2e HTTP integration tests (boots engine in-process)
python -m pytest tests/test_http_e2e.py -q

# Run a single test file
python -m pytest tests/test_evals.py -q

# Run a single test by name
python -m pytest tests/test_evals.py::test_no_src_directory_passes_when_absent -q

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

`pebble_engine.py` (~2255 lines) is the HTTP server + build orchestrator. Most of the build pipeline has been carved out into the `pebble/` package:

- `pebble.llm` — Gemini + Anthropic clients with vision support
- `pebble.industry` — 63-industry lookup with LLM fallback for new industries, fuzzy matching, writes new entries back to `industries.json`; also exposes `PAGE_CATALOG` (11 industry-aware page types) + `build_pages_block`
- `pebble.plan` — pure-function Pebble Plan generator. `build_pebble_plan(brief, industry_intel, dna) → dict`. Emitted as `plan.json` for every build; powers the `/api/plan` preview endpoint.
- `pebble.history` — per-build snapshot store. `snapshot_site(slug, reason, source) → Path`, `list_history(slug) → list[HistoryEntry]`, `restore_snapshot(slug, snapshot_id) → int`. Every `/api/generate`, `/api/refine`, and `/api/visual-edit` snapshots before mutating. Storage: `output/<slug>/history/<YYYYMMDDTHHMMSS-reason>/site/`.
- `pebble.cost` — token + cost estimation. `estimate_cost(prompt, response, model) → CostEstimate`. Used by `/api/generate` to write `tokens_used`, `estimated_cost_usd`, and `rate_card_used` into `build_meta.json` for every paid build.
- `pebble.postbuild` — Imagen image generation, npm install, `next dev`, Playwright screenshots
- `pebble.repair` — critique-and-fix loop wired in via `PEBBLE_AUTO_REPAIR`
- `pebble.evals` — 38 FOUNDATION checks + repair-corpus harness. Recent additions (May 2026): `perf_budget_or_lighter` (CWV), `hero_cta_above_fold`, `mobile_optimized_responsive`, `schema_org_jsonld_present`, `sitemap_and_robots_present`.
- `pebble.engagement` — per-user product analytics for the Pebble APP (NOT for generated sites — that's pebble.analytics). Records {event, timestamp} only — never content. Powers /api/admin/engagement. See module docstring for the privacy moat that distinguishes it from the `no_tracking_by_default` eval.
- `pebble.storage` — Supabase Storage uploads for form attachments. Magic-byte validation, MIME allowlist, per-IP + per-project quotas.
- `pebble.forms_webhook` + `pebble.forms_autoresponder` — outbound webhook delivery + auto-reply email on form submission. Per-project config, per-recipient throttle.
- `pebble.publish` — Cloudflare Pages publish flow. `pebble.domain` — custom domain mgmt.
- `pebble.email` — Resend SDK wrapper (welcome, password reset, form auto-responder).
- `pebble.security` — rate limiters, project locks, `require_project_owner`, slug validation.
- `pebble.server.build` — `/api/generate` and `/api/plan` request bodies. Snapshots site/ before overwriting.
- `pebble.server.projects` — `/api/projects` list + `/api/projects/<slug>/{history,star,claim}` + `/api/rollback` + DELETE. `claim` migrates anon builds onto the caller's user account (cheat-sheet inverted-onboarding pattern).
- `pebble.server.refine` — `/api/refine`. Two refinement classes:
  - **Deterministic** (`billable: false`): `simpler` (regex palette tone-down), `colors` (rotates 5 brand-safe palettes). No LLM call. Milliseconds.
  - **LLM-backed** (`billable: true`): `friendlier`, `professional`, `booking`. Single focused LLM turn.
  Every refinement snapshots first.
- `pebble.server.visual_edit` — `/api/visual-edit` for click-to-edit on the preview iframe. Three deterministic ops: `text`, `color`, `font-size`. **All billable: false** — the whole point is letting users tweak presentation without spending credits. Module also exports `PEBBLE_VISUAL_EDIT_BRIDGE` — a JS payload the preview server injects into every `/preview/<slug>/` HTML response, providing hover-outline + click-select + postMessage of element metadata to the parent workspace.
- `pebble.server.blocks` — `/api/blocks` (catalog) + `/api/projects/<slug>/blocks/insert`. DNA-themed drop-in sections (testimonials, pricing, FAQ, etc.). Billable: false.
- `pebble.server.admin` — admin-only diagnostics (users, projects, errors, engagement). Gated by `PEBBLE_ADMIN_EMAIL` allow-list.
- `pebble.server.auth` — legacy homegrown auth (deprecated as of Phase A.5, sunset 2026-11-16). Headers emit `Deprecation: true`. Set `PEBBLE_LEGACY_AUTH_DISABLED=true` to flip to 410.

`/api/generate` runs this sequence for each build:

```
quiz → slug + brief
  → design-system search (BM25 over CSV in skills/ui-ux-pro-max/data)
  → industry intelligence (industries.json → LLM fallback → cache)
  → hero imagery (Pexels photos + Pexels Video API)
  → Style DNA pick (industry-weighted via `style_dna.pick_dna_for_brief` — 13 cards with `industry_affinity` 15× boost + `industry_aversion` hard-exclude; pinned `_design_dna_id` overrides)
  → anti-slop audit (CONVERGENCE_FONTS, ACCEPTABLE_DISPLAY_PAIRS, WATCH_STYLES)
  → PROMPT.md assembled from skills/prompt_template.md
  → plan.json emitted alongside brief.json (Pebble Plan = 7-field user-facing summary)
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

9. **iOS Safari needs `100dvh`, not `100vh`.** iOS includes the URL bar in `100vh` and the page jumps when the bar collapses. Use the `.h-screen-safe` / `.min-h-screen-safe` utilities defined in `app/globals.css` (they fall back to `100vh` on iOS < 15.4). Phase 41 hardening: viewport meta has `viewport-fit=cover`, tap-highlight is killed globally, mobile menu has `.pb-safe` for the home-indicator. Don't add raw `h-screen` to new landing components — use the safe variants. **To test from a real iPhone on the same WiFi: `cd ui/v3 && npm run dev:mobile` (binds Next dev to 0.0.0.0). Then open `http://<your-LAN-IP>:3001/` on the phone — `ipconfig` (Windows) or `ifconfig` (Mac) prints the LAN IP.**

10. **Named Framer Motion variants MUST be wrapped via `withReducedMotion`.** `tests/test_motion_module_wiring.py` enforces it. If you declare a variant at module level (e.g. `const FADE_UP = {...}`), the component that imports it must call `useMemo(() => withReducedMotion(FADE_UP), [])` inside the function body. The pattern in `welcome-phase.tsx` is `_RAW` suffix on the const declarations + wrapped name in the component.

## Phase 40 + 41 landing architecture (May 2026)

The landing page (`ui/v3/components/phases/welcome-phase.tsx`, ~1645 lines) was rebuilt across Phase 40 (a → o) and Phase 41 (iOS hardening). Key components, all in `ui/v3/components/hero/`:

- **`landing-nav.tsx`** — sticky pill, shrinks on scroll past 10px, mobile menu via `Menu`/`X` icons with body scroll-lock + `pb-safe` for iPhone home-indicator. Brand mark + nav links + Sign In + Get Started all in Plus Jakarta Sans (one professional typeface end-to-end).
- **`shuffle-grid.tsx`** — hero backdrop, 4×4 grid of 16 real Pebble template PNGs from `public/templates-preview/`. Reshuffles every 3s (6s on screens ≤640px to spare low-end iPhones). Hydration-safe (deterministic initial state, first shuffle in `useEffect`).
- **`detective-input.tsx`** — the search bar / "six-pack" input. Row 1 is the input only (pure white `bg-white`, full-width for typewriter cycle). Row 2 is the action toolbar: mic (Web Speech API, auto-hidden on Firefox), paperclip (≤5 image uploads, multipart-posted to `/api/brand-extract`), Plan toggle (stamps `brief.planFirst`), Build button (glows when unlocked). Typewriter placeholder has a permanent "Hey Pebble! Build " prefix; only the body suffix types/erases. Rotating clickable suggestion pill below.
- **`swiper-steps.tsx`** — §2 "From sentence to site" horizontal swiper, replaces the old `StickyScrollStack`.
- **Sticky-scroll §3-§7** — each marketing section (DNA showcase, Perfect for, Testimonial, Pricing, Final CTA) is a tall outer with a `sticky top-0 h-screen-safe` inner. `useStickySection` hook reads `scrollYProgress` and applies a reveal curve (enter 0→0.25, dwell 0.25→0.75, exit 0.75→1).

The retired `BackgroundCarousel` + `StickyScrollStack` files are kept on disk for fast revert but not imported by the active path.

Plan-first flow: when `brief.planFirst === true`, `workspace-shell.tsx`'s `handleAdvanceFromWelcome` skips the idea questionnaire and routes directly to the existing `PlanPhase` (calls `/api/plan` cheap preview). Back button reads "Change my mind" and returns to welcome.

Brand-extract image ingestion: `pebble/server/brand_extract.py` accepts `multipart/form-data` with `images[]` (≤5 images, ≤10MB each, ≤60MB total, MIME allowlist + magic-byte check). `pebble/brand_extract.py` `extract_brand()` takes optional `inspiration_images: list[bytes]` and forwards them to the LLM via vision message blocks (Anthropic + Gemini both supported).

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

See `.claude/SENIOR_LEVEL_ROADMAP.md` for the strategic frame and the per-session memory files in `~/.claude/projects/C--Users-marci-pebble-engine/memory/project_2026-05-*.md` for the rolling hand-off log.

## Strategic context files

- `PROJECT_PLAN.md` (repo root, committed) — chapter-by-chapter shipping plan with ✓/[ ] per item. The living source of truth for "what's shipped vs. open."
- `.claude/SENIOR_LEVEL_ROADMAP.md` (gitignored) — positioning frame vs. Base44/Lovable; differentiators by axis. Synthesized from a 61-source NotebookLM run.
- User memory at `~/.claude/projects/C--Users-marci-pebble-engine/memory/` — persistent across sessions, auto-loaded. Per-session `project_2026-05-*.md` files are the rolling hand-off log.

## Product direction (May 2026 Codex-assisted spec)

The current engine is the back-end seed for a much larger app experience described in `project_pebble_product_vision.md` (user memory). High-level:

- **Audience:** universal design — anyone building a website or small business app. *Never* framed as "for seniors" or "50+", even though older users benefit. See `feedback_universal_design_not_senior.md`.
- **Product principle:** "Everything explained. Everything connected. Everything editable later."
- **Five future modes:** Guided (one Q at a time) · Chat (plain-language edits) · Design (click-to-edit preview) · Setup (domains/hosting/email/payments/SEO) · Learn (jargon explained inline). Today only the Guided questionnaire prototype exists, served by the v3 Next.js frontend at localhost:3000 (proxied to the engine at localhost:8000).
- **Pebble Plan:** the 7-field user-facing "here's what I'll build" summary now emitted as `plan.json` for every build — see `pebble/plan.py` and the `/api/plan` preview endpoint.
- **Honest "Launch Setup" checklist:** the Plan's `setup_needs` field lists all 14 spec items, but with `status: "auto" | "pending" | "manual"` so the UI doesn't over-promise. Only flip `pending → auto` when the underlying infra actually ships. Each item also declares `dependencies: [<other_id>]` edges so the UI renders the chain (`publish` unlocks after `hosting + pages + seo_basics`); cycles are guarded by `tests/test_plan_setup_dependencies.py`.

## HTTP API reference (2026-05-17)

All routes return JSON unless noted. Errors use `{ "error": "..." }` with appropriate HTTP status. Owner-gated routes require a Supabase session cookie + project ownership (or unclaimed project). Admin routes require an email in `PEBBLE_ADMIN_EMAIL`.

### Build pipeline

| Method | Path | Body / Query | Purpose |
|---|---|---|---|
| GET | `/api/health` | — | Engine + LLM readiness |
| GET | `/api/industries` | — | List industries.json entries for the typeahead |
| POST | `/api/plan` | brief JSON | Compute Pebble Plan WITHOUT running LLM (cheap preview) |
| POST | `/api/build` | brief JSON | Render prompt only; no generation |
| POST | `/api/generate` | brief JSON | Full build. Snapshots site/ first. Writes `build_meta.json` with `billable:true`, `tokens_used`, `estimated_cost_usd`, `rate_card_used`. |
| POST | `/api/migrate` | `{ slug, brief }` | Re-stamp an existing project with a fresh brief (no re-generate). |
| POST | `/api/inspire` | `{ industry }` | Surface industry-relevant Dribbble references. |

### Project management (owner-gated)

| Method | Path | Body / Query | Purpose |
|---|---|---|---|
| GET | `/api/projects` | — | **List every project for the dashboard** — slug, name, type, file_count, starred, built_at |
| GET | `/api/projects/<slug>/history` | — | List snapshots, newest-first — for the workspace history drawer |
| GET | `/api/projects/<slug>/analytics` | — | Page-view summary for the customer's generated site (7d window). |
| POST | `/api/rollback` | `{ slug, snapshot_id }` | Restore a previous snapshot. Pre-rollback state is also snapshotted (undoable). |
| POST | `/api/projects/<slug>/star` | `{ starred?: bool }` | Toggle (or set) the `.starred` sentinel file. |
| POST | `/api/projects/<slug>/claim` | — | Migrate an anonymous build onto the caller's user account (stamps `_user_id` atomically). 401 unauthed, 404 missing, 403 owned-by-other, 200 unowned or self-owned (idempotent). |
| DELETE | `/api/projects/<slug>` | — | Permanent hard-delete (no trash). Frontend should confirm. |
| POST | `/api/publish` | `{ slug }` | Deploy to Cloudflare Pages. |
| GET / POST | `/api/projects/<slug>/domain` | domain JSON | Custom domain management. |

### Editing

| Method | Path | Body / Query | Purpose |
|---|---|---|---|
| POST | `/api/refine` | `{ slug, refinement_id }` | Apply a refinement to an existing build. `billable: false` for `simpler`/`colors`, `billable: true` for `friendlier`/`professional`/`booking`. Always snapshots first. |
| POST | `/api/visual-edit` | `{ slug, op, ... }` | Click-to-edit from the preview iframe. Ops: `text`, `color`, `font-size`. **Always `billable: false`.** |
| GET | `/api/blocks` | — | List the DNA-themed block catalog (testimonials, pricing, FAQ, etc.). Public. |
| POST | `/api/projects/<slug>/blocks/insert` | `{ block_id }` | Insert one block into the site. Snapshots first. `billable: false`. |

### Inbox / forms (public submit + owner-gated config)

| Method | Path | Body / Query | Purpose |
|---|---|---|---|
| POST | `/api/forms/<slug>` | form JSON | Public form submit. Fires webhook + auto-responder asynchronously after 200. |
| POST | `/api/forms/<slug>/upload` | `{ filename, content_type, data: base64 }` | Public attachment upload to Supabase Storage. MIME allowlist + magic-byte validation + per-IP/per-project quotas. |
| GET / POST / DELETE | `/api/projects/<slug>/forms/webhook` | webhook config | Owner-gated outbound webhook URL config. |
| GET / POST / DELETE | `/api/projects/<slug>/forms/autoresponder` | autoresponder config | Owner-gated reply-email config. |
| POST | `/api/track/<slug>` | `{ path?, referrer? }` | Public page-view tracker for the customer's generated site. |

### Auth + account

| Method | Path | Body / Query | Purpose |
|---|---|---|---|
| GET | `/api/auth/me` | — | Resolve current session → user. |
| POST | `/api/auth/{signup,login,logout,forgot,reset}` | varies | **Deprecated** (Phase A.5, sunset 2026-11-16). v3 uses Supabase Auth directly. Headers emit `Deprecation: true`. |
| POST | `/api/account/delete` | `{ email_confirmation }` | GDPR account delete — drops Supabase user + scrubs project ownership. |
| POST | `/api/internal/supabase-webhook` | Supabase webhook payload | Welcome-email trigger on email verification. HMAC-signed. |

### Billing (Stripe)

| Method | Path | Body | Purpose |
|---|---|---|---|
| POST | `/api/checkout/create-session` | `{ plan: "starter" \| "pro" \| "setup_call" }` | Auth-gated (Bearer JWT). `starter`/`pro` → `mode=subscription`, returns `{url, session_id}`. `setup_call` → `mode=payment` ($99 one-time), success redirects to `PEBBLE_SETUP_CALL_LINK` (calendar). Stamps `pebble_user_id` + `pebble_plan` metadata so the webhook can route events back. |
| POST | `/api/billing/portal` | — | Auth-gated. Reads `stripe_customer_id` from `output/.users/<uid>/subscription.json`, mints a Stripe Customer Portal session, returns `{url}`. 404 if no subscription. |
| POST | `/api/internal/stripe-webhook` | Stripe event payload | HMAC-verified via `STRIPE_WEBHOOK_SECRET`. On `customer.subscription.{created,updated,deleted}` writes `output/.users/<uid>/subscription.json` with `{status, plan, stripe_customer_id, stripe_subscription_id, current_period_end, updated_at}`. Other event types 200-ignored. |

Env vars (all in `.env`): `STRIPE_SECRET_KEY` (sk_test_), `STRIPE_PUBLISHABLE_KEY` (pk_test_, v3-side only), `STRIPE_WEBHOOK_SECRET` (whsec_, from `stripe listen` or Dashboard), `PEBBLE_STRIPE_STARTER_PRICE_ID`, `PEBBLE_STRIPE_PRO_PRICE_ID`. Bootstrap the two price IDs once via `python -m pebble.stripe_bootstrap`.

### Admin (gated by `PEBBLE_ADMIN_EMAIL`)

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/admin/users` | All users + project counts |
| GET | `/api/admin/projects` | All projects + owner email + publish state |
| GET | `/api/admin/errors` | Tail of engine.err.log filtered to ERROR/WARN lines |
| GET | `/api/admin/engagement` | Per-user engagement buckets (power/active/at-risk) |

### Serving

| Method | Path | Purpose |
|---|---|---|
| GET | `/preview/<slug>/` | Serve generated site files. **HTML responses get the visual-edit bridge auto-injected before `</body>`** so the click-to-edit flow works without the generated site knowing about it. |
| GET | `/dist/` | Serve pre-built static assets (used by the v3 frontend in production). |
| GET | `/` | Plaintext liveness landing — engine is backend-only, points users to the v3 frontend at port 3000. |

The v3 Next.js frontend at `ui/v3/` proxies `/api/*` and `/preview/*` to the engine via `next.config.ts` rewrites; in dev, run v3 on port 3001 because port 3000 is Marc's pebbleapp.ai dev server.
