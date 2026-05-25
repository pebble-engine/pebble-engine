"""Unit tests for pebble.pending_state — Supabase-backed pending token storage.

All Supabase I/O is monkeypatched at the module's _supabase_insert,
_supabase_select, and _supabase_delete symbols so these tests are fully
offline and hermetic.

Coverage:
  email_change_pending:
    - create writes the expected shape to Supabase
    - lookup returns the row when token exists and is not expired
    - lookup returns None when token is unknown (404)
    - lookup returns None when token exists but is expired
  data_export_manifests:
    - create writes the expected shape to Supabase
    - lookup returns the row when token exists and is not expired
    - lookup returns None when token is unknown
    - lookup returns None when token is expired
  fail-closed:
    - helper raises RuntimeError when Supabase env vars are missing
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import pytest

import pebble.pending_state as ps


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _supabase_env(monkeypatch):
    """Ensure Supabase env vars are present for every test."""
    monkeypatch.setenv("PEBBLE_SUPABASE_URL", "https://proj.supabase.co")
    monkeypatch.setenv("PEBBLE_SUPABASE_SERVICE_ROLE_KEY", "service-role-jwt-fake")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _future_iso(hours: int = 24) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _past_iso(hours: int = 25) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


# ===========================================================================
# email_change_pending
# ===========================================================================

class TestCreateEmailChangePending:
    def test_writes_correct_shape_to_supabase(self, monkeypatch):
        """create_email_change_pending inserts a row with the right fields."""
        insert_calls: list[tuple[str, dict]] = []

        def fake_insert(table, row):
            insert_calls.append((table, row))

        monkeypatch.setattr(ps, "_supabase_insert", fake_insert)

        result = ps.create_email_change_pending("uid-001", "new@example.com", ttl_hours=24)

        assert len(insert_calls) == 1
        table, row = insert_calls[0]
        assert table == "email_change_pending"
        assert row["user_id"] == "uid-001"
        assert row["new_email"] == "new@example.com"
        assert "token" in row and len(row["token"]) >= 32
        assert "expires_at" in row
        assert "requested_at" in row

        # Return value carries the token and expiry
        assert result["token"] == row["token"]
        assert result["expires_at"] == row["expires_at"]

    def test_raises_on_supabase_failure(self, monkeypatch):
        """If _supabase_insert raises, create_email_change_pending propagates it."""
        monkeypatch.setattr(ps, "_supabase_insert", lambda t, r: (_ for _ in ()).throw(
            RuntimeError("Supabase down")))

        with pytest.raises(RuntimeError, match="Supabase down"):
            ps.create_email_change_pending("uid-001", "new@example.com")


class TestLookupEmailChangePending:
    def test_returns_row_when_token_valid(self, monkeypatch):
        """Returns the row when the token exists and is not expired."""
        fake_row = {
            "token": "tok-abc",
            "user_id": "uid-001",
            "new_email": "new@example.com",
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": _future_iso(24),
        }
        monkeypatch.setattr(ps, "_supabase_select", lambda table, token: fake_row)

        result = ps.lookup_email_change_pending("tok-abc")

        assert result is not None
        assert result["token"] == "tok-abc"
        assert result["new_email"] == "new@example.com"

    def test_returns_none_when_token_unknown(self, monkeypatch):
        """Returns None when PostgREST returns an empty list (token not found)."""
        monkeypatch.setattr(ps, "_supabase_select", lambda table, token: None)

        result = ps.lookup_email_change_pending("nonexistent-token")

        assert result is None

    def test_returns_none_when_token_expired(self, monkeypatch):
        """Returns None when the row exists but expires_at is in the past."""
        fake_row = {
            "token": "expired-tok",
            "user_id": "uid-001",
            "new_email": "new@example.com",
            "requested_at": _past_iso(48),
            "expires_at": _past_iso(25),  # expired 25h ago
        }
        monkeypatch.setattr(ps, "_supabase_select", lambda table, token: fake_row)

        result = ps.lookup_email_change_pending("expired-tok")

        assert result is None

    def test_raises_on_supabase_failure(self, monkeypatch):
        """Supabase error propagates — fail-closed."""
        monkeypatch.setattr(ps, "_supabase_select",
                            lambda t, tok: (_ for _ in ()).throw(
                                RuntimeError("network error")))

        with pytest.raises(RuntimeError, match="network error"):
            ps.lookup_email_change_pending("tok")


class TestDeleteEmailChangePending:
    def test_calls_supabase_delete(self, monkeypatch):
        """delete_email_change_pending calls _supabase_delete with the right args."""
        delete_calls: list[tuple[str, str]] = []

        def fake_delete(table, token):
            delete_calls.append((table, token))
            return True

        monkeypatch.setattr(ps, "_supabase_delete", fake_delete)

        result = ps.delete_email_change_pending("tok-abc")

        assert result is True
        assert delete_calls == [("email_change_pending", "tok-abc")]


# ===========================================================================
# data_export_manifests
# ===========================================================================

class TestCreateDataExportManifest:
    def test_writes_correct_shape_to_supabase(self, monkeypatch):
        """create_data_export_manifest inserts a row with the right fields."""
        insert_calls: list[tuple[str, dict]] = []

        def fake_insert(table, row):
            insert_calls.append((table, row))

        monkeypatch.setattr(ps, "_supabase_insert", fake_insert)

        result = ps.create_data_export_manifest(
            "uid-002", "/abs/path/export.zip", ttl_hours=24
        )

        assert len(insert_calls) == 1
        table, row = insert_calls[0]
        assert table == "data_export_manifests"
        assert row["user_id"] == "uid-002"
        assert row["zip_path"] == "/abs/path/export.zip"
        assert "token" in row and len(row["token"]) >= 32
        assert "expires_at" in row
        assert "requested_at" in row

        assert result["token"] == row["token"]
        assert result["expires_at"] == row["expires_at"]

    def test_raises_on_supabase_failure(self, monkeypatch):
        monkeypatch.setattr(ps, "_supabase_insert",
                            lambda t, r: (_ for _ in ()).throw(
                                RuntimeError("db error")))

        with pytest.raises(RuntimeError, match="db error"):
            ps.create_data_export_manifest("uid-002", "/abs/path/export.zip")


class TestLookupDataExportManifest:
    def test_returns_row_when_token_valid(self, monkeypatch):
        """Returns the row when the token exists and is not expired."""
        fake_row = {
            "token": "export-tok",
            "user_id": "uid-002",
            "zip_path": "/abs/path/export.zip",
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": _future_iso(24),
        }
        monkeypatch.setattr(ps, "_supabase_select", lambda table, token: fake_row)

        result = ps.lookup_data_export_manifest("export-tok")

        assert result is not None
        assert result["zip_path"] == "/abs/path/export.zip"

    def test_returns_none_when_token_unknown(self, monkeypatch):
        monkeypatch.setattr(ps, "_supabase_select", lambda table, token: None)

        result = ps.lookup_data_export_manifest("no-such-token")

        assert result is None

    def test_returns_none_when_token_expired(self, monkeypatch):
        """Returns None when the row exists but the token has expired."""
        fake_row = {
            "token": "old-export",
            "user_id": "uid-002",
            "zip_path": "/abs/path/export.zip",
            "requested_at": _past_iso(48),
            "expires_at": _past_iso(25),
        }
        monkeypatch.setattr(ps, "_supabase_select", lambda table, token: fake_row)

        result = ps.lookup_data_export_manifest("old-export")

        assert result is None

    def test_raises_on_supabase_failure(self, monkeypatch):
        monkeypatch.setattr(ps, "_supabase_select",
                            lambda t, tok: (_ for _ in ()).throw(
                                RuntimeError("network error")))

        with pytest.raises(RuntimeError, match="network error"):
            ps.lookup_data_export_manifest("tok")


# ===========================================================================
# Fail-closed: missing env vars
# ===========================================================================

class TestFailClosed:
    def test_create_email_change_raises_when_supabase_not_configured(self, monkeypatch):
        """Missing env vars → RuntimeError on the first network call."""
        monkeypatch.delenv("PEBBLE_SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("PEBBLE_SUPABASE_SERVICE_ROLE_KEY", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

        with pytest.raises(RuntimeError, match="SUPABASE_URL"):
            ps.create_email_change_pending("uid-001", "x@example.com")

    def test_lookup_email_change_raises_when_supabase_not_configured(self, monkeypatch):
        monkeypatch.delenv("PEBBLE_SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("PEBBLE_SUPABASE_SERVICE_ROLE_KEY", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

        with pytest.raises(RuntimeError, match="SUPABASE_URL"):
            ps.lookup_email_change_pending("any-token")

    def test_create_export_manifest_raises_when_supabase_not_configured(self, monkeypatch):
        monkeypatch.delenv("PEBBLE_SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("PEBBLE_SUPABASE_SERVICE_ROLE_KEY", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

        with pytest.raises(RuntimeError, match="SUPABASE_URL"):
            ps.create_data_export_manifest("uid-002", "/abs/path/export.zip")

    def test_lookup_export_manifest_raises_when_supabase_not_configured(self, monkeypatch):
        monkeypatch.delenv("PEBBLE_SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("PEBBLE_SUPABASE_SERVICE_ROLE_KEY", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

        with pytest.raises(RuntimeError, match="SUPABASE_URL"):
            ps.lookup_data_export_manifest("any-token")
