-- Pebble Phase A.1 — make `profiles.plan_tier` immutable from the row owner.
--
-- HOW TO RUN: Supabase Dashboard → SQL Editor → New Query → paste this
-- whole file → click Run. Idempotent — safe to re-run.
--
-- WHY: 001_profiles.sql gave the row owner an unrestricted UPDATE policy
-- on `public.profiles`. That means once any user is signed in they can
--
--     UPDATE public.profiles SET plan_tier = 'studio' WHERE id = auth.uid();
--
-- and self-promote to a paid tier without paying. The 2026-05-16 NLM
-- adversarial pass flagged this as the next thing that bites the moment
-- billing scaffolding lands. Lock it down NOW so we don't ship a billing
-- system on top of a free-promotion footgun.
--
-- WHAT THIS DOES:
-- 1. Adds a BEFORE-UPDATE trigger on `plan_tier` that aborts the update
--    unless the caller's JWT carries the `service_role` claim. Pebble's
--    paid-tier code path (the eventual Stripe webhook handler) will use
--    the service-role key; everything else — the user's signed-in
--    browser, the anon role, even an authenticated server-side call —
--    is denied.
-- 2. The trigger is column-specific (`UPDATE OF plan_tier`), so updates
--    to first_name / email / updated_at don't pay any extra cost.
-- 3. The trigger function is NOT `SECURITY DEFINER` because `auth.role()`
--    needs to read the calling session's role, not the function owner's.

-- ============================================================================

create or replace function public.protect_plan_tier()
returns trigger
language plpgsql
as $$
begin
  -- Allow no-op writes (same value) so framework upserts that re-emit
  -- every column don't trip on this. Only block actual changes.
  if new.plan_tier is distinct from old.plan_tier
     and coalesce(auth.role(), '') <> 'service_role'
  then
    raise exception 'plan_tier may only be modified by the service role'
      using errcode = '42501', -- insufficient_privilege
            hint = 'Use the Supabase service-role key from the billing webhook, not a user-scoped client.';
  end if;
  return new;
end;
$$;

drop trigger if exists profiles_protect_plan_tier on public.profiles;
create trigger profiles_protect_plan_tier
  before update of plan_tier on public.profiles
  for each row execute function public.protect_plan_tier();

-- ============================================================================
-- Defense-in-depth: explicit INSERT / DELETE deny policies so the intent
-- is documented, not relying on Postgres' "no policy ⇒ deny" default.
-- (001_profiles.sql defined only SELECT + UPDATE policies. The
-- `handle_new_user()` trigger writes via `security definer` and bypasses
-- RLS, so app code never needs to INSERT or DELETE from a client.)
-- ============================================================================

drop policy if exists "Profiles cannot be inserted by clients" on public.profiles;
create policy "Profiles cannot be inserted by clients" on public.profiles
  for insert with check (false);

drop policy if exists "Profiles cannot be deleted by clients" on public.profiles;
create policy "Profiles cannot be deleted by clients" on public.profiles
  for delete using (false);
