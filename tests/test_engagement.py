"""Tests for pebble.engagement — per-user product analytics.

This module is the PRIVACY-CRITICAL surface (T17, 2026-05-17). Three
classes of tests:

1. **Core API** — log_event / read_user_events / engagement_score.
2. **Privacy regression** — the event row must contain ONLY {event,
   timestamp}. No content. No DNA picks. No edited text. The user_id
   lives in the FILENAME, never inside any row.
3. **Input validation** — user_id and event_name must be sanitized so
   no caller can write outside the engagement dir or accidentally leak
   user input via the event-name field.

The engagement_summary endpoint test lives in test_admin.py; this file
covers the storage primitives.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from pebble import engagement


@pytest.fixture
def isolated_storage(tmp_path, monkeypatch):
    """Point engagement storage at tmp_path so tests don't pollute output/."""
    monkeypatch.setattr(engagement, "_engagement_dir", lambda: tmp_path / ".engagement")
    return tmp_path


# ---------------------------------------------------------------------------
# log_event
# ---------------------------------------------------------------------------

def test_log_event_creates_file_with_one_line(isolated_storage):
    assert engagement.log_event("user-abc", "build_completed") is True
    f = isolated_storage / ".engagement" / "user-abc.jsonl"
    assert f.exists()
    lines = f.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["event"] == "build_completed"
    assert "timestamp" in row


def test_log_event_appends_subsequent_calls(isolated_storage):
    engagement.log_event("u1", "build_completed")
    engagement.log_event("u1", "refine_used")
    engagement.log_event("u1", "visual_edit_used")
    f = isolated_storage / ".engagement" / "u1.jsonl"
    lines = f.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    events = [json.loads(l)["event"] for l in lines]
    assert events == ["build_completed", "refine_used", "visual_edit_used"]


def test_log_event_noop_on_none_user_id(isolated_storage):
    assert engagement.log_event(None, "build_completed") is False
    storage = isolated_storage / ".engagement"
    assert not storage.exists() or not any(storage.iterdir())


def test_log_event_noop_on_empty_user_id(isolated_storage):
    assert engagement.log_event("", "build_completed") is False


def test_log_event_rejects_path_traversal_in_user_id(isolated_storage):
    """User-id becomes the FILENAME, so '..' / '/' / '\\' must be rejected
    to prevent writing outside the engagement dir."""
    assert engagement.log_event("../escape", "evil") is False
    assert engagement.log_event("a/b", "evil") is False
    assert engagement.log_event("a\\b", "evil") is False
    assert engagement.log_event("..", "evil") is False


def test_log_event_rejects_extremely_long_user_id(isolated_storage):
    """Filename length caps protect against absurd inputs."""
    assert engagement.log_event("a" * 500, "evil") is False


def test_log_event_emits_only_event_and_timestamp_keys(isolated_storage):
    """PRIVACY REGRESSION — the most important test in this file.

    The event row must contain ONLY {event, timestamp}. Adding a user_id
    field would defeat the privacy moat (file path already encodes that
    and adding it inside the row makes the row identifiable on its own).
    Adding ANY other field risks leaking the content the user was editing
    when the event fired."""
    engagement.log_event("u1", "dna_picked")
    row = json.loads((isolated_storage / ".engagement" / "u1.jsonl").read_text().splitlines()[0])
    assert set(row.keys()) == {"event", "timestamp"}


def test_log_event_rejects_uppercase_event_name(isolated_storage):
    """Event names must be lowercase snake_case identifiers. Mixed case
    risks accidental data leakage if a caller passes user input."""
    assert engagement.log_event("u1", "BUILD_COMPLETED") is False


def test_log_event_rejects_event_name_with_spaces(isolated_storage):
    assert engagement.log_event("u1", "build completed") is False


def test_log_event_rejects_event_name_with_punctuation(isolated_storage):
    assert engagement.log_event("u1", "build!") is False
    assert engagement.log_event("u1", "build.completed") is False
    assert engagement.log_event("u1", "build/completed") is False


def test_log_event_rejects_event_name_starting_with_digit(isolated_storage):
    assert engagement.log_event("u1", "1build") is False


def test_log_event_accepts_canonical_event_names(isolated_storage):
    for name in (
        "build_completed",
        "refine_used",
        "visual_edit_used",
        "block_inserted",
        "project_starred",
        "project_deleted",
        "ok_event_1",
    ):
        assert engagement.log_event("u1", name) is True, name


# ---------------------------------------------------------------------------
# read_user_events
# ---------------------------------------------------------------------------

def test_read_user_events_empty_for_unknown_user(isolated_storage):
    assert engagement.read_user_events("nobody") == []


def test_read_user_events_returns_logged_events_chronologically(isolated_storage):
    engagement.log_event("u1", "build_completed")
    engagement.log_event("u1", "refine_used")
    events = engagement.read_user_events("u1")
    assert len(events) == 2
    assert events[0]["event"] == "build_completed"
    assert events[1]["event"] == "refine_used"


def test_read_user_events_respects_limit(isolated_storage):
    for i in range(10):
        engagement.log_event("u1", f"event_{i}")
    events = engagement.read_user_events("u1", limit=3)
    assert len(events) == 3
    assert [e["event"] for e in events] == ["event_7", "event_8", "event_9"]


def test_read_user_events_returns_empty_for_unsafe_user_id(isolated_storage):
    assert engagement.read_user_events("../escape") == []


def test_read_user_events_skips_corrupt_lines(isolated_storage):
    """A partially-written jsonl line shouldn't crash the reader."""
    storage = isolated_storage / ".engagement"
    storage.mkdir()
    (storage / "u1.jsonl").write_text(
        '{"event":"build_completed","timestamp":"2026-05-17T20:00:00+00:00"}\n'
        'not-valid-json\n'
        '{"event":"refine_used","timestamp":"2026-05-17T21:00:00+00:00"}\n'
    )
    events = engagement.read_user_events("u1")
    assert len(events) == 2
    assert [e["event"] for e in events] == ["build_completed", "refine_used"]


# ---------------------------------------------------------------------------
# engagement_score
# ---------------------------------------------------------------------------

def test_engagement_score_at_risk_for_zero_events(isolated_storage):
    assert engagement.engagement_score("nobody") == "at_risk"


def test_engagement_score_at_risk_for_one_distinct_event(isolated_storage):
    engagement.log_event("u1", "build_completed")
    engagement.log_event("u1", "build_completed")  # duplicate type
    assert engagement.engagement_score("u1") == "at_risk"


def test_engagement_score_active_for_two_distinct_events(isolated_storage):
    engagement.log_event("u1", "build_completed")
    engagement.log_event("u1", "refine_used")
    assert engagement.engagement_score("u1") == "active"


def test_engagement_score_active_for_four_distinct_events(isolated_storage):
    for e in ("build_completed", "refine_used", "visual_edit_used", "block_inserted"):
        engagement.log_event("u1", e)
    assert engagement.engagement_score("u1") == "active"


def test_engagement_score_power_for_five_distinct_events(isolated_storage):
    for e in ("build_completed", "refine_used", "visual_edit_used",
              "block_inserted", "project_starred"):
        engagement.log_event("u1", e)
    assert engagement.engagement_score("u1") == "power"


def test_engagement_score_excludes_events_older_than_30_days(isolated_storage):
    """A user who fired 6 different events 31 days ago is at-risk now."""
    storage = isolated_storage / ".engagement"
    storage.mkdir()
    old_ts = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
    events = [
        json.dumps({"event": f"e_{i}", "timestamp": old_ts}, separators=(",", ":"))
        for i in range(6)
    ]
    (storage / "u1.jsonl").write_text("\n".join(events) + "\n")
    assert engagement.engagement_score("u1") == "at_risk"


def test_engagement_score_counts_distinct_types_not_total(isolated_storage):
    """100 of the same event type = 1 distinct = at_risk."""
    for _ in range(100):
        engagement.log_event("u1", "build_completed")
    assert engagement.engagement_score("u1") == "at_risk"


# ---------------------------------------------------------------------------
# engagement_summary
# ---------------------------------------------------------------------------

def test_engagement_summary_empty_when_no_storage(isolated_storage):
    assert engagement.engagement_summary() == []


def test_engagement_summary_lists_users_with_scores(isolated_storage):
    engagement.log_event("u1", "build_completed")
    for e in ("a_event", "b_event", "c_event"):
        engagement.log_event("u2", e)
    for e in ("a_event", "b_event", "c_event", "d_event", "e_event"):
        engagement.log_event("u3", e)
    summary = engagement.engagement_summary()
    by_id = {s["user_id"]: s for s in summary}
    assert by_id["u1"]["score"] == "at_risk"
    assert by_id["u1"]["distinct_events"] == 1
    assert by_id["u1"]["total_events"] == 1
    assert by_id["u2"]["score"] == "active"
    assert by_id["u2"]["distinct_events"] == 3
    assert by_id["u3"]["score"] == "power"
    assert by_id["u3"]["distinct_events"] == 5


def test_engagement_summary_sorts_power_then_active_then_at_risk(isolated_storage):
    """Sort order matters for the admin UI — show power users first."""
    engagement.log_event("u_low", "build_completed")
    for e in ("a_event", "b_event", "c_event", "d_event", "e_event"):
        engagement.log_event("u_high", e)
    for e in ("a_event", "b_event"):
        engagement.log_event("u_mid", e)
    summary = engagement.engagement_summary()
    assert [s["user_id"] for s in summary] == ["u_high", "u_mid", "u_low"]


def test_engagement_summary_skips_files_with_unsafe_names(isolated_storage):
    """Defense in depth — if a malicious file lands in the dir, ignore it."""
    storage = isolated_storage / ".engagement"
    storage.mkdir()
    (storage / "good.jsonl").write_text(
        '{"event":"build_completed","timestamp":"' +
        datetime.now(timezone.utc).isoformat() + '"}\n'
    )
    (storage / "weird name.jsonl").write_text(
        '{"event":"build_completed","timestamp":"' +
        datetime.now(timezone.utc).isoformat() + '"}\n'
    )
    summary = engagement.engagement_summary()
    ids = {s["user_id"] for s in summary}
    assert ids == {"good"}


# ---------------------------------------------------------------------------
# Privacy regression — content NEVER leaks
# ---------------------------------------------------------------------------

def test_engagement_storage_never_contains_user_content(isolated_storage):
    """Log a bunch of events with potentially-sensitive-looking event names
    (NOT user content) and assert the storage files contain ONLY the event
    names + timestamps — no other text. Stand-in for the broader rule:
    nothing the user typed ever lands in engagement.jsonl."""
    engagement.log_event("u1", "build_completed")
    engagement.log_event("u1", "refine_used")
    engagement.log_event("u2", "visual_edit_used")
    sensitive_markers = [
        "swiss_magazine",      # DNA card name
        "Get a quote",         # edited CTA text
        "#ff6600",             # color picker value
        "user@example.com",    # email
        "(212) 555-1234",      # phone
        "Bearer ",             # auth token prefix
    ]
    storage = isolated_storage / ".engagement"
    for f in storage.glob("*.jsonl"):
        text = f.read_text(encoding="utf-8")
        for marker in sensitive_markers:
            assert marker not in text, (
                f"engagement file {f.name} contains marker '{marker}' — content leak!"
            )
