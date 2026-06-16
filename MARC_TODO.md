# Marc — captain checklist

You do **not** run terminal commands for verification. Open **[VERIFICATION_REPORT.md](VERIFICATION_REPORT.md)** after any agent batch — top line says PASS or FAIL.

**Deploy note (2026-06-16):** Railway watches `squitopest/pebble-engine` `main`, not `pebble-engine/pebble-engine`. Push both remotes or repoint Railway.

## Dashboard-only tasks

| # | Task | Doc | Agent status |
|---|------|-----|--------------|
| 1 | Supabase migrations if APIs 500 | `supabase/migrations/009_*.sql`, `010_*.sql` | Community/launchpad APIs **200** on prod — run migrations only if you add features |
| 2 | Cloudflare wildcard `*.pebbleapp.ai` | `docs/DNS_WILDCARD_SETUP.md` | **Marc** — required for publish |
| 3 | Stripe webhook + one test payment | `docs/STRIPE_E2E.md` | Env OK; **Marc** — complete live payment |
| 4 | Golden demo backup slug | `docs/GOLDEN_DEMO.md` | **Marc** — build `demo-dental-austin` |
| 5 | Beta invites when ready | `docs/BETA_INVITE.md`, `docs/BETA_RECRUIT.md` | **Marc** — set Railway env + send links |

## If verification FAILs

Tell the agent: "Fix failures in VERIFICATION_REPORT.md and re-run verify_all."
