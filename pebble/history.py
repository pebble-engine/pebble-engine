"""Per-build version history — snapshot site directories before destructive
edits so users can roll back to a known-good state.

Direct counter to the #1 complaint about Base44 ("no rollback, the AI just
overwrote my working file") and a foundation for the safe refinement +
visual-edit flows: any time the engine is about to overwrite the rendered
`site/` directory, we snapshot the previous state first.

Snapshots live at::

    output/<slug>/history/<timestamp>-<reason>/
        site/...      ← full copy of the previous site
        meta.json     ← {reason, written_at, files_count, source}

Storage is intentionally simple: a directory tree, no diffs, no compression.
Marketing sites are 30-100 files of plain text — a snapshot is a few hundred
KB. We can switch to git-style packed history later if disk pressure shows up.

Public API (used by the engine + tests):
- ``snapshot_site(slug, reason, source) -> Path | None``
- ``list_history(slug) -> list[HistoryEntry]``
- ``restore_snapshot(slug, snapshot_id) -> int``  (number of files restored)
- ``HistoryEntry`` dataclass
"""
from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# Resolved against the project root (parent of this file's package).
_PROJECT_ROOT = Path(__file__).parent.parent.resolve()
OUTPUT_DIR = _PROJECT_ROOT / "output"


@dataclass(frozen=True)
class HistoryEntry:
    """One snapshot in a build's history."""
    snapshot_id: str        # filesystem-safe id, e.g. "20260514T223045-generate"
    written_at: str         # ISO timestamp
    reason: str             # "generate", "refine", "visual-edit", "manual"
    source: str             # short description, e.g. "POST /api/refine friendlier"
    files_count: int        # number of files captured in this snapshot
    relative_path: str      # path under output/<slug>/history/ for UI deeplinks

    def to_dict(self) -> dict:
        return asdict(self)


# ---- Path helpers ---------------------------------------------------------

def _history_root(slug: str) -> Path:
    return OUTPUT_DIR / slug / "history"


def _site_dir(slug: str) -> Path:
    return OUTPUT_DIR / slug / "site"


_SAFE_REASON_RE = re.compile(r"[^a-z0-9-]+")


def _sanitize_reason(reason: str) -> str:
    """Filesystem-safe reason tag for the snapshot directory name."""
    lower = (reason or "snap").strip().lower()
    safe = _SAFE_REASON_RE.sub("-", lower).strip("-")
    return safe or "snap"


def _make_snapshot_id(reason: str, when: Optional[datetime] = None) -> str:
    """Generate a unique snapshot id — UTC timestamp + sanitized reason tag.

    Format: ``YYYYMMDDTHHMMSS-<reason>``. The trailing reason makes directory
    listings legible at a glance; the timestamp gives natural sort order.
    """
    ts = (when or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%S")
    return f"{ts}-{_sanitize_reason(reason)}"


# ---- Public API -----------------------------------------------------------

def snapshot_site(
    slug: str,
    reason: str = "generate",
    source: str = "",
) -> Optional[Path]:
    """Copy the current ``site/`` to ``history/<snapshot_id>/site/``.

    Returns the snapshot directory path on success, ``None`` if there's
    nothing to snapshot (no site dir, or empty). Never raises — the build
    pipeline should not abort because history failed.

    Args:
        slug: project slug (the directory name under ``output/``).
        reason: short tag like ``"generate"``, ``"refine"``, ``"visual-edit"``.
        source: longer description for the meta.json record.
    """
    site = _site_dir(slug)
    if not site.exists() or not site.is_dir():
        return None
    # Skip empty site dirs — nothing useful to record.
    files = [p for p in site.rglob("*") if p.is_file()]
    if not files:
        return None

    snapshot_id = _make_snapshot_id(reason)
    target = _history_root(slug) / snapshot_id
    target.mkdir(parents=True, exist_ok=True)
    target_site = target / "site"

    try:
        shutil.copytree(site, target_site, dirs_exist_ok=True)
    except Exception:
        # If the copy fails partway through, leave whatever we got and move on.
        # A partial snapshot is better than aborting the active build.
        pass

    meta = {
        "reason":      reason,
        "source":      source or reason,
        "written_at":  datetime.now(timezone.utc).isoformat() + "Z",
        "files_count": len(files),
    }
    try:
        (target / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    except Exception:
        pass

    return target


def list_history(slug: str) -> list[HistoryEntry]:
    """Return all snapshots for a build, newest first."""
    root = _history_root(slug)
    if not root.exists() or not root.is_dir():
        return []

    entries: list[HistoryEntry] = []
    for d in root.iterdir():
        if not d.is_dir():
            continue
        meta_path = d / "meta.json"
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        except Exception:
            meta = {}
        entries.append(HistoryEntry(
            snapshot_id=d.name,
            written_at=meta.get("written_at", ""),
            reason=meta.get("reason", "unknown"),
            source=meta.get("source", ""),
            files_count=int(meta.get("files_count", 0)),
            relative_path=f"output/{slug}/history/{d.name}/",
        ))
    # Newest first — directory names are sortable timestamps.
    entries.sort(key=lambda e: e.snapshot_id, reverse=True)
    return entries


def restore_snapshot(slug: str, snapshot_id: str, snapshot_current: bool = True) -> int:
    """Restore a previous snapshot to ``output/<slug>/site/``.

    Returns the number of files restored. Raises ``FileNotFoundError`` if
    the requested snapshot doesn't exist. By default snapshots the current
    site first so the restore itself is undoable — pass
    ``snapshot_current=False`` only in tests or when the caller has
    already snapshotted.
    """
    src = _history_root(slug) / snapshot_id / "site"
    if not src.exists() or not src.is_dir():
        raise FileNotFoundError(f"snapshot not found: output/{slug}/history/{snapshot_id}/site")

    dest = _site_dir(slug)

    if snapshot_current and dest.exists():
        snapshot_site(slug, reason="restore", source=f"rolling back to {snapshot_id}")

    # Wipe dest then copy. We use this in-place strategy instead of
    # rename + swap because the engine's preview server holds handles to
    # files under site/ on Windows; rename can fail with permission errors.
    if dest.exists():
        for child in dest.iterdir():
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                try: child.unlink()
                except Exception: pass
    else:
        dest.mkdir(parents=True, exist_ok=True)

    count = 0
    for src_file in src.rglob("*"):
        if src_file.is_file():
            rel = src_file.relative_to(src)
            dst_file = dest / rel
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
            count += 1
    return count


# ---- Diff helpers (Phase 35, 2026-05-21) ---------------------------------
#
# After every refinement or visual-edit, the workspace UI wants to surface
# "Frontend: Updated components/Hero.tsx (3 lines) / Backend: Untouched"
# — the Phase-3 diagram pattern. The data is already on disk (a snapshot
# was taken before the mutation), we just need to compute the diff.


@dataclass(frozen=True)
class FileDiff:
    """Per-file change record. ``status`` is one of: added | modified | deleted.

    For text files we also record line counts for the UI ("(3 lines changed)").
    For binary files (images, fonts) we set both counts to None.
    """
    path: str               # repo-relative, forward-slash, e.g. "components/Hero.tsx"
    status: str             # "added" | "modified" | "deleted"
    lines_added: Optional[int]
    lines_removed: Optional[int]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class DiffSummary:
    """High-level diff for one mutation. Drives the UI's diff panel.

    ``categories`` rolls files up by top-level directory so the UI can
    say "Frontend: Updated 3 components" instead of listing 7 files.
    """
    snapshot_id: str
    files: list[FileDiff]
    categories: dict[str, int]   # {"frontend": 3, "config": 1, ...}
    total_changed: int

    def to_dict(self) -> dict:
        return {
            "snapshot_id":   self.snapshot_id,
            "files":         [f.to_dict() for f in self.files],
            "categories":    self.categories,
            "total_changed": self.total_changed,
        }


# File extensions we treat as text for line-count diffs. Anything else is
# reported as added/modified/deleted without line counts.
_TEXT_EXTS = {
    ".tsx", ".ts", ".jsx", ".js", ".mjs", ".cjs",
    ".css", ".scss", ".html", ".json", ".md",
    ".py", ".sql", ".sh", ".yaml", ".yml", ".toml",
    ".txt", ".env", ".gitignore",
}


# Map top-level paths → category buckets. Keep this small and stable; the
# UI groups output by these bucket names.
def _categorize(rel_path: str) -> str:
    head = rel_path.split("/", 1)[0]
    if head in ("app", "components", "hooks", "lib"):
        return "Frontend"
    if head in ("public",):
        return "Assets"
    if head in ("api", "routes", "actions"):
        return "Backend"
    if head in ("styles",) or rel_path.endswith(".css"):
        return "Styles"
    if head in ("tests", "__tests__"):
        return "Tests"
    if rel_path in ("package.json", "tsconfig.json", "tailwind.config.ts",
                    "next.config.mjs", "vercel.json", ".env.example"):
        return "Config"
    return "Other"


def _read_lines_safe(path: Path) -> Optional[list[str]]:
    """Return file lines for text files; None for binary or read errors.

    Used for the line-count component of the diff. Lines are split on \\n
    so trailing-newline differences don't inflate counts.
    """
    if path.suffix.lower() not in _TEXT_EXTS:
        return None
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return None


def _diff_lines(before: Optional[list[str]], after: Optional[list[str]]) -> tuple[Optional[int], Optional[int]]:
    """Tiny line-level diff: returns (added, removed) counts.

    Not a true LCS diff — we use a SequenceMatcher-style ratio approximation
    that's good enough for "(3 lines changed)" labels and orders-of-magnitude
    cheaper than diffing every refine call against multi-file snapshots.
    Returns (None, None) for binary files.
    """
    if before is None or after is None:
        return (None, None)
    # Quick path: identical
    if before == after:
        return (0, 0)
    # Set-based approximation. Order-insensitive but the counts are still
    # informative for the UI ("3 lines changed" is what users care about).
    before_set = set(before)
    after_set = set(after)
    added   = sum(1 for line in after  if line not in before_set)
    removed = sum(1 for line in before if line not in after_set)
    return (added, removed)


def diff_against_snapshot(slug: str, snapshot_id: str) -> Optional[DiffSummary]:
    """Compute the change set between the current site and a snapshot.

    Returns None if either side is missing. Never raises — returns an
    empty diff (total_changed=0) for genuinely identical trees, and
    swallows per-file read errors as binary-style modifications.

    Caller convention: this is meant to be called AFTER a mutation (refine
    or visual-edit), comparing the pre-mutation snapshot to the new
    current state. The snapshot_id is whatever snapshot_site() returned
    just before the mutation.
    """
    snapshot_site_dir = _history_root(slug) / snapshot_id / "site"
    current_site_dir  = _site_dir(slug)
    if not snapshot_site_dir.exists() or not current_site_dir.exists():
        return None

    def _file_map(root: Path) -> dict[str, Path]:
        out: dict[str, Path] = {}
        for p in root.rglob("*"):
            if p.is_file():
                rel = p.relative_to(root).as_posix()
                out[rel] = p
        return out

    before_files = _file_map(snapshot_site_dir)
    after_files  = _file_map(current_site_dir)

    all_paths = sorted(set(before_files) | set(after_files))
    diffs: list[FileDiff] = []
    for rel in all_paths:
        b = before_files.get(rel)
        a = after_files.get(rel)
        if b and not a:
            diffs.append(FileDiff(path=rel, status="deleted", lines_added=None, lines_removed=None))
            continue
        if a and not b:
            after_lines = _read_lines_safe(a)
            line_count = len(after_lines) if after_lines is not None else None
            diffs.append(FileDiff(path=rel, status="added",
                                   lines_added=line_count, lines_removed=0 if line_count is not None else None))
            continue
        # Both exist — compare byte-equal first (cheap), then line counts.
        assert a is not None and b is not None
        try:
            if a.stat().st_size == b.stat().st_size and a.read_bytes() == b.read_bytes():
                continue  # identical, skip
        except Exception:
            pass
        added, removed = _diff_lines(_read_lines_safe(b), _read_lines_safe(a))
        diffs.append(FileDiff(path=rel, status="modified", lines_added=added, lines_removed=removed))

    categories: dict[str, int] = {}
    for d in diffs:
        cat = _categorize(d.path)
        categories[cat] = categories.get(cat, 0) + 1

    return DiffSummary(
        snapshot_id=snapshot_id,
        files=diffs,
        categories=categories,
        total_changed=len(diffs),
    )


__all__ = [
    "HistoryEntry",
    "FileDiff",
    "DiffSummary",
    "snapshot_site",
    "list_history",
    "restore_snapshot",
    "diff_against_snapshot",
]
