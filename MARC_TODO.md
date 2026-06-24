# Marc — captain checklist

You do **not** run terminal commands for verification. Open **[VERIFICATION_REPORT.md](VERIFICATION_REPORT.md)** after any agent batch — top line says PASS or FAIL.

**Deploy note (2026-06-16):** Railway watches `squitopest/pebble-engine` `main`, not `pebble-engine/pebble-engine`. Push both remotes or repoint Railway.

## Dashboard-only tasks

| # | Task | Doc | How |
|---|------|-----|-----|
| 1 | Supabase migrations if APIs 500 | `supabase/migrations/009_*.sql`, `010_*.sql` | Community/launchpad APIs **200** on prod — run migrations only if you add features |
| 2 | **Railway volume on `output/`** | [docs/RAILWAY_VOLUME.md](docs/RAILWAY_VOLUME.md) | Mount at `/app/output` → redeploy → `python scripts/verify_railway_volume.py` |
| 3 | Cloudflare wildcard `*.pebbleapp.ai` | [docs/DNS_WILDCARD_SETUP.md](docs/DNS_WILDCARD_SETUP.md) | Beta publish requires this — verify on phone LTE |
| 4 | Stripe webhook + one test payment | [docs/STRIPE_E2E.md](docs/STRIPE_E2E.md) | Env OK; complete one live test payment |
| 5 | Golden demo backup slug | [docs/GOLDEN_DEMO.md](docs/GOLDEN_DEMO.md) | Build + star `demo-dental-austin` before invites |
| 6 | Beta invites when ready | [docs/BETA_INVITE.md](docs/BETA_INVITE.md), [docs/BETA_RECRUIT.md](docs/BETA_RECRUIT.md) | `python scripts/_railway_beta_invite_once.py` after dogfood passes |

## Dogfood gate (before any invite)

Run yourself on pebbleapp.ai:

1. `python scripts/golden_path_prod.py` — health + onboarding APIs
2. Full build → Design preview loads within ~3 min
3. Click-to-edit works
4. Publish → `https://<slug>.pebbleapp.ai/` on phone LTE

Optional per-slug check: `python scripts/golden_path_prod.py --slug <your-slug>`

## If verification FAILs

Tell the agent: "Fix failures in VERIFICATION_REPORT.md and re-run verify_all."
