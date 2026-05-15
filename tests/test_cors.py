"""Tests for the 2026-05-16 NLM-pass hardening:

  - PEBBLE_ALLOWED_ORIGINS opt-in allowlist replaces the blanket ``*``
    when set (so credentialed CORS becomes spec-valid).
  - Wildcard mode drops ``Access-Control-Allow-Credentials: true`` (the
    spec-invalid combo today, which is the *footgun* if anyone later
    flips ``*`` to origin-reflection).
  - ``do_OPTIONS`` refuses preflight for ``/api/internal/*`` so internal
    endpoints don't accept cross-origin browser flows even by accident.
  - The 500 handler no longer leaks ``str(exc)`` to clients — the
    response carries a short ``error_id`` instead, with the full
    traceback logged server-side under that id.
"""
from __future__ import annotations

import http.client
import json
import threading
import time
from http.server import HTTPServer

import pytest

import pebble_engine


# ---- Tiny in-process HTTP fixture ------------------------------------------

@pytest.fixture
def engine_server():
    """Boot PebbleHandler on a real loopback socket so tests can issue
    actual HTTP requests (including OPTIONS preflights) end-to-end."""
    server = HTTPServer(("127.0.0.1", 0), pebble_engine.PebbleHandler)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield host, port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2.0)


def _options(host: str, port: int, path: str, origin: str | None = None) -> http.client.HTTPResponse:
    conn = http.client.HTTPConnection(host, port, timeout=5)
    headers = {"Access-Control-Request-Method": "POST"}
    if origin:
        headers["Origin"] = origin
    conn.request("OPTIONS", path, headers=headers)
    return conn.getresponse()


def _get(host: str, port: int, path: str, origin: str | None = None) -> http.client.HTTPResponse:
    conn = http.client.HTTPConnection(host, port, timeout=5)
    headers = {}
    if origin:
        headers["Origin"] = origin
    conn.request("GET", path, headers=headers)
    return conn.getresponse()


# ---- Wildcard mode (no allowlist) ------------------------------------------

def test_options_default_returns_wildcard_origin(engine_server, monkeypatch):
    monkeypatch.delenv("PEBBLE_ALLOWED_ORIGINS", raising=False)
    host, port = engine_server
    resp = _options(host, port, "/api/generate", origin="https://app.pebbleapp.ai")
    assert resp.status == 204
    assert resp.getheader("Access-Control-Allow-Origin") == "*"


def test_options_default_drops_credentials_when_wildcard(engine_server, monkeypatch):
    """When the engine answers with `Origin: *`, browsers ignore the
    combo of `*` + `Allow-Credentials: true` per the Fetch spec — but
    the misconfiguration is a documented footgun: flipping `*` to
    origin-reflection later silently lights up credentialed CORS for
    every origin. Drop the credentials header in wildcard mode to keep
    the response spec-valid and forwards-safe."""
    monkeypatch.delenv("PEBBLE_ALLOWED_ORIGINS", raising=False)
    host, port = engine_server
    resp = _options(host, port, "/api/generate", origin="https://app.pebbleapp.ai")
    assert resp.getheader("Access-Control-Allow-Credentials") is None


def test_json_response_drops_credentials_when_wildcard(engine_server, monkeypatch):
    monkeypatch.delenv("PEBBLE_ALLOWED_ORIGINS", raising=False)
    host, port = engine_server
    resp = _get(host, port, "/api/health", origin="https://elsewhere.example")
    assert resp.status == 200
    assert resp.getheader("Access-Control-Allow-Origin") == "*"
    assert resp.getheader("Access-Control-Allow-Credentials") is None


# ---- Allowlist mode --------------------------------------------------------

def test_options_with_allowlist_echoes_matching_origin(engine_server, monkeypatch):
    monkeypatch.setenv(
        "PEBBLE_ALLOWED_ORIGINS",
        "https://app.pebbleapp.ai,http://localhost:3001",
    )
    host, port = engine_server
    resp = _options(host, port, "/api/generate", origin="https://app.pebbleapp.ai")
    assert resp.status == 204
    assert resp.getheader("Access-Control-Allow-Origin") == "https://app.pebbleapp.ai"
    # When the origin is an allowlist match, credentialed CORS becomes
    # spec-valid — emit Allow-Credentials so cookies work end-to-end.
    assert resp.getheader("Access-Control-Allow-Credentials") == "true"
    # Vary: Origin tells caches not to serve one allowed origin's
    # response to a different allowed origin's request.
    vary = (resp.getheader("Vary") or "").lower()
    assert "origin" in vary


def test_options_with_allowlist_rejects_unknown_origin(engine_server, monkeypatch):
    monkeypatch.setenv("PEBBLE_ALLOWED_ORIGINS", "https://app.pebbleapp.ai")
    host, port = engine_server
    resp = _options(host, port, "/api/generate", origin="https://evil.example")
    # 204 (or 403; the test only requires that the off-list origin
    # doesn't get a green-light header back).
    assert resp.getheader("Access-Control-Allow-Origin") in (None, "")


def test_options_with_allowlist_handles_no_origin_header(engine_server, monkeypatch):
    """Some non-browser callers (curl, server-to-server) don't send an
    Origin. They should still get a 204 so they're not unnecessarily
    blocked at preflight; we just don't echo a phantom origin back."""
    monkeypatch.setenv("PEBBLE_ALLOWED_ORIGINS", "https://app.pebbleapp.ai")
    host, port = engine_server
    resp = _options(host, port, "/api/generate", origin=None)
    assert resp.status in (204, 200)


def test_json_response_with_allowlist_echoes_matching_origin(engine_server, monkeypatch):
    monkeypatch.setenv("PEBBLE_ALLOWED_ORIGINS", "https://app.pebbleapp.ai")
    host, port = engine_server
    resp = _get(host, port, "/api/health", origin="https://app.pebbleapp.ai")
    assert resp.status == 200
    assert resp.getheader("Access-Control-Allow-Origin") == "https://app.pebbleapp.ai"
    assert resp.getheader("Access-Control-Allow-Credentials") == "true"


# ---- Internal endpoints --------------------------------------------------

def test_options_refuses_preflight_for_internal_paths(engine_server, monkeypatch):
    """Internal endpoints (/api/internal/*) are server-to-server only.
    They never need a browser preflight, so explicitly refuse to bless
    a cross-origin browser flow toward them — defense-in-depth atop
    the existing bearer-secret gate."""
    monkeypatch.delenv("PEBBLE_ALLOWED_ORIGINS", raising=False)
    host, port = engine_server
    resp = _options(host, port, "/api/internal/supabase-webhook",
                    origin="https://evil.example")
    # 405 Method Not Allowed (browsers will block the actual POST).
    # 403 also acceptable. Anything BUT a 204+Allow-Origin is fine.
    assert resp.status in (403, 405)
    assert resp.getheader("Access-Control-Allow-Origin") in (None, "")


# ---- Non-leaking 500 handler ---------------------------------------------

def test_500_error_has_error_id_and_does_not_leak_exception(engine_server, monkeypatch):
    """The previous 500 handler returned ``f"Server error: {exc}"`` which
    could surface internal paths, env keys, or library tracebacks to
    callers. Replace with a stable generic message + correlation id."""
    monkeypatch.delenv("PEBBLE_ALLOWED_ORIGINS", raising=False)
    host, port = engine_server

    # Inject an attribute-error inside an existing handler by sending a
    # request to /api/projects/<slug>/history with an invalid slug shape
    # that bypasses validate_slug? Easier: rely on the GET handler's
    # bare-except wrapping by hitting a path that triggers a downstream
    # raise. We monkey-patch the health handler to raise something with
    # a juicy string in str(exc).
    poison = "SECRET_LEAK_PEBBLE_SUPABASE_WEBHOOK_SECRET=hunter2"

    def boom(self):  # noqa: ANN001
        raise RuntimeError(poison)

    monkeypatch.setattr(pebble_engine.PebbleHandler, "_handle_health", boom)

    resp = _get(host, port, "/api/health")
    body = resp.read().decode("utf-8", errors="replace")
    assert resp.status == 500
    # Critically: the raw exception string MUST NOT leak.
    assert poison not in body, f"Exception detail leaked to client: {body!r}"
    parsed = json.loads(body)
    assert parsed.get("error") == "Internal server error"
    # And we expect a correlation id so operators can grep the engine log.
    assert isinstance(parsed.get("error_id"), str) and len(parsed["error_id"]) >= 6
