"""Concurrent build slot limiter — queue v1 (2026-06-12).

When ``PEBBLE_BUILD_QUEUE=true``, at most ``PEBBLE_MAX_CONCURRENT_BUILDS``
( default 1 ) full LLM builds may run at once. Extra requests get HTTP 503
with ``code: queue_full`` so clients can retry.

This is the Phase-5 scale path from the senior plan — enough for beta
(5–20 users) without Redis. Swap for a durable job queue when you need
multiple engine workers.
"""
from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from typing import Iterator


class QueueFull(Exception):
    """Raised when no build slot is available."""


_ENABLED_VALUES = frozenset({"1", "true", "yes", "on"})
_SEM: threading.Semaphore | None = None
_LOCK = threading.Lock()
_ACTIVE = 0


def is_enabled() -> bool:
    return os.environ.get("PEBBLE_BUILD_QUEUE", "").strip().lower() in _ENABLED_VALUES


def max_concurrent() -> int:
    try:
        n = int(os.environ.get("PEBBLE_MAX_CONCURRENT_BUILDS", "1"))
        return max(1, min(n, 32))
    except ValueError:
        return 1


def _sem() -> threading.Semaphore:
    global _SEM
    if _SEM is None:
        with _LOCK:
            if _SEM is None:
                _SEM = threading.Semaphore(max_concurrent())
    return _SEM


def stats() -> dict:
    sem = _sem()
    with _LOCK:
        active = _ACTIVE
    return {
        "enabled":       is_enabled(),
        "max":           max_concurrent(),
        "active":        active,
        "slots_free":    sem._value,  # noqa: SLF001 — observability only
    }


@contextmanager
def slot() -> Iterator[None]:
    """Acquire one build slot when queue mode is on; no-op otherwise."""
    if not is_enabled():
        yield
        return
    sem = _sem()
    if not sem.acquire(blocking=False):
        raise QueueFull()
    global _ACTIVE
    with _LOCK:
        _ACTIVE += 1
    try:
        yield
    finally:
        with _LOCK:
            _ACTIVE -= 1
        sem.release()


__all__ = ["QueueFull", "is_enabled", "max_concurrent", "slot", "stats"]
