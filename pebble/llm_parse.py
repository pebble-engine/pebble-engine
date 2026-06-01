"""LLM response parsing primitives.

Extracted from pebble_engine.py (2026-06-01) so the build orchestrator
no longer owns parsing primitives that the repair loop and the server
modules need to import. Eliminates the ``_engine()`` lazy-import dance
in pebble.repair and the ``parse_files = pe.parse_files`` symbol
hoisting in pebble.server.build / pebble.server.refine.

Three public functions:

- :func:`parse_files` — extract ``<pebble-file path="...">...</pebble-file>``
  blocks from a full LLM response. Tolerant: missing/typo'd close tags
  do not cause the next file's body to be silently swallowed.
- :func:`parse_deletions` — extract ``<pebble-delete path="..."/>`` tags.
- :func:`detect_truncation` — count unmatched ``<pebble-file>`` opens
  (positive => the LLM ran out of output budget mid-write).

Backwards compatibility: pebble_engine re-exports these so existing
``from pebble_engine import parse_files`` imports keep working.
"""
from __future__ import annotations

import re

# Opening tag for <pebble-file path="..."> blocks. The trailing `\s*\n`
# is part of the match so the body slice doesn't include the newline
# right after the tag.
FILE_OPEN_RE = re.compile(r'<pebble-file\s+path="([^"]+)">\s*\n')

# Strips the trailing close tag off a parsed block body — tolerant of
# Gemini's `</peble-file>` / `</pebblefile>` typos.
_TRAILING_CLOSE_RE = re.compile(r'\n?\s*</p[a-z]*[\s-]?file>\s*$')

# Self-closing delete tag used by the repair loop. The LLM emits these to
# request file deletion — needed to repair structural failures like
# no_src_directory (files exist in the wrong place) that <pebble-file> alone
# can't address. Accepts both `<pebble-delete path="..."/>` and the slightly
# more permissive `<pebble-delete path="..."></pebble-delete>` forms.
_DELETE_TAG_RE = re.compile(
    r'<pebble-delete\s+path="([^"]+)"\s*(?:/>|></pebble-delete>)'
)

# Boundary detector for parse_files: a <pebble-file> block ends at the next
# <pebble-file> opening OR the next <pebble-delete> tag — both signal that
# the file body has ended.
_FILE_BOUNDARY_RE = re.compile(r'<pebble-(?:file\s+path|delete\s+path)="')


_PEBBLE_FILE_CLOSE_RE = re.compile(r'</p[a-z]*[\s-]?file>')


def detect_truncation(llm_output: str) -> int:
    """Return the count of unmatched `<pebble-file>` opening tags — i.e.
    how many files appear to have been cut off mid-stream by the LLM.

    Zero = the response is structurally balanced.
    Positive = the LLM ran out of output budget mid-write. The build
    has at least N incomplete file(s); the engine should mark the
    result `billable: false` so the user isn't charged for a broken
    site.

    Background: ``parse_files`` keys boundaries off the NEXT opening
    tag rather than requiring a close, so a truncated response with
    N opens / N-1 closes still parses N files — the last with a body
    cut mid-string. This function is the truncation guard the parser
    intentionally lacks. Counted with the same close-tag-typo regex
    the parser uses so Gemini's `</peble-file>` / `</pebblefile>`
    typos don't flag false positives.
    """
    opens = len(FILE_OPEN_RE.findall(llm_output))
    closes = len(_PEBBLE_FILE_CLOSE_RE.findall(llm_output))
    return max(0, opens - closes)


def parse_files(llm_output: str) -> list[tuple[str, str]]:
    """Extract ``<pebble-file path="...">`` blocks from an LLM response.

    Boundary strategy: each block runs from its opening tag until the NEXT
    ``<pebble-file>`` OR ``<pebble-delete>`` tag (or end of input). The
    canonical ``</pebble-file>`` closing tag is stripped off the tail if
    present, but the parser does not REQUIRE it — Gemini has been observed
    to typo the close as ``</peble-file>`` and a strict paired regex would
    silently swallow the next file's body.

    Embedded ``<pebble-delete>`` tags are not addressed by parse_files —
    they're between blocks now thanks to the boundary detector, but a safety
    net strips any that snuck inside.
    """
    out: list[tuple[str, str]] = []
    matches = list(FILE_OPEN_RE.finditer(llm_output))
    for i, m in enumerate(matches):
        path = m.group(1)
        body_start = m.end()
        # Find the next boundary AFTER body_start: another <pebble-file> open
        # OR a <pebble-delete>. Whichever comes first wins.
        next_boundary = _FILE_BOUNDARY_RE.search(llm_output, body_start)
        body_end = next_boundary.start() if next_boundary else len(llm_output)
        body = llm_output[body_start:body_end]
        body = _TRAILING_CLOSE_RE.sub("", body)
        body = _DELETE_TAG_RE.sub("", body)  # defense in depth
        out.append((path, body))
    return out


def parse_deletions(llm_output: str) -> list[str]:
    """Extract ``<pebble-delete path="..."/>`` tags from an LLM response.

    Returns the paths the LLM is requesting to delete. Caller is responsible
    for validating each path against the build's site root (path traversal,
    etc.) — see :func:`pebble.repair._apply_deletions`.
    """
    return [m.group(1) for m in _DELETE_TAG_RE.finditer(llm_output)]
