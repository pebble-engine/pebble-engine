# Beta readiness handoff (2026-06-16)

## Shipped

- Merged `claude/prod-preview-fixes` → `main` (`9273b4df`)
- Pushed `pebble-engine/pebble-engine` + `squitopest/pebble-engine` (Railway watches fork)
- Railway + Vercel redeployed; onboarding APIs live on prod
- `scripts/verify_onboarding_prod.py` + prod_smoke 6/6
- `docs/BETA_RECRUIT.md` — 10 invite links + outreach template

## Prod golden path (automated)

| Step | Check | Result |
|------|-------|--------|
| Health | `GET /api/health` | 200 |
| Brief infer | `POST /api/brief-infer` | 200 |
| Onboarding gate | `GET /api/onboarding/status` (no auth) | 401 |
| Frontend | `www.pebbleapp.ai` landing + signup?invite= | loads |
| Full build | signup → generate → preview | **Marc** — needs live account + ~3 min |

## Marc captain (still manual)

See [MARC_TODO.md](MARC_TODO.md): DNS wildcard, Stripe payment, beta invite env, golden demo slug.

## Evidence

```bash
python scripts/prod_smoke.py          # 6/6 OK
python scripts/verify_onboarding_prod.py
python scripts/verify_all.py --ci     # after this handoff
```

Latest [VERIFICATION_REPORT.md](VERIFICATION_REPORT.md) — expect **PASS**.
