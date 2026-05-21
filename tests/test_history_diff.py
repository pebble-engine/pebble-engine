"""Tests for diff_against_snapshot (Phase 35, 2026-05-21).

Pins the diff API that powers the workspace's diff panel — the Phase-3
diagram pattern where after every refinement the UI shows "Frontend:
Updated components/Hero.tsx (3 lines) / Backend: Untouched".

The diff is approximate by design (set-based line counts, not LCS) —
tests assert on the categories and file lists, not on exact line counts
for genuinely modified files. The line-count assertions check the
direction (some added / some removed) rather than the exact numbers.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import pebble.history as history


@pytest.fixture
def slug_with_site(tmp_path, monkeypatch):
    """A slug pointed at a fresh tmp output dir, with site/ pre-populated."""
    monkeypatch.setattr(history, "OUTPUT_DIR", tmp_path)
    slug = "diff-test"
    site = tmp_path / slug / "site"
    site.mkdir(parents=True)
    # Seed with a small site
    (site / "package.json").write_text('{"name": "diff-test"}', encoding="utf-8")
    (site / "components").mkdir()
    (site / "components" / "Hero.tsx").write_text(
        "export function Hero() {\n  return <h1>Hello</h1>;\n}\n",
        encoding="utf-8",
    )
    (site / "components" / "Footer.tsx").write_text(
        "export function Footer() {\n  return <footer>2026</footer>;\n}\n",
        encoding="utf-8",
    )
    (site / "public").mkdir()
    (site / "public" / "logo.png").write_bytes(b"\x89PNG\x00binary\x00content")
    return slug, tmp_path


# ------------------------------------------------------------------ #
# Snapshot then mutate                                                #
# ------------------------------------------------------------------ #


def test_no_changes_returns_zero_total(slug_with_site):
    slug, _root = slug_with_site
    snap = history.snapshot_site(slug, reason="test")
    assert snap is not None
    # Don't mutate the site — diff should be empty
    summary = history.diff_against_snapshot(slug, snap.name)
    assert summary is not None
    assert summary.total_changed == 0
    assert summary.files == []


def test_modified_file_is_categorized_frontend(slug_with_site):
    slug, root = slug_with_site
    snap = history.snapshot_site(slug, reason="pre-refine")
    assert snap is not None
    # Mutate Hero.tsx
    hero = root / slug / "site" / "components" / "Hero.tsx"
    hero.write_text(
        "export function Hero() {\n  return <h1>Hello world</h1>;\n}\n",
        encoding="utf-8",
    )
    summary = history.diff_against_snapshot(slug, snap.name)
    assert summary is not None
    assert summary.total_changed == 1
    assert summary.files[0].path == "components/Hero.tsx"
    assert summary.files[0].status == "modified"
    assert summary.categories.get("Frontend") == 1


def test_added_file_shows_lines_added_only(slug_with_site):
    slug, root = slug_with_site
    snap = history.snapshot_site(slug, reason="pre-add")
    new_file = root / slug / "site" / "components" / "Pricing.tsx"
    new_file.write_text("// new pricing card\nexport function Pricing() {}\n", encoding="utf-8")
    summary = history.diff_against_snapshot(slug, snap.name)
    assert summary is not None
    matches = [f for f in summary.files if f.path == "components/Pricing.tsx"]
    assert len(matches) == 1
    diff = matches[0]
    assert diff.status == "added"
    assert diff.lines_added is not None
    assert diff.lines_added > 0
    assert diff.lines_removed == 0


def test_deleted_file_shows_status_deleted(slug_with_site):
    slug, root = slug_with_site
    snap = history.snapshot_site(slug, reason="pre-delete")
    (root / slug / "site" / "components" / "Footer.tsx").unlink()
    summary = history.diff_against_snapshot(slug, snap.name)
    assert summary is not None
    matches = [f for f in summary.files if f.path == "components/Footer.tsx"]
    assert len(matches) == 1
    assert matches[0].status == "deleted"
    assert matches[0].lines_added is None
    assert matches[0].lines_removed is None


def test_binary_modified_file_has_no_line_counts(slug_with_site):
    slug, root = slug_with_site
    snap = history.snapshot_site(slug, reason="pre-binary-mut")
    (root / slug / "site" / "public" / "logo.png").write_bytes(b"\x89PNG\x00new\x00content\x00more")
    summary = history.diff_against_snapshot(slug, snap.name)
    assert summary is not None
    matches = [f for f in summary.files if f.path == "public/logo.png"]
    assert len(matches) == 1
    assert matches[0].status == "modified"
    assert matches[0].lines_added is None
    assert matches[0].lines_removed is None


def test_multiple_categories_rollup(slug_with_site):
    slug, root = slug_with_site
    snap = history.snapshot_site(slug, reason="pre-multi")
    # Change frontend file
    (root / slug / "site" / "components" / "Hero.tsx").write_text("// changed\n", encoding="utf-8")
    # Add a config file
    (root / slug / "site" / "next.config.mjs").write_text("export default {};\n", encoding="utf-8")
    # Change a public asset
    (root / slug / "site" / "public" / "logo.png").write_bytes(b"different bytes")
    summary = history.diff_against_snapshot(slug, snap.name)
    assert summary is not None
    assert summary.total_changed == 3
    assert summary.categories.get("Frontend") == 1
    assert summary.categories.get("Config") == 1
    assert summary.categories.get("Assets") == 1


# ------------------------------------------------------------------ #
# Edge cases                                                          #
# ------------------------------------------------------------------ #


def test_missing_snapshot_returns_none(slug_with_site):
    slug, _ = slug_with_site
    assert history.diff_against_snapshot(slug, "nonexistent-snap") is None


def test_missing_current_site_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "OUTPUT_DIR", tmp_path)
    slug = "no-site-yet"
    # Create the snapshot directory directly (simulating an old snapshot
    # whose live site has since been deleted)
    snap_root = tmp_path / slug / "history" / "20260101T000000-test" / "site"
    snap_root.mkdir(parents=True)
    (snap_root / "package.json").write_text('{}', encoding="utf-8")
    assert history.diff_against_snapshot(slug, "20260101T000000-test") is None


def test_to_dict_is_json_serializable(slug_with_site):
    """The diff summary needs to round-trip through JSON for the API response."""
    import json
    slug, root = slug_with_site
    snap = history.snapshot_site(slug, reason="pre-json")
    (root / slug / "site" / "components" / "Hero.tsx").write_text("// changed\n", encoding="utf-8")
    summary = history.diff_against_snapshot(slug, snap.name)
    assert summary is not None
    payload = summary.to_dict()
    # Must round-trip cleanly
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)
    assert decoded["total_changed"] == summary.total_changed
    assert decoded["files"][0]["path"] == summary.files[0].path


def test_categorize_known_paths():
    assert history._categorize("components/Hero.tsx") == "Frontend"
    assert history._categorize("app/page.tsx") == "Frontend"
    assert history._categorize("public/logo.png") == "Assets"
    assert history._categorize("api/contact.ts") == "Backend"
    assert history._categorize("tests/test_foo.py") == "Tests"
    assert history._categorize("package.json") == "Config"
    assert history._categorize("next.config.mjs") == "Config"
    assert history._categorize("random/path/file.txt") == "Other"
