-- Pebble community feed + notifications (2026-05-24 / Batch C 2026-06-12)
--
-- HOW TO RUN: Supabase Dashboard → SQL Editor → paste → Run.
-- Idempotent where possible. Safe to re-run on prod that already has
-- these tables (CREATE IF NOT EXISTS).
--
-- Powers:
--   GET /api/community/feed   (public events)
--   GET /api/community/stats  (cached hero numbers)
--   GET /api/notifications    (private bell)

-- ============================================================================
-- events — notifications + community feed rows
-- ============================================================================
create table if not exists public.events (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid references auth.users(id) on delete set null,
  kind        text not null,
  visibility  text not null default 'private'
              check (visibility in ('private', 'public')),
  title       text not null,
  body        text,
  meta        jsonb,
  created_at  timestamptz not null default now()
);

create index if not exists events_visibility_created_idx
  on public.events (visibility, created_at desc);

create index if not exists events_user_private_idx
  on public.events (user_id, created_at desc)
  where visibility = 'private';

-- Service role (engine) reads/writes everything. No direct client access.
alter table public.events enable row level security;

-- ============================================================================
-- notification_reads — per-user "mark as read" for the bell
-- ============================================================================
create table if not exists public.notification_reads (
  user_id   uuid not null references auth.users(id) on delete cascade,
  event_id  uuid not null references public.events(id) on delete cascade,
  read_at   timestamptz not null default now(),
  primary key (user_id, event_id)
);

alter table public.notification_reads enable row level security;

-- ============================================================================
-- community_stats — single-row cache for /community hero strip
-- ============================================================================
create table if not exists public.community_stats (
  id                  int primary key default 1 check (id = 1),
  total_users         int not null default 0,
  total_sites         int not null default 0,
  launches_this_week  int not null default 0,
  templates_count     int not null default 0,
  refreshed_at        timestamptz not null default now()
);

insert into public.community_stats (id)
values (1)
on conflict (id) do nothing;

alter table public.community_stats enable row level security;
