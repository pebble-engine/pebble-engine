# Beta invite — 5–20 users

**Gate:** Run `python scripts/prod_smoke.py` green before inviting anyone.

## Invite-only mode

Set on Railway (engine):

```env
PEBBLE_BETA_INVITE_ONLY=true
PEBBLE_BETA_INVITE_CODES=demo2026,partner01,partner02
```

When enabled, `POST /api/generate` and `POST /api/generate-stream` require header:

`X-Pebble-Invite: <code>`

v3 sends this automatically when user enters code at signup (stored in `localStorage` key `pebble_invite_code`).

## Credit limits (existing)

Free tier credits enforced in `pebble/server/build.py` — 402 `credits_low` when exhausted.

Recommended beta caps:

| Plan | Builds/month | Notes |
|------|--------------|-------|
| Beta invite | 3 full builds | Enough to publish once |
| Starter | Stripe plan | After payment works |

## Marc — invite flow

1. Generate 10 codes in env (or Supabase `invite_codes` later)
2. Email/DM each tester: link `https://www.pebbleapp.ai/signup?invite=<code>`
3. Monitor `GET /api/admin/engagement` (admin email in `PEBBLE_ADMIN_EMAIL`)

## Rollback

Set `PEBBLE_BETA_INVITE_ONLY=false` or remove env var — open signup resumes.
