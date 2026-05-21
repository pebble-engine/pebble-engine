"""Text sanitation helpers (Phase 20a, 2026-05-20).

Why this exists
---------------
On 2026-05-20 the mechanic-shop-inqueens Qwen build rendered "Mechanic shop
inQueens" as its H1 because the user's typed input had been propagated
verbatim into ``brief.business_name`` (autocorrect ran "in Queens" together
into "inQueens" and v3's ``deriveProjectName`` did no casing fix). The
generated TSX is faithful to the brief — so the fix has to happen *before*
the brief reaches the LLM.

This module is the canonical place for that work. Keep it dependency-free
so it can be imported from anywhere on the engine side (server/build.py,
server/migrate.py, server/projects.py — anywhere a brief is touched).
"""
from __future__ import annotations

import re


# Split camelCase runs of TWO or more lowercase chars followed by an uppercase
# letter. Two-or-more guards against legitimate brand casing like "iPhone" or
# "iPad" where a single leading lowercase letter precedes uppercase — those
# stay intact. "inQueens" → "in Queens"; "PebbleEngine" → "Pebble Engine".
_CAMEL_SPLIT = re.compile(r"([a-z]{2,})([A-Z])")

# Collapse any run of whitespace down to a single space.
_WS_RUN = re.compile(r"\s+")


def sanitize_business_name(raw: str) -> str:
    """Normalize a user-typed business name for hero rendering.

    Three operations:

    1. Collapse whitespace runs to single spaces and trim ends.
    2. Split obvious camelCase concatenations (``inQueens`` → ``in Queens``),
       preserving brand casing that uses a single leading lowercase
       letter (``iPhone``, ``iPad``, ``eBay``).
    3. Title-case each whitespace-delimited word — but only if the word
       has *no* uppercase letters yet. Words that already contain any
       uppercase letter are left alone, which preserves intentional
       casing like ``ACME``, ``iPhone``, ``AT&T``, ``McDonald``.

    Returns an empty string for ``None`` / empty / whitespace-only input
    so callers can decide what to do (fall back to ``"untitled"``, etc.).

    Examples
    --------
    >>> sanitize_business_name("Mechanic shop inQueens")
    'Mechanic Shop In Queens'
    >>> sanitize_business_name("iphone repair")
    'Iphone Repair'
    >>> sanitize_business_name("iPhone Repair")
    'iPhone Repair'
    >>> sanitize_business_name("ACME Corp")
    'ACME Corp'
    >>> sanitize_business_name("joe's plumbing")
    "Joe's Plumbing"
    >>> sanitize_business_name("")
    ''
    >>> sanitize_business_name("   ")
    ''
    """
    if not raw:
        return ""
    # Step 1 — whitespace normalize
    s = _WS_RUN.sub(" ", raw).strip()
    if not s:
        return ""
    # Step 2 — split camelCase concatenations
    s = _CAMEL_SPLIT.sub(r"\1 \2", s)
    # Step 3 — title-case word-by-word, preserving anything with internal caps
    out_words: list[str] = []
    for word in s.split(" "):
        if not word:
            continue
        if any(ch.isupper() for ch in word):
            # Brand casing or already-cased — leave alone
            out_words.append(word)
        else:
            # All lowercase — title-case it. Use str[0].upper() + str[1:]
            # instead of .title() so apostrophes don't trigger weird
            # behavior ("joe's" → "Joe's", not "Joe'S").
            out_words.append(word[0].upper() + word[1:])
    return " ".join(out_words)
