# Self-prompt — Speed + live preview sprint (next plan)

Use this as the opening prompt for the next Cursor/Claude session after onboarding funnel ships.

---

## Context

Pebble Engine (`pebble-engine`) is pivoting to hosted SaaS for non-technical SMB owners. The v3 Next.js frontend (`ui/v3/`) proxies to a Python engine on `:8000`. Recent work (2026-06-12) shipped:

- Hidden **brief infer** (`POST /api/brief-infer`) + **brief compose** (`POST /api/brief-compose`)
- **Micro-confirm** phase (`confirm-brief-phase.tsx`) — user never sees AI rewrite
- **Plan required until 2 completed builds** (`GET /api/onboarding/status`)
- Funnel: `welcome → confirm → plan → generate → draft → ready → design`
- Template-match modal demoted when user arrives with a prompt

Verification gate: `python scripts/verify_all.py --ci` must PASS before claiming done.

## Goal

Close the **perceived speed gap** vs Lovable, Base44, and Google Stitch. Users should feel progress within seconds of submitting a prompt — not stare at a blank wait during Plan or generate.

Marc's product constraints:
- Prompt enrichment stays **hidden** (compose already runs during Plan — don't surface it)
- Signup-before-build stays for beta
- Universal design — never "for seniors"
- iOS-safe viewport utilities (`h-screen-safe`) on new UI

---

## Live three-way comparison (REQUIRED — do with Marc hand-in-hand)

Every speed sprint session must include at least **one live run on all three products with the same prompt**, timed and recorded. Marc will watch three browser windows side-by-side while the agent works Pebble and documents Lovable + Base44 in parallel.

### Where Marc watches (three windows)

| Product | URL | Notes |
|---------|-----|--------|
| **Pebble (new funnel)** | **http://localhost:3001/** (or the port `npm run dev` prints) | Onboarding funnel ships in repo first — **use local dev until deployed**. Requires engine + frontend both running (see below). |
| **Pebble (prod baseline)** | **https://www.pebbleapp.ai/** | Compare only after deploy; prod may lag local until Marc pushes. |
| **Lovable** | **https://lovable.dev/** → dashboard prompt | Marc is authenticated. Flow: prompt → editor with live iframe on right. |
| **Base44** | **https://app.base44.com/** | Marc is authenticated. Flow: prompt → `/plan?id=…` questionnaire → build. |

**Pebble local setup (Marc + agent both need this):**

```bash
# Terminal 1 — engine :8000
python pebble_engine.py

# Terminal 2 — v3 frontend (proxies /api/* and /preview/* to :8000)
cd ui/v3 && npm run dev
```

Open **http://localhost:3001/** — landing with DetectiveInput → confirm → plan → generate. Health check: `curl -s http://127.0.0.1:8000/api/health`.

**Where Marc sees the agent work on Pebble:**
- **His browser:** same `localhost:3001` URL — he drives or mirrors what the agent does.
- **Cursor browser panel:** agent uses `cursor-ide-browser` MCP (`browser_navigate`, `browser_snapshot`, screenshots) on `localhost:3001`; Marc can follow in Glass if browser tools are visible, or match steps in his own window.
- **Terminal output:** engine logs at `engine.log` / SSE events during generate.

**Suggested screen layout for Marc:** three windows tiled (Pebble left, Lovable center, Base44 right) or three monitors. Use the **same stopwatch** (phone or https://www.online-stopwatch.com/) started on each product's **Send/Build** click.

### Standard test prompts (rotate across runs)

Use one prompt per comparison session; write it in `docs/SPEED_BENCHMARK.md`:

1. **SMB default:** `I own a bakery in Brooklyn — need a site where locals can find us and get in touch.`
2. **Service + booking:** `Mobile dog grooming in Austin, want bookings and a price list.`
3. **Minimal:** `Coffee shop website for my neighborhood cafe.`

All three products get the **identical string** (paste, don't rephrase).

### Timestamps to capture (per product)

| Milestone | Pebble | Lovable | Base44 |
|-----------|--------|---------|--------|
| T0 | Click Build on landing | Click Send on dashboard | Click Send on home |
| T1 | Confirm screen visible | Editor opens | Plan questionnaire visible |
| T2 | Plan card visible | First preview pixel in iframe | Plan complete / build starts |
| T3 | Draft/SSE first event | Site feels "usable" | Preview/editor usable |
| T4 | Preview iframe first pixel | — | — |
| T5 | Ready / Open editor | — | — |

Agent records wall-clock seconds (T1−T0, T2−T0, …) in a table. Take **screenshots at T1, T2, T4** for each product (`browser_take_screenshot` or Marc manual).

### Live test on Pebble (mandatory acceptance)

Before claiming the speed sprint done:

1. Run full funnel locally with standard prompt #1 while Marc watches.
2. Confirm: confirm phase shows inferred bakery/Brooklyn **without AI language**; Plan appears (if `builds_completed < 2`); generate streams; preview loads in design phase.
3. Re-run after any speed UX change; delta must be logged in `docs/SPEED_BENCHMARK.md`.
4. If iframe preview fails locally, check `curl -s http://127.0.0.1:8000/api/health` and engine.err.log — do not skip the live test.

### Comparison write-up template

Add to `docs/SPEED_BENCHMARK.md` after each session:

```markdown
## Live run — YYYY-MM-DD — prompt: "…"

| Milestone | Pebble (local) | Lovable | Base44 |
|-----------|----------------|---------|--------|
| T1 … | Xs | Xs | Xs |
| … | | | |

**Winner this run:** …
**Pebble gap:** …
**Ship next:** …
```

---

## Research tasks (do first)

1. **Live three-way run** (see above) with Marc — baseline timings before coding.
2. Time the current Pebble funnel locally: prompt → confirm → plan fetch → generate-stream first SSE event → iframe preview ready. Record p50 targets.
3. Read competitors' UX patterns from the live run + [`docs/competitor-audit-2026-05-14.md`](docs/competitor-audit-2026-05-14.md).
4. Inventory existing Pebble assets: `DraftPhase` SSE events, `/preview/<slug>/` on-demand starter, `pebble/postbuild.py` dev server + Playwright screenshots, Plan phase loading skeleton.

## Implementation directions (pick + plan)

### A. Plan-phase perceived progress (cheap, high ROI)

While `/api/plan` + hidden `brief-compose` run (~1–3s):
- Show animated "building your plan" with **deterministic wireframe skeleton** derived from infer chips (industry, goal) — not LLM-generated
- Optional: stream partial plan fields if backend can emit early (would need `/api/plan-stream` or chunked response)

### B. Generate-phase live preview (medium)

Today: `DraftPhase` shows SSE progress; preview iframe loads after build completes.

Target: show **progressive preview** as files land:
- Engine already streams SSE from `/api/generate-stream` — extend events with `preview_hint` or `file_written` for hero/layout
- Iframe loads `/preview/<slug>/` when first HTML exists (HEAD pre-warm already in `workspace-shell.tsx`)
- Consider low-res wireframe overlay until hero video poster ready

### C. Time-to-first-pixel benchmarks (required acceptance)

| Milestone | Target | How to measure |
|-----------|--------|----------------|
| Confirm screen visible | < 500ms after submit | Playwright on `ui/v3` |
| Plan card visible | < 2s | Network + render |
| First preview pixel | < 60s p50 full build | SSE timestamp vs iframe load |
| Interactive preview | < 90s p50 | Playwright |

Add `scripts/benchmark_funnel.py` or pytest marker `@pytest.mark.integration` with mocked generate.

### D. Do NOT break

- `skills/prompt_template.md` brace doubling
- Eval suite / repair loop
- Hidden compose — never show `extra_context` in UI
- Credit/paywall 402 handling
- Ownership-scoped `/api/projects`

## Suggested plan file structure

1. **Live three-way baseline** with Marc → `docs/SPEED_BENCHMARK.md`
2. Plan-phase skeleton UI (frontend only)
3. SSE preview hints (engine + frontend)
4. **Second live three-way run** after changes — same prompt, compare deltas
5. Benchmark script + CI optional job
6. `verify_all.py` PASS + handoff

## Key files to read

- `ui/v3/components/workspace-shell.tsx` — funnel, autostart, iframe pre-warm
- `ui/v3/components/phases/plan-phase.tsx`, `draft-phase.tsx`
- `pebble/server/build_stream.py` — SSE event shape
- `pebble/server/preview_serve.py`, `preview_ondemand.py`
- `docs/ONBOARDING.md`, `HANDOFF_ONBOARDING_2026-06-12.md`
- `docs/competitor-audit-2026-05-14.md` — Lovable/Base44 flow reference

## Success criteria

- [ ] **Live three-way comparison completed** (before + after) with timings in `docs/SPEED_BENCHMARK.md`
- [ ] **Live Pebble funnel test** passed locally with Marc watching (confirm → plan → generate → preview)
- [ ] User sees meaningful motion within 2s of confirming brief
- [ ] Preview iframe shows *something* before generate fully completes (even if wireframe)
- [ ] `verify_all.py --ci` PASS
- [ ] No regression to onboarding funnel tests (`tests/test_brief_infer_compose.py`)

---

**Start by:** start Pebble locally (`pebble_engine.py` + `ui/v3 npm run dev`), open three browser windows (Pebble / Lovable / Base44), run standard prompt #1 with Marc timing all three, then call `superpowers:brainstorming` before writing the implementation plan.
