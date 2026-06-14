"""Tests for concurrent build slot limiter."""
from __future__ import annotations

import threading

import pytest

from pebble import build_queue as bq


def test_disabled_by_default(monkeypatch):
    monkeypatch.delenv("PEBBLE_BUILD_QUEUE", raising=False)
    assert bq.is_enabled() is False
    with bq.slot():
        pass


def test_queue_full_when_at_capacity(monkeypatch):
    monkeypatch.setenv("PEBBLE_BUILD_QUEUE", "true")
    monkeypatch.setenv("PEBBLE_MAX_CONCURRENT_BUILDS", "1")
    bq._SEM = None  # noqa: SLF001 — reset for test

    with bq.slot():
        with pytest.raises(bq.QueueFull):
            with bq.slot():
                pass


def test_two_slots_when_configured(monkeypatch):
    monkeypatch.setenv("PEBBLE_BUILD_QUEUE", "true")
    monkeypatch.setenv("PEBBLE_MAX_CONCURRENT_BUILDS", "2")
    bq._SEM = None  # noqa: SLF001

    entered = threading.Event()
    release = threading.Event()

    def holder():
        with bq.slot():
            entered.set()
            release.wait(timeout=5)

    t = threading.Thread(target=holder, daemon=True)
    t.start()
    assert entered.wait(timeout=2)
    with bq.slot():
        pass
    release.set()
    t.join(timeout=2)
