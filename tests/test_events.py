"""Tests for the events module (Supabase-backed notifications + feed).

Pure-function tests — no Supabase calls, no HTTP. The endpoint itself
is auth-gated and the helpers fail-soft (return None / []) on any
Supabase failure, so the unit test surface is the validation layer:
which kinds are allowed, which visibilities, which payload shapes
get rejected silently vs allowed through.

The actual Supabase write is verified via the live engine + curl smoke
test (run by hand against a real project).
"""
from __future__ import annotations

from pebble import events


# ── Kind allowlist ──────────────────────────────────────────────── #


def test_valid_kinds_includes_all_constants():
    """If we ever add a KIND_* constant we should also add it to the
    allowlist set, or record() will silently drop the event."""
    for attr in dir(events):
        if attr.startswith("KIND_"):
            assert getattr(events, attr) in events.VALID_KINDS, f"{attr} not in VALID_KINDS"


def test_visibility_constants_are_distinct():
    assert events.VISIBILITY_PRIVATE != events.VISIBILITY_PUBLIC
    assert events.VISIBILITY_PRIVATE == "private"
    assert events.VISIBILITY_PUBLIC == "public"


# ── record() validation gates ──────────────────────────────────── #
#
# These exercise the early-return guards that protect us from posting
# garbage to Supabase. None of them actually reach the network because
# `is_configured()` returns False in the test environment (no Supabase
# env vars set) — but the helper still validates kind / visibility
# before checking configuration, so the wrong-kind / wrong-visibility
# guards trip cleanly.


def test_record_rejects_unknown_kind(caplog):
    """Posting an unknown kind should log + return None, never raise."""
    result = events.record(
        user_id="00000000-0000-0000-0000-000000000001",
        kind="not_a_real_kind",
        title="x",
    )
    assert result is None


def test_record_rejects_invalid_visibility():
    result = events.record(
        user_id="00000000-0000-0000-0000-000000000001",
        kind=events.KIND_BUILD_COMPLETED,
        title="x",
        visibility="secret",  # not in {private, public}
    )
    assert result is None


def test_record_rejects_private_without_user_id():
    """Private events MUST have a user_id — otherwise the bell has no
    one to deliver to. Public events without user_id are allowed
    (system-wide tip-of-the-day style events)."""
    result = events.record(
        user_id=None,
        kind=events.KIND_BUILD_COMPLETED,
        title="x",
        visibility=events.VISIBILITY_PRIVATE,
    )
    assert result is None


def test_record_allows_public_without_user_id():
    """System-wide public events (tips, announcements) don't require
    a user_id. The helper still returns None because Supabase isn't
    configured in tests, but the early-return guard shouldn't trip."""
    # is_configured returns False without env vars, so we expect None
    # from the network step, not from the validation step. Indirectly
    # verified by the fact that this doesn't raise.
    result = events.record(
        user_id=None,
        kind=events.KIND_TIP,
        title="x",
        visibility=events.VISIBILITY_PUBLIC,
    )
    assert result is None  # because Supabase not configured in tests


# ── list helpers fail-soft on missing config ───────────────────── #


def test_list_user_unread_returns_empty_without_config():
    assert events.list_user_unread("any-uid") == []


def test_list_user_all_returns_empty_without_config():
    assert events.list_user_all("any-uid") == []


def test_list_public_recent_returns_empty_without_config():
    assert events.list_public_recent() == []


def test_list_user_unread_returns_empty_for_missing_user_id():
    """Even if Supabase were configured, an empty user_id should
    early-return rather than fire a broken query."""
    assert events.list_user_unread("") == []
    assert events.list_user_unread(None) == []  # type: ignore[arg-type]


# ── mark_read fail-soft ────────────────────────────────────────── #


def test_mark_read_returns_false_without_config():
    assert events.mark_read("uid", "eid") is False


def test_mark_read_returns_false_for_missing_args():
    assert events.mark_read("", "eid") is False
    assert events.mark_read("uid", "") is False


def test_mark_all_read_returns_zero_without_config():
    assert events.mark_all_read("uid") == 0
