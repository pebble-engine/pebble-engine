"""Tests for pebble.email_drip — post-first-build drip sequence (Ch 11.6)."""
from __future__ import annotations

import datetime as _dt
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from pebble.email_drip import _render, process_due, schedule_drip


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_drip_file(tmp_path: Path, uid: str, *, day_offsets: tuple = (-2, -1, 6)) -> Path:
    """Create a realistic email_drip.json with send_at offsets relative to now.
    Negative = already due; positive = future.
    """
    user_dir = tmp_path / ".users" / uid
    user_dir.mkdir(parents=True, exist_ok=True)
    now = _dt.datetime.now(_dt.timezone.utc)
    drip_file = user_dir / "email_drip.json"
    drip_file.write_text(json.dumps({
        "email": f"{uid}@example.com",
        "first_name": "Alice",
        "slug": "alice-plumbing",
        "scheduled_at": (now - _dt.timedelta(days=8)).isoformat(),
        "scheduled": [
            {
                "day": 1,
                "type": "tips_next",
                "send_at": (now + _dt.timedelta(days=day_offsets[0])).isoformat(),
                "sent_at": None,
            },
            {
                "day": 3,
                "type": "tips_refine",
                "send_at": (now + _dt.timedelta(days=day_offsets[1])).isoformat(),
                "sent_at": None,
            },
            {
                "day": 7,
                "type": "tips_live",
                "send_at": (now + _dt.timedelta(days=day_offsets[2])).isoformat(),
                "sent_at": None,
            },
        ],
    }), encoding="utf-8")
    return drip_file


# ---------------------------------------------------------------------------
# schedule_drip
# ---------------------------------------------------------------------------

class TestScheduleDrip:
    def test_creates_file_with_three_entries(self, tmp_path):
        result = schedule_drip(
            "abc123", "alice@example.com", first_name="Alice",
            slug="alice-plumbing", output_dir=tmp_path,
        )
        assert result is True
        drip = tmp_path / ".users" / "abc123" / "email_drip.json"
        assert drip.exists()
        data = json.loads(drip.read_text())
        assert data["email"] == "alice@example.com"
        assert data["first_name"] == "Alice"
        assert data["slug"] == "alice-plumbing"
        assert len(data["scheduled"]) == 3
        types = [s["type"] for s in data["scheduled"]]
        assert types == ["tips_next", "tips_refine", "tips_live"]

    def test_idempotent_returns_false_on_second_call(self, tmp_path):
        schedule_drip("abc123", "alice@example.com", output_dir=tmp_path)
        result = schedule_drip("abc123", "alice@example.com", output_dir=tmp_path)
        assert result is False

    def test_idempotent_does_not_overwrite_existing(self, tmp_path):
        schedule_drip("abc123", "alice@example.com", slug="first-build", output_dir=tmp_path)
        schedule_drip("abc123", "bob@example.com", slug="second-build", output_dir=tmp_path)
        data = json.loads(
            (tmp_path / ".users" / "abc123" / "email_drip.json").read_text()
        )
        assert data["email"] == "alice@example.com"
        assert data["slug"] == "first-build"

    def test_rejects_missing_email(self, tmp_path):
        assert schedule_drip("abc123", "", output_dir=tmp_path) is False

    def test_rejects_email_without_at(self, tmp_path):
        assert schedule_drip("abc123", "notanemail", output_dir=tmp_path) is False

    def test_rejects_empty_user_id(self, tmp_path):
        assert schedule_drip("", "alice@example.com", output_dir=tmp_path) is False

    def test_send_at_offsets_use_env_override(self, tmp_path, monkeypatch):
        monkeypatch.setenv("PEBBLE_DRIP_DAYS_1", "0")
        monkeypatch.setenv("PEBBLE_DRIP_DAYS_3", "1")
        monkeypatch.setenv("PEBBLE_DRIP_DAYS_7", "2")
        schedule_drip("u1", "u@example.com", output_dir=tmp_path)
        data = json.loads((tmp_path / ".users" / "u1" / "email_drip.json").read_text())
        days = [s["day"] for s in data["scheduled"]]
        assert days == [0, 1, 2]

    def test_creates_user_dir_if_missing(self, tmp_path):
        assert not (tmp_path / ".users" / "newuid").exists()
        schedule_drip("newuid", "x@x.com", output_dir=tmp_path)
        assert (tmp_path / ".users" / "newuid" / "email_drip.json").exists()


# ---------------------------------------------------------------------------
# process_due
# ---------------------------------------------------------------------------

class TestProcessDue:
    def _send_ok(self, message):
        return {"ok": True, "provider": "log", "id": "test-id"}

    def test_sends_two_due_emails_skips_future(self, tmp_path):
        _make_drip_file(tmp_path, "u1", day_offsets=(-2, -1, 6))

        with patch("pebble.email_drip.send", side_effect=self._send_ok) as mock_send:
            result = process_due(tmp_path)

        assert result["sent"] == 2
        assert result["skipped"] == 1
        assert result["errors"] == []
        assert mock_send.call_count == 2

    def test_marks_sent_at_in_file(self, tmp_path):
        _make_drip_file(tmp_path, "u2", day_offsets=(-1, -1, -1))

        with patch("pebble.email_drip.send", side_effect=self._send_ok):
            process_due(tmp_path)

        data = json.loads(
            (tmp_path / ".users" / "u2" / "email_drip.json").read_text()
        )
        for item in data["scheduled"]:
            assert item["sent_at"] is not None

    def test_skips_already_sent(self, tmp_path):
        now = _dt.datetime.now(_dt.timezone.utc)
        user_dir = tmp_path / ".users" / "u3"
        user_dir.mkdir(parents=True, exist_ok=True)
        (user_dir / "email_drip.json").write_text(json.dumps({
            "email": "u3@example.com",
            "first_name": "",
            "slug": "",
            "scheduled_at": now.isoformat(),
            "scheduled": [
                {
                    "day": 1,
                    "type": "tips_next",
                    "send_at": (now - _dt.timedelta(hours=1)).isoformat(),
                    "sent_at": now.isoformat(),  # already sent
                },
            ],
        }), encoding="utf-8")

        with patch("pebble.email_drip.send", side_effect=self._send_ok) as mock_send:
            result = process_due(tmp_path)

        assert result["skipped"] == 1
        assert result["sent"] == 0
        assert mock_send.call_count == 0

    def test_skips_future_emails(self, tmp_path):
        _make_drip_file(tmp_path, "u4", day_offsets=(1, 3, 7))

        with patch("pebble.email_drip.send", side_effect=self._send_ok) as mock_send:
            result = process_due(tmp_path)

        assert result["sent"] == 0
        assert result["skipped"] == 3
        assert mock_send.call_count == 0

    def test_handles_missing_users_dir(self, tmp_path):
        result = process_due(tmp_path)
        assert result == {"sent": 0, "skipped": 0, "errors": []}

    def test_records_error_on_malformed_json(self, tmp_path):
        user_dir = tmp_path / ".users" / "bad"
        user_dir.mkdir(parents=True, exist_ok=True)
        (user_dir / "email_drip.json").write_text("{not valid json}", encoding="utf-8")

        result = process_due(tmp_path)
        assert result["errors"]
        assert "bad" in result["errors"][0]

    def test_skips_user_without_email(self, tmp_path):
        now = _dt.datetime.now(_dt.timezone.utc)
        user_dir = tmp_path / ".users" / "noemail"
        user_dir.mkdir(parents=True, exist_ok=True)
        (user_dir / "email_drip.json").write_text(json.dumps({
            "email": "",
            "slug": "",
            "scheduled_at": now.isoformat(),
            "scheduled": [
                {"day": 1, "type": "tips_next",
                 "send_at": (now - _dt.timedelta(hours=1)).isoformat(), "sent_at": None},
            ],
        }), encoding="utf-8")

        with patch("pebble.email_drip.send", side_effect=self._send_ok) as mock_send:
            result = process_due(tmp_path)

        assert mock_send.call_count == 0

    def test_handles_send_failure_gracefully(self, tmp_path):
        _make_drip_file(tmp_path, "u5", day_offsets=(-1, -1, -1))

        def _fail(message):
            return {"ok": False, "provider": "log", "id": "", "error": "smtp error"}

        with patch("pebble.email_drip.send", side_effect=_fail):
            result = process_due(tmp_path)

        assert result["sent"] == 0
        assert len(result["errors"]) == 3

    def test_processes_multiple_users(self, tmp_path):
        _make_drip_file(tmp_path, "ua", day_offsets=(-1, 5, 6))
        _make_drip_file(tmp_path, "ub", day_offsets=(-1, -1, 5))

        with patch("pebble.email_drip.send", side_effect=self._send_ok):
            result = process_due(tmp_path)

        assert result["sent"] == 3  # 1 from ua + 2 from ub


# ---------------------------------------------------------------------------
# _render — smoke tests for each email type
# ---------------------------------------------------------------------------

class TestRender:
    def test_tips_next_fields(self):
        msg = _render("tips_next", "x@x.com", "Bob", "bob-plumbing")
        assert msg.to == "x@x.com"
        assert "ready" in msg.subject.lower()
        assert "Bob" in msg.text
        assert "bob-plumbing" in msg.text
        assert "<html" in (msg.html or "")

    def test_tips_refine_fields(self):
        msg = _render("tips_refine", "x@x.com", None, "")
        assert "there" in msg.text  # fallback name
        assert "quick wins" in msg.subject.lower()

    def test_tips_live_fields(self):
        msg = _render("tips_live", "x@x.com", "Carol", "carol-bakery")
        assert "live" in msg.subject.lower()
        assert "Carol" in msg.text

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="unknown drip email type"):
            _render("bogus_type", "x@x.com", None, "")

    def test_html_contains_cta_link(self):
        msg = _render("tips_live", "x@x.com", None, "my-slug")
        assert "my-slug" in (msg.html or "")
        assert "Publish" in (msg.html or "")
