"""Detect truncated LLM responses so the engine never bills for a
half-written site.

2026-05-17: the vector-lane build truncated mid-stream (32 opening
<pebble-file> tags / 31 closing) and wrote `billable: true` despite
having no `app/page.tsx`. The parser's boundary detector keys off the
NEXT opening tag rather than requiring a closing tag, so it cheerfully
extracted 32 files — the last one with a half-finished body.

This suite locks the detector behavior. The signal is simple: count
canonical `<pebble-file path=` opens and `</pebble-file>` closes; if
opens > closes, the response is truncated.
"""
from __future__ import annotations

from pebble_engine import detect_truncation


# ---------- clean responses --------------------------------------------

def test_empty_response_is_not_truncated():
    assert detect_truncation("") == 0


def test_no_pebble_blocks_is_not_truncated():
    assert detect_truncation("hello world this is plain text") == 0


def test_well_formed_single_file_is_not_truncated():
    assert detect_truncation('<pebble-file path="a.txt">\nbody\n</pebble-file>') == 0


def test_well_formed_multi_file_is_not_truncated():
    text = (
        '<pebble-file path="a.txt">\nA\n</pebble-file>\n'
        '<pebble-file path="b.txt">\nB\n</pebble-file>\n'
        '<pebble-file path="c.txt">\nC\n</pebble-file>'
    )
    assert detect_truncation(text) == 0


# ---------- truncated responses ----------------------------------------

def test_truncated_last_file_is_detected():
    """The vector-lane case: last file has opening tag but no close."""
    text = (
        '<pebble-file path="a.txt">\nA\n</pebble-file>\n'
        '<pebble-file path="b.txt">\nIncomplete body cut off mid-string'
    )
    assert detect_truncation(text) == 1


def test_only_one_file_truncated_is_detected():
    """Sometimes the LLM cuts off in the very first file."""
    text = '<pebble-file path="a.txt">\nIncomplete'
    assert detect_truncation(text) == 1


def test_multiple_missing_closes_detected():
    """If somehow multiple closes are missing, the delta reflects it."""
    text = (
        '<pebble-file path="a.txt">\nA1\n'  # missing close
        '<pebble-file path="b.txt">\nB1\n'  # missing close
        '<pebble-file path="c.txt">\nC1\n</pebble-file>'
    )
    assert detect_truncation(text) == 2


# ---------- tolerant of close-tag typos --------------------------------

def test_typo_close_tag_still_counts():
    """Gemini occasionally typos the close as </peble-file> or
    </pebblefile>. The detector tolerates these — same regex used by
    the parser's `_TRAILING_CLOSE_RE`."""
    text = (
        '<pebble-file path="a.txt">\nA\n</pebble-file>\n'
        '<pebble-file path="b.txt">\nB\n</peble-file>\n'  # typo close
        '<pebble-file path="c.txt">\nC\n</pebblefile>'    # typo close
    )
    assert detect_truncation(text) == 0


def test_typo_close_at_truncation_boundary():
    """Truncation past a typo close should still be detected: the
    truncated tail has no close at all."""
    text = (
        '<pebble-file path="a.txt">\nA\n</peble-file>\n'
        '<pebble-file path="b.txt">\nIncomplete'
    )
    assert detect_truncation(text) == 1


# ---------- ordering doesn't matter ------------------------------------

def test_detects_when_close_count_exceeds_open_count():
    """Defensive: extra close tags (e.g. embedded in a code block) are
    NOT truncation — return 0 to avoid false positives. We only care
    about opens > closes."""
    text = (
        '<pebble-file path="a.txt">\n'
        'console.log("</pebble-file>");\n'  # literal in source
        '</pebble-file>'
    )
    assert detect_truncation(text) == 0
