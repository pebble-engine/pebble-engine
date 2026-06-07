"""Publish-time transparency guard.

Scans a generated site for leftover placeholders / sample content so the
publish flow can warn a non-technical owner BEFORE they ship fake-looking
or unfinished content to real visitors. This is the safety net that makes
"fill the template in for them, then remind them to add their real info"
honest: transparency that does NOT depend on the owner reading a reminder,
because the publish step actively catches leftovers.

It's also a trust feature Lovable doesn't have — they happily let you ship
fabricated reviews/stats.

Detection modes (precision matters — we must not nag on real copy or flag
legitimate code):
  - CONTACT tokens (exact): "[BUSINESS PHONE]", "[EMAIL]", etc. — both modes.
  - SAMPLE phrases (case-insensitive, curated to avoid real-copy collisions):
    "replace me", "lorem ipsum", "your happy customer", … — both modes.
  - GENERIC brackets ("[Add a review …]") — LOOSE mode only (content/*.ts
    data files, where a bracketed token is always a placeholder). NOT applied
    to .tsx/.ts code files, so array destructuring `const [a, b] = …` and
    indexing `arr[0]` are never flagged.

Fail-open: any internal/read error yields "ready" — we never block a user's
publish because of our own scan failure.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# Exact contact placeholders the content-swap + build prompts emit.
CONTACT_TOKENS = [
    "[BUSINESS PHONE]",
    "[BUSINESS EMAIL]",
    "[BUSINESS ADDRESS]",
    "[STREET ADDRESS]",
    "[EMAIL]",
    "[ADDRESS]",
    "[PHONE]",
]

# Labeled metric/social-proof placeholders the content-swap prompt emits when
# the brief gives no real numbers (kind "sample"). Lowercase / "#"-leading, so
# they need explicit matching — the generic bracket pattern alone misses them.
METRIC_TOKENS = [
    "[rating]",
    "[# of reviews]",
    "[# served]",
    "[# of years]",
    "[year]",
]

# Curated sample phrases. Deliberately specific so they don't fire on real
# marketing copy (e.g. we do NOT include broad strings like "your area").
SAMPLE_PHRASES = [
    "replace me",
    "replace this",
    "your happy customer",
    "sample review",
    "sample testimonial",
    "lorem ipsum",
    "placeholder text",
    "edit this text",
]

# Generic bracket token (content files only). Any 2–60 chars inside [...];
# we filter out pure-numeric / single-char (code like [0], [i]) below.
_BRACKET_RE = re.compile(r"\[([^\[\]]{2,60})\]")
_PURE_NUMERIC_RE = re.compile(r"^[\d\s,.;:]+$")
_COMMENT_PREFIXES = ("//", "*", "/*")

_CONTENT_GLOBS = ("content/*.ts", "content/*.tsx")
_CODE_DIRS = ("app", "components", "lib")
_CODE_SUFFIXES = (".ts", ".tsx")
_SKIP_DIRS = {"node_modules", ".next", "dist", "build", ".git"}


def _is_placeholder_bracket(inner: str) -> bool:
    """In a content data file, a bracketed token is a placeholder unless it
    is purely numeric (`[0]`, `[1,2]`) or a single character (`[i]`).
    Everything else inside brackets in a .ts data file is a fill-me slot."""
    inner = inner.strip()
    if len(inner) < 2:
        return False
    if _PURE_NUMERIC_RE.match(inner):
        return False
    # JS array/string literals (["Portland", "Metro"]) and object-ish content
    # contain quotes/braces — they are real data, not fill-me placeholders.
    if any(c in inner for c in ('"', "'", "{", "}")):
        return False
    return True


def _is_comment_line(stripped: str) -> bool:
    return stripped.startswith(_COMMENT_PREFIXES)


def find_placeholders(text: str, *, loose: bool) -> list[dict[str, Any]]:
    """Return a list of placeholder hits in ``text``.

    Each hit: {kind: contact|sample|bracket, token, line, snippet}.
    ``loose`` enables the generic bracket pattern (content data files).
    Comment lines are skipped in both modes so the file's own convention
    docs ("use [SQUARE BRACKETS]") and dev comments never false-positive.
    """
    hits: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()

    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or _is_comment_line(stripped):
            continue
        low = line.lower()

        for tok in CONTACT_TOKENS:
            if tok in line:
                key = (lineno, tok)
                if key not in seen:
                    seen.add(key)
                    hits.append({"kind": "contact", "token": tok,
                                 "line": lineno, "snippet": stripped[:140]})

        for tok in METRIC_TOKENS:
            if tok in low:
                # preserve original casing of the match
                pos = low.find(tok)
                matched = line[pos:pos + len(tok)]
                key = (lineno, matched.lower())
                if key not in seen:
                    seen.add(key)
                    hits.append({"kind": "sample", "token": matched,
                                 "line": lineno, "snippet": stripped[:140]})

        for ph in SAMPLE_PHRASES:
            pos = low.find(ph.lower())
            if pos != -1:
                matched = line[pos:pos + len(ph)]
                key = (lineno, matched.lower())
                if key not in seen:
                    seen.add(key)
                    hits.append({"kind": "sample", "token": matched,
                                 "line": lineno, "snippet": stripped[:140]})

        if loose:
            for m in _BRACKET_RE.finditer(line):
                if not _is_placeholder_bracket(m.group(1)):
                    continue
                tok = m.group(0)
                if tok in CONTACT_TOKENS or tok.lower() in (t.lower() for t in METRIC_TOKENS):
                    continue  # already recorded
                key = (lineno, tok)
                if key not in seen:
                    seen.add(key)
                    hits.append({"kind": "bracket", "token": tok,
                                 "line": lineno, "snippet": stripped[:140]})

    return hits


def _scan_file(f: Path, site_dir: Path, *, loose: bool) -> list[dict[str, Any]]:
    try:
        text = f.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    try:
        rel = str(f.relative_to(site_dir)).replace("\\", "/")
    except ValueError:
        rel = f.name
    out = find_placeholders(text, loose=loose)
    for h in out:
        h["file"] = rel
    return out


def scan_site(site_dir: Path | str) -> list[dict[str, Any]]:
    """Scan a generated site directory. content/*.ts → loose; app|components|lib
    *.ts(x) → strict. Returns all placeholder hits (each tagged with file)."""
    site_dir = Path(site_dir)
    out: list[dict[str, Any]] = []
    if not site_dir.exists():
        return out

    for pat in _CONTENT_GLOBS:
        for f in sorted(site_dir.glob(pat)):
            if f.is_file():
                out.extend(_scan_file(f, site_dir, loose=True))

    for d in _CODE_DIRS:
        base = site_dir / d
        if not base.exists():
            continue
        for f in sorted(base.rglob("*")):
            if not f.is_file() or f.suffix not in _CODE_SUFFIXES:
                continue
            if any(part in _SKIP_DIRS for part in f.parts):
                continue
            out.extend(_scan_file(f, site_dir, loose=False))

    return out


def publish_readiness(site_dir: Path | str) -> dict[str, Any]:
    """High-level publish gate result for the publish flow / UI.

    Returns {ready, count, items, message}. Non-blocking by design: the UI
    surfaces the message and lets the owner publish anyway or go fix things.
    """
    items = scan_site(site_dir)
    count = len(items)
    if count == 0:
        return {"ready": True, "count": 0, "items": [],
                "message": "No placeholder content found — ready to publish."}

    kinds: dict[str, int] = {}
    for i in items:
        kinds[i["kind"]] = kinds.get(i["kind"], 0) + 1

    parts: list[str] = []
    if kinds.get("contact"):
        parts.append(f"{kinds['contact']} contact placeholder"
                     f"{'s' if kinds['contact'] != 1 else ''} (phone/email/address)")
    sample_n = kinds.get("bracket", 0) + kinds.get("sample", 0)
    if sample_n:
        parts.append(f"{sample_n} sample/placeholder text item"
                     f"{'s' if sample_n != 1 else ''}")

    message = (
        "Your site still has " + " and ".join(parts) + ". "
        "Fill these in or hide them before publishing so your visitors never "
        "see placeholder content."
    )
    return {"ready": False, "count": count, "items": items, "message": message}


__all__ = ["find_placeholders", "scan_site", "publish_readiness",
           "CONTACT_TOKENS", "SAMPLE_PHRASES"]
