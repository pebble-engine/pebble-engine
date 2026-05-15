"""Tests for the security primitives (rate limiter, trusted-proxy IP,
project ownership check, atomic token consumption, session reverse-index).

These cover the holes NotebookLM flagged in the 2026-05-14 evening
review pass.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import pebble_engine
import pebble.auth as auth_mod
import pebble.security as security_mod


# ---- Rate limiter -------------------------------------------------------

def test_rate_limiter_allows_then_blocks_after_burst():
    rl = security_mod.RateLimiter(rate=0.01, burst=3)
    assert rl.allow("k") is True
    assert rl.allow("k") is True
    assert rl.allow("k") is True
    assert rl.allow("k") is False  # burst exhausted


def test_rate_limiter_refills_over_time():
    rl = security_mod.RateLimiter(rate=10.0, burst=2)  # 10 tokens/sec
    assert rl.allow("k") is True
    assert rl.allow("k") is True
    assert rl.allow("k") is False
    time.sleep(0.25)  # 2.5 tokens refilled
    assert rl.allow("k") is True


def test_rate_limiter_keys_are_isolated():
    rl = security_mod.RateLimiter(rate=0.01, burst=1)
    assert rl.allow("a") is True
    assert rl.allow("a") is False
    assert rl.allow("b") is True   # different key, separate bucket


def test_rate_limiter_empty_key_is_always_allowed():
    rl = security_mod.RateLimiter(rate=0.01, burst=1)
    assert rl.allow("") is True
    assert rl.allow("") is True  # never block unkeyed callers


# ---- Trusted-proxy client IP -------------------------------------------

def _mock_handler(client_ip: str, xff: str | None = None) -> MagicMock:
    h = MagicMock()
    h.client_address = (client_ip, 12345)
    h.headers = MagicMock()
    h.headers.get = lambda name, default=None: xff if name == "X-Forwarded-For" else default
    return h


def test_client_ip_ignores_xff_by_default(monkeypatch):
    monkeypatch.delenv("PEBBLE_TRUSTED_PROXIES", raising=False)
    h = _mock_handler("203.0.113.5", xff="1.2.3.4")
    assert security_mod.client_ip(h) == "203.0.113.5"


def test_client_ip_honors_xff_only_from_trusted_proxy(monkeypatch):
    monkeypatch.setenv("PEBBLE_TRUSTED_PROXIES", "10.0.0.0/8")
    # Proxy in 10/8 — XFF is trusted
    h = _mock_handler("10.0.1.1", xff="1.2.3.4, 10.0.1.1")
    assert security_mod.client_ip(h) == "1.2.3.4"
    # Random caller pretending to be a proxy — XFF ignored
    h2 = _mock_handler("203.0.113.5", xff="1.2.3.4")
    assert security_mod.client_ip(h2) == "203.0.113.5"


def test_client_ip_robust_to_malformed_xff(monkeypatch):
    monkeypatch.setenv("PEBBLE_TRUSTED_PROXIES", "10.0.0.0/8")
    h = _mock_handler("10.0.0.1", xff="garbage,,,, ")
    # First non-empty after split is "garbage" — we don't try to validate
    # it as an IP; just pass it through. The hashed-IP path handles whatever.
    assert security_mod.client_ip(h) == "garbage"


# ---- require_project_owner ----------------------------------------------

# ---- Slug validation (Tier-1 from 2026-05-15 evening NLM pass) ----------

def test_is_valid_slug_accepts_engine_shapes():
    assert security_mod.is_valid_slug("wildflower-bakery")
    assert security_mod.is_valid_slug("test-project")
    assert security_mod.is_valid_slug("a")
    assert security_mod.is_valid_slug("project-with_underscore")
    assert security_mod.is_valid_slug("abc123-def")


def test_is_valid_slug_rejects_path_traversal():
    """Without this gate, a slug like ``../config`` would route through
    OUTPUT_DIR / slug to anywhere on the filesystem the engine can read."""
    for evil in ("..", "../", "../etc", "..\\..", "/etc/passwd", "foo/bar",
                 "foo\\bar", "foo/../bar", ".hidden"):
        assert not security_mod.is_valid_slug(evil), f"should reject {evil!r}"


def test_is_valid_slug_rejects_special_chars():
    for evil in ("foo bar", "foo;bar", "foo$bar", "foo|bar", "foo`bar",
                 "foo\nbar", "foo<bar", "foo>bar", "", "FOO"):
        assert not security_mod.is_valid_slug(evil), f"should reject {evil!r}"


def test_is_valid_slug_rejects_overlong():
    """Cap at 100 chars — engine slugs are always far shorter."""
    assert not security_mod.is_valid_slug("a" * 101)
    assert security_mod.is_valid_slug("a" * 100)


def test_validate_slug_emits_400_on_failure(tmp_path, monkeypatch):
    """The HTTP wrapper writes a 400 to the handler when the slug fails."""
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    handler = MagicMock()
    captured = {}
    def fake_json(status, body):
        captured["status"] = status
        captured["body"] = body
    handler._json = fake_json
    assert security_mod.validate_slug(handler, "../etc") is False
    assert captured["status"] == 400
    assert "invalid" in captured["body"]["error"].lower()


def test_require_project_owner_rejects_traversal_slug(tmp_path, monkeypatch):
    """Critical defense — without this, ``../`` segments resolve through
    OUTPUT_DIR / slug to a sibling directory the user can probe."""
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    handler = MagicMock()
    captured = {}
    handler._json = lambda s, b: captured.update({"status": s, "body": b})
    handler.client_address = ("127.0.0.1", 12345)
    handler.headers = MagicMock()
    handler.headers.get = lambda *a, **k: None
    handler.headers.__contains__ = lambda *a: False
    # Returns None (callers bail) and emits a 400 — never reaches .exists().
    assert security_mod.require_project_owner(handler, "../config") is None
    assert captured["status"] == 400


# ---- Per-slug write lock ------------------------------------------------

def test_project_lock_serializes_concurrent_acquires():
    """First acquirer takes the lock; second times out fast."""
    with security_mod.project_lock("slug-x", timeout=0.05) as got1:
        assert got1 is True
        with security_mod.project_lock("slug-x", timeout=0.05) as got2:
            assert got2 is False


def test_project_lock_distinct_slugs_are_independent():
    """Acquiring one slug's lock doesn't block another."""
    with security_mod.project_lock("slug-a", timeout=0.05) as got_a:
        assert got_a is True
        with security_mod.project_lock("slug-b", timeout=0.05) as got_b:
            assert got_b is True


def test_project_lock_releases_after_with_block():
    """Once a with-block exits, the lock must be free again."""
    with security_mod.project_lock("slug-r", timeout=0.05) as got1:
        assert got1 is True
    with security_mod.project_lock("slug-r", timeout=0.05) as got2:
        assert got2 is True


def test_require_project_owner_404_for_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    handler = MagicMock()
    handler._json = MagicMock()
    result = security_mod.require_project_owner(handler, "ghost")
    assert result is None
    handler._json.assert_called_with(404, {"error": "project not found: ghost"})


def test_require_project_owner_401_when_not_signed_in(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    (tmp_path / "good-co").mkdir()
    handler = MagicMock()
    handler._json = MagicMock()
    handler.headers = MagicMock()
    handler.headers.get = lambda *_args, **_kw: None
    result = security_mod.require_project_owner(handler, "good-co")
    assert result is None
    args, _ = handler._json.call_args
    assert args[0] == 401


def test_require_project_owner_403_when_owned_by_someone_else(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    project = tmp_path / "good-co"
    project.mkdir()
    (project / "brief.json").write_text(json.dumps({"_user_id": "owner-uuid"}))
    # Mock auth to return a different user id
    handler = MagicMock()
    handler._json = MagicMock()
    handler.headers = MagicMock()
    handler.headers.get = lambda *_args, **_kw: "pebble_session=fake"
    monkeypatch.setattr("pebble.server.auth.current_user_id", lambda h: "intruder-uuid")
    result = security_mod.require_project_owner(handler, "good-co")
    assert result is None
    args, _ = handler._json.call_args
    assert args[0] == 403


def test_require_project_owner_allows_when_unclaimed(tmp_path, monkeypatch):
    """Unclaimed (legacy) projects with no _user_id are accessible to any
    signed-in user — consistent with run_list_projects."""
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    project = tmp_path / "good-co"
    project.mkdir()
    (project / "brief.json").write_text(json.dumps({"business_name": "Good Co"}))
    handler = MagicMock()
    handler._json = MagicMock()
    handler.headers = MagicMock()
    handler.headers.get = lambda *_args, **_kw: "pebble_session=fake"
    monkeypatch.setattr("pebble.server.auth.current_user_id", lambda h: "any-user")
    result = security_mod.require_project_owner(handler, "good-co")
    assert result == "any-user"


# ---- Atomic password reset token consumption ----------------------------

def test_consume_token_only_succeeds_once(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    tok = auth_mod.create_password_reset_token("user-1")

    a = auth_mod.consume_password_reset_token(tok.token)
    b = auth_mod.consume_password_reset_token(tok.token)
    assert a is not None and a.user_id == "user-1"
    assert b is None  # second call sees nothing


def test_consume_token_under_concurrency_at_most_one_winner(tmp_path, monkeypatch):
    """Race-stress: many threads attempt to consume the same token.
    Exactly one should win, all others get None."""
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    tok = auth_mod.create_password_reset_token("user-1")

    results: list = []
    barrier = threading.Barrier(8)

    def attempt():
        barrier.wait()
        results.append(auth_mod.consume_password_reset_token(tok.token))

    threads = [threading.Thread(target=attempt) for _ in range(8)]
    for t in threads: t.start()
    for t in threads: t.join()

    winners = [r for r in results if r is not None]
    assert len(winners) == 1, f"expected exactly 1 winner, got {len(winners)}"


def test_consume_token_returns_none_when_expired(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    tok = auth_mod.create_password_reset_token("user-1")
    # Manually expire on disk
    p = tmp_path / ".password_resets" / f"{tok.token}.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["expires_at"] = "2000-01-01T00:00:00+00:00"
    p.write_text(json.dumps(data), encoding="utf-8")
    assert auth_mod.consume_password_reset_token(tok.token) is None


# ---- O(1) session revocation via reverse index --------------------------

def test_revoke_all_uses_index_not_directory_walk(tmp_path, monkeypatch):
    """Verify the index path is populated by create_session and consumed
    by revoke_all_sessions_for."""
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    user = auth_mod.create_user("u@example.com", "valid-password")

    s1 = auth_mod.create_session(user.id)
    s2 = auth_mod.create_session(user.id)

    # The reverse index has both
    index = auth_mod._load_sessions_index()
    assert sorted(index[user.id]) == sorted([s1.token, s2.token])

    other = auth_mod.create_user("other@example.com", "valid-password")
    s3 = auth_mod.create_session(other.id)

    revoked = auth_mod.revoke_all_sessions_for(user.id)
    assert revoked == 2

    # Other user's session untouched
    assert auth_mod.get_session(s3.token) is not None
    assert auth_mod.get_session(s1.token) is None
    assert auth_mod.get_session(s2.token) is None


def test_revoke_session_keeps_index_consistent(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    user = auth_mod.create_user("u@example.com", "valid-password")
    s1 = auth_mod.create_session(user.id)
    s2 = auth_mod.create_session(user.id)
    auth_mod.revoke_session(s1.token)
    index = auth_mod._load_sessions_index()
    assert index[user.id] == [s2.token]


def test_revoke_all_falls_back_when_index_missing(tmp_path, monkeypatch):
    """If the index file doesn't exist (legacy sessions), we still find
    and revoke every matching session by walking the directory."""
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    user = auth_mod.create_user("u@example.com", "valid-password")
    s = auth_mod.create_session(user.id)
    # Wipe the index, simulating legacy state
    auth_mod._sessions_index_path().unlink()
    revoked = auth_mod.revoke_all_sessions_for(user.id)
    assert revoked == 1
    assert auth_mod.get_session(s.token) is None
