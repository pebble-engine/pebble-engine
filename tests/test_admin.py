"""Tests for the admin support tools (read-only).

Auth model:
- PEBBLE_ADMIN_EMAIL unset → 503 (admin disabled)
- Not signed in → 401
- Signed in as non-admin → 403
- Signed in as admin → 200 + payload
"""
from __future__ import annotations

import json
import socket
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import pebble_engine
import pebble.history as history_mod


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def engine_server(tmp_path, monkeypatch):
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.setattr(history_mod, "OUTPUT_DIR", out)
    # Tests start with admin disabled — opt in per-case via monkeypatch.setenv
    monkeypatch.delenv("PEBBLE_ADMIN_EMAIL", raising=False)

    port = _find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), pebble_engine.PebbleHandler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    time.sleep(0.1)
    try:
        yield {
            "base":   f"http://127.0.0.1:{port}",
            "output": out,
            "monkey": monkeypatch,
        }
    finally:
        server.shutdown()
        server.server_close()


def _get(base: str, path: str, cookie: str | None = None) -> tuple[int, dict | str]:
    headers = {"Cookie": cookie} if cookie else {}
    req = urllib.request.Request(f"{base}{path}", headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            try: return resp.status, json.loads(text)
            except Exception: return resp.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except Exception: return e.code, text


def _signup_get_cookie(base: str, email: str, password: str) -> str:
    data = json.dumps({"email": email, "password": password}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/auth/signup",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        sc = resp.headers.get("Set-Cookie", "")
    return sc.split(";", 1)[0].strip() if sc else ""


# ---- 503 when admin disabled --------------------------------------------

def test_users_503_when_no_admins_configured(engine_server):
    status, body = _get(engine_server["base"], "/api/admin/users")
    assert status == 503


def test_projects_503_when_no_admins_configured(engine_server):
    status, body = _get(engine_server["base"], "/api/admin/projects")
    assert status == 503


def test_errors_503_when_no_admins_configured(engine_server):
    status, body = _get(engine_server["base"], "/api/admin/errors")
    assert status == 503


# ---- 401 / 403 ----------------------------------------------------------

def test_users_401_when_not_signed_in(engine_server):
    engine_server["monkey"].setenv("PEBBLE_ADMIN_EMAIL", "marc@example.com")
    status, body = _get(engine_server["base"], "/api/admin/users")
    assert status == 401


def test_users_403_when_signed_in_as_non_admin(engine_server):
    engine_server["monkey"].setenv("PEBBLE_ADMIN_EMAIL", "marc@example.com")
    cookie = _signup_get_cookie(engine_server["base"], "regular@example.com", "valid-password")
    status, body = _get(engine_server["base"], "/api/admin/users", cookie=cookie)
    assert status == 403


# ---- 200 for admin ------------------------------------------------------

def test_users_lists_emails_for_admin(engine_server):
    engine_server["monkey"].setenv("PEBBLE_ADMIN_EMAIL", "admin@example.com")
    # Create some users
    admin_cookie = _signup_get_cookie(engine_server["base"], "admin@example.com", "admin-password")
    _signup_get_cookie(engine_server["base"], "alice@example.com", "alice-password")
    _signup_get_cookie(engine_server["base"], "bob@example.com",   "bob-password")

    status, body = _get(engine_server["base"], "/api/admin/users", cookie=admin_cookie)
    assert status == 200
    assert body["count"] == 3
    emails = {u["email"] for u in body["users"]}
    assert emails == {"admin@example.com", "alice@example.com", "bob@example.com"}


def test_admin_email_is_case_insensitive(engine_server):
    engine_server["monkey"].setenv("PEBBLE_ADMIN_EMAIL", "Admin@Example.com")
    cookie = _signup_get_cookie(engine_server["base"], "admin@example.com", "admin-password")
    status, body = _get(engine_server["base"], "/api/admin/users", cookie=cookie)
    assert status == 200


def test_projects_lists_with_owner_join(engine_server):
    out = engine_server["output"]
    engine_server["monkey"].setenv("PEBBLE_ADMIN_EMAIL", "admin@example.com")
    admin_cookie = _signup_get_cookie(engine_server["base"], "admin@example.com", "admin-password")

    # Sign up a regular user and learn their id
    alice_cookie = _signup_get_cookie(engine_server["base"], "alice@example.com", "alice-password")
    me_req = urllib.request.Request(
        f"{engine_server['base']}/api/auth/me",
        headers={"Cookie": alice_cookie},
    )
    with urllib.request.urlopen(me_req, timeout=5) as resp:
        alice = json.loads(resp.read().decode("utf-8"))
    alice_id = alice["user"]["id"]

    # Seed a project owned by alice
    project = out / "good-co"
    project.mkdir()
    (project / "site").mkdir()
    (project / "site" / "page.tsx").write_text("x")
    (project / "brief.json").write_text(json.dumps({
        "business_name": "Good Co", "_user_id": alice_id
    }))

    status, body = _get(engine_server["base"], "/api/admin/projects", cookie=admin_cookie)
    assert status == 200
    assert body["count"] == 1
    row = body["projects"][0]
    assert row["slug"] == "good-co"
    assert row["user_email"] == "alice@example.com"


def test_errors_returns_filtered_tail(engine_server, tmp_path):
    engine_server["monkey"].setenv("PEBBLE_ADMIN_EMAIL", "admin@example.com")
    cookie = _signup_get_cookie(engine_server["base"], "admin@example.com", "admin-password")

    # Plant a fake error log in the project root (engine treats engine.err.log
    # as its log file). Point PROJECT_ROOT at tmp so we don't touch the real one.
    engine_server["monkey"].setattr(pebble_engine, "PROJECT_ROOT", tmp_path)
    log_path = tmp_path / "engine.err.log"
    log_path.write_text(
        "INFO: routine startup\n"
        "ERROR: something exploded at module x\n"
        "WARNING: deprecated path\n"
        "INFO: handled a request\n",
        encoding="utf-8",
    )

    status, body = _get(engine_server["base"], "/api/admin/errors", cookie=cookie)
    assert status == 200
    lines = [r["line"] for r in body["errors"]]
    assert any("ERROR" in ln for ln in lines)
    assert any("WARNING" in ln for ln in lines)
    # INFO lines are filtered out
    assert all("INFO: routine" not in ln for ln in lines)


# ---- T17: /api/admin/engagement ------------------------------------------

def test_engagement_503_when_no_admins_configured(engine_server):
    status, body = _get(engine_server["base"], "/api/admin/engagement")
    assert status == 503


def test_engagement_401_when_not_signed_in(engine_server):
    engine_server["monkey"].setenv("PEBBLE_ADMIN_EMAIL", "admin@example.com")
    status, _ = _get(engine_server["base"], "/api/admin/engagement")
    assert status == 401


def test_engagement_403_when_signed_in_as_non_admin(engine_server):
    engine_server["monkey"].setenv("PEBBLE_ADMIN_EMAIL", "admin@example.com")
    cookie = _signup_get_cookie(engine_server["base"], "other@example.com", "otherpass123")
    status, _ = _get(engine_server["base"], "/api/admin/engagement", cookie=cookie)
    assert status == 403


def test_engagement_returns_bucketed_users_for_admin(engine_server):
    """Admin gets a sorted list of users with engagement bucket + counts."""
    engine_server["monkey"].setenv("PEBBLE_ADMIN_EMAIL", "admin@example.com")
    # Plant some engagement events directly (don't trigger real routes).
    storage = engine_server["output"] / ".engagement"
    storage.mkdir()
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    (storage / "user-power").write_text("")  # placeholder, will be overwritten below
    for uid, events in [
        ("user-power",  ["a", "b", "c", "d", "e"]),
        ("user-active", ["a", "b"]),
        ("user-stuck",  ["a"]),
    ]:
        (storage / f"{uid}.jsonl").write_text(
            "\n".join(json.dumps({"event": e, "timestamp": now}, separators=(",", ":")) for e in events) + "\n",
            encoding="utf-8",
        )
    cookie = _signup_get_cookie(engine_server["base"], "admin@example.com", "adminpass123")
    status, body = _get(engine_server["base"], "/api/admin/engagement", cookie=cookie)
    assert status == 200
    users = body["users"]
    # Sort order: power → active → at_risk
    assert [u["user_id"] for u in users] == ["user-power", "user-active", "user-stuck"]
    assert users[0]["score"] == "power"
    assert users[1]["score"] == "active"
    assert users[2]["score"] == "at_risk"
    assert users[0]["distinct_events"] == 5
    assert "now" in body
    assert "count" in body
    # email field is present even when empty (admin UI relies on it)
    assert all("email" in u for u in users)
