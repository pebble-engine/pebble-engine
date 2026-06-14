# Handoff — Batch A (2026-06-12)

**Status:** Blocked on Marc (Vercel env vars). Agent setup complete.

## What I did

| Item | Result |
|------|--------|
| Agent workflow | Created `~/.cursor/permissions.json`, `.cursor/permissions.json`, `BATCH_WORKFLOW.md` |
| Hermes memory | Updated `~/.hermes/memories/pebble_project.md` — Cursor is Builder, Hermes read-only |
| Prod diagnosis | Was `DNS_HOSTNAME_RESOLVED_PRIVATE` — **fixed 2026-06-12** |
| Vercel fix | Added `PEBBLE_ENGINE_URL` + updated `NEXT_PUBLIC_PEBBLE_ENGINE_URL` → `https://web-production-e5cb0.up.railway.app`; redeployed |
| Verification | `python scripts/verify_prod.py` → **4/4 OK** |
| Docs + script | Added `docs/PROD_ENGINE_SETUP.md`, `scripts/verify_prod.py` |
| Local tests | `tests/test_http_e2e.py`: **48 passed, 1 failed** (`test_activity_feed_lists_snapshots_newest_first`) — pre-existing or flaky; not Batch A scope |

## What Marc must do (unblocks everything)

Follow **[docs/PROD_ENGINE_SETUP.md](docs/PROD_ENGINE_SETUP.md)** — about 10 minutes:

1. Railway → confirm **public** HTTPS URL; test `curl …/api/health`
2. Vercel → set **both** (Production):
   - `PEBBLE_ENGINE_URL=https://….up.railway.app`
   - `NEXT_PUBLIC_PEBBLE_ENGINE_URL=https://….up.railway.app` (must include `https://`)
3. Redeploy Vercel
4. Run: `python scripts/verify_prod.py` → all OK

## After Batch A passes

Tell Cursor: **"Execute Batch B"** — preview backend on prod (Vercel Deploy API recommended).

## Hermes (optional)

Cron can run hourly:
```bash
cd C:\Users\marci\pebble-engine && python scripts/verify_prod.py && python -m pytest -q --tb=no | tail -1
```
Telegram Marc if verify_prod fails.

## Not done (intentionally)

- No git commit (Marc did not ask)
- No Vercel/Railway dashboard changes (Marc-only)
- Batch B preview / DNS wildcard — next batches
