"""SSE build stream generator for POST /api/generate-stream.

Runs run_build() in a background thread with a progress_cb that puts
(event_type, data) tuples into a thread-safe queue. The generator
reads from that queue and yields SSE frames to FastAPI's
StreamingResponse.

Event types emitted (in order):
  started    {"slug": str}
  industry   {"key": str | null}
  style      {"dna_label": str, "dna_id": str}
  generating {"model": str, "max_tokens": int}
  writing    {"file_count": int}
  evaluating {}                    (only when PEBBLE_AUTO_REPAIR=true)
  done       {full GenerateResponse payload}
  error      {"error": str}        (then stream closes)
"""
from __future__ import annotations

import json
import queue
import threading
from typing import Iterator

from pebble.server.build import run_build
from pebble.server.shim import make_shim

_TIMEOUT_S = 180  # seconds before we give up waiting for the next event


def build_stream_generator(
    body: bytes,
    headers: dict,
    client_host: str = "127.0.0.1",
) -> Iterator[str]:
    """Yield SSE frames while run_build() runs in a background thread."""
    q: queue.Queue = queue.Queue()
    shim = make_shim(
        path="/api/generate",
        method="POST",
        body=body,
        headers=headers,
        client_host=client_host,
    )

    def _cb(event_type: str, data: dict) -> None:
        q.put((event_type, data))

    def _run() -> None:
        try:
            run_build(shim, generate=True, progress_cb=_cb)
        except Exception as exc:
            q.put(("error", {"error": str(exc)}))
        finally:
            q.put(None)  # sentinel — stream is done

    threading.Thread(target=_run, daemon=True).start()

    while True:
        try:
            item = q.get(timeout=_TIMEOUT_S)
        except queue.Empty:
            yield f'event: error\ndata: {json.dumps({"error": f"build timed out after {_TIMEOUT_S}s"})}\n\n'
            break
        if item is None:
            break
        event_type, data = item
        yield f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
