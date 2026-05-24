"""Tests for the data-export flow.

POST /api/account/export-request:
- Authed user → kicks off background zip + emails link
- Rate-limited: 1 per 24h

GET /api/account/export-download?token=<token>:
- Valid unused token → streams the zip file
- Expired token → 410 Gone
- Unknown token → 404
"""
from __future__ import annotations

import json
import time
import zipfile
from pathlib import Path

import pytest

import pebble.server.account as account_mod


class _FakeHandler:
    def __init__(self, *, path="/api/account/export-request"):
        self.path = path
        self.headers = {"Authorization": "Bearer test", "User-Agent": "TestUA/1.0"}
        self.client_address = ("127.0.0.1", 0)
        self.responses: list[tuple[int, dict]] = []
        self.raw_writes: list[bytes] = []
        self.sent_status = None
        self.sent_headers: dict[str, str] = {}

    def _json(self, status, body):
        self.responses.append((status, body))

    def send_response(self, status):
        self.sent_status = status

    def send_header(self, k, v):
        self.sent_headers[k] = v

    def end_headers(self):
        pass

    @property
    def wfile(self):
        outer = self

        class W:
            def write(self, data):
                outer.raw_writes.append(data)

        return W()


def test_export_request_kicks_off_background_thread(tmp_path, monkeypatch):
    """Returns 200 immediately, audit_log data_export_requested written,
    background thread starts and eventually emails + writes data_export_delivered."""
    out = tmp_path / "output"
    out.mkdir()
    (out / "project-a" / "site").mkdir(parents=True)
    (out / "project-a" / "brief.json").write_text(
        json.dumps({"_user_id": "u-1", "name": "A"})
    )
    monkeypatch.setattr(account_mod, "OUTPUT_DIR", out)
    monkeypatch.setattr(
        account_mod, "require_user",
        lambda h: {"id": "u-1", "email": "test@example.com"},
    )
    # Reset limiter so prior test state doesn't bleed.
    account_mod._reset_data_export_limiter_for_tests()

    audit_calls: list[dict] = []
    monkeypatch.setattr(
        "pebble.audit_log.log_event_for_handler",
        lambda **kw: audit_calls.append(kw),
    )
    monkeypatch.setattr(
        "pebble.audit_log.log_event",
        lambda **kw: audit_calls.append(kw),
    )
    email_calls: list[tuple[str, str]] = []
    monkeypatch.setattr(
        "pebble.email.send_data_export_ready",
        lambda email, download_url: email_calls.append((email, download_url)),
    )

    h = _FakeHandler()
    account_mod.run_request_data_export(h)

    # Returns 200 immediately.
    assert h.responses[-1][0] == 200
    assert "email" in (h.responses[-1][1].get("message") or "").lower()

    # Audit data_export_requested logged (synchronous, before thread).
    assert any(c.get("event_type") == "data_export_requested" for c in audit_calls)

    # Background thread completes (give it a moment).
    for _ in range(50):
        if email_calls or any(
            c.get("event_type") == "data_export_delivered" for c in audit_calls
        ):
            break
        time.sleep(0.1)

    # Email sent + delivered audit row written.
    assert len(email_calls) == 1
    assert email_calls[0][0] == "test@example.com"
    assert "/api/account/export-download?token=" in email_calls[0][1]
    assert any(c.get("event_type") == "data_export_delivered" for c in audit_calls)


def test_export_request_rate_limited(tmp_path, monkeypatch):
    """Second request within 24h → 429."""
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(account_mod, "OUTPUT_DIR", out)
    monkeypatch.setattr(
        account_mod, "require_user",
        lambda h: {"id": "u-1", "email": "test@example.com"},
    )
    account_mod._reset_data_export_limiter_for_tests()

    monkeypatch.setattr("pebble.audit_log.log_event_for_handler", lambda **kw: None)
    monkeypatch.setattr("pebble.audit_log.log_event", lambda **kw: None)
    monkeypatch.setattr(
        "pebble.email.send_data_export_ready", lambda email, download_url: None
    )

    h1 = _FakeHandler()
    account_mod.run_request_data_export(h1)
    assert h1.responses[-1][0] == 200

    # Second request immediately — must be rate-limited.
    h2 = _FakeHandler()
    account_mod.run_request_data_export(h2)
    assert h2.responses[-1][0] == 429


def test_download_with_valid_token_streams_zip(tmp_path, monkeypatch):
    """Manifest with valid token → 200 + zip bytes streamed."""
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(account_mod, "OUTPUT_DIR", out)

    # Create a real zip file + manifest.
    user_id = "u-1"
    exports = out / ".exports" / user_id
    exports.mkdir(parents=True)
    zip_path = exports / "test-export.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("test.txt", "hello")

    manifest_path = exports / "test-export.manifest.json"
    expires_at = "2099-01-01T00:00:00+00:00"  # far future
    manifest_path.write_text(
        json.dumps({
            "token": "good-token-abc",
            "zip_path": str(zip_path),
            "user_id": user_id,
            "expires_at": expires_at,
            "requested_at": "2026-05-24T00:00:00+00:00",
        })
    )

    h = _FakeHandler(path="/api/account/export-download?token=good-token-abc")
    account_mod.run_download_export(h)
    assert h.sent_status == 200
    assert "attachment" in h.sent_headers.get("Content-Disposition", "")
    # Streamed bytes are the zip file.
    streamed = b"".join(h.raw_writes)
    assert streamed.startswith(b"PK")  # zip magic bytes


def test_download_with_expired_token_410(tmp_path, monkeypatch):
    """Expired token → 410 Gone (tells user to re-request)."""
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(account_mod, "OUTPUT_DIR", out)

    exports = out / ".exports" / "u-1"
    exports.mkdir(parents=True)
    zip_path = exports / "expired.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("x", "")
    manifest_path = exports / "expired.manifest.json"
    manifest_path.write_text(
        json.dumps({
            "token": "expired-tok",
            "zip_path": str(zip_path),
            "user_id": "u-1",
            "expires_at": "2020-01-01T00:00:00+00:00",  # past
            "requested_at": "2020-01-01T00:00:00+00:00",
        })
    )

    h = _FakeHandler(path="/api/account/export-download?token=expired-tok")
    account_mod.run_download_export(h)
    assert h.responses[-1][0] == 410


def test_download_with_unknown_token_404(tmp_path, monkeypatch):
    """Unknown token → 404 (no manifest matches)."""
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(account_mod, "OUTPUT_DIR", out)

    h = _FakeHandler(path="/api/account/export-download?token=does-not-exist")
    account_mod.run_download_export(h)
    assert h.responses[-1][0] == 404
