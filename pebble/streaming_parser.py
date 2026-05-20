"""Incremental `<pebble-file>` block parser.

The legacy `pebble_engine.parse_files` operates on the FULL LLM response
after the call completes. For the streaming flow (Phase 13a) we need a
parser that accepts text chunks as they arrive and yields each
``(path, content)`` pair as soon as the closing ``</pebble-file>`` tag
shows up — so the engine can write the file to disk and emit a
``file_written`` SSE event in real time, instead of holding 50 files in
memory and writing them all at once at the end.

The parser is FORGIVING in the same ways the legacy parser is:
- Tolerates LLM-emitted typos in the close tag (`</pebble-file>`,
  `</pebble file>`, `</p-file>` — anything matching the same close regex).
- Skips preamble text before the first `<pebble-file>` tag.
- Trims the trailing close tag from each emitted block.

It is STRICTER in one way:
- Refuses to emit a block until its close tag is unambiguously present
  (we don't guess based on the next-open boundary). This avoids
  flushing an incomplete file on a partial stream that might get
  interrupted mid-block. If the stream ends with an unclosed block,
  `flush_remaining()` can recover whatever was captured.

Usage:
    parser = StreamingFileParser()
    for chunk in client.generate_stream(...):
        parser.feed(chunk)
        for path, content in parser.drain():
            write_file(path, content)
            emit("file_written", {"path": path})
    # Stream ended — if the LLM left a final block without a close tag,
    # yield it on best-effort:
    for path, content in parser.flush_remaining():
        write_file(path, content)
"""
from __future__ import annotations

import re
from typing import Iterator


# Tolerant patterns matching `pebble_engine.FILE_OPEN_RE` and
# `_PEBBLE_FILE_CLOSE_RE`. Keep these in sync if the upstream constants
# change — pinned by test_streaming_parser.py.
_OPEN_RE  = re.compile(r'<pebble-file\s+path="([^"]+)">\s*\n?', re.IGNORECASE)
_CLOSE_RE = re.compile(r'</p[a-z]*[\s-]?file>', re.IGNORECASE)


class StreamingFileParser:
    """Stateful parser that yields complete <pebble-file> blocks as they
    finish streaming in. Thread-unsafe — use one instance per stream."""

    __slots__ = ("_buf", "_completed", "_total_yielded")

    def __init__(self) -> None:
        self._buf: str = ""
        # Queue of (path, content) tuples ready to be drained. We hold
        # them in a list rather than yielding directly so the engine can
        # `drain()` at its own cadence (e.g. once per stream chunk) and
        # observe deterministic ordering.
        self._completed: list[tuple[str, str]] = []
        self._total_yielded: int = 0

    def feed(self, chunk: str) -> None:
        """Append a chunk of streaming text to the buffer and detect
        any newly-completed `<pebble-file>` blocks. Safe to call with
        an empty string."""
        if not chunk:
            return
        self._buf += chunk
        self._extract_complete_blocks()

    def drain(self) -> Iterator[tuple[str, str]]:
        """Yield every (path, content) tuple that completed since the
        last drain. Drain is non-destructive past the act of yielding —
        already-yielded tuples are not re-emitted."""
        while self._completed:
            yield self._completed.pop(0)

    def total_yielded(self) -> int:
        """Total number of complete file blocks the parser has surfaced
        (since instantiation). Includes anything still queued in
        ``_completed`` waiting to be drained."""
        return self._total_yielded

    def flush_remaining(self) -> Iterator[tuple[str, str]]:
        """At stream end, recover any final block whose close tag never
        arrived. Best-effort — if the buffer still contains an open
        block with no close, treat the rest of the buffer as the body
        and emit it. Useful for surviving a stream that gets truncated
        mid-final-file (still better to surface than to lose silently)."""
        # First, drain anything already queued
        yield from self.drain()

        # Then attempt to recover an unterminated trailing block
        open_match = _OPEN_RE.search(self._buf)
        if not open_match:
            return
        path = open_match.group(1)
        # No close tag found — take everything from the open to EOF
        content = self._buf[open_match.end():].rstrip()
        # Strip any partial close tag fragment at the end (e.g. "</pebbl")
        # by walking back until we find clean content. Conservative:
        # only strip obvious partial tag starts.
        for partial in ("</pebble-file", "</pebble-fil", "</pebble-fi",
                        "</pebble-f", "</pebble-", "</pebble", "</pebbl",
                        "</pebb", "</peb", "</pe", "</p", "</", "<"):
            if content.endswith(partial):
                content = content[:-len(partial)].rstrip()
                break
        if content:
            self._buf = self._buf[:open_match.start()]  # remove emitted region
            self._completed.append((path, content))
            self._total_yielded += 1
            yield self._completed.pop(0)

    # ---- internals -------------------------------------------------------

    def _extract_complete_blocks(self) -> None:
        """Scan the buffer for complete <pebble-file>...</pebble-file>
        pairs. For each one found, append to _completed and advance the
        buffer past it. Leaves any incomplete trailing block in the buffer
        for the next feed() call to complete."""
        while True:
            open_match = _OPEN_RE.search(self._buf)
            if not open_match:
                # No open tag at all — keep buffering but trim safe
                # prefix to bound memory if the LLM emits a long preamble.
                # We keep the last 80 chars (max length of an open tag
                # being constructed) so we don't truncate mid-tag.
                if len(self._buf) > 200:
                    self._buf = self._buf[-80:]
                return

            # Look for the corresponding close tag AFTER the open
            after_open = self._buf[open_match.end():]
            close_match = _CLOSE_RE.search(after_open)
            if not close_match:
                # Open tag present but no close yet — wait for more chunks
                return

            path = open_match.group(1)
            # Content is everything between the open tag's end and the
            # close tag's start. Strip trailing whitespace (matches the
            # legacy parser's behavior via _TRAILING_CLOSE_RE).
            content = after_open[:close_match.start()].rstrip()
            self._completed.append((path, content))
            self._total_yielded += 1

            # Advance buffer past the close tag so subsequent searches
            # start fresh
            advance_to = open_match.end() + close_match.end()
            self._buf = self._buf[advance_to:]


__all__ = ["StreamingFileParser"]
