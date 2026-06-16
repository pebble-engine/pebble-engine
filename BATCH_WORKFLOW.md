# Pebble batch workflow

One batch = one goal, one branch, tests before "done."

## Roles

| Role | Tool |
|------|------|
| Builder | Cursor Agent (any LLM session in this repo) |
| Captain | Marc (Vercel, Railway, DNS, Stripe) |

## Rules

1. **One batch, one scope** — finish or block before starting the next.
2. **Verification gate:** `python scripts/verify_all.py` must exit 0 before claiming done.
3. **Deploy:** push to `squitopest/main` when Marc asks or plan says ship.
4. **End every batch** with `HANDOFF_*.md` using [HANDOFF_TEMPLATE.md](HANDOFF_TEMPLATE.md).
5. **Marc-only:** production env vars, DNS, Stripe dashboard clicks.
6. **Marc reads:** [VERIFICATION_REPORT.md](VERIFICATION_REPORT.md) — PASS/FAIL at top; no terminal required.

## Verification

```bash
python scripts/verify_all.py
```

See [docs/VERIFICATION.md](docs/VERIFICATION.md).

## Starter phrase (Marc)

> Execute Batch X from the plan. Work autonomously until pytest passes or blocked. Write HANDOFF when done.
