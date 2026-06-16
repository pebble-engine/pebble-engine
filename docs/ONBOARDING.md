# Onboarding — senior Python developer

Welcome to Pebble Engine. This guide gets you productive on day one.

## What Pebble is

A Python HTTP server generates production Next.js 14 marketing sites from a short intake flow. The v3 Next.js app (`ui/v3/`) is the product UI; the engine is the brain. See [ARCHITECTURE.md](ARCHITECTURE.md).

## Day 1 setup

```bash
git clone https://github.com/squitopest/pebble-engine.git
cd pebble-engine
cp .env.example .env   # fill keys locally — never commit .env
pip install -r requirements.txt
python pebble_engine.py                    # engine :8000
cd ui/v3 && npm install && npm run dev     # frontend :3001
```

## Commands you will use daily

| Task | Command |
|------|---------|
| Full test suite | `python -m pytest -q` |
| HTTP integration | `python -m pytest tests/test_http_e2e.py -q` |
| **Verification gate** | `python scripts/verify_all.py` |
| Evals on a build | `python -m pebble.evals output/<slug>` |
| Prod smoke (network) | `python scripts/prod_smoke.py` |

After `verify_all.py`, open **[VERIFICATION_REPORT.md](../VERIFICATION_REPORT.md)** at repo root.

## Where to put code

| You are building… | Put it in… |
|-------------------|------------|
| New API endpoint | `pebble/server/<name>.py` + `router.py` |
| Business logic | `pebble/<name>.py` |
| Tests | `tests/test_<name>.py` |
| Prod check | `scripts/verify_<name>_prod.py` |

**Avoid** growing [`pebble_engine.py`](../pebble_engine.py) — it should stay a thin HTTP shell.

## Important modules

- **Build pipeline:** `pebble/server/build.py`, `pebble/server/build_stream.py`
- **Preview:** `pebble/server/preview_serve.py`, `preview_ondemand.py`, `pebble/vercel_deploy.py`
- **Publish:** `pebble/server/publish_instant.py`, `pebble/publish.py`
- **Auth / projects:** `pebble/server/projects.py`, `pebble/security.py`
- **Quality moat:** `pebble/evals/`, `pebble/repair.py`, `skills/prompt_template.md`

## CI

GitHub Actions runs `python scripts/verify_all.py --ci` on push/PR. Artifact: `verification-report`.

## Gotchas (read once)

1. `skills/prompt_template.md` uses Python `str.format()` — double literal braces `{{` `}}`
2. `next/image` does not forward refs — wrap in a `div`
3. `pebble_engine.py` OUTPUT_DIR — projects on disk under `output/`
4. Pytest marker `integration` — excluded in CI until mocked; see `pyproject.toml`

## More docs

- [VERIFICATION.md](VERIFICATION.md) — evidence before "done"
- [BATCH_WORKFLOW.md](../BATCH_WORKFLOW.md) — how agents batch work
- [CLAUDE.md](../CLAUDE.md) — full project map for AI assistants
- [PROD_ENGINE_SETUP.md](PROD_ENGINE_SETUP.md) — Vercel ↔ Railway wiring

## User onboarding funnel (2026-06)

Product flow from landing prompt to first publish:

```
welcome prompt → signup (if needed) → confirm (micro-confirm UI)
  → plan (required until 2 completed builds) → brief-compose (hidden, during Plan)
  → generate → draft → ready → design (+ first-build checklist)
```

| Step | API / module | User-visible? |
|------|----------------|---------------|
| Infer from prompt | `POST /api/brief-infer`, `pebble/brief_infer.py` | No — pre-fills confirm |
| Micro-confirm | `ui/v3/components/phases/confirm-brief-phase.tsx` | Yes |
| Plan gate | `GET /api/onboarding/status`, `pebble/onboarding.py` | Yes (Plan card) |
| Hidden compose | `POST /api/brief-compose`, `pebble/brief_compose.py` | No — merges `extra_context` silently |
| Generate | `POST /api/generate-stream` | Yes (draft animation) |

**Local signup blocked by Cloudflare Turnstile?** Production Turnstile keys are hostname-bound. On `localhost`, the widget auto-bypasses (`DEV_BYPASS`); restart `npm run dev` after pulling. Or use **Sign in** at `/login` (no Turnstile) if you already have an account.

**Three-window speed comparison:** Pebble `localhost:3001` · Lovable `lovable.dev` · Base44 `app.base44.com` — see [`docs/SPEED_BENCHMARK.md`](SPEED_BENCHMARK.md).
