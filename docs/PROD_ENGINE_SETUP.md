# Production engine connection (pebbleapp.ai → Railway)

**Problem:** `https://www.pebbleapp.ai/api/*` returns `404` with `DNS_HOSTNAME_RESOLVED_PRIVATE`. Vercel cannot reach the Railway engine hostname in `PEBBLE_ENGINE_URL`.

**Symptom:** Templates/Examples stuck on "Loading…", builds fail, community API empty.

## Fix (Marc — ~10 minutes)

### 1. Railway — get the **public** HTTPS URL

1. Open [Railway dashboard](https://railway.app) → Pebble engine service
2. **Settings → Networking → Public Networking** must be **ON**
3. Copy the public URL, e.g. `https://web-production-xxxx.up.railway.app`
4. In a browser or terminal, confirm it works:
   ```bash
   curl -s https://YOUR-RAILWAY-URL.up.railway.app/api/health
   ```
   Expect JSON with engine/LLM status — not 404.

### 2. Vercel — set both env vars (Production)

Project: **pebble-engine** (or whichever serves `pebbleapp.ai`)

| Variable | Value | Notes |
|----------|-------|-------|
| `PEBBLE_ENGINE_URL` | `https://web-production-xxxx.up.railway.app` | **Must include `https://`** — used by Next.js rewrites |
| `NEXT_PUBLIC_PEBBLE_ENGINE_URL` | Same URL | Browser + SSE direct calls; see `ui/v3/lib/engine-base.ts` |

**Common mistake:** hostname only (`web-production-xxxx.up.railway.app`) without `https://` breaks browser API calls.

Apply to **Production** (and Preview if you test preview deploys).

### 3. Redeploy Vercel

After saving env vars: **Deployments → Redeploy** latest (or push any commit).

### 4. Verify

```bash
curl -s https://www.pebbleapp.ai/api/health
curl -s https://www.pebbleapp.ai/api/templates | head -c 200
```

Or run from repo root:

```bash
python scripts/verify_prod.py
```

All checks should pass before beta or investor demos.

## Architecture (unchanged)

```
User → pebbleapp.ai (Vercel / v3)
     → /api/* rewritten to Railway (PEBBLE_ENGINE_URL)
     → NEXT_PUBLIC_PEBBLE_ENGINE_URL for SSE + direct fetch
```

Preview and publish are separate batches (B and DNS wildcard).
