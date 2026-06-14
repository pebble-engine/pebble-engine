# Preview strategy (decided 2026-06-12)

**Decision:** **Vercel Deployments API** (`PEBBLE_PREVIEW_BACKEND=vercel`)

## Why Vercel (not Fly)

| Criterion | Vercel Deploy API | Fly per-slug | Fly fleet |
|-----------|-------------------|--------------|-----------|
| Engine stays Python-only | Yes | Yes | Yes |
| SSR + Resend contact forms | Yes | Yes | Yes |
| Already in repo | `pebble/vercel_deploy.py` | `pebble/fly_preview.py` | `pebble/fly_fleet.py` |
| Prod status (Jun 2026) | **Shipped** on Railway | Not enabled | Not deployed |

Fly remains a fallback if Vercel token limits bite. Do **not** run both in prod.

## Prod env (Railway)

```env
PEBBLE_PREVIEW_BACKEND=vercel
VERCEL_TOKEN=<from Vercel account settings>
VERCEL_TEAM_ID=<team id if applicable>
```

## Verify

```bash
python scripts/verify_preview_prod.py
```

Workspace design-phase iframe should load `/preview/<slug>/` (engine proxies to Vercel deployment).

## Marc-only

- Create/restrict `VERCEL_TOKEN` (full account or team token with deploy scope)
- Redeploy Railway after env changes

See `docs/PROD_PREVIEW_SETUP.md` for the full runbook.
