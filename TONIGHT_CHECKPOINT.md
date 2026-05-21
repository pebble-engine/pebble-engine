# Tonight checkpoint — 2026-05-20 evening, post-Webild teardown

## Two big things landed since you stepped away

### 1. Phase 23a verification — the picker fix WORKS

Re-ran your exact mechanic brief. With the haystack widened + Terminal aversion tightened, the picker now correctly lands on **Weather Report DNA** (dashboard-style trades layout) instead of Terminal.

**Side-by-side at a glance:**

| | morning (broken) | now (Phase 23a) |
|---|---|---|
| Layout DNA | Terminal | **Weather Report** |
| Hero | `$ whoami` text-on-black | Dashboard panel: phone-first CTA · OPEN/CLOSED dot · "Today's Availability" with checkmarks · WAIT TIME |
| Nav | `./services./about./contact./call` | Utility bar with hours announcement + "CALL NOW" button |
| Vibe | Hacker terminal | A real mechanic shop site |

**See it live:**
- **http://localhost:3061** — NEW Weather Report mechanic build (post-fix)
- **http://localhost:3060** — OLD Terminal mechanic build (for comparison — same brief, broken picker)

Build stats for the new one:
- 187s, $0.021, 59 files, Qwen Flash (free tier — anonymous curl)
- Slug: `mechanic-shop-in-queens` (clean, title-cased thanks to Phase 20a)

There IS one inner-page compile warning in the new build (a `document.body.classList.contains(...)` reference inside JSX — Qwen put browser-only code where SSR runs it). Homepage renders fine; some inner page errors. That's a new failure mode to add to the next_js_static_check eval — queued for a future phase.

### 2. Phase 25a — Plan Reveal in workspace (Webild-parity UX)

Shipped the single highest-ROI UX change we identified from the Webild teardown. **Engine + v3 frontend changes, end-to-end, TypeScript clean, 1716 tests still passing.**

**What it does:** during a build, the v3 workspace now shows a "Pebble's plan" card that animates in as SSE events arrive — the same first-15-seconds pattern that made Webild feel magical:

| When | What animates in |
|---|---|
| `started` event (T+1s) | Project name (e.g. "Mechanic Shop In Queens") |
| `industry` event (T+3s) | Industry chip |
| `layout` event (T+5s) | Layout chip (e.g. "Weather Report") |
| `style` event (T+7s) | Color palette swatches + DNA chip |
| `plan` event (T+10s) | Full 10-section Site Structure list |
| each `file` event | Checkmark on matching page in the structure list |

The user goes from "submitted prompt" to "I can see Pebble's complete plan + sections checking off in real time" in under 15 seconds. The actual generation still takes 2-3 minutes, but the perception gap closes hard.

**To test it end-to-end:**
1. **http://localhost:3001** — v3 workspace (booting now)
2. Hard-refresh (Ctrl+Shift+R)
3. Start a new project — type any business idea
4. Submit — watch the Plan Reveal card paint in piece by piece

**Engine changes** (all in `pebble/server/build.py`):
- `started` event now includes `business_name`
- `style` event now includes `palette` (5 color hex strings) + `signature_moves`
- New `plan` event after plan.json write, with full pages list

**v3 changes:**
- `ui/v3/lib/api.ts` — added `plan` to `SSEEvent` type, extended `started`/`style` shapes
- `ui/v3/components/phases/draft-phase.tsx` — new Plan Reveal section, palette swatch animation, page checklist with shipped-state tracking

## What's running for you right now

| Port | What | Status |
|---|---|---|
| **8000** | Pebble engine (Qwen Plus default, Phase 25a code loaded) | alive |
| **3001** | v3 workspace (Plan Reveal wired in) | booting |
| **3060** | mechanic-shop-inqueens (OLD Terminal DNA build) | alive |
| **3061** | mechanic-shop-in-queens (NEW Weather Report build, post-fix) | alive |

## What's NOT done — staged in task list for later

- **Phase 25b** — Bot persona ("Pebble" greeting + status narration via GPT-4o-mini through OpenRouter). Tomorrow.
- **Phase 26** — Template gallery (10-15 pre-generated industry templates, 10-100× cost reduction, free-tier carrot). Next weekend.
- **Phase 27** — Cloud sandbox preview (per-project shareable URLs like Webild's `3000-<id>.sandbox.webild.io`). 2-week sprint.
- **Phase 28** — Hybrid model routing (GPT-4o-mini for chat + Qwen Flash for free tier + Claude Sonnet for paid tier). In parallel with template gallery.

## Working-tree status (`C:/Users/marci/pebble-engine/`)

Branch `main`, **nothing committed today** (per CLAUDE.md "only commit when requested"). All changes visible via `git status` — your call when to commit + push.

New files this evening (Phase 23a + Phase 25a):
- `pebble/text.py` (this morning's title-case)
- `pebble/next_config_patch.py` (this morning's allowedDevOrigins)
- `tests/test_text_sanitize.py` (28 tests)
- `tests/test_no_invented_time_markers.py` (34 tests)
- `tests/test_next_config_patch.py` (10 tests)
- `MORNING_RESULTS.md`, `END_OF_DAY_RESULTS.md`, `TONIGHT_CHECKPOINT.md`

Modified files:
- `pebble/server/build.py` (sanitize_business_name + ensure_allowed_dev_origins wiring + Phase 25a SSE event additions)
- `pebble/evals/checks.py` (no_invented_time_markers)
- `pebble/prompt_diet.py` (time-marker directive)
- `pebble/layout_dna.py` (Phase 23a haystack + Terminal aversion)
- `pebble/compare_prompts.py` (this morning's cp1252 fix)
- `ui/v3/lib/state.ts` (Phase 20a deriveProjectName)
- `ui/v3/lib/api.ts` (Phase 25a SSE event types)
- `ui/v3/components/phases/draft-phase.tsx` (Phase 25a Plan Reveal)
- `tests/test_layout_dna.py` (Phase 23a regression tests)

Tests: **1716 passing**, 0 failures.
