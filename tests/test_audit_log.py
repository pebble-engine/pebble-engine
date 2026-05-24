"""Tests for pebble.audit_log — the security-event logger.

The helper is fire-and-forget: it must never raise (an audit-log outage
cannot be allowed to break the calling endpoint, which would be worse
than a missed log entry).
"""
from __future__ import annotations

from unittest.mock import patch, MagicMock
import pytest

from pebble import audit_log


def test_log_event_calls_supabase_with_correct_shape():
    """The helper should call into _supabase_insert with the expected row shape."""
    with patch("pebble.audit_log._supabase_insert") as mock_insert:
        audit_log.log_event(
            user_id="u-123",
            event_type="password_change",
            ip="203.0.113.4",
            user_agent="Mozilla/5.0",
            metadata={"trigger": "settings_page"},
        )
        mock_insert.assert_called_once()
        row = mock_insert.call_args[0][0]
        assert row["user_id"]     == "u-123"
        assert row["event_type"]  == "password_change"
        assert row["ip"]          == "203.0.113.4"
        assert row["user_agent"]  == "Mozilla/5.0"
        assert row["metadata"]    == {"trigger": "settings_page"}


def test_log_event_swallows_errors():
    """If the Supabase insert raises, the helper must NOT re-raise.
    A logging failure cannot break the calling endpoint."""
    with patch("pebble.audit_log._supabase_insert", side_effect=RuntimeError("supabase down")):
        # Should not raise.
        audit_log.log_event(user_id="u-1", event_type="x", ip=None, user_agent=None, metadata={})


def test_log_event_for_handler_extracts_ip_from_xff():
    """The handler-aware wrapper should pull IP from X-Forwarded-For and UA from User-Agent."""
    fake_handler = MagicMock()
    fake_handler.headers = {"User-Agent": "TestBot/1.0", "X-Forwarded-For": "203.0.113.7, 10.0.0.1"}
    fake_handler.client_address = ("127.0.0.1", 12345)
    with patch("pebble.audit_log._supabase_insert") as mock_insert:
        audit_log.log_event_for_handler(
            handler=fake_handler,
            user_id="u-1",
            event_type="email_change",
            metadata={"new_email": "redacted"},
        )
        row = mock_insert.call_args[0][0]
        # XFF takes precedence over client_address; first IP in the chain wins.
        assert row["ip"]         == "203.0.113.7"
        assert row["user_agent"] == "TestBot/1.0"


def test_log_event_for_handler_falls_back_to_client_address():
    """When there's no X-Forwarded-For header, use the handler's client_address."""
    fake_handler = MagicMock()
    fake_handler.headers = {"User-Agent": "DirectClient/2.0"}  # no XFF
    fake_handler.client_address = ("198.51.100.5", 54321)
    with patch("pebble.audit_log._supabase_insert") as mock_insert:
        audit_log.log_event_for_handler(
            handler=fake_handler,
            user_id="u-2",
            event_type="account_delete_requested",
            metadata={},
        )
        row = mock_insert.call_args[0][0]
        assert row["ip"] == "198.51.100.5"


def test_log_event_truncates_long_user_agent():
    """Some bots send absurdly long UAs; cap at 512 chars to bound DB writes."""
    with patch("pebble.audit_log._supabase_insert") as mock_insert:
        audit_log.log_event(
            user_id="u-1",
            event_type="x",
            ip=None,
            user_agent="x" * 1000,
            metadata={},
        )
        row = mock_insert.call_args[0][0]
        assert len(row["user_agent"]) == 512
