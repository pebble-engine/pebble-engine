# Marc — after senior plan execution

Builder completed all plan todos. Pushed to `squitopest/main` (`013e413d`).

## Your short list (dashboard clicks only)

| # | Task | Doc |
|---|------|-----|
| 1 | Run Supabase migrations if APIs 500 on `events` / `public_templates` | `supabase/migrations/009_*.sql`, `010_*.sql` |
| 2 | Cloudflare wildcard `*.pebbleapp.ai` | `docs/DNS_WILDCARD_SETUP.md` |
| 3 | Stripe webhook + one test payment | `docs/STRIPE_E2E.md` |
| 4 | Pre-build golden demo slug | `docs/GOLDEN_DEMO.md` |
| 5 | Enable beta invites when ready | `docs/BETA_INVITE.md` |

## Verify (anytime)

```bash
python scripts/prod_smoke.py
```

## Telegram ping (optional)

```bash
python scripts/notify_batch_complete.py --handoff HANDOFF_PLAN_EXECUTION_2026-06-12.md
```
