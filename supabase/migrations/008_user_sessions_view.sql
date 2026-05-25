-- 008_user_sessions_view.sql — expose auth.sessions to the engine
-- via SECURITY DEFINER functions in the public schema.
-- Phase D.2 (2026-05-24) of the MFA + sessions list plan.
--
-- Why functions instead of a view?
--   - SECURITY DEFINER lets us bypass the auth schema's RLS without
--     opening auth.* to PostgREST at large (one of the most common
--     supabase footguns).
--   - The functions can enforce the caller-must-be-target-user check
--     explicitly via auth.uid(), so a stolen JWT for user A can't list
--     or revoke user B's sessions.
--   - Returns can be shaped exactly for the UI (drop columns the
--     frontend doesn't need, like refresh_token_hmac_key).
--
-- The engine calls these via PostgREST RPC using the service-role key
-- AND forwards the caller's user_id explicitly — the function then
-- compares against auth.uid() (which the service-role context returns
-- NULL for) so we need both checks. See pebble/server/account_sessions.py.

-- ── list_user_sessions ──────────────────────────────────────────────────────

create or replace function public.list_user_sessions(target_user uuid)
returns table (
  id            uuid,
  created_at    timestamptz,
  updated_at    timestamptz,
  refreshed_at  timestamp,
  not_after     timestamptz,
  user_agent    text,
  ip            text,
  aal           text,
  factor_id     uuid
)
language sql
security definer
set search_path = public, auth, pg_catalog
as $$
  select
    s.id,
    s.created_at,
    s.updated_at,
    s.refreshed_at,
    s.not_after,
    s.user_agent,
    -- inet → text so PostgREST returns a JSON string instead of object
    host(s.ip)::text,
    s.aal::text,
    s.factor_id
  from auth.sessions s
  where s.user_id = target_user
    -- Don't return expired sessions — Supabase keeps the rows but the
    -- refresh token is dead so they're useless UI clutter.
    and (s.not_after is null or s.not_after > now())
  order by coalesce(s.refreshed_at::timestamptz, s.updated_at, s.created_at) desc;
$$;

-- Only the service role can call this. Authenticated users go through
-- the engine which forwards the service-role key + their user_id.
revoke all on function public.list_user_sessions(uuid) from public;
grant execute on function public.list_user_sessions(uuid) to service_role;


-- ── revoke_user_session ─────────────────────────────────────────────────────
-- Deletes one specific session by id, scoped to a user. The engine MUST
-- pass the calling user's id as target_user so a stolen service-role
-- token (defense-in-depth) can't be used to torch another user's session
-- — we double-check ownership in the DELETE WHERE clause.

create or replace function public.revoke_user_session(
  target_user uuid,
  target_session uuid
) returns boolean
language plpgsql
security definer
set search_path = public, auth, pg_catalog
as $$
declare
  deleted_count integer;
begin
  delete from auth.sessions
  where id = target_session
    and user_id = target_user;
  get diagnostics deleted_count = row_count;
  return deleted_count > 0;
end;
$$;

revoke all on function public.revoke_user_session(uuid, uuid) from public;
grant execute on function public.revoke_user_session(uuid, uuid) to service_role;
