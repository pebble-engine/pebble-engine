"""Smoke tests for pebble.morning_brief — the Tier-2 morning brief generator.

Per-section unit tests with synthetic fixtures so the brief works on a
fresh checkout (no engine logs, no users) AND on a populated repo. The
big invariant we care about: a bug in one section MUST NOT prevent the
others from rendering — that's the Tier-2 reliability principle baked
into build_brief()'s try/except.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import pebble.morning_brief as mb


# ---------------------------------------------------------------------------
# Fixture — point all module-level paths at a clean tmp_path
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_root(tmp_path, monkeypatch):
    """Repoint mb's module globals at tmp_path so every section reads
    from an isolated fake repo. Sentry/Supabase env-var stubs cleared
    so the PAT-gated sections take the no-op path by default."""
    mb._set_root(tmp_path)
    monkeypatch.delenv("SENTRY_PAT", raising=False)
    monkeypatch.delenv("PEBBLE_SUPABASE_PAT", raising=False)
    return tmp_path


# ---------------------------------------------------------------------------
# Engine log section
# ---------------------------------------------------------------------------

def test_engine_log_missing_file_is_info_not_crash(temp_root):
    """Fresh checkout has no engine.err.log — section should degrade
    gracefully to info, not raise."""
    section = mb.section_engine_log(window_hours=24)
    assert section.severity == "info"
    assert "no engine.err.log yet" in "\n".join(section.lines)


def _now_iso() -> str:
    """ISO timestamp in the same format pebble/log.py emits."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def test_engine_log_picks_up_errors(temp_root):
    err_log = temp_root / "engine.err.log"
    err_log.write_text(
        f"{_now_iso()} INFO  normal line\n"
        f"{_now_iso()} ERROR something exploded\n"
        "Traceback (most recent call last):\n"
        "  File \"foo.py\", line 1, in <module>\n"
        "    raise ValueError('boom')\n"
        "ValueError: boom\n",
        encoding="utf-8",
    )
    section = mb.section_engine_log(window_hours=24)
    assert section.severity == "critical"
    # One ERROR record (the traceback frames attach to it, not separate)
    assert section.meta["error_count"] == 1


def test_engine_log_warnings_only_is_warn(temp_root):
    err_log = temp_root / "engine.err.log"
    err_log.write_text(
        f"{_now_iso()} WARN  cookie path missing trailing slash\n",
        encoding="utf-8",
    )
    section = mb.section_engine_log(window_hours=24)
    assert section.severity == "warn"
    assert section.meta["warn_count"] >= 1


def test_engine_log_noise_patterns_suppressed(temp_root):
    """DeprecationWarning shouldn't push the section to warn."""
    err_log = temp_root / "engine.err.log"
    err_log.write_text(
        f"{_now_iso()} WARN  DeprecationWarning: foo will be removed in v2\n",
        encoding="utf-8",
    )
    section = mb.section_engine_log(window_hours=24)
    assert section.severity == "ok"
    assert section.meta["warn_count"] == 0


def test_engine_log_filters_old_records_out(temp_root):
    """Errors older than the window should NOT bump severity."""
    err_log = temp_root / "engine.err.log"
    # Build a log with one old error (8 days ago) and nothing recent
    old_ts = (datetime.now(timezone.utc) - timedelta(days=8)).strftime("%Y-%m-%dT%H:%M:%S")
    err_log.write_text(
        f"{old_ts} ERROR ancient explosion (should not surface)\n",
        encoding="utf-8",
    )
    section = mb.section_engine_log(window_hours=24)
    assert section.severity == "ok"
    assert section.meta["error_count"] == 0
    # Brief mentions the older record count for honesty
    assert "outside window" in "\n".join(section.lines)


def test_engine_log_traceback_attaches_to_parent_in_window(temp_root):
    """Untimestamped continuation lines belong to the previous record's
    in-window decision. A traceback under a recent ERROR comes through;
    a traceback under an old error stays buried."""
    err_log = temp_root / "engine.err.log"
    old_ts = (datetime.now(timezone.utc) - timedelta(days=8)).strftime("%Y-%m-%dT%H:%M:%S")
    err_log.write_text(
        f"{old_ts} ERROR old issue (out of window)\n"
        f"  File 'old.py', line 1\n"
        f"OldError: old\n"
        f"{_now_iso()} ERROR recent issue (in window)\n"
        f"  File 'new.py', line 1\n"
        f"NewError: new\n",
        encoding="utf-8",
    )
    section = mb.section_engine_log(window_hours=24)
    assert section.severity == "critical"
    # Only the recent record counts
    assert section.meta["error_count"] == 1


# ---------------------------------------------------------------------------
# Build activity section
# ---------------------------------------------------------------------------

def test_builds_empty_output_dir_is_info(temp_root):
    section = mb.section_builds(window_hours=24)
    assert section.severity == "info"
    assert "no output/ directory yet" in section.lines[0]


def test_builds_counts_within_window(temp_root):
    output = temp_root / "output"
    output.mkdir()
    recent = datetime.now(timezone.utc) - timedelta(hours=2)
    old    = datetime.now(timezone.utc) - timedelta(days=5)
    for slug, ts, cost in [("alpha", recent, 0.02), ("beta", recent, 0.05),
                            ("ancient", old, 0.99)]:
        d = output / slug
        d.mkdir()
        (d / "build_meta.json").write_text(json.dumps({
            "built_at": ts.isoformat(),
            "model":    "qwen/qwen3.6-plus",
            "estimated_cost_usd": cost,
            "billable": True,
            "tokens_used": {"input": 1000, "output": 500},
        }), encoding="utf-8")
    section = mb.section_builds(window_hours=24)
    # Only the 2 recent builds count
    assert section.meta["count"] == 2
    # The ancient $0.99 build must NOT be summed into the total
    assert section.meta["total_cost_usd"] == pytest.approx(0.07)


def test_builds_handles_unparseable_meta_gracefully(temp_root):
    """A corrupt build_meta.json should be skipped, not crash."""
    output = temp_root / "output"
    output.mkdir()
    bad = output / "broken"
    bad.mkdir()
    (bad / "build_meta.json").write_text("not json", encoding="utf-8")
    section = mb.section_builds(window_hours=24)
    assert section.meta["count"] == 0   # silently skipped


# ---------------------------------------------------------------------------
# Engagement section
# ---------------------------------------------------------------------------

def test_engagement_empty_dir_is_info(temp_root):
    section = mb.section_engagement(window_hours=24)
    assert section.severity == "info"


def test_engagement_aggregates_per_user(temp_root):
    eng = temp_root / "output" / ".engagement"
    eng.mkdir(parents=True)
    now = datetime.now(timezone.utc)
    (eng / "user-aaa.jsonl").write_text("\n".join([
        json.dumps({"event": "build_completed", "timestamp": now.isoformat()}),
        json.dumps({"event": "build_completed", "timestamp": now.isoformat()}),
        json.dumps({"event": "project_starred", "timestamp": now.isoformat()}),
    ]), encoding="utf-8")
    section = mb.section_engagement(window_hours=24)
    assert section.meta["active_users"] == 1


# ---------------------------------------------------------------------------
# Subscriptions section
# ---------------------------------------------------------------------------

def test_subscriptions_empty_users_dir_is_info(temp_root):
    section = mb.section_subscriptions(_window_hours=24)
    assert section.severity == "info"


def test_subscriptions_aggregates_plans_and_pending_deletion(temp_root):
    users = temp_root / "output" / ".users"
    users.mkdir(parents=True)
    # Two active starter accounts
    for uid in ["u1", "u2"]:
        d = users / uid
        d.mkdir()
        (d / "subscription.json").write_text(json.dumps({
            "plan": "starter", "status": "active",
        }), encoding="utf-8")
    # One pending-deletion user
    (users / "u3").mkdir()
    (users / "u3" / "pending_deletion.json").write_text("{}", encoding="utf-8")
    section = mb.section_subscriptions(_window_hours=24)
    text = "\n".join(section.lines)
    assert "starter×2" in text
    assert "1 account(s) pending deletion" in text


# ---------------------------------------------------------------------------
# Sentry + Supabase no-op (PAT missing)
# ---------------------------------------------------------------------------

def test_sentry_skipped_without_pat(temp_root):
    section = mb.section_sentry(window_hours=24)
    assert section.severity == "info"
    assert "SENTRY_PAT not set" in section.lines[0]


def test_supabase_advisors_skipped_without_pat(temp_root):
    section = mb.section_supabase_advisors(_window_hours=24)
    assert section.severity == "info"
    assert "PEBBLE_SUPABASE_PAT not set" in section.lines[0]


# ---------------------------------------------------------------------------
# Top-level build_brief — one bad section MUST NOT poison the rest
# ---------------------------------------------------------------------------

def test_build_brief_isolates_section_failures(temp_root, monkeypatch):
    """If one section builder raises, the brief should still include
    every other section + a FAILED marker for the broken one."""
    def boom(_window_hours):
        raise RuntimeError("intentional test crash")

    # Replace one builder with one that always crashes
    monkeypatch.setattr(mb, "_SECTION_BUILDERS",
                        [boom, mb.section_engine_log, mb.section_git])
    brief = mb.build_brief(window_hours=24)
    titles = [s.title for s in brief.sections]
    assert any("FAILED" in t for t in titles)
    assert "Engine errors" in titles
    assert "Code activity (git)" in titles


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

def test_render_markdown_includes_severity_badge(temp_root):
    brief = mb.build_brief(window_hours=24)
    out = mb.render_markdown(brief)
    assert out.startswith("# ")
    # Severity badge from _SEVERITY_BADGE table — one of these MUST appear
    assert any(b in out for b in ("🟢", "🔵", "🟡", "🔴"))


def test_render_json_is_parseable(temp_root):
    brief = mb.build_brief(window_hours=24)
    out = mb.render_json(brief)
    parsed = json.loads(out)
    assert "sections" in parsed
    assert parsed["window_hours"] == 24
