# Handoff — Verification system + senior-dev structure (2026-06-12)

## Goal

Institutionalize evidence-based verification, remove Hermes/Telegram from the repo workflow, add CI + onboarding docs, and extract preview/health handlers from `pebble_engine.py`.

## Changes

- `docs/VERIFICATION.md`, `HANDOFF_TEMPLATE.md` — verification contract + handoff template
- `.cursor/rules/verification.mdc`, `.cursor/rules/architecture.mdc` — agent rules
- `scripts/verify_all.py`, `scripts/verify_handoff.py` — autonomous proof runner
- `scripts/prod_smoke.py` — `--json` structured output
- `.github/workflows/verify.yml` — CI on every push/PR
- `docs/ARCHITECTURE.md`, `docs/ONBOARDING.md` — senior dev onboarding
- `pebble/server/health.py`, `pebble/server/preview_serve.py` — extracted from `pebble_engine.py`
- `pebble_engine.py` — thin delegates for health + preview
- `BATCH_WORKFLOW.md`, `CLAUDE.md`, `MARC_TODO.md` — Hermes removed; verify_all gate
- `scripts/notify_batch_complete.py` — deleted (Telegram/Hermes)
- `.cursor/permissions.json` — allow `verify_all` / `verify_handoff`
- `pyproject.toml` — `integration` pytest marker
- Test fixes for ownership-scoped projects, Supabase pending-state mocks, brand-extract DNS, examples count

## Evidence

**From [VERIFICATION_REPORT.md](VERIFICATION_REPORT.md):**

```
**Status:** PASS
**When:** 2026-06-14T15:22:57Z
**Commit:** c9ca8b22

## Summary for Marc

All automated checks passed. Safe to trust this batch.

## Details

| Check | Result | Exit |
|-------|--------|------|
| pytest | 2678 passed, 0 failed (CI: not integration) | 0 |
| prod_smoke | 4/4 scripts OK | 0 |
```

## Marc-only

None
