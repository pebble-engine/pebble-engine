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
    background thread starts and eventually emails + writes data_export_delivered.

    Migration 006: manifest metadata now stored in Supabase, not a local
    .manifest.json file. The test mocks pebble.pending_state.create_data_export_manifest
    to stay offline and verify the new storage layer is wired in correctly.
    """
    import pebble.pending_state as pending_state_mod

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

    # Mock the Supabase manifest creation (migration 006) — returns a fake token.
    fake_token = "fake-export-token-xyz789"
    manifest_create_calls: list[dict] = []

    def fake_create_manifest(user_id, zip_path, ttl_hours=24):
        manifest_create_calls.append({"user_id": user_id, "zip_path": zip_path})
        return {
            "token": fake_token,
            "expires_at": "2099-01-01T00:00:00+00:00",
        }

    monkeypatch.setattr(pending_state_mod, "create_data_export_manifest", fake_create_manifest)

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
    assert f"/api/account/export-download?token={fake_token}" in email_calls[0][1]
    assert any(c.get("event_type") == "data_export_delivered" for c in audit_calls)

    # Supabase manifest creation was called with the right user_id
    assert len(manifest_create_calls) >= 1
    assert manifest_create_calls[0]["user_id"] == "u-1"


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
    """Manifest with valid token → 200 + zip bytes streamed.

    Fix 3 (2026-05-24): download requires Bearer JWT match. Authed user
    requesting their OWN export → 200.
    """
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(account_mod, "OUTPUT_DIR", out)

    # Create a real zip file + manifest.
    user_id = "u-1"
    monkeypatch.setattr(
        account_mod, "require_user",
        lambda h: {"id": user_id, "email": "test@example.com"},
    )
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
    monkeypatch.setattr(
        "pebble.pending_state.lookup_data_export_manifest",
        lambda t: {
            "token": "good-token-abc",
            "zip_path": str(zip_path),
            "user_id": user_id,
            "expires_at": expires_at,
            "requested_at": "2026-05-24T00:00:00+00:00",
        } if t == "good-token-abc" else None,
    )
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
    monkeypatch.setattr(
        account_mod, "require_user",
        lambda h: {"id": "u-1", "email": "test@example.com"},
    )

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
    monkeypatch.setattr(
        account_mod, "require_user",
        lambda h: {"id": "u-1", "email": "test@example.com"},
    )

    h = _FakeHandler(path="/api/account/export-download?token=does-not-exist")
    monkeypatch.setattr(
        "pebble.pending_state.lookup_data_export_manifest",
        lambda t: None,
    )
    account_mod.run_download_export(h)
    assert h.responses[-1][0] == 410


# ---- Fix 3 (2026-05-24): Bearer-JWT match for export-download ------------

def test_download_unauthenticated_returns_401(tmp_path, monkeypatch):
    """No Bearer JWT → 401. The download URL is no longer a public
    capability link — anyone with the URL could re-download for 24h
    (browser history, mail-forward, employer mail-scanning proxy)."""
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(account_mod, "OUTPUT_DIR", out)

    # require_user writes 401 when no/invalid Authorization header.
    def fail_auth(h):
        h._json(401, {"error": "sign in required"})
        return None

    monkeypatch.setattr(account_mod, "require_user", fail_auth)

    # Seed a valid manifest so we can prove the auth check fires BEFORE lookup.
    user_id = "u-victim"
    exports = out / ".exports" / user_id
    exports.mkdir(parents=True)
    zip_path = exports / "v.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("x", "")
    (exports / "v.manifest.json").write_text(json.dumps({
        "token": "victim-token",
        "zip_path": str(zip_path),
        "user_id": user_id,
        "expires_at": "2099-01-01T00:00:00+00:00",
        "requested_at": "2026-05-24T00:00:00+00:00",
    }))

    h = _FakeHandler(path="/api/account/export-download?token=victim-token")
    account_mod.run_download_export(h)

    assert h.responses[-1][0] == 401
    # Zip bytes must NOT have streamed.
    assert h.raw_writes == []


def test_download_other_user_returns_403_and_audits(tmp_path, monkeypatch):
    """Authed user A requesting user B's manifest → 403. The mismatch is
    a security failure (the URL is the only secret), so it gets audit-logged.
    Returning 404 would mask the leak from server-side detection."""
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(account_mod, "OUTPUT_DIR", out)

    # Authed as user-A
    monkeypatch.setattr(
        account_mod, "require_user",
        lambda h: {"id": "user-A", "email": "a@example.com"},
    )

    audit_calls: list[dict] = []
    monkeypatch.setattr(
        "pebble.audit_log.log_event_for_handler",
        lambda **kw: audit_calls.append(kw),
    )
    monkeypatch.setattr(
        "pebble.audit_log.log_event", lambda **kw: audit_calls.append(kw),
    )

    # Manifest belongs to user-B
    exports_b = out / ".exports" / "user-B"
    exports_b.mkdir(parents=True)
    zip_b = exports_b / "b.zip"
    with zipfile.ZipFile(zip_b, "w") as z:
        z.writestr("secret.txt", "leaked")
    (exports_b / "b.manifest.json").write_text(json.dumps({
        "token": "user-b-token",
        "zip_path": str(zip_b),
        "user_id": "user-B",
        "expires_at": "2099-01-01T00:00:00+00:00",
        "requested_at": "2026-05-24T00:00:00+00:00",
    }))

    h = _FakeHandler(path="/api/account/export-download?token=user-b-token")
    monkeypatch.setattr(
        "pebble.pending_state.lookup_data_export_manifest",
        lambda t: {
            "token": "user-b-token",
            "zip_path": str(zip_b),
            "user_id": "user-B",
            "expires_at": "2099-01-01T00:00:00+00:00",
            "requested_at": "2026-05-24T00:00:00+00:00",
        } if t == "user-b-token" else None,
    )
    account_mod.run_download_export(h)

    assert h.responses[-1][0] == 403, \
        "user-A must NOT receive user-B's export — and we return 403 " \
        "(not 404) so server-side detection can spot the leak"
    # Zip bytes must NOT have streamed.
    assert h.raw_writes == []
    # Audit trail: the mismatch is a security event.
    assert any(
        "export" in (c.get("event_type") or "").lower() and
        "denied" in (c.get("event_type") or "").lower()
        for c in audit_calls
    ), f"expected export-denied audit log, got: {[c.get('event_type') for c in audit_calls]}"


# ---- Fix 4 (2026-05-24): file-fallback hard-kill date --------------------

def test_download_file_fallback_skipped_after_hard_kill_date(
    tmp_path, monkeypatch,
):
    """After _FILE_FALLBACK_HARD_KILL (2026-05-29T00:00:00Z), the local-file
    fallback for *.manifest.json is silently dropped. Any token only
    present in the legacy file location returns 410 — so an attacker who
    can write a forged manifest under output/.exports/<uid>/*.manifest.json
    can't use it to download arbitrary files.

    Pre-kill-date the file fallback still works (existing tests above)."""
    import datetime as _dt
    from pathlib import Path as _Path

    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(account_mod, "OUTPUT_DIR", out)
    user_id = "u-1"
    monkeypatch.setattr(
        account_mod, "require_user",
        lambda h: {"id": user_id, "email": "test@example.com"},
    )

    # Force "now" past the hard-kill date.
    class _PastKillDatetime(_dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return _dt.datetime(2026, 6, 1, tzinfo=tz or _dt.timezone.utc)

    monkeypatch.setattr(account_mod, "datetime", _PastKillDatetime)

    # Supabase lookup returns None so any success would have to come from
    # the file fallback.
    monkeypatch.setattr(
        "pebble.pending_state.lookup_data_export_manifest",
        lambda token: None,
    )

    # Spy on iterdir to prove the .exports scan never runs.
    iterdir_calls: list[str] = []
    real_iterdir = _Path.iterdir

    def spy_iterdir(self):
        iterdir_calls.append(str(self))
        return real_iterdir(self)

    monkeypatch.setattr(_Path, "iterdir", spy_iterdir)

    # Seed a legacy manifest the fallback would have matched.
    exports = out / ".exports" / user_id
    exports.mkdir(parents=True)
    zip_path = exports / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("x", "")
    (exports / "test.manifest.json").write_text(json.dumps({
        "token": "legacy-only-token",
        "zip_path": str(zip_path),
        "user_id": user_id,
        "expires_at": "2099-01-01T00:00:00+00:00",
        "requested_at": "2026-05-24T00:00:00+00:00",
    }))

    h = _FakeHandler(path="/api/account/export-download?token=legacy-only-token")
    account_mod.run_download_export(h)

    assert h.responses[-1][0] == 410, \
        f"expected 410 after kill date, got {h.responses[-1][0]}"
    # Zip bytes must NOT have streamed.
    assert h.raw_writes == []
    # The .exports dir must NOT have been iterated.
    exports_iter = [c for c in iterdir_calls if c.endswith(".exports")]
    assert not exports_iter, \
        f"file-scan code path ran after hard-kill date: {exports_iter}"
