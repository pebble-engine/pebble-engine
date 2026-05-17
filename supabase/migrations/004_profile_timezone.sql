-- Migration 004: add timezone + display_name to profiles.
--
-- HOW TO RUN: Supabase Dashboard → SQL Editor → New Query → paste → Run.
-- Idempotent — safe to re-run.
--
-- timezone: IANA tz string (e.g. "America/New_York"). Defaults to UTC.
-- display_name: user's preferred public name (first_name is the auth-
--   provisioned value; display_name is what they choose later). NULL
--   means "fall back to first_name in UI".

alter table public.profiles
  add column if not exists timezone    text not null default 'UTC',
  add column if not exists display_name text;

-- The existing set_updated_at trigger already fires on any UPDATE, so
-- no trigger changes are needed here.
