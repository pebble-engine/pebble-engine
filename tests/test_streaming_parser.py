"""StreamingFileParser tests — pin the incremental <pebble-file> parser.

The parser is the core of Phase 13a (live streaming UX). It receives
LLM output one chunk at a time and yields each complete file block as
soon as its close tag arrives. Bugs here would either:
- Lose a file silently (close tag detection broken)
- Emit a file too early (boundary detection wrong)
- Hold memory forever (preamble accumulation runaway)

So the test coverage is wider than usual.
"""
from __future__ import annotations

import pytest

from pebble.streaming_parser import StreamingFileParser


# ------------------------------------------------------------------ #
# Single-chunk cases — basic correctness                               #
# ------------------------------------------------------------------ #

def test_single_complete_file_in_one_chunk():
    p = StreamingFileParser()
    p.feed('<pebble-file path="app/page.tsx">\nexport default function() {}\n</pebble-file>')
    out = list(p.drain())
    assert out == [("app/page.tsx", "export default function() {}")]
    assert p.total_yielded() == 1


def test_two_files_in_one_chunk():
    p = StreamingFileParser()
    p.feed(
        '<pebble-file path="a.ts">\nA\n</pebble-file>\n'
        '<pebble-file path="b.ts">\nB\n</pebble-file>'
    )
    out = list(p.drain())
    assert out == [("a.ts", "A"), ("b.ts", "B")]


def test_empty_feed_is_noop():
    p = StreamingFileParser()
    p.feed("")
    assert list(p.drain()) == []
    assert p.total_yielded() == 0


# ------------------------------------------------------------------ #
# Chunk-split cases — the whole point of the parser                   #
# ------------------------------------------------------------------ #

def test_open_tag_split_across_chunks():
    p = StreamingFileParser()
    p.feed('<pebble-file path="a')
    assert list(p.drain()) == []
    p.feed('.ts">\nbody\n</pebble-file>')
    out = list(p.drain())
    assert out == [("a.ts", "body")]


def test_body_split_across_many_chunks():
    p = StreamingFileParser()
    chunks = [
        '<pebble-file path="big.ts">\n',
        'line 1\n',
        'line 2\n',
        'line 3\n',
        '</pebble-file>',
    ]
    yielded: list[tuple[str, str]] = []
    for c in chunks:
        p.feed(c)
        yielded.extend(p.drain())
    assert yielded == [("big.ts", "line 1\nline 2\nline 3")]


def test_close_tag_split_across_chunks():
    p = StreamingFileParser()
    p.feed('<pebble-file path="x.ts">\ncontent\n</pebble-')
    assert list(p.drain()) == []
    p.feed('file>')
    out = list(p.drain())
    assert out == [("x.ts", "content")]


def test_files_emitted_in_order_as_each_completes():
    """When chunks come in such that file A completes early, then more
    of file B comes in, A should be emitted FIRST and remain available
    even after later drain() calls don't include it again."""
    p = StreamingFileParser()
    p.feed('<pebble-file path="a.ts">\nA\n</pebble-file><pebble-file path="b.ts">\nB1\n')
    out_first = list(p.drain())
    assert out_first == [("a.ts", "A")]
    p.feed('B2\n</pebble-file>')
    out_second = list(p.drain())
    assert out_second == [("b.ts", "B1\nB2")]


# ------------------------------------------------------------------ #
# Preamble handling                                                    #
# ------------------------------------------------------------------ #

def test_preamble_before_first_file_is_discarded():
    """LLMs sometimes emit a preamble like 'Here is your site:' before
    the first tag. Discard silently — only file blocks matter."""
    p = StreamingFileParser()
    p.feed("Here is your site:\n\n")
    p.feed('<pebble-file path="a.ts">\nA\n</pebble-file>')
    out = list(p.drain())
    assert out == [("a.ts", "A")]


def test_long_preamble_does_not_blow_buffer():
    """If the LLM emits 100KB of preamble before the first tag, the
    parser must not accumulate it all in memory. Buffer should be
    bounded by a small constant when no open tag is present."""
    p = StreamingFileParser()
    p.feed("x" * 100_000)
    # Buffer should be trimmed to a small constant — verify indirectly
    # by checking that a subsequent fully-formed file block still parses
    p.feed('<pebble-file path="a.ts">\nA\n</pebble-file>')
    out = list(p.drain())
    assert out == [("a.ts", "A")]


# ------------------------------------------------------------------ #
# Tolerance for typo'd close tags (matches legacy _PEBBLE_FILE_CLOSE_RE) #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("close_tag", [
    "</pebble-file>",
    "</pebble file>",   # space instead of dash
    "</pebble-File>",   # different case
    "</PEBBLE-FILE>",   # all caps
])
def test_tolerates_typo_close_tags(close_tag):
    p = StreamingFileParser()
    p.feed(f'<pebble-file path="x.ts">\nbody\n{close_tag}')
    out = list(p.drain())
    assert len(out) == 1
    assert out[0][0] == "x.ts"
    assert out[0][1] == "body"


# ------------------------------------------------------------------ #
# flush_remaining — recovery from truncated stream                     #
# ------------------------------------------------------------------ #

def test_flush_remaining_recovers_unterminated_block():
    """If the stream ends mid-block (no close tag), flush_remaining
    should yield the block on best-effort so the file isn't lost."""
    p = StreamingFileParser()
    p.feed('<pebble-file path="rescued.ts">\nfull content\nno close tag yet')
    # Normal drain returns nothing because no close tag yet
    assert list(p.drain()) == []
    # flush_remaining surfaces the block
    out = list(p.flush_remaining())
    assert len(out) == 1
    assert out[0][0] == "rescued.ts"
    assert "full content" in out[0][1]


def test_flush_remaining_strips_partial_close_tag_fragment():
    """If the stream truncated mid-close-tag (e.g. '</pebble-fil'), the
    partial tag should be stripped from the recovered content."""
    p = StreamingFileParser()
    p.feed('<pebble-file path="r.ts">\nbody here\n</pebble-fil')
    out = list(p.flush_remaining())
    assert len(out) == 1
    assert "body here" in out[0][1]
    assert "</pebble-fil" not in out[0][1]


def test_flush_remaining_returns_nothing_when_clean():
    """When all blocks closed cleanly, flush_remaining is a no-op."""
    p = StreamingFileParser()
    p.feed('<pebble-file path="a.ts">\nA\n</pebble-file>')
    list(p.drain())
    assert list(p.flush_remaining()) == []


# ------------------------------------------------------------------ #
# total_yielded counter                                                #
# ------------------------------------------------------------------ #

def test_total_yielded_increments_on_each_block():
    p = StreamingFileParser()
    assert p.total_yielded() == 0
    p.feed('<pebble-file path="a">\nA\n</pebble-file>')
    assert p.total_yielded() == 1
    list(p.drain())  # drain doesn't reset the total
    assert p.total_yielded() == 1
    p.feed('<pebble-file path="b">\nB\n</pebble-file>')
    assert p.total_yielded() == 2


# ------------------------------------------------------------------ #
# Realistic — 30-file simulated stream                                 #
# ------------------------------------------------------------------ #

def test_realistic_30_file_stream_arrives_byte_by_byte():
    """Simulate a worst-case streaming scenario where the LLM emits one
    BYTE per chunk for a full 30-file response. The parser must yield
    exactly 30 files in the original order."""
    full_response = "".join(
        f'<pebble-file path="file_{i:02d}.ts">\nbody {i}\n</pebble-file>\n'
        for i in range(30)
    )
    p = StreamingFileParser()
    collected: list[tuple[str, str]] = []
    for ch in full_response:
        p.feed(ch)
        collected.extend(p.drain())
    assert len(collected) == 30
    for i, (path, body) in enumerate(collected):
        assert path == f"file_{i:02d}.ts"
        assert body == f"body {i}"
