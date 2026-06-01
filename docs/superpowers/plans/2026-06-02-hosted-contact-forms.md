# Hosted Contact Forms for Published Static Sites — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Make a non-technical user's contact form actually deliver email after they publish — with NO Resend key and NO `.env` file on their side — by routing the generated static site's form to Pebble's existing `POST /api/forms/<slug>` endpoint instead of a self-hosted Next.js Server Action that can't run on a static Cloudflare Pages deploy.

**Why (decided 2026-06-01):** Verified the Cloudflare publish path deploys a STATIC artifact (`pebble/publish.py:307-334`). The current generated contact form is a Next.js Server Action (`skills/prompt_template.md` Code Pattern 8) which has no runtime on a static deploy. Pebble already runs `POST /api/forms/<slug>` (public; webhook delivery + autoresponder via Pebble's own Resend key — `pebble/server/forms.py`). Routing the static form there removes the `.env` wall entirely and reuses built infra.

**Architecture:** Add a **published-mode** contact form variant. When a site is published as a static artifact, its `ContactForm` does a plain `fetch()` POST to `<ENGINE_URL>/api/forms/<slug>` (the engine resolves the project owner's plan, sends via Pebble Resend, fires webhook + autoresponder). The Server-Action variant stays for local `next dev`/Vercel users. The published site must carry two values: its `slug` and the engine base URL — baked in at publish time via a generated `lib/pebble-config.ts` (or `NEXT_PUBLIC_*` inlined into the static build).

**Tech Stack:** Python engine (publish + prompt template), Next.js 14 generated sites, the existing `pebble/server/forms.py` endpoint, pytest + eval suite.

---

## Open questions to resolve at task 0 (verify before building)

- [ ] **Q1 — How does the published static site learn its slug + engine URL?** Options: (a) `pebble/publish.py` writes a `public/pebble-config.json` (or `lib/pebble-config.ts`) into the artifact at publish time; (b) inline `NEXT_PUBLIC_PEBBLE_ENGINE_URL` + slug at build. Confirm the static export reads runtime `public/*.json` via `fetch("/pebble-config.json")` OR a build-time constant. (Static export inlines `NEXT_PUBLIC_*` at build, so if publish runs a build, prefer that; if publish uploads pre-built `out/`, prefer the `public/pebble-config.json` fetch.)
- [ ] **Q2 — CORS.** `POST /api/forms/<slug>` must accept cross-origin POSTs from the published domain (`<slug>.pages.dev` / custom domain). Check `route_options` + `_cors_decision` in `pebble/server/router.py` — forms submit is public, so confirm the CORS allowlist permits it or add the published-site origins.
- [ ] **Q3 — Eval impact.** `contact_form_uses_server_action` (pebble/evals/checks.py) currently REQUIRES the Server Action. A published-mode form would fail it. Decide: keep Server Action as the GENERATED default (eval unchanged) and only SWAP to fetch-mode at publish time (so the eval still passes on the pre-publish build), OR add a published-mode eval. Recommendation: swap at publish so the dev-mode build keeps the Server Action + eval green.

---

## Task 1: Engine writes a published-site config into the artifact

**Files:**
- Modify: `pebble/publish.py` (in `publish_to_cloudflare`, before hashing/upload, write `public/pebble-config.json` into the artifact source_dir)
- Test: `tests/test_publish.py` (extend)

- [ ] **Step 1: Write the failing test** — assert that after `publish_to_cloudflare` prepares the artifact, `public/pebble-config.json` exists in the uploaded set with `{"slug": "<slug>", "engineUrl": "<env>"}`. (Mock the CF HTTP calls; assert the file was staged.)
- [ ] **Step 2:** Run it; expect FAIL (no config written).
- [ ] **Step 3:** Implement — derive `engine_url` from `PEBBLE_PUBLIC_ENGINE_URL` env (fall back to the request host), write `public/pebble-config.json` into `source_dir` before the hash pass. Never write secrets — only slug + public engine URL.
- [ ] **Step 4:** Run; expect PASS.
- [ ] **Step 5:** Commit.

## Task 2: Prompt template — publish-aware ContactForm

**Files:**
- Modify: `skills/prompt_template.md` (Code Pattern 8 — add the fetch-to-`/api/forms/<slug>` path)
- Modify: `pebble/evals/checks.py` if Q3 chooses an eval change (default: no change — swap happens at publish)

- [ ] **Step 1:** Decide per Q3. If swapping at publish (recommended), the generated ContactForm stays a Server Action; ADD a small client helper that, when `window` + `/pebble-config.json` is present (published mode), POSTs to the engine instead. Spell out the exact TSX in the template (doubled braces for `str.format()` — see CLAUDE.md hard-rule #1).
- [ ] **Step 2:** Run the smoke tests (`tests/test_smoke.py`) — the template must still render (brace-balance) and the eval suite must stay green.
- [ ] **Step 3:** Commit.

## Task 3: Publish-time form rewrite (if swapping at publish)

**Files:**
- Modify: `pebble/publish.py` (a `_rewrite_contact_form_for_static(source_dir)` step that points the form at `/api/forms/<slug>` when building the static artifact)
- Test: `tests/test_publish.py`

- [ ] **Step 1:** Failing test — after publish prep, the artifact's ContactForm references `fetch(`...`/api/forms/` not a Server Action import.
- [ ] **Step 2:** FAIL.
- [ ] **Step 3:** Implement the rewrite (string-level, guarded; skip if already fetch-mode).
- [ ] **Step 4:** PASS.
- [ ] **Step 5:** Commit.

## Task 4: CORS + end-to-end verification

- [ ] **Step 1:** Per Q2, ensure `POST /api/forms/<slug>` returns CORS headers for the published origin. Add a test in `tests/test_forms.py` asserting an `Origin: https://<slug>.pages.dev` POST is accepted.
- [ ] **Step 2:** Manual E2E: publish a test build, submit the live form, confirm the email arrives + webhook/autoresponder fire. Document the result.
- [ ] **Step 3:** Commit.

---

## Self-Review
- Goal (form works post-publish, no user .env) → Tasks 1-4 ✓
- Premise correction (static deploy) is the entire rationale ✓
- Q1/Q2/Q3 are explicit verify-first gates, not placeholders — they MUST be answered at task 0 because they change the implementation shape ✓
- Keeps the Server Action + its eval green for dev/Vercel users; only published static builds get rewritten ✓
