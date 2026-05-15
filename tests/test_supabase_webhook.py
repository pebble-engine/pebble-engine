"""Tests for /api/internal/supabase-webhook — the endpoint Supabase
Database Webhooks call when a new row lands in public.profiles."""
from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import patch

import pytest

from pebble.server import supabase_webhook as webhook


WEBHOOK_SECRET = "test-secret-abc123"


class FakeHandler:
    """Minimal handler shaped like BaseHTTPRequestHandler — captures the
    JSON response so tests can assert on status + body."""
    def __init__(self, body: dict | str | None = None, auth: str | None = None):
        if isinstance(body, dict):
            raw = json.dumps(body).encode("utf-8")
        elif isinstance(body, str):
            raw = body.encode("utf-8")
        else:
            raw = b""
        self.rfile = BytesIO(raw)
        self.headers = {"Content-Length": str(len(raw))}
        if auth:
            self.headers["Authorization"] = auth
        self.status: int | None = None
        self.json_body: dict | None = None

    def _json(self, status: int, payload: dict, extra_headers=None) -> None:
        self.status = status
        self.json_body = payload


@pytest.fixture
def with_secret(monkeypatch):
    monkeypatch.setenv("PEBBLE_SUPABASE_WEBHOOK_SECRET", WEBHOOK_SECRET)


@pytest.fixture
def captured_send():
    """Patch send_welcome_async so we can assert on calls without actually
    queueing real emails."""
    calls: list[tuple] = []

    def fake(email, first_name=None, sender=None):  # noqa: ARG001
        calls.append((email, first_name))
        return None

    with patch.object(webhook, "send_welcome_async", side_effect=fake):
        yield calls


# ---- Auth / config gates ---------------------------------------------------

def test_webhook_returns_503_when_secret_not_configured(monkeypatch):
    monkeypatch.delenv("PEBBLE_SUPABASE_WEBHOOK_SECRET", raising=False)
    h = FakeHandler({"type": "INSERT", "table": "profiles"}, auth=f"Bearer {WEBHOOK_SECRET}")
    webhook.run_supabase_webhook(h)
    assert h.status == 503


def test_webhook_returns_401_without_auth_header(with_secret):
    h = FakeHandler({"type": "INSERT", "table": "profiles"})
    webhook.run_supabase_webhook(h)
    assert h.status == 401


def test_webhook_returns_401_with_wrong_secret(with_secret):
    h = FakeHandler({"type": "INSERT", "table": "profiles"}, auth="Bearer wrong-value")
    webhook.run_supabase_webhook(h)
    assert h.status == 401


def test_webhook_returns_401_when_bearer_prefix_missing(with_secret):
    """Just the secret without 'Bearer ' must fail — the format matters."""
    h = FakeHandler({"type": "INSERT", "table": "profiles"}, auth=WEBHOOK_SECRET)
    webhook.run_supabase_webhook(h)
    assert h.status == 401


# ---- Body parsing ----------------------------------------------------------

def test_webhook_returns_400_on_invalid_json(with_secret):
    h = FakeHandler("not-json{", auth=f"Bearer {WEBHOOK_SECRET}")
    webhook.run_supabase_webhook(h)
    assert h.status == 400


def test_webhook_returns_400_on_huge_body(with_secret):
    """100 KB body — far over the sanity ceiling for a Supabase webhook
    payload. The handler should refuse rather than allocate."""
    huge = json.dumps({"type": "INSERT", "table": "profiles", "junk": "x" * 100_000})
    h = FakeHandler(huge, auth=f"Bearer {WEBHOOK_SECRET}")
    webhook.run_supabase_webhook(h)
    assert h.status == 400


# ---- Event filtering -------------------------------------------------------

def test_webhook_ignores_update_events(with_secret, captured_send):
    h = FakeHandler(
        {"type": "UPDATE", "table": "profiles", "record": {"email": "u@e.com"}},
        auth=f"Bearer {WEBHOOK_SECRET}",
    )
    webhook.run_supabase_webhook(h)
    assert h.status == 200
    assert h.json_body["action"] == "ignored"
    assert captured_send == []


def test_webhook_ignores_delete_events(with_secret, captured_send):
    h = FakeHandler(
        {"type": "DELETE", "table": "profiles", "old_record": {"email": "u@e.com"}},
        auth=f"Bearer {WEBHOOK_SECRET}",
    )
    webhook.run_supabase_webhook(h)
    assert h.status == 200
    assert captured_send == []


def test_webhook_ignores_inserts_on_other_tables(with_secret, captured_send):
    h = FakeHandler(
        {"type": "INSERT", "table": "projects", "record": {"email": "u@e.com"}},
        auth=f"Bearer {WEBHOOK_SECRET}",
    )
    webhook.run_supabase_webhook(h)
    assert h.status == 200
    assert h.json_body["action"] == "ignored"
    assert captured_send == []


def test_webhook_skips_when_record_has_no_email(with_secret, captured_send):
    h = FakeHandler(
        {"type": "INSERT", "table": "profiles", "record": {"id": "abc"}},
        auth=f"Bearer {WEBHOOK_SECRET}",
    )
    webhook.run_supabase_webhook(h)
    assert h.status == 200
    assert h.json_body["action"] == "skipped"
    assert captured_send == []


# ---- Happy path ------------------------------------------------------------

def test_webhook_triggers_welcome_email_on_profile_insert(with_secret, captured_send):
    h = FakeHandler(
        {
            "type": "INSERT",
            "table": "profiles",
            "schema": "public",
            "record": {
                "id": "abc-123",
                "email": "marc@example.com",
                "first_name": "Marc",
                "plan_tier": "free",
            },
        },
        auth=f"Bearer {WEBHOOK_SECRET}",
    )
    webhook.run_supabase_webhook(h)
    assert h.status == 200
    assert h.json_body["action"] == "welcome_sent"
    assert h.json_body["email"] == "marc@example.com"
    assert captured_send == [("marc@example.com", "Marc")]


def test_webhook_passes_none_first_name_when_missing(with_secret, captured_send):
    h = FakeHandler(
        {
            "type": "INSERT",
            "table": "profiles",
            "record": {"email": "u@e.com"},
        },
        auth=f"Bearer {WEBHOOK_SECRET}",
    )
    webhook.run_supabase_webhook(h)
    assert h.status == 200
    assert captured_send == [("u@e.com", None)]


def test_webhook_trims_and_caps_first_name(with_secret, captured_send):
    long_name = "  " + "a" * 200 + "  "
    h = FakeHandler(
        {
            "type": "INSERT",
            "table": "profiles",
            "record": {"email": "u@e.com", "first_name": long_name},
        },
        auth=f"Bearer {WEBHOOK_SECRET}",
    )
    webhook.run_supabase_webhook(h)
    assert h.status == 200
    sent_email, sent_name = captured_send[0]
    assert sent_email == "u@e.com"
    assert sent_name is not None
    assert len(sent_name) == 80   # capped
    assert sent_name == "a" * 80  # trimmed
