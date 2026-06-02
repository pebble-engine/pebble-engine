# pebble/server/preview_paths.py
"""Pure path helper for the /preview/<slug>/ dev-server proxy.

The router strips the query string off ``handler.path`` for route matching
and stashes the original on ``handler._raw_path``. When proxying to a live
``next dev`` server we must forward the ORIGINAL path (query intact) — Next's
image optimizer (/_next/image?url=...&w=...&q=...) 400s without its query.
Isolated here so it is unit-testable without booting the engine.
"""
from __future__ import annotations


def preview_forward_path(raw_path: str, slug_prefix: str) -> str:
    """Strip ``slug_prefix`` from ``raw_path``, preserving the query string.

    ``raw_path``    — original request path WITH query (handler._raw_path),
                      e.g. ``/preview/foo/_next/image?url=X&w=1920&q=75``.
    ``slug_prefix`` — ``/preview/<raw-slug>`` (no trailing slash).

    Returns the path to send to the dev server. Empty remainder and
    query-only remainder both normalize to a leading ``/`` so the dev
    server always receives an absolute path.
    """
    if not raw_path.startswith(slug_prefix):
        return raw_path  # defensive: nothing to strip
    rest = raw_path[len(slug_prefix):]
    if not rest or rest.startswith("?"):
        rest = "/" + rest
    return rest
