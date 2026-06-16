# Beta recruit — 5–10 testers

**Prerequisite:** `python scripts/prod_smoke.py` → all green (includes onboarding APIs).

## Invite codes (Marc — set on Railway)

```env
PEBBLE_BETA_INVITE_ONLY=true
PEBBLE_BETA_INVITE_CODES=beta01,beta02,beta03,beta04,beta05,beta06,beta07,beta08,beta09,beta10
```

After saving, Railway redeploys automatically (~2 min). Confirm:

```bash
curl -s https://www.pebbleapp.ai/api/health | grep beta_invite_only
# expect: "beta_invite_only": true
```

## Per-tester link

| # | Code | Signup URL |
|---|------|------------|
| 1 | beta01 | https://www.pebbleapp.ai/signup?invite=beta01 |
| 2 | beta02 | https://www.pebbleapp.ai/signup?invite=beta02 |
| 3 | beta03 | https://www.pebbleapp.ai/signup?invite=beta03 |
| 4 | beta04 | https://www.pebbleapp.ai/signup?invite=beta04 |
| 5 | beta05 | https://www.pebbleapp.ai/signup?invite=beta05 |
| 6 | beta06 | https://www.pebbleapp.ai/signup?invite=beta06 |
| 7 | beta07 | https://www.pebbleapp.ai/signup?invite=beta07 |
| 8 | beta08 | https://www.pebbleapp.ai/signup?invite=beta08 |
| 9 | beta09 | https://www.pebbleapp.ai/signup?invite=beta09 |
| 10 | beta10 | https://www.pebbleapp.ai/signup?invite=beta10 |

## Outreach template (DM or email)

> Hi — I'm opening a small beta for Pebble (AI website builder for small businesses). You'd get 3 free full builds and a published URL.
>
> Sign up here: https://www.pebbleapp.ai/signup?invite=beta0X
>
> Flow: type what your business is → confirm we heard you right → see a plan → watch it build → click to edit → publish.
>
> Reply with any friction (signup, first build, publish). Thanks!

## Who to recruit

- 2–3 non-technical small-business owners (bakery, dental, contractor)
- 2 designers who've used Lovable or Squarespace
- 1–2 technical friends for bug reports only

## Monitor (Marc, daily during beta)

```bash
# Admin engagement buckets (requires PEBBLE_ADMIN_EMAIL session or curl with cookie)
curl -s https://www.pebbleapp.ai/api/admin/engagement

# Engine errors
curl -s https://www.pebbleapp.ai/api/admin/errors
```

Watch for: signup drop-off, `credits_low` 402s, publish DNS failures, confirm-phase confusion.

## Rollback

Set `PEBBLE_BETA_INVITE_ONLY=false` on Railway — open signup resumes without codes.
