"""snapshot_site / diff_against_snapshot must exclude node_modules + build dirs.

2026-06-01 live-test bug: once a project's preview is warmed locally, the
on-demand warmup runs `npm install`, so output/<slug>/site/ gains a
node_modules tree (~12k files). snapshot_site() copytree'd the WHOLE site
inside the per-slug project_lock, so each edit held the lock for minutes
copying node_modules — and every other edit 409'd with "another edit is
already in progress". diff_against_snapshot() walked + byte-compared the
live site (incl. node_modules) too. Both must skip dependency/build dirs.
"""
import pebble.history as history


def _make_site(tmp_path, slug):
    site = tmp_path / slug / "site"
    (site / "app").mkdir(parents=True)
    (site / "app" / "page.tsx").write_text("export default () => <main/>;", encoding="utf-8")
    (site / "app" / "globals.css").write_text("@tailwind base;", encoding="utf-8")
    # Simulate an installed dependency tree + build output.
    (site / "node_modules" / "react" / "deep" / "nested").mkdir(parents=True)
    (site / "node_modules" / "react" / "index.js").write_text("module.exports={}", encoding="utf-8")
    (site / "node_modules" / "react" / "deep" / "nested" / "x.js").write_text("//x", encoding="utf-8")
    (site / ".next" / "cache").mkdir(parents=True)
    (site / ".next" / "cache" / "blob").write_text("binary", encoding="utf-8")
    return site


def test_snapshot_excludes_node_modules_and_next(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "OUTPUT_DIR", tmp_path)
    _make_site(tmp_path, "p1")

    snap_dir = history.snapshot_site("p1", reason="visual-edit-text")
    assert snap_dir is not None
    snap_site = snap_dir / "site"

    # Source files ARE snapshotted:
    assert (snap_site / "app" / "page.tsx").exists()
    assert (snap_site / "app" / "globals.css").exists()
    # Dependency + build dirs are NOT:
    assert not (snap_site / "node_modules").exists(), "node_modules must be excluded"
    assert not (snap_site / ".next").exists(), ".next must be excluded"

    # The recorded file count reflects source files only (2), not ~12k.
    import json
    meta = json.loads((snap_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["files_count"] == 2


def test_snapshot_still_skips_truly_empty_site(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "OUTPUT_DIR", tmp_path)
    site = tmp_path / "empty" / "site"
    site.mkdir(parents=True)
    assert history.snapshot_site("empty") is None


def test_snapshot_not_empty_when_only_node_modules_present(tmp_path, monkeypatch):
    """A site that somehow has ONLY node_modules (no real source) snapshots
    as empty — there's nothing meaningful to record."""
    monkeypatch.setattr(history, "OUTPUT_DIR", tmp_path)
    site = tmp_path / "depsonly" / "site"
    (site / "node_modules" / "x").mkdir(parents=True)
    (site / "node_modules" / "x" / "a.js").write_text("//a", encoding="utf-8")
    assert history.snapshot_site("depsonly") is None


def test_diff_ignores_node_modules(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "OUTPUT_DIR", tmp_path)
    _make_site(tmp_path, "p2")
    snap_dir = history.snapshot_site("p2", reason="pre-edit")
    snapshot_id = snap_dir.name

    # Mutate a real file + add MORE node_modules churn (must be ignored).
    site = tmp_path / "p2" / "site"
    (site / "app" / "page.tsx").write_text("export default () => <main>edited</main>;", encoding="utf-8")
    (site / "node_modules" / "react" / "extra.js").write_text("//noise", encoding="utf-8")

    diff = history.diff_against_snapshot("p2", snapshot_id)
    assert diff is not None
    changed = {fd.path for fd in diff.files}
    assert "app/page.tsx" in changed
    # No node_modules path should appear in the diff:
    assert not any("node_modules" in p for p in changed)
