-- 006_pending_state.sql — Move email-change tokens + data-export manifests
-- from local filesystem (output/.users/, output/.exports/) into Supabase.
-- NLM 2026-05-25 critique: local-file state breaks multi-instance scale.
-- Phase A2 trust-account-surface hardening.

create table if not exists public.email_change_pending (
  token         text          primary key,
  user_id       uuid          not null references auth.users(id) on delete cascade,
  new_email     text          not null,
  requested_at  timestamptz   not null default now(),
  expires_at    timestamptz   not null
);
create index if not exists email_change_pending_user_idx
  on public.email_change_pending (user_id, expires_at desc);
alter table public.email_change_pending enable row level security;
-- No SELECT policy for the authenticated role — the token IS the auth
-- (anyone who can present the token is the legitimate recipient).
-- Service role bypasses RLS for the engine's lookups.

create table if not exists public.data_export_manifests (
  token         text          primary key,
  user_id       uuid          not null references auth.users(id) on delete cascade,
  zip_path      text          not null,       -- absolute path on the engine host
  requested_at  timestamptz   not null default now(),
  expires_at    timestamptz   not null
);
create index if not exists data_export_manifests_user_idx
  on public.data_export_manifests (user_id, expires_at desc);
alter table public.data_export_manifests enable row level security;
-- Same model — token is the bearer auth. Service role manages.
