# Batch B handoff — Preview on prod (2026-06-12)

**Goal:** Workspace preview works on production (Railway has no Node).

**Strategy:** `PEBBLE_PREVIEW_BACKEND=vercel` — engine deploys generated site source to Vercel Deployments API; `/preview/<slug>/` proxies the result with visual-edit bridge.

## Done (Cursor Agent)

| Item | Location |
|------|----------|
| Health diagnostics | `/api/health` now returns `preview_backend`, `vercel_configured`, `preview_prod_ready` |
| Railway one-shot fix | `python scripts/_railway_fix_preview_once.py` (needs `RAILWAY_TOKEN` in `.env`) |
| Prod verify script | `python scripts/verify_preview_prod.py` |
| Setup guide | `docs/PROD_PREVIEW_SETUP.md` |
| Tests | `test_health_*` preview fields, `test_preview_vercel_backend_shows_splash_without_deployment`, all `test_vercel_deploy.py` pass |
| `.env.example` | Preview backend + Railway token documented |

**Pytest:** 2642 passed, 25 failed (same pre-existing network/repair corpus failures as Batch A).

## Prod status — BLOCKED (two steps)

### 1. Railway engine is stale code

Prod `/api/health` has **no** `preview_backend` field → Railway still runs old `pebblewebsite/pebble-engine` (~2 weeks frozen).

**Fix:** Railway project `magnificent-simplicity` → service `web` → Source → point at **`squitopest/pebble-engine`** branch `main`. (Repo relink was started 2026-06-06; picker may need Railway incident cleared.)

### 2. Preview env vars not set on Railway

Even after code deploy, set on Railway service `web`:

| Variable | Value |
|----------|--------|
| `PEBBLE_PREVIEW_BACKEND` | `vercel` |
| `VERCEL_TOKEN` | Same as local `.env` |
| `VERCEL_TEAM_ID` | Same as local `.env` |

**Automated:** Add `RAILWAY_TOKEN=...` to `.env` (from https://railway.com/account/tokens), then:

```bash
python scripts/_railway_fix_preview_once.py
python scripts/verify_preview_prod.py   # expect 3/3 OK after redeploy
```

## Verify end-to-end (after unblock)

1. `python scripts/verify_preview_prod.py` → all OK
2. pebbleapp.ai → sign in → open project workspace
3. Preview iframe: splash ~1–2 min on first open, then live site
4. Click-to-edit still works (same-origin proxy + bridge)

## Rollback

Railway: `PEBBLE_PREVIEW_BACKEND=local` + redeploy (preview breaks on prod again; local unchanged).

## Next batch

**Batch C** — Community feed from real Supabase events.
