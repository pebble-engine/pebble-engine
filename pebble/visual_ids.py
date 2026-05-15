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


# Finds positions where an opening tag for one of our TARGET_TAGS begins.
# The lookahead ensures we don't match prefixes (``<buttonless>`` isn't a
# button). The actual tag-end is found by ``_find_open_tag_end`` below
# because JSX expression containers ``{...}``, template literals
# `` `...` ``, and quoted attribute values can legally contain ``>`` and
# ``<`` characters — a flat regex would close the tag too early at the
# first ``>`` inside an arrow function or a URL.
_TAG_NAME_RE = re.compile(
    r"<(?P<tag>" + "|".join(TARGET_TAGS) + r")(?=[\s/>])",
    re.IGNORECASE,
)

_HAS_ID_RE = re.compile(r"\sdata-pebble-id\s*=", re.IGNORECASE)


def _find_open_tag_end(text: str, start: int) -> Optional[int]:
    """Scan forward from ``start`` (the position just after the tag name)
    and return the index of the ``>`` that closes the opening tag.
    Returns ``None`` if no close is found (e.g. truncated input).

    Tracks three kinds of nesting so that ``>`` characters inside them
    don't fool us into closing the tag early:

    1. **Quoted strings** ``"..."`` and ``'...'`` — for attribute values
       like ``href="https://x.com/?q=>foo"``.
    2. **JSX expression containers** ``{...}`` — for handlers like
       ``onClick={() => doStuff()}`` and styles like ``style={{x: 1}}``.
       Brace depth is tracked so nested ``{}`` (e.g. ``style={{}}``)
       balance correctly.
    3. **Template literals** `` `...` `` — for ``className={`flex ${cond
       && 'on'}`}``. Backticks are treated as a quote-like delimiter;
       ``${...}`` interpolations inside the backtick are skipped along
       with everything else, because they're balanced within the
       template's own grammar (they exit when the backtick closes).
    """
    i = start
    n = len(text)
    brace_depth = 0          # depth inside JSX {...} expressions
    quote: Optional[str] = None  # current quote char, or None
    while i < n:
        ch = text[i]
        if quote:
            # Inside a string of some kind. Only the matching close char
            # exits — and a backslash escape skips the next character.
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if brace_depth > 0:
            # Inside a JSX expression. Track nested braces, and enter
            # quote / template-literal states as needed.
            if ch == "{":
                brace_depth += 1
            elif ch == "}":
                brace_depth -= 1
            elif ch == '"' or ch == "'" or ch == "`":
                quote = ch
            i += 1
            continue
        # Top-level attrs.
        if ch == '"' or ch == "'":
            quote = ch
        elif ch == "{":
            brace_depth = 1
        elif ch == ">":
            return i
        elif ch == "<":
            # Malformed — unexpected new tag start before close.
            return None
        i += 1
    return None

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

    for m in _TAG_NAME_RE.finditer(text):
        # Skip overlapping matches caused by manifest mutations earlier
        # in the loop (we slice positions from the original ``text``).
        if m.start() < pos:
            continue

        tag_close = _find_open_tag_end(text, m.end())
        if tag_close is None:
            # Malformed input — leave this region alone.
            continue

        chunks.append(text[pos:m.start()])
        tag = m.group("tag").lower()
        self_close = tag_close > m.end() and text[tag_close - 1] == "/"
        # ``attrs`` is everything between the tag name and the closing ``>``
        # (minus the optional self-closing ``/``).
        attrs_end = tag_close - 1 if self_close else tag_close
        attrs = text[m.end():attrs_end]

        if _HAS_ID_RE.search(attrs):
            # Already tagged — preserve as-is.
            chunks.append(text[m.start():tag_close + 1])
            pos = tag_close + 1
            continue

        new_id = _new_id()
        while new_id in manifest:
            new_id = _new_id()

        # Append `` data-pebble-id="<id>"`` to the existing attrs region.
        # Strip trailing whitespace from attrs to avoid double-spacing,
        # then add a single space before the new attribute.
        new_attrs = attrs.rstrip() + f' data-pebble-id="{new_id}"'
        rebuilt = f"<{m.group('tag')}{new_attrs}{'/' if self_close else ''}>"
        chunks.append(rebuilt)
        modified = True

        snap = _TEXT_AFTER_OPEN_RE.match(text[tag_close + 1:])
        original_text = (snap.group(1).strip() if snap else "")[:80]

        manifest[new_id] = {
            "file":          file_path.relative_to(site_dir).as_posix(),
            "tag":           tag,
            "original_text": original_text,
        }
        pos = tag_close + 1

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


# Builds before the 2026-05-15 scanner fix can have arrow functions
# mangled into ``onClick={() = data-pebble-id="pb-xxx"> doStuff()}`` —
# JSX compile errors. This pattern is unique to the bug (no legitimate
# JSX has ``= data-pebble-id="..."`` in that position), so the repair
# is safe to apply unconditionally.
_MANGLED_ARROW_RE = re.compile(r'=\s+data-pebble-id="(pb-[a-f0-9]+)">')


def repair_mangled_files(site_dir: Path) -> int:
    """Walk ``site_dir`` and undo arrow-function corruption from the old
    injector. Restores ``=>`` and drops the broken injection (the next
    ``inject_pebble_ids`` will re-add a proper id at a valid position).
    Returns the number of files repaired.
    """
    if not site_dir.exists() or not site_dir.is_dir():
        return 0
    repaired = 0
    lost_ids: set[str] = set()
    for f in _iter_files(site_dir):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        matches = list(_MANGLED_ARROW_RE.finditer(text))
        if not matches:
            continue
        lost_ids.update(m.group(1) for m in matches)
        new_text = _MANGLED_ARROW_RE.sub("=>", text)
        if new_text != text:
            f.write_text(new_text, encoding="utf-8")
            repaired += 1
    # Drop the now-orphaned manifest entries so the next inject doesn't
    # see them as "already tagged" (since they aren't, in the source).
    if lost_ids:
        manifest = load_manifest(site_dir)
        for pid in lost_ids:
            manifest.pop(pid, None)
        (site_dir / ".pebble-ids.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
    return repaired


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
