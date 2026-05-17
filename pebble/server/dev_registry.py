"""Ephemeral in-process registry of active ``next dev`` servers.

Populated by the build pipeline when PEBBLE_AUTO_RUN=true.  Cleared on
engine restart — correct, because the child processes are also gone.

Both ``pebble.server.build`` (writer) and ``pebble_engine._handle_preview``
(reader) import from here, avoiding any circular-import concern.
"""
from __future__ import annotations
import socket

_LIVE: dict[str, str] = {}  # slug → "http://127.0.0.1:<port>"


def register(slug: str, url: str) -> None:
    """Record a newly-started dev server for *slug*."""
    _LIVE[slug] = url


def get_url(slug: str) -> str | None:
    """Return the live dev-server URL for *slug*, or None.

    Performs a 100 ms TCP probe before returning so a dead process is
    evicted rather than causing a proxy hang.
    """
    url = _LIVE.get(slug)
    if not url:
        return None
    try:
        port = int(url.rsplit(":", 1)[-1])
        with socket.create_connection(("127.0.0.1", port), timeout=0.1):
            pass
        return url
    except OSError:
        _LIVE.pop(slug, None)
        return None
