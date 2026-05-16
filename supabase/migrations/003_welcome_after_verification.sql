-- Pebble Phase A.5 migration 003: welcome email only AFTER email verification.
--
-- HOW TO RUN: Supabase Dashboard → SQL Editor → New Query → paste this
-- whole file → click Run. Idempotent — safe to re-run.
--
-- WHY THIS EXISTS:
-- The 2026-05-16 NotebookLM adversarial pass flagged a signup-abuse
-- vector: today's `on_auth_user_created` trigger fires on auth.users
-- INSERT, which happens BEFORE the email confirmation link is clicked
-- for password signups. An attacker can email-bomb a victim by typing
-- their address into /signup repeatedly. Migration 1c666f1 added a
-- per-recipient throttle (2/hr) as a mitigation, but the structural
-- fix is: don't run the welcome flow until the address is verified.
--
-- HOW IT WORKS:
-- 1. handle_new_user() now early-returns if email_confirmed_at is null.
--    - OAuth signups: the provider has already verified the address,
--      so Supabase sets email_confirmed_at on INSERT — function inserts
--      profile, webhook fires, welcome email sent. (Unchanged behavior.)
--    - Password signups: email_confirmed_at is null on INSERT — function
--      no-ops. No profile, no webhook, no welcome email.
-- 2. A new trigger (on_auth_user_email_confirmed) fires the same
--    function when email_confirmed_at flips from null to non-null —
--    i.e. when the password user finishes clicking the confirmation
--    link. Profile gets created then; webhook fires then.
--
-- IMPACT ON EXISTING USERS:
-- - Already-confirmed users: have a profiles row from 001. No change.
-- - Unconfirmed-but-existing users: when they eventually confirm, the
--   new UPDATE trigger creates their profile + sends the welcome.
--   (Slight delay in their welcome from when they originally signed
--    up; acceptable trade-off.)
-- - Brand-new password signups: no welcome until they verify.

-- ============================================================================
-- 1. Gate handle_new_user on email_confirmed_at.
-- ============================================================================
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  -- Don't provision the profile row until the address is verified.
  -- For OAuth signups Supabase sets email_confirmed_at on INSERT
  -- (the provider already verified). For password signups it stays
  -- null until the confirmation link is clicked.
  if new.email_confirmed_at is null then
    return new;
  end if;

  insert into public.profiles (id, email, first_name)
  values (
    new.id,
    new.email,
    coalesce(
      new.raw_user_meta_data->>'first_name',
      new.raw_user_meta_data->>'name',
      split_part(new.email, '@', 1)
    )
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

-- ============================================================================
-- 2. Add the verification-flip trigger.
-- ============================================================================
-- BEFORE/AFTER UPDATE OF <col> only fires when that column appears in the
-- SET list, so unrelated updates (e.g. last_sign_in_at on every login)
-- don't pay trigger overhead.
--
-- The WHEN clause is the actual guard: fire exactly once, on the
-- null → not-null transition. If an admin later re-saves the same
-- value or rotates a confirmed_at timestamp, no re-fire.

drop trigger if exists on_auth_user_email_confirmed on auth.users;
create trigger on_auth_user_email_confirmed
  after update of email_confirmed_at on auth.users
  for each row
  when (old.email_confirmed_at is null and new.email_confirmed_at is not null)
  execute function public.handle_new_user();

-- ============================================================================
-- Backfill check — if you have password users who signed up before this
-- migration ran AND confirmed BEFORE it ran, they'll already have a
-- profile from 001 (so they're fine). If they signed up before but
-- haven't confirmed yet, the new UPDATE trigger fires when they
-- eventually do. No backfill SQL needed.
-- ============================================================================
