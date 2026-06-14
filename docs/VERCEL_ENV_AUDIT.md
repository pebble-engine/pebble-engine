# Vercel env audit — pebbleapp.ai (2026-06-12)

Frontend project: **pebble-engine-oovy** → `www.pebbleapp.ai`

## Required (engine proxy)

| Variable | Purpose | Example |
|----------|---------|---------|
| `PEBBLE_ENGINE_URL` | Next.js rewrites `/api/*` → engine | `https://web-production-e5cb0.up.railway.app` |
| `NEXT_PUBLIC_PEBBLE_ENGINE_URL` | Browser SSE + direct CORS calls | Same URL **with `https://`** |

## Required (Supabase auth in v3)

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Public anon key |

## Required (Stripe checkout UI)

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | `pk_test_...` or live |

## Verify after change

```bash
python scripts/verify_prod.py
curl -s https://www.pebbleapp.ai/api/health | head -c 200
```

Must **not** return `DNS_HOSTNAME_RESOLVED_PRIVATE`.

## Marc checklist

1. Vercel → Project → Settings → Environment Variables
2. Set both engine URLs to the **public** Railway HTTPS hostname
3. Redeploy production
4. Run `python scripts/verify_prod.py`

See `docs/PROD_ENGINE_SETUP.md`.
