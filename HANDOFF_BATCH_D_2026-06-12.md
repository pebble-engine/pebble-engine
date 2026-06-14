# Batch D handoff — Launchpad v1 (2026-06-12)

**Goal:** Submit published slug + public showcase grid (replace Launchpad stub + template-only community showcase).

## Done (Cursor Agent)

| Item | Detail |
|------|--------|
| Migration | `supabase/migrations/010_launchpad.sql` — `public_templates` table |
| Backend | `pebble/launchpad.py` + `pebble/server/launchpad_api.py` |
| Routes | `GET /api/launchpad/showcase`, `GET /api/launchpad/screenshot/<slug>`, `GET/POST/DELETE /api/projects/<slug>/launchpad` |
| UI | `/community/launchpad` — gallery + owner submit/withdraw |
| Community | Showcase section reads live Launchpad when entries exist |
| Sidebar | Launchpad no longer marked "Soon" |
| Tests | `tests/test_launchpad.py`, e2e public showcase |
| Verify | `python scripts/verify_launchpad_prod.py` |

**v1 behaviour:** Auto-approve on submit (no moderation queue). Gallery only lists rows whose project is still instant-published. Submit records public `template_submitted` event.

## Blocked on deploy (Marc)

See **`MARC_TODO.md`** — one commit/push for **Batch C + D** together (all local changes).

## Supabase (once per env)

If `GET /api/launchpad/showcase` returns empty forever and engine logs show HTTP 404 on `public_templates`, run:

- `supabase/migrations/010_launchpad.sql`

(`009_events_community.sql` too if Batch C tables missing.)

## Pytest

```bash
python -m pytest tests/test_launchpad.py tests/test_http_e2e.py::test_launchpad_showcase_is_public -q
```

## Next (post Phase 1)

- Prod smoke: signup → build → publish → submit Launchpad → see card on `/community`
- Wildcard `*.pebbleapp.ai` DNS (instant publish URLs)
- Stripe E2E + beta invite
