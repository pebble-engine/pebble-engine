# Marc — captain checklist

You do **not** run terminal commands for verification. Open **[VERIFICATION_REPORT.md](VERIFICATION_REPORT.md)** after any agent batch — top line says PASS or FAIL.

## Dashboard-only tasks

| # | Task | Doc |
|---|------|-----|
| 1 | Supabase migrations if APIs 500 | `supabase/migrations/009_*.sql`, `010_*.sql` |
| 2 | Cloudflare wildcard `*.pebbleapp.ai` | `docs/DNS_WILDCARD_SETUP.md` |
| 3 | Stripe webhook + one test payment | `docs/STRIPE_E2E.md` |
| 4 | Golden demo backup slug | `docs/GOLDEN_DEMO.md` |
| 5 | Beta invites when ready | `docs/BETA_INVITE.md` |

## If verification FAILs

Tell the agent: "Fix failures in VERIFICATION_REPORT.md and re-run verify_all."
