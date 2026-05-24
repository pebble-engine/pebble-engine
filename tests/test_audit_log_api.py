"""Tests for /api/account/activity — returns the calling user's
last 100 audit_log rows (RLS-scoped via the user's JWT).
"""
from __future__ import annotations

from unittest.mock import patch, MagicMock
import pytest

import pebble.server.audit_log_api as audit_api


class _FakeHandler:
    def __init__(self, *, bearer: str = "test-token", path: str = "/api/account/activity"):
        self.path = path
        self.headers = {"Authorization": f"Bearer {bearer}"}
        self.client_address = ("127.0.0.1", 0)
        self.responses: list[tuple[int, dict]] = []

    def _json(self, status: int, body: dict) -> None:
        self.responses.append((status, body))


def test_get_activity_returns_user_rows(monkeypatch):
    """Happy path: returns the user's audit_log rows shaped for the UI."""
    monkeypatch.setattr(audit_api, "require_user",
        lambda h: {"id": "u-1", "email": "test@example.com"})
    fake_rows = [
        {"id": "row-1", "event_type": "password_change", "ip": "1.2.3.4",
         "user_agent": "Mozilla/5.0", "metadata": {}, "created_at": "2026-05-24T10:00:00Z"},
        {"id": "row-2", "event_type": "email_change_confirmed", "ip": "1.2.3.4",
         "user_agent": "Mozilla/5.0", "metadata": {"new_email_redacted": "n***@example.com"},
         "created_at": "2026-05-24T09:00:00Z"},
    ]
    monkeypatch.setattr(audit_api, "_fetch_user_audit_log",
        lambda token, user_id, limit: fake_rows)

    h = _FakeHandler()
    audit_api.run_get_activity(h)
    assert h.responses[-1][0] == 200
    body = h.responses[-1][1]
    assert body["events"] == fake_rows
    assert body["count"] == 2


def test_get_activity_401_when_no_user(monkeypatch):
    """require_user returning None means it already 401'd — handler exits."""
    responded = []
    monkeypatch.setattr(audit_api, "require_user",
        lambda h: responded.append("401") or None)
    h = _FakeHandler()
    audit_api.run_get_activity(h)
    # require_user is responsible for sending 401; our handler just returns
    assert h.responses == []  # we didn't send a second response


def test_get_activity_500_on_supabase_failure(monkeypatch):
    """If the Supabase call raises, return 500 with a friendly error
    (don't leak stack trace)."""
    monkeypatch.setattr(audit_api, "require_user",
        lambda h: {"id": "u-1", "email": "test@example.com"})
    monkeypatch.setattr(audit_api, "_fetch_user_audit_log",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("supabase down")))

    h = _FakeHandler()
    audit_api.run_get_activity(h)
    assert h.responses[-1][0] == 500
    assert "couldn't load" in h.responses[-1][1]["error"].lower() \
        or "could not" in h.responses[-1][1]["error"].lower()


def test_get_activity_respects_limit_param(monkeypatch):
    """?limit=10 → passes 10 to the fetch helper. Max 100."""
    monkeypatch.setattr(audit_api, "require_user",
        lambda h: {"id": "u-1", "email": "test@example.com"})
    captured = {}
    def fake_fetch(token, user_id, limit):
        captured["limit"] = limit
        return []
    monkeypatch.setattr(audit_api, "_fetch_user_audit_log", fake_fetch)

    h = _FakeHandler(path="/api/account/activity?limit=10")
    audit_api.run_get_activity(h)
    assert captured["limit"] == 10

    # Way over the cap → clamped
    h2 = _FakeHandler(path="/api/account/activity?limit=99999")
    audit_api.run_get_activity(h2)
    assert captured["limit"] == 100
