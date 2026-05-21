"""Build Integrity tests — Phase 36 (2026-05-21).

Pins the curated checklist contract + the publishable gate logic. Doesn't
re-test individual check functions — they're owned by tests/test_evals.py
and friends. These tests assert on the surface API:

  - CRITICAL_CHECKS is a stable, ordered list
  - Each entry points at a real check function (no broken refs)
  - run_integrity() returns None for missing slugs
  - is_publishable() respects must_pass semantics
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import pebble.evals.runner as eval_runner
from pebble.integrity import (
    CRITICAL_CHECKS,
    IntegrityCheck,
    IntegrityResult,
    is_publishable,
    run_integrity,
)


# ------------------------------------------------------------------ #
# CRITICAL_CHECKS shape                                                #
# ------------------------------------------------------------------ #


def test_critical_checks_is_non_empty():
    assert len(CRITICAL_CHECKS) > 0


def test_critical_checks_have_unique_ids():
    ids = [c.id for c in CRITICAL_CHECKS]
    assert len(ids) == len(set(ids)), f"duplicate id in CRITICAL_CHECKS: {ids}"


def test_critical_checks_have_non_empty_labels():
    for c in CRITICAL_CHECKS:
        assert c.label.strip(), f"empty label for {c.id}"
        assert len(c.label) < 60, f"label too long for {c.id} ({len(c.label)} chars)"


def test_critical_checks_fns_are_callable():
    for c in CRITICAL_CHECKS:
        assert callable(c.fn), f"{c.id}.fn is not callable"


def test_at_least_some_checks_are_must_pass():
    """Otherwise the publishable gate is meaningless."""
    must_pass_count = sum(1 for c in CRITICAL_CHECKS if c.must_pass)
    assert must_pass_count >= 3, "expected at least 3 must_pass checks; got " + str(must_pass_count)


# ------------------------------------------------------------------ #
# run_integrity                                                       #
# ------------------------------------------------------------------ #


def test_missing_build_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(eval_runner, "OUTPUT_DIR", tmp_path)
    import pebble.integrity as integrity_mod
    monkeypatch.setattr(integrity_mod, "OUTPUT_DIR", tmp_path)
    assert run_integrity("nonexistent-slug") is None


def test_build_without_brief_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(eval_runner, "OUTPUT_DIR", tmp_path)
    import pebble.integrity as integrity_mod
    monkeypatch.setattr(integrity_mod, "OUTPUT_DIR", tmp_path)
    # Create dir but no brief.json
    (tmp_path / "incomplete").mkdir()
    assert run_integrity("incomplete") is None


def test_minimal_build_runs_all_checks(tmp_path, monkeypatch):
    """A build with brief.json but no site/ should still run every check —
    each check either passes, skips, or fails gracefully."""
    monkeypatch.setattr(eval_runner, "OUTPUT_DIR", tmp_path)
    import pebble.integrity as integrity_mod
    monkeypatch.setattr(integrity_mod, "OUTPUT_DIR", tmp_path)

    slug = "minimal"
    build = tmp_path / slug
    build.mkdir()
    (build / "brief.json").write_text(json.dumps({
        "business_name": "Test", "business_type": "test", "extra_context": ""
    }))

    results = run_integrity(slug)
    assert results is not None
    assert len(results) == len(CRITICAL_CHECKS)
    # Order is preserved
    assert [r.id for r in results] == [c.id for c in CRITICAL_CHECKS]
    # Every result has the four expected status values, never None
    for r in results:
        assert r.status in {"pass", "fail", "skip", "error"}
        assert r.label
        assert r.id


# ------------------------------------------------------------------ #
# is_publishable                                                       #
# ------------------------------------------------------------------ #


def _result(id_: str, status: str, must_pass: bool) -> IntegrityResult:
    return IntegrityResult(id=id_, label=id_, status=status, message="", must_pass=must_pass)


def test_all_passing_is_publishable():
    rs = [_result("a", "pass", True), _result("b", "pass", True), _result("c", "pass", False)]
    assert is_publishable(rs) is True


def test_must_pass_failing_blocks_publish():
    rs = [_result("a", "pass", True), _result("b", "fail", True)]
    assert is_publishable(rs) is False


def test_soft_failing_does_not_block():
    """A non-must_pass failure is warning-only."""
    rs = [_result("a", "pass", True), _result("b", "fail", False)]
    assert is_publishable(rs) is True


def test_must_pass_skipped_blocks_publish():
    """Skip is not pass — if a hard gate couldn't even run, we don't ship."""
    rs = [_result("a", "skip", True)]
    assert is_publishable(rs) is False


def test_must_pass_errored_blocks_publish():
    rs = [_result("a", "error", True)]
    assert is_publishable(rs) is False


def test_empty_results_publishable():
    """Vacuously true — no checks to fail."""
    assert is_publishable([]) is True


# ------------------------------------------------------------------ #
# Result.to_dict shape                                                #
# ------------------------------------------------------------------ #


def test_to_dict_has_required_keys():
    r = _result("foo", "pass", True)
    d = r.to_dict()
    assert set(d.keys()) == {"id", "label", "status", "message", "must_pass"}
