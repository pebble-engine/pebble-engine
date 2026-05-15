-- Pebble Phase A schema: user profile mirror + Row Level Security.
--
-- HOW TO RUN: Supabase Dashboard → SQL Editor → New Query → paste this
-- whole file → click Run. Idempotent — safe to re-run.
--
-- What this does:
-- 1. Creates a `profiles` table in the `public` schema that mirrors
--    `auth.users` and adds app-specific fields (first_name, plan_tier).
-- 2. Installs a trigger so every new sign-up automatically gets a
--    `profiles` row, populated from the user's auth metadata if present.
-- 3. Locks down the table with Row Level Security so each user can ONLY
--    read + update their own profile.

create extension if not exists "uuid-ossp";

-- ============================================================================
-- profiles — one row per signed-up user. Keyed by auth.users.id.
-- ============================================================================
create table if not exists public.profiles (
  id          uuid references auth.users on delete cascade primary key,
  email       text,
  first_name  text,
  plan_tier   text not null default 'free'
              check (plan_tier in ('free','solo','studio')),
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

-- Update `updated_at` automatically whenever a row changes.
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists profiles_set_updated_at on public.profiles;
create trigger profiles_set_updated_at
  before update on public.profiles
  for each row execute function public.set_updated_at();

-- ============================================================================
-- Auto-provision a profile row when a new user signs up.
-- ============================================================================
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
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

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ============================================================================
-- Row Level Security — owner-only read + update.
-- ============================================================================
alter table public.profiles enable row level security;

drop policy if exists "Profiles are visible to their owner" on public.profiles;
create policy "Profiles are visible to their owner" on public.profiles
  for select using (auth.uid() = id);

drop policy if exists "Profiles are updatable by their owner" on public.profiles;
create policy "Profiles are updatable by their owner" on public.profiles
  for update using (auth.uid() = id) with check (auth.uid() = id);

-- ============================================================================
-- Sanity check — when this script finishes, you should see one row per
-- existing user. If you've already signed up before running this, your
-- profile will be missing — re-run as a one-off:
--
--   insert into public.profiles (id, email, first_name)
--   select id, email, coalesce(raw_user_meta_data->>'first_name', split_part(email,'@',1))
--   from auth.users
--   on conflict (id) do nothing;
-- ============================================================================
