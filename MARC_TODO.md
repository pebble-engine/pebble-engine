# Marc — when you're back

Small list of things only you can do. Everything else was handled by the agent.

## 1. Deploy Batch C + D (required — ~5 min)

All code is **local only** (not committed). One push ships community feed + Launchpad:

```bash
git add pebble/community_stats.py pebble/server/supabase_webhook.py pebble/launchpad.py pebble/server/launchpad_api.py pebble/server/router.py pebble_engine.py ui/v3/app/community/ ui/v3/lib/api.ts ui/v3/components/workspace/dashboard-sidebar.tsx tests/ supabase/migrations/009_events_community.sql supabase/migrations/010_launchpad.sql scripts/verify_community_prod.py scripts/verify_launchpad_prod.py
git commit -m "feat(community): live feed, Launchpad v1 showcase + submit"
git push squitopest HEAD:main
```

Wait ~2 min for Railway + Vercel redeploys.

## 2. Supabase SQL (only if tables missing)

Run in Supabase SQL Editor if APIs log errors on `events` or `public_templates`:

| Migration | Powers |
|-----------|--------|
| `supabase/migrations/009_events_community.sql` | Community feed + stats |
| `supabase/migrations/010_launchpad.sql` | Launchpad gallery |

## 3. Supabase webhook (verify once)

Dashboard → Database → Webhooks → `public.profiles` INSERT →

`https://web-production-e5cb0.up.railway.app/api/internal/supabase-webhook`

(with `Authorization: Bearer <PEBBLE_SUPABASE_WEBHOOK_SECRET>`)

## 4. Verify when back

```bash
python scripts/verify_prod.py
python scripts/verify_community_prod.py
python scripts/verify_launchpad_prod.py
```

Then manually:

- https://www.pebbleapp.ai/community — stats show **39 templates**; honest empty activity or real rows
- https://www.pebbleapp.ai/community/launchpad — gallery + sign-in submit form (not stub)
- Optional smoke: publish a test slug → submit to Launchpad → card appears on both pages

## 5. Optional / later

- Wildcard DNS `*.pebbleapp.ai` for live instant-publish URLs
- Stripe webhook E2E + beta invite (senior plan Phase 3)
- Say **"commit and push"** anytime if you want the agent to run git for you
