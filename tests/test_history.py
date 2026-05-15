"""Tests for ``pebble.history``.

Covers: snapshot create, list ordering, restore round-trip, empty-site
no-op, missing-snapshot error, snapshot-on-restore.
"""
from __future__ import annotations

import time
from pathlib import Path

import pytest

import pebble.history as h


@pytest.fixture
def fake_output(tmp_path, monkeypatch):
    """Redirect pebble.history's OUTPUT_DIR to a tmp path so each test is
    isolated and the real output/ tree is untouched."""
    monkeypatch.setattr(h, "OUTPUT_DIR", tmp_path / "output")
    return tmp_path / "output"


def _seed_site(output_dir: Path, slug: str, files: dict[str, str]) -> Path:
    site = output_dir / slug / "site"
    site.mkdir(parents=True, exist_ok=True)
    for rel, content in files.items():
        full = site / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
    return site


# ---- snapshot_site --------------------------------------------------------

def test_snapshot_creates_directory_with_meta(fake_output):
    _seed_site(fake_output, "slug-1", {
        "app/page.tsx": "export default function P() { return <main>hi</main>; }",
        "package.json": '{"name":"x"}',
    })
    snap = h.snapshot_site("slug-1", reason="generate", source="POST /api/generate")
    assert snap is not None
    assert snap.exists()
    assert (snap / "site" / "app" / "page.tsx").read_text() == "export default function P() { return <main>hi</main>; }"
    meta = (snap / "meta.json").read_text()
    assert "generate" in meta
    assert "files_count" in meta


def test_snapshot_returns_none_when_no_site_dir(fake_output):
    snap = h.snapshot_site("nonexistent-slug", reason="generate")
    assert snap is None


def test_snapshot_returns_none_when_site_is_empty(fake_output):
    # Empty site dir — no files. We don't want to clutter history with empty snapshots.
    (fake_output / "empty-slug" / "site").mkdir(parents=True)
    snap = h.snapshot_site("empty-slug")
    assert snap is None


def test_snapshot_sanitizes_reason_for_filesystem(fake_output):
    _seed_site(fake_output, "slug-1", {"a.txt": "x"})
    snap = h.snapshot_site("slug-1", reason="POST /api/refine — make it friendlier!")
    assert snap is not None
    # The directory name should have no spaces or punctuation that fails on Windows.
    assert " " not in snap.name
    assert "/" not in snap.name


# ---- list_history --------------------------------------------------------

def test_list_history_returns_newest_first(fake_output):
    _seed_site(fake_output, "slug-1", {"a.txt": "v1"})
    h.snapshot_site("slug-1", reason="generate")
    time.sleep(1.05)  # snapshot ids are second-resolution; force a different timestamp
    (fake_output / "slug-1" / "site" / "a.txt").write_text("v2", encoding="utf-8")
    h.snapshot_site("slug-1", reason="refine")
    time.sleep(1.05)
    (fake_output / "slug-1" / "site" / "a.txt").write_text("v3", encoding="utf-8")
    h.snapshot_site("slug-1", reason="visual-edit")

    entries = h.list_history("slug-1")
    assert len(entries) == 3
    # Reason order = newest first
    assert [e.reason for e in entries] == ["visual-edit", "refine", "generate"]


def test_list_history_empty_when_no_history_dir(fake_output):
    _seed_site(fake_output, "slug-1", {"a.txt": "x"})
    assert h.list_history("slug-1") == []


def test_history_entry_has_relative_path_for_ui(fake_output):
    _seed_site(fake_output, "slug-1", {"a.txt": "x"})
    h.snapshot_site("slug-1", reason="generate")
    entries = h.list_history("slug-1")
    assert entries[0].relative_path.startswith("output/slug-1/history/")
    assert entries[0].snapshot_id


# ---- restore_snapshot ----------------------------------------------------

def test_restore_brings_back_old_file_content(fake_output):
    _seed_site(fake_output, "slug-1", {"app/page.tsx": "ORIGINAL"})
    h.snapshot_site("slug-1", reason="generate")
    time.sleep(1.05)
    # Mutate
    (fake_output / "slug-1" / "site" / "app" / "page.tsx").write_text("MUTATED", encoding="utf-8")
    # Restore
    entries = h.list_history("slug-1")
    restored = h.restore_snapshot("slug-1", entries[0].snapshot_id)
    assert restored >= 1
    assert (fake_output / "slug-1" / "site" / "app" / "page.tsx").read_text() == "ORIGINAL"


def test_restore_snapshots_current_first_so_restore_is_undoable(fake_output):
    _seed_site(fake_output, "slug-1", {"a.txt": "v1"})
    h.snapshot_site("slug-1", reason="generate")  # snap 1
    time.sleep(1.05)
    (fake_output / "slug-1" / "site" / "a.txt").write_text("v2", encoding="utf-8")
    h.snapshot_site("slug-1", reason="refine")     # snap 2
    time.sleep(1.05)
    (fake_output / "slug-1" / "site" / "a.txt").write_text("v3", encoding="utf-8")

    # Restore back to snap 1 (originally "v1") — the restore should ALSO
    # create a fresh snapshot capturing the v3 state we're rolling away from.
    entries = h.list_history("slug-1")
    snap_1_id = next(e.snapshot_id for e in entries if e.reason == "generate")
    h.restore_snapshot("slug-1", snap_1_id)

    entries_after = h.list_history("slug-1")
    # 3 snapshots existed (generate, refine, and the implicit pre-restore snapshot of v3)
    assert len(entries_after) == 3
    reasons = [e.reason for e in entries_after]
    assert "restore" in reasons


def test_restore_missing_snapshot_raises(fake_output):
    _seed_site(fake_output, "slug-1", {"a.txt": "x"})
    with pytest.raises(FileNotFoundError):
        h.restore_snapshot("slug-1", "20990101T000000-bogus")


def test_restore_removes_files_not_in_snapshot(fake_output):
    """Restoring should reset the site to the snapshot — files added after the
    snapshot must NOT linger."""
    _seed_site(fake_output, "slug-1", {"a.txt": "v1"})
    h.snapshot_site("slug-1", reason="generate")
    time.sleep(1.05)
    # Add a new file after the snapshot
    (fake_output / "slug-1" / "site" / "new-file.txt").write_text("added later", encoding="utf-8")
    assert (fake_output / "slug-1" / "site" / "new-file.txt").exists()

    entries = h.list_history("slug-1")
    h.restore_snapshot("slug-1", entries[0].snapshot_id, snapshot_current=False)

    # The file that wasn't in the snapshot should be gone
    assert not (fake_output / "slug-1" / "site" / "new-file.txt").exists()
    assert (fake_output / "slug-1" / "site" / "a.txt").read_text() == "v1"
