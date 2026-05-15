"""Structural tests for the public.profiles RLS migrations.

These pin the intent — the actual SQL runs in Supabase's Postgres, not
here — so a future "tidy up the policies" refactor can't silently
re-open the holes the 2026-05-16 NLM pass identified.

What we check:
- 001_profiles.sql still has the SELECT + UPDATE policies and the
  SECURITY DEFINER signup trigger.
- 002_plan_tier_lockdown.sql exists and:
    * blocks owner-driven plan_tier updates,
    * denies client INSERT and DELETE on the profiles table.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MIG_001 = REPO_ROOT / "supabase" / "migrations" / "001_profiles.sql"
MIG_002 = REPO_ROOT / "supabase" / "migrations" / "002_plan_tier_lockdown.sql"


# ---- 001 sanity (regression guard) ----------------------------------------

def test_001_still_enables_rls():
    sql = MIG_001.read_text(encoding="utf-8").lower()
    assert "alter table public.profiles enable row level security" in sql


def test_001_handle_new_user_is_security_definer():
    sql = MIG_001.read_text(encoding="utf-8")
    # The trigger function inserts the profile row on every signup. It
    # MUST stay SECURITY DEFINER + SET search_path, otherwise either the
    # insert breaks (RLS denies it) or search-path hijacking opens up.
    body = re.search(
        r"create or replace function public\.handle_new_user\(\)(.*?)(?:create or replace|\Z)",
        sql,
        re.S | re.I,
    )
    assert body, "handle_new_user() function block not found in 001"
    chunk = body.group(1).lower()
    assert "security definer" in chunk
    assert "set search_path = public" in chunk


# ---- 002 plan_tier lockdown -----------------------------------------------

def test_002_migration_exists():
    assert MIG_002.is_file(), f"Missing: {MIG_002}"


def test_002_defines_protect_plan_tier_trigger_function():
    sql = MIG_002.read_text(encoding="utf-8").lower()
    assert "create or replace function public.protect_plan_tier" in sql
    # Function must guard via auth.role() — the JWT claim is what
    # distinguishes a user-scoped session from a service-role one.
    assert "auth.role()" in sql, (
        "protect_plan_tier must inspect auth.role() to allow service-role writes"
    )


def test_002_blocks_distinct_plan_tier_updates():
    """The trigger only raises when the new value actually differs from
    the old one — same-value upserts must pass so frameworks that re-
    emit every column don't break."""
    sql = MIG_002.read_text(encoding="utf-8").lower()
    assert "is distinct from old.plan_tier" in sql
    assert "raise exception" in sql


def test_002_trigger_is_column_specific_before_update():
    """`BEFORE UPDATE OF plan_tier` keeps the fast path for other
    columns (first_name, email, updated_at) free of trigger overhead."""
    sql = MIG_002.read_text(encoding="utf-8").lower()
    assert re.search(
        r"create trigger profiles_protect_plan_tier\s+before update of plan_tier on public\.profiles",
        sql,
    ), "trigger should be BEFORE UPDATE OF plan_tier (column-scoped)"


def test_002_adds_explicit_insert_deny_policy():
    """No policy ⇒ Postgres default-denies, but be explicit so the
    intent is documented for future operators."""
    sql = MIG_002.read_text(encoding="utf-8").lower()
    assert re.search(
        r"create policy[^;]+for insert[^;]+with check\s*\(\s*false\s*\)",
        sql,
    ), "missing explicit INSERT-deny policy on public.profiles"


def test_002_adds_explicit_delete_deny_policy():
    sql = MIG_002.read_text(encoding="utf-8").lower()
    assert re.search(
        r"create policy[^;]+for delete[^;]+using\s*\(\s*false\s*\)",
        sql,
    ), "missing explicit DELETE-deny policy on public.profiles"


def test_002_is_idempotent():
    """Marc reruns migrations from the dashboard; everything in 002
    must be safe to run twice."""
    sql = MIG_002.read_text(encoding="utf-8").lower()
    assert "drop trigger if exists profiles_protect_plan_tier" in sql
    assert "drop policy if exists" in sql
    assert "create or replace function public.protect_plan_tier" in sql
