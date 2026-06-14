# Senior plan execution handoff (2026-06-12)

Plan: Pebble Project Review and Path Forward — all todos addressed.

## Automated (Builder)

| Todo | Deliverable |
|------|-------------|
| fix-prod-engine-connection | ✅ `verify_prod.py` passes on pebbleapp.ai |
| pick-preview-strategy | `docs/PREVIEW_STRATEGY.md` — **Vercel** chosen |
| enable-fly-preview | **Skipped** — Vercel is prod path |
| deploy-v3-vercel | `docs/VERCEL_ENV_AUDIT.md` |
| community-launchpad-v1 | Batch C+D code + migrations |
| prod-smoke-test-suite | `scripts/prod_smoke.py` + manual checklist |
| wire-dns-publish | `docs/DNS_WILDCARD_SETUP.md` |
| stripe-e2e | `docs/STRIPE_E2E.md` + `scripts/verify_stripe_setup.py` |
| golden-demo | `docs/GOLDEN_DEMO.md` |
| beta-invite | `docs/BETA_INVITE.md` + `pebble/beta_invite.py` + signup `?invite=` |
| build-queue | `pebble/build_queue.py` (`PEBBLE_BUILD_QUEUE=true`) |
| setup-agent-permissions | `.cursor/permissions.json` + user `~/.cursor/permissions.json` |
| setup-batch-protocol | `BATCH_WORKFLOW.md` |
| setup-telegram-status | `scripts/notify_batch_complete.py` |
| update-hermes-memory | `~/.hermes/memories/pebble_project.md` updated |

## Pytest

`2655 passed, 26 failed` (pre-existing failures unchanged).

## Marc-only (still required)

1. **Supabase SQL** if missing: `009_events_community.sql`, `010_launchpad.sql`
2. **DNS wildcard** `*.pebbleapp.ai` — `docs/DNS_WILDCARD_SETUP.md`
3. **Stripe** live webhook + one test payment — `docs/STRIPE_E2E.md`
4. **Beta invites** — set `PEBBLE_BETA_INVITE_*` on Railway when ready
5. **Golden demo** — pre-build backup slug per `docs/GOLDEN_DEMO.md`

## Verify after deploy

```bash
python scripts/prod_smoke.py
```
