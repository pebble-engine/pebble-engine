-- 007_security_perf_quick_fixes.sql
-- Two findings from `supabase get_advisors` run on 2026-05-24:
--   1. audit_log RLS re-evaluates auth.uid() per row — wrap in (select ...)
--      so Postgres caches the call as an initplan and the policy stays cheap
--      at scale. Docs:
--      https://supabase.com/docs/guides/database/postgres/row-level-security#call-functions-with-select
--   2. waitlist insert policy is `WITH CHECK (true)` — anyone (anon role)
--      can insert any row shape. Tighten to require a plausibly-shaped email
--      so spam can't pile in `email=""` / `email="x"` junk. The existing
--      `unique` constraint already prevented duplicates, but didn't block
--      garbage shapes.

-- Fix 1: audit_log RLS init-plan optimization
drop policy if exists "users can view own audit log" on public.audit_log;
create policy "users can view own audit log"
  on public.audit_log for select
  using ((select auth.uid()) = user_id);

-- Fix 2: waitlist insert policy — basic email shape check
drop policy if exists "Allow anonymous inserts" on public.waitlist;
create policy "Allow anonymous inserts"
  on public.waitlist for insert
  with check (
    email is not null
    and length(email) between 5 and 254
    and email like '%@%.%'
  );
