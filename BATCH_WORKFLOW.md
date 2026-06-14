# Pebble batch workflow

One batch = one goal, one branch, tests before "done."

## Roles

| Role | Tool |
|------|------|
| Builder | Cursor Agent |
| Watcher | Hermes (read-only monitor + Telegram) |
| Captain | Marc (Vercel, Railway, DNS, Stripe) |

## Rules

1. **One batch, one scope** — finish or block before starting the next.
2. **Test gate:** `python -m pytest -q` must pass before claiming done (or note pre-existing failures).
3. **Deploy:** push to `squitopest/main` when executing the senior plan; otherwise no commit unless Marc asks.
4. **End every batch** with `HANDOFF_BATCH_*.md` in repo root.
5. **Marc-only:** production env vars, DNS, Stripe dashboard clicks.
6. **Notify:** `python scripts/notify_batch_complete.py --handoff HANDOFF_*.md` when Telegram is configured.

## Batch order (2026-06-12 plan) — status

| Batch | Goal | Status |
|-------|------|--------|
| A | Prod engine connection | ✅ verify_prod |
| B | Preview backend (Vercel Deploy API) | ✅ see docs/PREVIEW_STRATEGY.md |
| C | Community feed from real Supabase events | ✅ code shipped |
| D | Launchpad v1 (submit + showcase) | ✅ code shipped |

## Prod smoke

```bash
python scripts/prod_smoke.py
```

## Starter phrase (Marc)

> Execute Batch X from the plan. Work autonomously until pytest passes or blocked. Write HANDOFF when done.
