"""Tests for pebble.server.dev_registry and the engine-side preview proxy.

The registry is an ephemeral in-process map so that ``/preview/<slug>/``
can proxy to a live ``next dev`` process when PEBBLE_AUTO_RUN=true.  Without
it, Next.js apps 404 on every request because there is no compiled
``index.html`` on disk.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEV_REGISTRY = REPO_ROOT / "pebble" / "server" / "dev_registry.py"
BUILD_PY = REPO_ROOT / "pebble" / "server" / "build.py"
ENGINE_PY = REPO_ROOT / "pebble_engine.py"


# ── registry module ──────────────────────────────────────────────────────────

def test_dev_registry_module_exists():
    assert DEV_REGISTRY.is_file(), f"Missing: {DEV_REGISTRY}"


def test_dev_registry_exports():
    src = DEV_REGISTRY.read_text(encoding="utf-8")
    assert "def register(" in src, "dev_registry missing register()"
    assert "def get_url(" in src, "dev_registry missing get_url()"


def test_dev_registry_liveness_check_present():
    """get_url must do a TCP probe — not just dict lookup — so dead processes
    are evicted rather than causing a proxy hang."""
    src = DEV_REGISTRY.read_text(encoding="utf-8")
    assert "socket" in src, "dev_registry must import socket for liveness check"
    assert "create_connection" in src or "connect(" in src, (
        "dev_registry.get_url must attempt a TCP connection to validate liveness"
    )


def test_dev_registry_evicts_on_dead_port():
    """Functional: register a URL on a port that is not listening; get_url
    should return None and remove the entry so the next call is also None."""
    import socket
    from pebble.server import dev_registry

    # Find a free port (guaranteed closed after the context manager exits).
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        dead_port = s.getsockname()[1]
    # Port is closed now.
    dead_url = f"http://127.0.0.1:{dead_port}"
    dev_registry.register("__test_dead__", dead_url)
    result = dev_registry.get_url("__test_dead__")
    assert result is None, "get_url should return None for a dead port"
    assert "__test_dead__" not in dev_registry._LIVE, (
        "dead entry should be evicted from _LIVE"
    )


# ── build.py wiring ──────────────────────────────────────────────────────────

def test_build_registers_dev_server():
    """build.py must call dev_registry.register after a successful dev-server
    start so _handle_preview can proxy to it."""
    src = BUILD_PY.read_text(encoding="utf-8")
    assert "dev_registry" in src or "_reg_dev" in src, (
        "build.py must import from pebble.server.dev_registry to register the dev server"
    )
    assert re.search(r"_reg_dev\s*\(|register\s*\(slug", src), (
        "build.py must call register(slug, …) after the dev server starts"
    )


# ── engine proxy wiring ───────────────────────────────────────────────────────

def test_engine_has_proxy_to_dev_method():
    src = ENGINE_PY.read_text(encoding="utf-8")
    assert "def _proxy_to_dev(" in src, (
        "pebble_engine.py missing _proxy_to_dev method — "
        "proxy path from _handle_preview is broken"
    )


def test_engine_preview_checks_dev_registry():
    src = ENGINE_PY.read_text(encoding="utf-8")
    assert "dev_registry" in src or "get_url" in src, (
        "pebble_engine._handle_preview must import from dev_registry "
        "to check for a live next dev process"
    )
    assert "_proxy_to_dev" in src, (
        "pebble_engine._handle_preview must call _proxy_to_dev"
    )


def test_engine_proxy_falls_through_to_static():
    """The proxy call must be guarded so a failed proxy still serves static
    files (engine restart case / old builds without a dev server)."""
    src = ENGINE_PY.read_text(encoding="utf-8")
    # The proxy block must be wrapped in try/except or check a bool return.
    # Look for the pattern: `if self._proxy_to_dev(...)` or try/except around it.
    assert re.search(
        r"if\s+self\._proxy_to_dev|try:.*_proxy_to_dev",
        src,
        re.DOTALL,
    ), (
        "pebble_engine must guard _proxy_to_dev so failures fall through "
        "to static file serving"
    )
