"""Tests for `pebble.url_fetch.post_webhook` — the SSRF-hardened
outbound webhook delivery primitive.

The function is used by the form-inbox webhook feature (Track 4 of the
2026-05-16 autonomous session): when a generated site's contact form
posts to /api/forms/<slug>, the engine fires-and-forgets a JSON POST
to a user-configured webhook URL (Zapier/Slack/HubSpot/etc.). The URL
is attacker-controlled, so it MUST go through the same SSRF defenses
as the inbound /api/inspire / /api/migrate fetchers.

These tests cover scheme, address, and request-shape concerns. Real-
network calls are mocked at the lowest reasonable layer.
"""
from __future__ import annotations

import json
import socket
from typing import Any

import pytest

from pebble import url_fetch
from pebble.url_fetch import post_webhook


# ---- Input validation ----------------------------------------------------

def test_post_webhook_rejects_empty_url():
    ok, err = post_webhook("", {"x": 1})
    assert ok is False
    assert "url is required" in err.lower()


def test_post_webhook_rejects_none_url():
    ok, err = post_webhook(None, {"x": 1})  # type: ignore[arg-type]
    assert ok is False


def test_post_webhook_rejects_non_http_scheme():
    for bad in ("ftp://example.com", "file:///etc/passwd", "gopher://example.com"):
        ok, err = post_webhook(bad, {})
        assert ok is False, f"should reject {bad}"
        assert "scheme" in err.lower(), f"error should mention scheme for {bad}: {err}"


def test_post_webhook_rejects_when_hostname_missing():
    # "http:///path" has no hostname
    ok, err = post_webhook("http:///path", {})
    assert ok is False
    assert "host" in err.lower()


def test_post_webhook_rejects_invalid_json_payload():
    """The payload must be JSON-serializable. A circular ref or a non-
    serializable object should be caught BEFORE any network call."""
    class NotJsonable:
        pass
    ok, err = post_webhook("https://example.com/hook", {"bad": NotJsonable()})
    assert ok is False
    assert "json" in err.lower() or "serializ" in err.lower()


# ---- SSRF: private-IP resolution ----------------------------------------

def test_post_webhook_rejects_localhost(monkeypatch):
    """localhost is in the explicit blocklist — never resolves."""
    ok, err = post_webhook("http://localhost/hook", {})
    assert ok is False
    assert "private" in err.lower() or "blocked" in err.lower()


def test_post_webhook_rejects_private_resolved_ip(monkeypatch):
    """A public-looking hostname that resolves to a private IP must be
    rejected. Closes the SSRF amplification angle on webhook delivery."""
    def fake_getaddrinfo(host, port, **kwargs):
        # Return a private IP for any host.
        return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("10.0.0.1", 0))]
    monkeypatch.setattr("socket.getaddrinfo", fake_getaddrinfo)
    ok, err = post_webhook("https://attacker.example/hook", {})
    assert ok is False
    assert "private" in err.lower() or "blocked" in err.lower()


def test_post_webhook_rejects_multi_a_with_one_private(monkeypatch):
    """The multi-A SSRF: first record public, second record private.
    The shared _resolve_safely must refuse if ANY record is private."""
    def fake_getaddrinfo(host, port, **kwargs):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("8.8.8.8", 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("169.254.169.254", 0)),
        ]
    monkeypatch.setattr("socket.getaddrinfo", fake_getaddrinfo)
    ok, err = post_webhook("https://attacker.example/hook", {})
    assert ok is False


# ---- Success / failure response handling --------------------------------

class _FakeResponse:
    def __init__(self, status: int, body: bytes = b""):
        self.status = status
        self._body = body

    def read(self, _n: int = -1) -> bytes:
        return self._body

    def getheaders(self):
        return []


class _FakeConn:
    """Mock HTTPSConnection-shaped object."""
    def __init__(self, status: int = 200, body: bytes = b"ok", raises: Exception = None):
        self._status = status
        self._body = body
        self._raises = raises
        self.requests: list[dict[str, Any]] = []
        self.closed = False
        self.timeout = 10.0

    def request(self, method, path, body=None, headers=None):
        if self._raises:
            raise self._raises
        self.requests.append({"method": method, "path": path, "body": body, "headers": headers or {}})

    def getresponse(self):
        if self._raises:
            raise self._raises
        return _FakeResponse(self._status, self._body)

    def close(self):
        self.closed = True


def _fake_resolve(host):
    # Pretend every hostname resolves to a public IP.
    return ("8.8.8.8", socket.AF_INET)


def test_post_webhook_success_returns_true(monkeypatch):
    fake_conn = _FakeConn(status=200)
    monkeypatch.setattr(url_fetch, "_resolve_safely", _fake_resolve)
    monkeypatch.setattr(url_fetch, "_open_pinned", lambda *_args, **_kw: fake_conn)
    ok, err = post_webhook("https://example.com/hook", {"event": "form.submitted"})
    assert ok is True
    assert err is None
    # Verify we sent a POST with JSON body
    assert len(fake_conn.requests) == 1
    req = fake_conn.requests[0]
    assert req["method"] == "POST"
    assert json.loads(req["body"]) == {"event": "form.submitted"}
    assert req["headers"]["Content-Type"].startswith("application/json")


def test_post_webhook_treats_201_204_as_success(monkeypatch):
    """Many webhook receivers reply 201 Created or 204 No Content — also success."""
    for status in (200, 201, 202, 204, 299):
        fake_conn = _FakeConn(status=status)
        monkeypatch.setattr(url_fetch, "_resolve_safely", _fake_resolve)
        monkeypatch.setattr(url_fetch, "_open_pinned", lambda *_a, **_k: fake_conn)
        ok, err = post_webhook("https://example.com/hook", {})
        assert ok, f"status {status} should be treated as success, got error: {err}"


def test_post_webhook_returns_error_on_4xx(monkeypatch):
    fake_conn = _FakeConn(status=404)
    monkeypatch.setattr(url_fetch, "_resolve_safely", _fake_resolve)
    monkeypatch.setattr(url_fetch, "_open_pinned", lambda *_a, **_k: fake_conn)
    ok, err = post_webhook("https://example.com/hook", {})
    assert ok is False
    assert "404" in err


def test_post_webhook_returns_error_on_5xx(monkeypatch):
    fake_conn = _FakeConn(status=503)
    monkeypatch.setattr(url_fetch, "_resolve_safely", _fake_resolve)
    monkeypatch.setattr(url_fetch, "_open_pinned", lambda *_a, **_k: fake_conn)
    ok, err = post_webhook("https://example.com/hook", {})
    assert ok is False
    assert "503" in err


def test_post_webhook_returns_error_on_timeout(monkeypatch):
    fake_conn = _FakeConn(raises=socket.timeout("simulated"))
    monkeypatch.setattr(url_fetch, "_resolve_safely", _fake_resolve)
    monkeypatch.setattr(url_fetch, "_open_pinned", lambda *_a, **_k: fake_conn)
    ok, err = post_webhook("https://example.com/hook", {})
    assert ok is False
    assert "timeout" in err.lower()


def test_post_webhook_returns_error_on_oserror(monkeypatch):
    fake_conn = _FakeConn(raises=OSError("conn refused"))
    monkeypatch.setattr(url_fetch, "_resolve_safely", _fake_resolve)
    monkeypatch.setattr(url_fetch, "_open_pinned", lambda *_a, **_k: fake_conn)
    ok, err = post_webhook("https://example.com/hook", {})
    assert ok is False
    assert "network error" in err.lower() or "oserror" in err.lower()


def test_post_webhook_closes_connection_on_failure(monkeypatch):
    """Defensive: even on exception, the socket must be closed."""
    fake_conn = _FakeConn(raises=OSError("boom"))
    monkeypatch.setattr(url_fetch, "_resolve_safely", _fake_resolve)
    monkeypatch.setattr(url_fetch, "_open_pinned", lambda *_a, **_k: fake_conn)
    post_webhook("https://example.com/hook", {})
    assert fake_conn.closed is True


def test_post_webhook_sends_pebble_user_agent(monkeypatch):
    fake_conn = _FakeConn(status=200)
    monkeypatch.setattr(url_fetch, "_resolve_safely", _fake_resolve)
    monkeypatch.setattr(url_fetch, "_open_pinned", lambda *_a, **_k: fake_conn)
    post_webhook("https://example.com/hook", {})
    ua = fake_conn.requests[0]["headers"].get("User-Agent", "")
    assert "Pebble" in ua, f"User-Agent should identify Pebble, got {ua!r}"
