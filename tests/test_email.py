"""Tests for the transactional email module + password reset flow.

We exercise FileSender directly (always available, no network) and mock
Resend/Postmark/SendGrid via urllib monkeypatching so the production
senders are exercised without hitting the live APIs.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

import pebble_engine
import pebble.auth as auth_mod
import pebble.email as email_mod


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Remove any developer env that would change behavior."""
    for k in (
        "PEBBLE_EMAIL_PROVIDER", "PEBBLE_EMAIL_RESEND_KEY", "RESEND_API_KEY",
        "PEBBLE_EMAIL_POSTMARK_TOKEN", "PEBBLE_EMAIL_SENDGRID_KEY",
        "PEBBLE_EMAIL_FROM", "PEBBLE_PUBLIC_URL",
    ):
        monkeypatch.delenv(k, raising=False)


# ---- EmailMessage validation -------------------------------------------

def test_message_requires_valid_recipient():
    with pytest.raises(email_mod.EmailError):
        email_mod.EmailMessage(to="not-an-email", subject="x", text="y")


def test_message_requires_subject_and_text():
    with pytest.raises(email_mod.EmailError):
        email_mod.EmailMessage(to="a@b.co", subject="", text="y")
    with pytest.raises(email_mod.EmailError):
        email_mod.EmailMessage(to="a@b.co", subject="x", text="")


def test_message_defaults_from_addr():
    m = email_mod.EmailMessage(to="a@b.co", subject="x", text="y")
    assert "@" in (m.from_addr or "")


# ---- FileSender (dev) ---------------------------------------------------

def test_file_sender_writes_eml(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    sender = email_mod.FileSender()
    res = sender.send(email_mod.EmailMessage(
        to="alice@example.com", subject="Hi there", text="Body", html="<p>Body</p>",
    ))
    assert res["ok"] is True
    assert res["provider"] == "log"
    outbox = tmp_path / ".email_outbox"
    files = list(outbox.glob("*.eml"))
    assert len(files) == 1
    contents = files[0].read_text(encoding="utf-8", errors="replace")
    assert "Subject: Hi there" in contents
    assert "To: alice@example.com" in contents
    assert "Body" in contents


def test_get_sender_defaults_to_file_when_provider_unset():
    s = email_mod.get_sender()
    assert isinstance(s, email_mod.FileSender)


def test_get_sender_resolves_resend(monkeypatch):
    monkeypatch.setenv("PEBBLE_EMAIL_PROVIDER", "resend")
    assert isinstance(email_mod.get_sender(), email_mod.ResendSender)


def test_get_sender_unknown_falls_back_to_log(monkeypatch):
    monkeypatch.setenv("PEBBLE_EMAIL_PROVIDER", "carrier-pigeon")
    assert isinstance(email_mod.get_sender(), email_mod.FileSender)


# ---- ResendSender / PostmarkSender / SendgridSender mocks --------------

def _mock_urlopen(payload: dict, status: int = 200, headers: dict | None = None):
    resp = MagicMock()
    resp.__enter__.return_value = resp
    resp.__exit__.return_value = False
    resp.read.return_value = json.dumps(payload).encode("utf-8")
    resp.status = status
    if headers:
        resp.headers = MagicMock()
        resp.headers.get.side_effect = lambda k, d="": headers.get(k, d)
    return resp


def test_resend_sender_posts_to_api(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    monkeypatch.setenv("PEBBLE_EMAIL_RESEND_KEY", "re_TEST")
    captured: dict = {}
    def fake_urlopen(req, timeout=15):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.headers)
        captured["data"] = json.loads(req.data.decode("utf-8"))
        return _mock_urlopen({"id": "msg-123"})
    monkeypatch.setattr(email_mod.urllib.request, "urlopen", fake_urlopen)
    res = email_mod.ResendSender().send(email_mod.EmailMessage(
        to="alice@example.com", subject="Hi", text="Hello", html="<p>Hello</p>"
    ))
    assert res["ok"] is True
    assert res["id"] == "msg-123"
    assert "api.resend.com" in captured["url"]
    assert captured["headers"]["Authorization"] == "Bearer re_TEST"
    assert captured["data"]["to"] == ["alice@example.com"]
    assert captured["data"]["html"] == "<p>Hello</p>"


def test_resend_sender_raises_when_key_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    monkeypatch.delenv("PEBBLE_EMAIL_RESEND_KEY", raising=False)
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    with pytest.raises(email_mod.EmailError):
        email_mod.ResendSender().send(email_mod.EmailMessage(
            to="a@b.co", subject="x", text="y"
        ))


def test_postmark_sender_posts_to_api(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    monkeypatch.setenv("PEBBLE_EMAIL_POSTMARK_TOKEN", "pm-TOK")
    captured: dict = {}
    def fake_urlopen(req, timeout=15):
        captured["headers"] = dict(req.headers)
        captured["data"] = json.loads(req.data.decode("utf-8"))
        return _mock_urlopen({"MessageID": "pm-msg-1"})
    monkeypatch.setattr(email_mod.urllib.request, "urlopen", fake_urlopen)
    res = email_mod.PostmarkSender().send(email_mod.EmailMessage(
        to="bob@example.com", subject="Y", text="Body"
    ))
    assert res["ok"] is True
    assert res["id"] == "pm-msg-1"
    assert captured["headers"]["X-postmark-server-token"] == "pm-TOK"
    assert captured["data"]["To"] == "bob@example.com"


def test_sendgrid_sender_posts_to_api(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    monkeypatch.setenv("PEBBLE_EMAIL_SENDGRID_KEY", "sg-K")
    def fake_urlopen(req, timeout=15):
        return _mock_urlopen({}, status=202, headers={"X-Message-Id": "sg-1"})
    monkeypatch.setattr(email_mod.urllib.request, "urlopen", fake_urlopen)
    res = email_mod.SendgridSender().send(email_mod.EmailMessage(
        to="c@example.com", subject="Z", text="Body"
    ))
    assert res["ok"] is True
    assert res["id"] == "sg-1"


# ---- top-level send() catches sender errors ----------------------------

def test_send_catches_email_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    class Broken:
        name = "broken"
        def send(self, m): raise email_mod.EmailError("simulated")
    res = email_mod.send(
        email_mod.EmailMessage(to="x@y.co", subject="s", text="t"),
        sender=Broken(),
    )
    assert res["ok"] is False
    assert "simulated" in res["error"]


def test_send_writes_audit_copy_when_using_external_sender(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    class Ok:
        name = "external"
        def send(self, m): return {"ok": True, "provider": self.name, "id": "x"}
    email_mod.send(
        email_mod.EmailMessage(to="audit@x.co", subject="s", text="t"),
        sender=Ok(),
    )
    outbox = tmp_path / ".email_outbox"
    assert len(list(outbox.glob("*.eml"))) >= 1


# ---- Pebble-specific templates -----------------------------------------

def test_welcome_message_includes_email_and_link():
    msg = email_mod.render_welcome("user@example.com")
    assert "Welcome" in msg.subject
    assert "user@example.com" in msg.text
    assert msg.html and "user@example.com" in msg.html


def test_password_reset_message_contains_link():
    msg = email_mod.render_password_reset("user@example.com", "https://pebble.example/reset?token=xyz")
    assert "Reset" in msg.subject or "reset" in msg.subject.lower()
    assert "https://pebble.example/reset?token=xyz" in msg.text
    assert msg.html and "https://pebble.example/reset?token=xyz" in msg.html


def test_send_welcome_writes_to_outbox(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    res = email_mod.send_welcome("user@example.com")
    assert res["ok"] is True
    eml_files = list((tmp_path / ".email_outbox").glob("*.eml"))
    assert len(eml_files) == 1


# ---- pebble.auth password reset tokens ---------------------------------

def test_password_reset_token_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    tok = auth_mod.create_password_reset_token("user-123")
    fetched = auth_mod.get_password_reset_token(tok.token)
    assert fetched is not None
    assert fetched.user_id == "user-123"


def test_password_reset_token_expired_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    tok = auth_mod.create_password_reset_token("user-123")
    # Manually expire by rewriting the file
    path = tmp_path / ".password_resets" / f"{tok.token}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["expires_at"] = "2000-01-01T00:00:00+00:00"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert auth_mod.get_password_reset_token(tok.token) is None
    # Read-on-expiry should have deleted the file
    assert not path.exists()


def test_consume_password_reset_token_deletes(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    tok = auth_mod.create_password_reset_token("user-123")
    used = auth_mod.consume_password_reset_token(tok.token)
    assert used is not None
    # Token is gone — replays are blocked
    assert auth_mod.consume_password_reset_token(tok.token) is None


def test_update_user_password_rehashes(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    user = auth_mod.create_user("user@example.com", "old-password-123")
    updated = auth_mod.update_user_password(user.id, "new-password-456")
    assert updated is not None
    assert auth_mod.authenticate("user@example.com", "old-password-123") is None
    assert auth_mod.authenticate("user@example.com", "new-password-456") is not None


def test_revoke_all_sessions_for_user(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    user = auth_mod.create_user("user@example.com", "password-aaa")
    s1 = auth_mod.create_session(user.id)
    s2 = auth_mod.create_session(user.id)
    other = auth_mod.create_user("other@example.com", "password-bbb")
    s3 = auth_mod.create_session(other.id)

    count = auth_mod.revoke_all_sessions_for(user.id)
    assert count == 2
    assert auth_mod.get_session(s1.token) is None
    assert auth_mod.get_session(s2.token) is None
    assert auth_mod.get_session(s3.token) is not None
