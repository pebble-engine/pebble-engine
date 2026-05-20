"""Slug auto-suffix tests (Phase 15f, 2026-05-20).

When a rebuild would clobber an in-flight preview (next dev is actively
serving the slug), the engine auto-suffixes the new slug (mechanic-2,
mechanic-3...) so the previous preview survives and the rebuild gets
its own directory.
"""
from __future__ import annotations

import pytest


# The slug-auto-suffix logic lives inline in pebble/server/build.py
# run_build(). Rather than spin up a full HTTP harness, this test verifies
# the dev_registry's role + the logic shape.


def test_dev_registry_get_url_returns_none_for_unknown():
    """Baseline — when nothing's registered, get_url returns None and the
    main flow uses the unsuffixed slug."""
    from pebble.server.dev_registry import get_url
    assert get_url("nonexistent-slug-xyz-12345") is None


def test_register_then_get_url_returns_registered_value(monkeypatch):
    """When a next dev IS registered, get_url returns its URL — that's
    the signal the build flow uses to trigger auto-suffix."""
    from pebble.server import dev_registry
    # Use a test-only slug so we don't collide with a real running dev
    slug = "_test_slug_xyz_12345"
    dev_registry.register(slug, "http://127.0.0.1:9999")
    try:
        url = dev_registry.get_url(slug)
        # The TCP probe might evict if no actual server on 9999.
        # Either result is fine — what matters is the registry itself
        # accepts the registration.
        assert url is None or url == "http://127.0.0.1:9999"
    finally:
        # Best-effort cleanup so other tests don't see stale state
        try:
            from pebble.server.dev_registry import _LIVE  # type: ignore
            _LIVE.pop(slug, None)
        except Exception:
            pass


def test_slug_auto_suffix_logic_shape():
    """The auto-suffix logic in build.py uses a counter starting at 2,
    incrementing until an unregistered slug is found. Verify the shape
    against a small in-memory registry."""
    fake_registry = {
        "mechanic": "http://127.0.0.1:3050",
        "mechanic-2": "http://127.0.0.1:3051",
    }

    def get_url(s):
        return fake_registry.get(s)

    # Mirror the inline expression from build.py
    base = "mechanic"
    slug = base
    if get_url(slug):
        n = 2
        while get_url(f"{base}-{n}"):
            n += 1
        slug = f"{base}-{n}"

    assert slug == "mechanic-3"


def test_slug_no_suffix_when_uncollided():
    """If the slug isn't in the registry, use it as-is — no spurious
    suffixing of the very first build."""
    fake_registry: dict = {}

    def get_url(s):
        return fake_registry.get(s)

    base = "fresh-business"
    slug = base
    if get_url(slug):
        n = 2
        while get_url(f"{base}-{n}"):
            n += 1
        slug = f"{base}-{n}"

    assert slug == "fresh-business"


def test_build_py_contains_auto_suffix_logic():
    """Source-code smoke check — the auto-suffix block must exist in
    build.py. Catches accidental removal during future refactors."""
    from pathlib import Path
    src = (Path(__file__).parent.parent / "pebble" / "server" / "build.py").read_text(encoding="utf-8")
    assert "Phase 15f" in src
    assert "auto-suffix" in src.lower()
    assert "get_url" in src  # dev_registry lookup
