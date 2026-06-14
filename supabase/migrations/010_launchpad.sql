-- Launchpad v1 — public showcase submissions (Batch D 2026-06-12)
--
-- HOW TO RUN: Supabase Dashboard → SQL Editor → paste → Run.
-- Idempotent (CREATE IF NOT EXISTS).
--
-- Powers:
--   GET  /api/launchpad/showcase
--   POST /api/projects/<slug>/launchpad
--   GET  /api/community/stats (templates_count when rows exist)

create table if not exists public.public_templates (
  id              uuid primary key default gen_random_uuid(),
  user_id         uuid not null references auth.users(id) on delete cascade,
  slug            text not null unique,
  business_name   text not null,
  industry        text,
  tagline         text,
  url             text,
  status          text not null default 'approved'
                  check (status in ('pending', 'approved', 'rejected')),
  submitted_at    timestamptz not null default now(),
  approved_at     timestamptz,
  meta            jsonb
);

create index if not exists public_templates_status_submitted_idx
  on public.public_templates (status, submitted_at desc);

alter table public.public_templates enable row level security;

-- Service role (engine) reads/writes everything. No direct client access.
