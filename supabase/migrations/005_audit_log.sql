-- 005_audit_log.sql — append-only audit table for security-relevant events.
-- RLS: users can only see their own rows. Service role can insert.
-- Phase A1 of the trust + account-surface plan (2026-05-24).

create table if not exists public.audit_log (
  id          uuid          primary key default gen_random_uuid(),
  user_id     uuid          not null references auth.users(id) on delete cascade,
  event_type  text          not null,
  ip          text,
  user_agent  text,
  metadata    jsonb         not null default '{}'::jsonb,
  created_at  timestamptz   not null default now()
);

create index if not exists audit_log_user_created_idx
  on public.audit_log (user_id, created_at desc);

alter table public.audit_log enable row level security;

-- Users see only their own rows. Service role bypasses RLS automatically.
create policy "users can view own audit log"
  on public.audit_log for select
  using (auth.uid() = user_id);

-- No INSERT/UPDATE/DELETE policy for authenticated role — only the service
-- role (used by the pebble.audit_log helper) writes. This makes the log
-- append-only from the user's perspective and tamper-resistant.
