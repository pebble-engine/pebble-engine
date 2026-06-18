# Production preview setup (Railway → Vercel Deploy API)

**Problem:** Workspace preview runs `npm install` + `next dev` on the engine. Railway’s Python container has no Node, so prod preview fails with “npm not found” or “Preview file not found: index.html”.

**Fix:** Enable the built-in **Vercel preview backend**. After each build, the engine POSTs the generated site source to Vercel’s Deployments API; Vercel runs `next build` on their infra. The engine proxies `/preview/<slug>/` through that deployment (same-origin + visual-edit bridge).

## One-command fix (agent or Marc)

1. Add a Railway API token to `.env` (one-time):
   ```
   RAILWAY_TOKEN=...   # from https://railway.com/account/tokens
   ```
   `VERCEL_TOKEN` and `VERCEL_TEAM_ID` should already be in `.env`.

2. Run:
   ```bash
   python scripts/_railway_fix_preview_once.py
   ```

3. Wait ~2 minutes for Railway to redeploy, then verify:
   ```bash
   python scripts/verify_preview_prod.py
   ```

   Expect:
   - `preview_backend = vercel`
   - `vercel_configured = True`
   - `preview_prod_ready = True`

## Manual Railway dashboard (if no API token)

Project: **magnificent-simplicity** → service **web** → Variables:

| Variable | Value |
|----------|--------|
| `PEBBLE_PREVIEW_BACKEND` | `vercel` |
| `VERCEL_TOKEN` | Same as local `.env` (Vercel account token) |
| `VERCEL_TEAM_ID` | Same as local `.env` |

Redeploy the service after saving.

## How preview works after fix

```
User opens /workspace/<slug>
  → iframe loads /preview/<slug>/ (via pebbleapp.ai → Railway)
  → engine reads output/<slug>/.vercel-preview.json
  → proxies HTML from *.vercel.app + injects click-to-edit bridge
  → if build still deploying: auto-refresh splash (~1–2 min first time)
```

Build/refine triggers a background Vercel redeploy (not every click-edit).

## Deployment Protection (Vercel Authentication)

If the Vercel team has **Deployment Protection** enabled (common on Pro teams), preview
URLs return an auth wall unless the engine sends `x-vercel-protection-bypass`. The engine
now enables **Protection Bypass for Automation** on each preview project at deploy time and
stores the secret in `output/<slug>/.vercel-preview.json`.

**Repair an existing project** (after deploying this fix):

```bash
python -m pebble.vercel_deploy bakery --repair-bypass
```

Optional: set `VERCEL_AUTOMATION_BYPASS_SECRET` (32 alphanumeric chars) on Railway to use
one team-wide secret for all preview projects.

## Verify end-to-end

1. `python scripts/verify_preview_prod.py` — config OK
2. Sign in on pebbleapp.ai → build or open an existing project
3. Design phase iframe should show the site (or “warming up” splash, then site)

## Rollback

Set `PEBBLE_PREVIEW_BACKEND=local` on Railway and redeploy. Previews will break on prod again but local dev is unchanged.

## Alternative: Fly preview

`PEBBLE_PREVIEW_BACKEND=fly` + `FLY_API_TOKEN` is also supported (per-slug Fly apps). Vercel Deploy API is recommended for beta (SSR + Server Actions, no extra Fly ops).
