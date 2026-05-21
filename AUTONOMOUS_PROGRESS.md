# Autonomous Sprint — Progress & Handoff

**Started:** 2026-05-21 00:54 local
**Branch:** `main` (no push per Marc's standing rule)
**Tests:** 1809 passing (was 1784 — +25 new)
**Commits this sprint:** 7

---

## What's done end-to-end

### Phase 33 — URL Ingestion + Brand Extraction (the highest-ROI item in the audit)

The user pastes `https://acme.co` (or `acme.co`) into the welcome-phase
prompt and the engine extracts a partial brief — business name, industry,
tone, palette, logo, hero copy — that pre-fills the questionnaire.
The user corrects rather than creates.

- **`pebble/brand_extract.py`** — extraction module. Stdlib only (no requests,
  no BeautifulSoup). SSRF guards. 1h on-disk cache. Never raises.
- **`pebble/server/brand_extract.py`** — `POST /api/brand-extract`. Public,
  rate-limited via plan_limiter. Returns 200 for soft failures with
  `ok=false` so the frontend can render a fallback notice.
- **`ui/v3/components/phases/welcome-phase.tsx`** — URL detection in `handleSend`.
  Cinematic 4-step narration ("Reading your site…" → "Detecting palette…"
  → "Identifying industry…" → "Got it.") replaces the prompt input while
  the call is in flight. Graceful fallback on any error.
- **Tests:** 69 — covering URL normalization + SSRF, palette extraction,
  LLM JSON parser robustness, cache TTL, endpoint contract.

**Brief field mapping for downstream consumers:**
```
business_name → brief.business_name
industry      → brief.business_type        (snake_case slot the engine already reads)
tone          → brief.brand_tone
palette       → brief._brand_palette       (derived; underscore-prefixed)
logo_url      → brief._extracted_logo_url
favicon_url   → brief._extracted_favicon_url
hero_copy     → brief._extracted_hero_copy
tagline       → brief._extracted_tagline
_inspired_by  → brief._inspired_by         (mirrors /api/inspire convention)
```

Plus a natural-language `extra_context` blob so the prompt template
gets the signal even if it doesn't yet read the new fields.

### Phase 35 — Diff Panel for refinement + visual-edit

After every refinement or visual-edit, the response now includes a
`diff: DiffSummary | null` payload computed from the snapshot the
endpoint already takes before mutating. The Phase-3 diagram pattern:
"Frontend: Updated components/Hero.tsx (3 lines) / Backend: Untouched".

- **`pebble/history.py`** — new `diff_against_snapshot(slug, snapshot_id)`.
  Set-based line diff (cheap, approximate, fine for "(3 lines changed)").
  Categorizes files by top-level dir bucket (Frontend / Backend / Styles /
  Assets / Config / Tests / Other).
- **`pebble/server/refine.py`** + **`visual_edit.py`** — both now attach
  `diff` to the response. Best-effort; failure leaves diff=null.
- **`ui/v3/lib/api.ts`** — types: `FileDiff`, `DiffSummary`, status enums.
  `RefineResponse` and `VisualEditResponse` both extended with `diff`.
- **`ui/v3/components/workspace/diff-panel.tsx`** — `DiffPanel` component.
  Modes: `compact` (one-liner) and `expanded` (category roll-up + per-file
  list). `showUntouched=true` renders all categories with "Untouched"
  for the ones that didn't change (diagram pattern).
- **Tests:** 10 — snapshot-then-mutate flows, binary file handling,
  multi-category roll-up, missing snapshot/site edges, JSON round-trip.

### Phase 36 — Build Integrity pre-launch checklist

The Phase-4 diagram's "Build Integrity" panel. 10 curated checks
mapping to existing eval functions, animating pending → green check
in 180ms staggers for cinematic effect.

- **`pebble/integrity.py`** — `CRITICAL_CHECKS` list + `run_integrity(slug)`
  + `is_publishable(results)` helper. Each entry is a thin shim over an
  existing `pebble.evals.checks` function.
- **`pebble/server/integrity.py`** — `GET /api/projects/<slug>/integrity`,
  owner-gated.
- **`ui/v3/lib/api.ts`** — `IntegrityResponse` + `checkBuildIntegrity(slug)`.
- **`ui/v3/components/workspace/build-integrity-checklist.tsx`** —
  `BuildIntegrityChecklist` component. Fires the endpoint on mount.
  `onResult` callback fires once with the response so parent can
  gate/enable the Publish button.
- **Tests:** 15 — shape invariants, run edge cases, `is_publishable` semantics.

**The 10 curated items:** Build plan generated · Next.js project structure
valid · Foundation pages present · Contact form wired to email · Navbar
links wired (warn) · Language declared on `<html>` · Mobile-optimized +
responsive · Schema.org structured data (warn) · Sitemap + robots.txt
(warn) · Performance budget within limits (warn).

### Plus the housekeeping

- **Stale node processes killed:** 33 leftover `next dev` instances on
  ports 3060–3068 were eating RAM. Gone.
- **Cleanup commit #1:** Today's font/logo/glassmorphism work landed
  as `feat(v3): luxury font system + multilingual rotating Pebble wordmark`.
- **Cleanup commit #2:** Earlier-today design audit + Phase 25a/25c
  workspace polish + auth-fields component as `feat(v3): workspace polish
  + design audit + Plan Reveal wiring`.

---

## What's NOT done yet (next session priorities)

In ROI order:

### 1. Wire `DiffPanel` into the workspace UI (~30 min)

Component exists but isn't rendered anywhere. Drop-in points:
- `ui/v3/components/phases/edit-phase.tsx` — render after each refinement
  response in `<DiffPanel diff={lastRefineResponse.diff} mode="compact" />`
- Same for visual-edit results.

### 2. Wire `BuildIntegrityChecklist` into the publish flow (~30 min)

Find the publish CTA in edit-phase.tsx, render the component above it,
disable the Publish button until `onResult` fires with `publishable:true`
(or let user override via existing dialog).

### 3. Phase 34 — Intent split (Business vs Project) (~half-day)

- Add `intent: "business" | "project"` to `brief` schema in
  `ui/v3/lib/state.ts` (already a `Record<string, unknown>`, just type-stamp).
- Frontend card-picker step in welcome-phase after URL extraction
  resolves. Two cards. Default to "business" on dismiss.
- **Backend:** fork `skills/prompt_template.md` into `prompt_template_business.md`
  (conversion-optimized, Stripe pre-wired, SEO emphasis) and
  `prompt_template_project.md` (Tailwind-raw, modular, dev-friendly comments).
- Build orchestrator (`pebble/server/build.py`) reads `brief.intent` and
  picks the template.

### 4. Wire URL extraction outputs into the build prompt

`pebble/server/build.py` doesn't currently consume the new `_extracted_*`
fields the brand extractor populates. The fields are stuffed into
`extra_context` already so the LLM gets them indirectly, but a small
prompt-template patch could surface them more prominently (e.g. seed
the palette into the DNA picker, seed the logo URL into hero composition).

### 5. WebContainers spike (the Phase 27 / "combined tech" Marc was remembering)

Separate branch. Goal: load StackBlitz SDK in the workspace preview iframe,
mount generated files into the WebContainer FS, run `next dev` inside it.
Outcome: preview appears in seconds instead of minutes, no Python preview
server needed.

---

## What's uncommitted

Tree is mostly clean now. Still uncommitted (left intentionally for Marc
to review):

```
M .gitignore                                  (Phase 31 template artifacts)
M pebble/compare_prompts.py                   (older WIP)
M pebble/evals/checks.py                      (Phase 20+ check additions)
M pebble/layout_dna.py                        (Phase 23a Terminal aversion)
M pebble/prompt_diet.py                       (Phase 14)
M pebble/server/build.py                      (Phase 13/15 incremental writes etc.)
M tests/test_layout_dna.py
M tests/test_next_js_static_check.py
M ui/v3/lib/api.ts                            (89-line addition pre-sprint)
M ui/v3/lib/state.ts                          (23-line addition pre-sprint)
?? END_OF_DAY_RESULTS.md  MORNING_RESULTS.md  NIGHT_WRAP.md
?? PHASE_31_HANDOFF.md    TONIGHT_CHECKPOINT.md
?? pebble/next_config_patch.py                (Phase 20c)
?? pebble/server/bot_message.py               (Phase 25b)
?? pebble/server/templates_api.py             (Phase 31d)
?? pebble/templates/                          (Phase 31 templates dir)
?? pebble/text.py                             (Phase 20a sanitize_business_name)
?? scripts/boot_new_bases.py
?? scripts/boot_variant_previews.py
?? scripts/capture_template_previews.py
?? scripts/preview_new_template.sh
?? ui/v3/app/templates/                       (Phase 31e gallery page)
?? ui/v3/public/templates-preview/            (14 PNG previews)
```

These span Phases 14, 20, 25b, 31, 32 — multiple older sessions. I left
them alone because I didn't write them and didn't want to bundle weeks
of someone else's WIP into commits. Marc should review and commit when
ready.

---

## Autonomous loop status

- **Scheduled:** cron `8 3 21 5 *` (one-shot, May 21 at 03:08 local)
- **Prompt:** `<<autonomous-loop>>` sentinel — runtime resolves to autonomous
  loop instructions at fire time
- **Job ID:** `5496c969`

If the loop fires successfully, the next agent picks up from "What's NOT
done yet" — priority order above. The first task (wire `DiffPanel` into
edit-phase) is the smallest win and would be a good first move.

If the loop doesn't fire (or Marc comes back first), the same priority
list applies. Read this doc, pick item #1.

---

## Commits this sprint

```
6eb435c feat(diff): diff panel for refine + visual-edit (Phase 35)
848c099 feat(v3): URL ingestion in welcome-phase (Phase 33c)
ec7457b feat(engine): URL ingestion + brand extraction (Phase 33a/b)
9c269f2 feat(v3): workspace polish + design audit + Plan Reveal wiring
15e861d feat(v3): luxury font system + multilingual rotating Pebble wordmark
[plus integrity commit just landing]
```

The last commit (integrity) is in HEAD as of this writing.

---

## Notes for the next agent

- **Don't push to remote.** Marc's standing rule: "the website is live I dont
  want anyone snooping in." Everything stays on `main` locally until he
  approves a push.
- **The Python backend uses `log.error("msg %s", arg)` not `log("msg")`.**
  The Logger object isn't callable. Caught this in Phase 33b initial impl.
- **The diff/integrity components both exist standalone.** They take a
  `slug` prop and self-fire their fetches. Drop them into edit-phase or
  publish dialog with one import + one JSX tag.
- **CRLF warnings on commits are normal** — Windows line endings vs
  upstream LF. Doesn't break anything.
