# Supabase performance migration — `auth_rls_initplan` fix

**Status:** ready to apply. ~30 seconds in Supabase SQL Editor.
**Priority:** low (no user-facing impact at current scale — surface noise only).
**Discovered by:** morning brief, `get_advisors performance` query.

## Why

Supabase's performance advisor (lint `0003_auth_rls_initplan`) flagged two RLS
policies on `public.profiles` that call `auth.uid()` directly:

```
Profiles are visible to their owner    SELECT   USING (auth.uid() = id)
Profiles are updatable by their owner  UPDATE   USING / WITH CHECK (auth.uid() = id)
```

Postgres re-evaluates `auth.uid()` once per row instead of caching the
result for the whole query. Wrapping it in `(SELECT auth.uid())` flips
that — Postgres treats it as a subquery whose result is computed once
and reused. The official Supabase guide:

https://supabase.com/docs/guides/database/postgres/row-level-security#call-functions-with-select

At Pebble's current scale (~2 active subscriptions) the per-row overhead
is invisible. The fix matters once the `profiles` table grows or
queries start pulling many rows in one shot (e.g. an admin dashboard
listing users).

## What it does NOT change

- Policy SEMANTICS — both policies still check "is the calling user the
  row owner". Same access decision, just evaluated efficiently.
- Other policies on `profiles` (`cannot be deleted`, `cannot be inserted`)
  are untouched — they don't use `auth.uid()` at all.
- Any application code. v3 + the engine keep working identically.

## Paste-ready SQL

Open Supabase Dashboard → SQL Editor → New query → paste → Run:

```sql
-- ============================================================
-- Pebble Supabase performance fix — 2026-05-23
-- Resolves advisor 0003 (auth_rls_initplan) on public.profiles.
--
-- Wraps auth.uid() in (SELECT auth.uid()) so Postgres caches the
-- result for the whole query instead of re-evaluating per row.
-- Same access semantics, faster at scale.
--
-- Idempotent + atomic — runs in a transaction; if either DROP or
-- CREATE fails, nothing changes. Safe to run multiple times.
-- ============================================================

BEGIN;

-- 1) SELECT policy — visible-to-owner

DROP POLICY IF EXISTS "Profiles are visible to their owner" ON public.profiles;

CREATE POLICY "Profiles are visible to their owner" ON public.profiles
  FOR SELECT
  USING ((SELECT auth.uid()) = id);

-- 2) UPDATE policy — updatable-by-owner (both qual AND with_check)

DROP POLICY IF EXISTS "Profiles are updatable by their owner" ON public.profiles;

CREATE POLICY "Profiles are updatable by their owner" ON public.profiles
  FOR UPDATE
  USING ((SELECT auth.uid()) = id)
  WITH CHECK ((SELECT auth.uid()) = id);

COMMIT;
```

## Verify after running

Re-fetch the performance advisors. Both `auth_rls_initplan` WARN findings
should be gone:

```bash
# (via the Supabase MCP, when you next ask Claude to check)
get_advisors performance
```

Expected after: only `unused_index` (INFO) on `idx_waitlist_email`
remains — a different, lower-priority finding I'm leaving for a future
cleanup pass (drop the index if waitlist email lookups never happen).

## Brief window risk

DROP POLICY + CREATE POLICY inside a transaction is atomic from any
other session's view — neither the dropped state nor the half-created
state is observable. Zero risk at current scale.

If we ever do this on a high-traffic production table, the safer
pattern is `ALTER POLICY ... USING ...` — but Postgres doesn't support
ALTER POLICY's expression in current versions, hence the DROP/CREATE
inside a transaction.
