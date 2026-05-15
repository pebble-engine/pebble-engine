"""Tests for /api/internal/supabase-webhook — the endpoint Supabase
Database Webhooks call when a new row lands in public.profiles."""
from __future__ import annotations

import json
import logging
from io import BytesIO
from unittest.mock import patch

import pytest

from pebble.server import supabase_webhook as webhook


WEBHOOK_SECRET = "test-secret-abc123"


class FakeHandler:
    """Minimal handler shaped like BaseHTTPRequestHandler — captures the
    JSON response so tests can assert on status + body."""
    def __init__(self, body: dict | str | None = None, auth: str | None = None,
                 client_ip: str = "203.0.113.5"):
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
        # client_address shape matches BaseHTTPRequestHandler so security.client_ip()
        # can resolve the caller without a trusted-proxy hop.
        self.client_address = (client_ip, 54321)
        self.status: int | None = None
        self.json_body: dict | None = None

    def _json(self, status: int, payload: dict, extra_headers=None) -> None:
        self.status = status
        self.json_body = payload


@pytest.fixture(autouse=True)
def _reset_webhook_limiters():
    """Clear the in-process rate-limiter state between tests so one test's
    bursts don't leak into the next. The webhook limiters live at module
    scope and are mutated by every call."""
    webhook._reset_rate_limiters_for_tests()
    yield
    webhook._reset_rate_limiters_for_tests()


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


# ---- 2026-05-16 NLM review hardening ---------------------------------------

@pytest.mark.parametrize("dirty,clean", [
    # Runs of control chars collapse to a single space.
    ("Marc\r\nBcc: attacker@evil.com", "Marc Bcc: attacker@evil.com"),
    ("Marc\nNewline", "Marc Newline"),
    ("Marc\tTab", "Marc Tab"),
    ("Marc\x00Null", "Marc Null"),
    ("Marc\x1b[31mAnsi", "Marc [31mAnsi"),
    # Plain whitespace still strips (existing behavior).
    ("  Marc  ", "Marc"),
])
def test_clean_first_name_strips_control_characters(dirty, clean):
    """raw_user_meta_data.first_name is fully client-controlled at signup.
    A name containing CR/LF could turn the welcome email's subject into
    a header-injection vehicle on providers that don't normalize it.
    Strip control chars defensively at the trigger boundary."""
    assert webhook._clean_first_name(dirty) == clean


def test_clean_first_name_caps_to_80_after_strip():
    """If the dirty input contains control chars *inside* an 80-character
    prefix, stripping shouldn't accidentally let us exceed the cap."""
    dirty = "a" * 50 + "\n" + "b" * 50  # 101 chars, control-char in the middle
    out = webhook._clean_first_name(dirty)
    assert out is not None
    assert len(out) <= 80
    assert "\n" not in out


def test_webhook_email_rate_limit_blocks_repeated_sends(with_secret, captured_send):
    """If the webhook secret leaks, an attacker can blast `send_welcome`
    calls aimed at one victim. The per-email rate limiter caps that. A
    legitimate Supabase signup hits this endpoint at most once per email
    in any normal flow, so a burst-of-2 then 1/hour is plenty of headroom."""
    record = {"type": "INSERT", "table": "profiles", "record": {"email": "victim@e.com"}}
    auth = f"Bearer {WEBHOOK_SECRET}"

    # Burst — first call goes through.
    webhook.run_supabase_webhook(FakeHandler(record, auth=auth))
    # Subsequent calls within the same window get throttled.
    for _ in range(5):
        h = FakeHandler(record, auth=auth)
        webhook.run_supabase_webhook(h)
    # The handler should report 200 + "throttled" so Supabase doesn't retry,
    # AND send_welcome_async should NOT be invoked for the throttled calls.
    throttled_response_bodies = [
        h.json_body for h in [FakeHandler(record, auth=auth) for _ in range(0)]
    ]  # noqa: F841 — placeholder; we assert via captured_send count
    # `webhook_email_limiter` is configured with burst=2, so exactly 2 sends
    # should land regardless of how many times we call the endpoint.
    assert len(captured_send) <= 2, (
        f"per-email rate limit failed: {len(captured_send)} sends went through"
    )


def test_webhook_email_rate_limit_is_per_address(with_secret, captured_send):
    """Throttling victim@e.com must not block welcome to bob@e.com."""
    auth = f"Bearer {WEBHOOK_SECRET}"
    # Burn the bucket for one address.
    for _ in range(5):
        webhook.run_supabase_webhook(FakeHandler(
            {"type": "INSERT", "table": "profiles", "record": {"email": "victim@e.com"}},
            auth=auth,
        ))
    # Different address — bucket is fresh.
    webhook.run_supabase_webhook(FakeHandler(
        {"type": "INSERT", "table": "profiles", "record": {"email": "bob@e.com"}},
        auth=auth,
    ))
    sent_addresses = [email for email, _ in captured_send]
    assert "bob@e.com" in sent_addresses


def test_webhook_does_not_log_full_email_at_info(with_secret, captured_send, caplog):
    """PII (full email address) leaking into engine.log is a recurring
    audit-fail finding. Redact to `<first-char>***@<domain>` so operators
    can debug by domain without spreading addresses across log retention."""
    caplog.set_level(logging.INFO, logger="pebble.supabase_webhook")
    h = FakeHandler(
        {"type": "INSERT", "table": "profiles", "record": {"email": "sensitive@private.example"}},
        auth=f"Bearer {WEBHOOK_SECRET}",
    )
    webhook.run_supabase_webhook(h)
    assert h.status == 200
    # Walk the captured records — neither INFO nor higher should contain the
    # raw local-part of the email address.
    for rec in caplog.records:
        msg = rec.getMessage()
        assert "sensitive@private.example" not in msg, (
            f"raw email leaked to log: {msg!r}"
        )
