"""Pebble Engine — structured logging.

A single shared ``pebble`` logger replaces the ad-hoc ``print()`` calls that
used to be scattered across the codebase. Level is controlled by the
``PEBBLE_LOG_LEVEL`` environment variable (default ``INFO``). Output goes to
stderr so it doesn't collide with stdout-based tooling or HTTP body bytes.

Usage:

    from pebble.log import log
    log.info("Fetching industry photos from Pexels...")
    log.warning("industry intel resolution failed: %s", exc)

The format keeps the engine's existing visual style — two-space indent so
progress messages line up under the startup banner — while adding a level
prefix and an ISO timestamp.

The HTTP server's own request log (``log_message`` on ``BaseHTTPRequestHandler``)
is intentionally untouched. That's a different concern and Python's stdlib
already does it.
"""

from __future__ import annotations

import logging
import os
import sys


_DEFAULT_LEVEL = "INFO"
_FORMAT = "%(asctime)s %(levelname)-5s %(message)s"
_DATEFMT = "%Y-%m-%dT%H:%M:%S"


def _resolve_level() -> int:
    name = os.environ.get("PEBBLE_LOG_LEVEL", _DEFAULT_LEVEL).strip().upper() or _DEFAULT_LEVEL
    return getattr(logging, name, logging.INFO)


def _configure() -> logging.Logger:
    logger = logging.getLogger("pebble")
    # Idempotent: re-importing must not stack handlers.
    if getattr(logger, "_pebble_configured", False):
        logger.setLevel(_resolve_level())
        return logger
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATEFMT))
    logger.addHandler(handler)
    logger.setLevel(_resolve_level())
    logger.propagate = False  # don't double-log via the root logger
    logger._pebble_configured = True  # type: ignore[attr-defined]
    return logger


log = _configure()


__all__ = ["log"]
