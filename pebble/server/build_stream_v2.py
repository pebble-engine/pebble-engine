"""SSE build stream for POST /api/v2/generate-stream.

Runs build_v2_core() in a background thread with a progress_cb that puts
(event_type, data) tuples into a thread-safe queue; the generator reads from
the queue and yields SSE frames. Mirrors build_stream.py (the v1 path) so the
v3 workspace's live build feed renders identically.

Event types emitted (in order):
  started        {"slug": str, "business_name": str}
  industry       {"key": str | null}
  generating     {"model": str, "max_tokens": int}
  style          {"dna_label": str, "dna_id": str, "palette": [...], "signature_moves": []}
  writing        {"file_count": int}
  preview_ready  {"slug": str, "url": str}
  done           {full GenerateResponse payload}
  error          {"error": str, "status"?: int}   (then stream closes)
"""
from __future__ import annotations

import json
import queue
import threading
from typing import Iterator

from pebble.server.build_v2 import build_v2_core, BuildV2Error

_TIMEOUT_S = 180  # v2 builds are ~10-30s; 3 min is a generous stuck-call net.


def build_stream_v2_generator(body: bytes) -> Iterator[str]:
    """Yield SSE frames while build_v2_core() runs in a background thread."""
    q: queue.Queue = queue.Queue()

    try:
        brief = json.loads(body.decode("utf-8")) if body else {}
    except Exception:
        yield f'event: error\ndata: {json.dumps({"error": "invalid json body"})}\n\n'
        return

    def _cb(event_type: str, data: dict) -> None:
        q.put((event_type, data))

    def _run() -> None:
        try:
            result = build_v2_core(brief, progress_cb=_cb)
            q.put(("done", result))
        except BuildV2Error as e:
            q.put(("error", {"error": e.message, "status": e.status}))
        except Exception as exc:  # noqa: BLE001 — surface any build crash as SSE
            q.put(("error", {"error": str(exc)}))
        finally:
            q.put(None)  # sentinel

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
