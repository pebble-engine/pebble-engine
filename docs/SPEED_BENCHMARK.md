# Speed benchmark — Pebble vs Lovable vs Base44

Standard prompt (session 2026-06-15):

> I own a bakery in Brooklyn — need a site where locals can find us and get in touch.

## Live run — 2026-06-15 — baseline (before speed UX ship)

| Milestone | Pebble (local) | Lovable | Base44 |
|-----------|----------------|---------|--------|
| T0 — Send/Build click | 0s | _(Marc: fill in)_ | _(Marc: fill in)_ |
| T1 — Confirm / editor / plan Q | Signup gate (~2s to `/signup?redirect=/workspace#phase=confirm`) | _(Marc)_ | _(Marc)_ |
| T2 — Plan card / first preview pixel | API plan **0.013s** (see below); UI after auth | _(Marc)_ | _(Marc)_ |
| T3 — Draft SSE first event | Requires logged-in full generate | _(Marc)_ | _(Marc)_ |
| T4 — Preview iframe first pixel | `preview_ready` SSE (~60–90s typical) | _(Marc)_ | _(Marc)_ |
| T5 — Ready / open editor | After generate completes | _(Marc)_ | _(Marc)_ |

**Pebble API-only timings** (`python scripts/benchmark_funnel.py`):

| Step | Seconds |
|------|---------|
| `/api/health` | 0.435 |
| `/api/brief-infer` | 0.004 |
| `/api/brief-compose` | 0.002 |
| `/api/plan` | 0.013 |
| **Total before generate** | **0.454** |

**Winner this run:** _(Marc — run Lovable + Base44 in parallel, paste times above)_

**Pebble gap:** Perceived wait is dominated by **generate** (60–180s), not infer/plan. Competitors show iframe preview within seconds of Send.

**Ship next (this sprint):** Plan wireframe skeleton + inline draft iframe on `preview_ready`.

---

## Live run — 2026-06-15 — after speed UX ship

| Milestone | Pebble (local) | Lovable | Base44 |
|-----------|----------------|---------|--------|
| T1 — Confirm visible | Wireframe skeleton instant on Plan mount; confirm after signup | _(Marc)_ | _(Marc)_ |
| T2 — Plan card | Same API ~0.45s pre-generate | _(Marc)_ | _(Marc)_ |
| T4 — Inline preview | Draft phase iframe on `preview_ready` (no new tab) | _(Marc)_ | _(Marc)_ |

**UX changes shipped:**

- [`plan-wireframe-skeleton.tsx`](../ui/v3/components/phases/plan-wireframe-skeleton.tsx) — animated wireframe from brief chips during Plan load
- [`draft-phase.tsx`](../ui/v3/components/phases/draft-phase.tsx) — inline **Live preview** iframe when engine emits `preview_ready`
- [`scripts/benchmark_funnel.py`](../scripts/benchmark_funnel.py) — repeatable API milestone timing

**How to re-run Pebble live test (Marc logged in):**

1. `python pebble_engine.py` + `cd ui/v3 && npm run dev -- -p 3001`
2. Open http://localhost:3001/ → Start Building Free → paste prompt → Build
3. Confirm → Plan (wireframe) → Start Building → watch Draft for **Live preview** panel

**Three-window comparison:** Pebble `localhost:3001` · Lovable `lovable.dev` · Base44 `app.base44.com`

### Local signup / Turnstile (2026-06-15)

Production Cloudflare Turnstile keys are bound to `pebbleapp.ai`. On **localhost**, signup used to hang with "Create account" disabled. Fixed: widget + precheck accept `DEV_BYPASS` on localhost. **Restart `npm run dev`** after pulling. Existing users: **http://localhost:3001/login** (no Turnstile on login).

---

## Targets (acceptance)

| Milestone | Target |
|-----------|--------|
| Confirm screen | < 500ms after submit |
| Plan card (or wireframe) | < 2s |
| First preview pixel | < 60s p50 full build |
| Interactive preview | < 90s p50 |

---

## Live run — 2026-06-16 — prod (post-beta deploy)

**Engine:** `https://www.pebbleapp.ai` (`python scripts/benchmark_funnel.py --engine https://www.pebbleapp.ai`)

| Step | Seconds |
|------|---------|
| `/api/health` | 0.235 |
| `/api/brief-infer` | 0.190 |
| `/api/brief-compose` | 0.173 |
| `/api/plan` | 0.210 |
| **Total before generate** | **0.808** |

Lovable / Base44 columns: run post-beta per [PROMPT_SPEED_PLAN.md](../PROMPT_SPEED_PLAN.md).

