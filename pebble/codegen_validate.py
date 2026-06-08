"""Detect truncated / grossly-incomplete generated source files.

The LLM stream can be cut mid-file (max_tokens, stream boundary), leaving a
``.tsx`` file that ends mid-statement. ``next dev`` is lazy + lenient so the
site appears to build; ``next build`` (required to publish) then fails. This
module gives the Python engine a Node-less way to catch that class of defect
right after generation, so a truncated site is never reported as a clean build.

Approach: **bracket-balance** scan. We strip block comments, then count
``{}``, ``()`` and ``[]``. Truncation reliably leaves *more opens than closes*
(the function, the `return (`, the JSX scope all hang open). A complete module
balances. We deliberately do NOT track ``'`` / ``"`` strings: in TSX, quotes
appear in JSX *text* ("today's menu", 'She said "hi"') where they are not
string delimiters, so any quote-state machine false-positives. Brackets are
immune to that — apostrophes don't change the bracket count, and brackets
inside string literals are virtually always balanced ("(555)", "[rating]").
A stray *closer* (e.g. an emoji ":)") only makes the delta negative, which we
never flag — truncation is always a *positive* (unclosed-opens) imbalance.
Heuristic guard, not a parser; targets gross truncation with low false positives.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# Directories we never scan (deps + build artifacts).
_SKIP_DIRS = {"node_modules", ".next", ".turbo", "dist", "build", "out", ".git"}
_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs"}

# Strip /* block comments */ only. We do NOT strip // line comments because
# "https://..." inside a string would lose its trailing bracket and false-
# positive; lone unbalanced brackets in real line comments are vanishingly rare.
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)

_PAIRS = (("{", "}"), ("(", ")"), ("[", "]"))


def check_source_complete(text: str) -> tuple[bool, str]:
    """Return (is_complete, reason) for one source file's text.

    Flags a file when it has more OPEN than CLOSE brackets of any kind — the
    signature of a stream cut off mid-file."""
    if not text.strip():
        return True, "empty"
    src = _BLOCK_COMMENT.sub(" ", text)
    for op, cl in _PAIRS:
        delta = src.count(op) - src.count(cl)
        if delta > 0:
            return False, f"{delta} unclosed '{op}' (likely truncated mid-file)"
    return True, "ok"


def find_truncated_files(site_dir: Path) -> list[dict[str, Any]]:
    """Scan a generated site's source tree; return a list of
    {file, reason} for files that look truncated/incomplete."""
    site_dir = Path(site_dir)
    broken: list[dict[str, Any]] = []
    for path in site_dir.rglob("*"):
        if path.is_dir():
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if path.suffix not in _EXTS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        ok, reason = check_source_complete(text)
        if not ok:
            broken.append({"file": path.relative_to(site_dir).as_posix(), "reason": reason})
    return broken


def build_integrity(site_dir: Path, response_truncated_count: int = 0) -> dict[str, Any]:
    """Combine the response-level truncation signal (unmatched <pebble-file>
    opens, from pe.detect_truncation) with file-level content validation
    (this module). Returns a dict the build pipeline folds into build_meta.

    ``billable`` is False when ANYTHING looks truncated/broken — the user must
    not be charged for a site that won't compile or publish.
    """
    broken = find_truncated_files(site_dir)
    truncated = bool(response_truncated_count) or bool(broken)
    return {
        "truncated": truncated,
        "billable": not truncated,
        "broken_files": broken,
        "response_truncated_count": int(response_truncated_count),
    }


__all__ = ["check_source_complete", "find_truncated_files", "build_integrity"]
