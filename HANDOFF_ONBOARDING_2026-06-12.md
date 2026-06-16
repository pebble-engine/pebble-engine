# Handoff — Onboarding funnel upgrade (2026-06-12)

## Summary

Shipped the onboarding funnel upgrade: hidden brief infer/compose, friendly micro-confirm phase, Plan required until 2 completed builds, template-match modal demotion for prompt autostart, and first-build post-publish checklist.

## Funnel

```
prompt → signup? → brief-infer (hidden) → confirm → plan (if builds < 2) → brief-compose (hidden) → generate → draft → ready → design → checklist
```

## Files touched

**Backend (new)**
- `pebble/brief_infer.py` — heuristic infer, no LLM
- `pebble/brief_compose.py` — template + optional mini-LLM merge into `extra_context`
- `pebble/onboarding.py` — `plan_required` until 2 builds
- `pebble/server/brief_infer_api.py`, `brief_compose_api.py`, `onboarding_api.py`
- `pebble/server/router.py` — routes wired

**Frontend**
- `ui/v3/components/phases/confirm-brief-phase.tsx` — "Here's what we heard"
- `ui/v3/components/post-build-checklist.tsx` — first-build nudge
- `ui/v3/components/phases/use-phase.ts` — `confirm` phase
- `ui/v3/components/workspace-shell.tsx` — funnel wiring, onboarding status, checklist
- `ui/v3/components/phases/plan-phase.tsx` — silent `brief-compose` on mount
- `ui/v3/components/phases/welcome-phase.tsx` — `_raw_prompt` stash
- `ui/v3/lib/api.ts` — `fetchBriefInfer`, `fetchBriefCompose`, `fetchOnboardingStatus`

**Tests / docs**
- `tests/test_brief_infer_compose.py`
- `docs/ONBOARDING.md` — funnel section

## Evidence

```
python scripts/verify_all.py --ci → VERIFICATION_REPORT.md Status: PASS
python -m pytest tests/test_brief_infer_compose.py -q → 7 passed
python -m pytest tests/test_http_e2e.py -k "brief_infer or brief_compose or onboarding_status" -q → 5 passed
Live (logged in): confirm → plan → Start Building; no extra_context shown in UI
Turnstile localhost bypass for signup (turnstile-widget + precheck DEV_BYPASS)
```

## Plan gaps closed (2026-06-15)

- `_composed_at` on brief compose patch
- Plan phase blocks Start Building while compose in flight
- Confirm skips infer when brand-extract already filled fields (`_inspired_by` / `_extracted_*`)
- Brand extract sets `_raw_prompt` for hidden compose
- HTTP e2e for `/api/brief-infer`, `/api/brief-compose`, `/api/onboarding/status`

## Not in scope (next plan)

Speed / Stitch-style live preview during Plan wait and build — see `PROMPT_SPEED_PLAN.md`.

## Marc blockers (unchanged)

Supabase migrations 009/010, Stripe E2E, beta invite env, DNS wildcard, golden demo backup, commit/push this batch.
