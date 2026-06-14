# Batch C handoff — Community feed (2026-06-12)

**Goal:** `/community` uses real Supabase-backed feed + stats; no fake activity when API is healthy but empty.

## Done (Cursor Agent)

| Item | Detail |
|------|--------|
| Signup → feed | `supabase_webhook` records public `joined_pebble` event (no PII in title/body) |
| Stats fix | `templates_count` falls back to engine registry (39) when `public_templates` empty |
| UI | Honest empty state; seed activity **only** when API fails (not when feed is quiet) |
| Migration | `supabase/migrations/009_events_community.sql` for new envs |
| Tests | `test_community_stats.py`, e2e `/api/community/*` |
| Verify | `python scripts/verify_community_prod.py` |

**Prod today (pre-deploy):** APIs work — feed `[]`, stats `templates_count: 0` until this batch ships.

## Blocked on deploy (Marc ~5 min)

See **`MARC_TODO.md`** — commit + push to `squitopest/main` for Railway (webhook) + Vercel (UI).

## How feed fills going forward

| Action | Event | Visibility |
|--------|-------|------------|
| Signup (webhook) | `joined_pebble` | public |
| Publish site | `site_published` | public + private bell |
| Build complete | `build_completed` | private bell only |

## Pytest

Run: `python -m pytest tests/test_community_stats.py tests/test_http_e2e.py::test_community_feed_is_public tests/test_http_e2e.py::test_community_stats_is_public -q`

## Next batch

**Batch D** — Launchpad v1 (submit published slug + showcase grid).
