"""Inject stable ``data-pebble-id`` attributes into generated source files.

After ``/api/generate`` writes site files, ``inject_pebble_ids(site_dir)``
walks every .tsx/.jsx/.html file, attaches ``data-pebble-id="pb-xxxxxx"`` to
each text-bearing or interactive tag that doesn't already have one, and
writes a manifest at ``<site>/.pebble-ids.json`` mapping each id to its
source file + a snapshot of the wrapped text.

That manifest lets ``/api/visual-edit`` perform surgical edits: the iframe
bridge sends ``pebble_id``, we look up the file + tag, and modify within
the bounds of that single element. The old "find original_text across the
site" heuristic stays as the fallback path for older builds (no manifest).

Design choices:

- **Plain regex, no JSX/HTML parser.** Generated code is reasonably regular;
  full AST parsing is slow and adds dependencies. The regex is conservative:
  it only matches tags from ``TARGET_TAGS`` and skips anything already
  carrying ``data-pebble-id``.
- **6 hex chars per id.** 16.7M combinations is more than enough for one
  site's worth of tags without practical collision risk.
- **Idempotent.** Tags already carrying an id are left untouched, so the
  function is safe to call after partial edits / refines.
"""
from __future__ import annotations

import json
import re
import secrets
from pathlib import Path
from typing import Iterable, Optional


# Tags worth tagging — text-bearing or interactive elements that users are
# likely to click and want to edit. Skip layout-only tags (div, section,
# nav, etc.) to avoid noise. Section roots are useful for color/background
# edits though, so we include a few structural ones.
TARGET_TAGS = (
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "span", "a", "button", "li", "blockquote",
    "figcaption", "summary", "label", "td", "th", "small",
    "strong", "em",
)


# JSX/HTML opening tag. Matches the tag name + any attrs up to the closing >.
# Excludes < and > to avoid running past the tag boundary in malformed JSX,
# but does not handle > inside attribute values (rare; not worth parsing).
_TAG_OPEN_RE = re.compile(
    r"<(?P<tag>" + "|".join(TARGET_TAGS) + r")(?P<attrs>\s[^<>]*?)?(?P<close>/?)>",
    re.IGNORECASE,
)

_HAS_ID_RE = re.compile(r"\sdata-pebble-id\s*=", re.IGNORECASE)

# Snapshot the first ~80 chars of text immediately after the opening tag —
# kept in the manifest for human/debug use, not used by the edit path.
_TEXT_AFTER_OPEN_RE = re.compile(r"^([^<{]{1,120})")


def _new_id() -> str:
    """Short, URL-safe id (e.g. ``pb-a1b2c3``). 24 bits of entropy."""
    return "pb-" + secrets.token_hex(3)


def _iter_files(site_dir: Path) -> Iterable[Path]:
    for pattern in ("**/*.tsx", "**/*.jsx", "**/*.html"):
        yield from site_dir.glob(pattern)


def _inject_into_file(file_path: Path, site_dir: Path) -> dict[str, dict]:
    """Inject ids into one file. Returns ``{id: {file, tag, original_text}}``.
    Writes the file back only if at least one tag was modified.
    """
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception:
        return {}

    chunks: list[str] = []
    manifest: dict[str, dict] = {}
    pos = 0
    modified = False

    for m in _TAG_OPEN_RE.finditer(text):
        chunks.append(text[pos:m.start()])
        tag = m.group("tag").lower()
        attrs = m.group("attrs") or ""
        self_close = m.group("close") == "/"

        if _HAS_ID_RE.search(attrs):
            # Already tagged — preserve as-is.
            chunks.append(text[m.start():m.end()])
            pos = m.end()
            continue

        new_id = _new_id()
        while new_id in manifest:
            new_id = _new_id()

        new_attrs = (attrs.rstrip() if attrs else "") + f' data-pebble-id="{new_id}"'
        rebuilt = f"<{m.group('tag')}{new_attrs}{'/' if self_close else ''}>"
        chunks.append(rebuilt)
        modified = True

        snap = _TEXT_AFTER_OPEN_RE.match(text[m.end():])
        original_text = (snap.group(1).strip() if snap else "")[:80]

        manifest[new_id] = {
            "file":          file_path.relative_to(site_dir).as_posix(),
            "tag":           tag,
            "original_text": original_text,
        }
        pos = m.end()

    if not modified:
        return {}

    chunks.append(text[pos:])
    file_path.write_text("".join(chunks), encoding="utf-8")
    return manifest


def inject_pebble_ids(site_dir: Path) -> dict[str, dict]:
    """Inject ids across every supported file under ``site_dir`` and persist
    the manifest at ``<site_dir>/.pebble-ids.json``. Returns the manifest.

    Safe to call repeatedly: existing ids are preserved.
    """
    if not site_dir.exists() or not site_dir.is_dir():
        return {}

    # Merge: keep any pre-existing manifest entries (e.g. from earlier injects
    # whose tags still exist) and add new ones.
    manifest = load_manifest(site_dir)

    for f in _iter_files(site_dir):
        file_manifest = _inject_into_file(f, site_dir)
        manifest.update(file_manifest)

    # Drop entries whose files no longer exist (e.g. file deleted across a
    # regen) so the manifest doesn't grow forever.
    pruned = {
        pid: entry for pid, entry in manifest.items()
        if (site_dir / entry["file"]).exists()
    }

    (site_dir / ".pebble-ids.json").write_text(
        json.dumps(pruned, indent=2), encoding="utf-8"
    )
    return pruned


def load_manifest(site_dir: Path) -> dict[str, dict]:
    """Read the manifest, or return {} if missing/corrupt."""
    path = site_dir / ".pebble-ids.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


# ---- Tag location helpers (used by visual-edit handlers) ------------------

def find_tag_open(text: str, pebble_id: str) -> Optional[tuple[int, int]]:
    """Return ``(open_start, open_end)`` byte offsets of the opening tag that
    carries ``data-pebble-id="<pebble_id>"`` in ``text``, or None."""
    needle = f'data-pebble-id="{pebble_id}"'
    idx = text.find(needle)
    if idx < 0:
        return None
    open_start = text.rfind("<", 0, idx)
    if open_start < 0:
        return None
    in_quote: Optional[str] = None
    i = idx
    while i < len(text):
        ch = text[i]
        if in_quote:
            if ch == in_quote:
                in_quote = None
        elif ch in ('"', "'"):
            in_quote = ch
        elif ch == ">":
            return (open_start, i + 1)
        i += 1
    return None


def find_element_span(text: str, pebble_id: str) -> Optional[tuple[int, int, int, int]]:
    """Locate the full element wrapping ``pebble_id`` inside ``text``.
    Returns ``(open_start, open_end, close_start, close_end)``. For
    self-closing tags, ``close_start == close_end == open_end``.

    Tracks depth for nested same-tag children (e.g. nested ``<span>``).
    """
    open_pos = find_tag_open(text, pebble_id)
    if not open_pos:
        return None
    open_start, open_end = open_pos

    tag_m = re.match(r"<([a-zA-Z0-9]+)", text[open_start:open_end])
    if not tag_m:
        return None
    tag = tag_m.group(1)

    if text[open_end - 2:open_end] == "/>":
        return (open_start, open_end, open_end, open_end)

    open_re = re.compile(r"<" + re.escape(tag) + r"(\s[^<>]*?)?>", re.IGNORECASE)
    close_re = re.compile(r"</" + re.escape(tag) + r"\s*>", re.IGNORECASE)

    depth = 1
    pos = open_end
    while pos < len(text):
        next_open = open_re.search(text, pos)
        next_close = close_re.search(text, pos)
        if not next_close:
            return None
        if next_open and next_open.start() < next_close.start():
            depth += 1
            pos = next_open.end()
        else:
            depth -= 1
            if depth == 0:
                return (open_start, open_end, next_close.start(), next_close.end())
            pos = next_close.end()
    return None
