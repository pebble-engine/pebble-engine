"""Tests for the form inbox flow."""
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
import pebble.forms as forms_mod


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
    port = _find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), pebble_engine.PebbleHandler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    time.sleep(0.1)
    try:
        yield {"base": f"http://127.0.0.1:{port}", "output": out}
    finally:
        server.shutdown()
        server.server_close()


def _request(method: str, base: str, path: str, body: dict | None = None, headers: dict | None = None) -> tuple[int, dict | str]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    hdrs = {"Content-Type": "application/json"} if data else {}
    if headers: hdrs.update(headers)
    req = urllib.request.Request(f"{base}{path}", data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            try: return resp.status, json.loads(text)
            except Exception: return resp.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except Exception: return e.code, text


def _signup_get_cookie_and_id(base: str, email: str, password: str) -> tuple[str, str]:
    data = json.dumps({"email": email, "password": password}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/auth/signup",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        sc = resp.headers.get("Set-Cookie", "")
        body = json.loads(resp.read().decode("utf-8"))
    cookie = sc.split(";", 1)[0].strip() if sc else ""
    return cookie, body["user"]["id"]


def _seed_project(output: Path, slug: str, owner_id: str | None = None) -> Path:
    """Seed a project. When owner_id is provided, stamp it into brief.json
    so /api/projects/<slug>/inbox and /analytics owner checks pass."""
    project = output / slug
    project.mkdir()
    (project / "site").mkdir()
    (project / "site" / "page.tsx").write_text("x")
    if owner_id:
        (project / "brief.json").write_text(json.dumps({"_user_id": owner_id}))
    return project


# ---- pebble.forms unit tests --------------------------------------------

def test_normalize_drops_honeypot_and_clamps_lengths(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    rec = forms_mod.save_submission("good-co", {
        "name":               "Alice",
        forms_mod.HONEYPOT_FIELD: "BOT-WAS-HERE",
        "huge":               "x" * 10000,
    })
    assert forms_mod.HONEYPOT_FIELD not in rec.fields
    assert rec.fields["name"] == "Alice"
    assert len(rec.fields["huge"]) <= forms_mod.MAX_FIELD_LEN


def test_normalize_caps_field_count(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    many = {f"f{i}": "x" for i in range(100)}
    rec = forms_mod.save_submission("good-co", many)
    assert len(rec.fields) <= 32  # MAX_FIELDS_PER_FORM


def test_normalize_rejects_non_dict(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    with pytest.raises(forms_mod.FormError):
        forms_mod.save_submission("good-co", "not a dict")  # type: ignore[arg-type]


def test_ip_hash_is_not_raw_ip(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    rec = forms_mod.save_submission("good-co", {"x": "y"}, ip="203.0.113.42")
    assert rec.ip_hash
    assert "203.0.113" not in (rec.ip_hash or "")
    assert len(rec.ip_hash or "") == 16


def test_is_honeypot_trip_detects_non_empty():
    assert forms_mod.is_honeypot_trip({forms_mod.HONEYPOT_FIELD: "i am a bot"})
    assert not forms_mod.is_honeypot_trip({forms_mod.HONEYPOT_FIELD: ""})
    assert not forms_mod.is_honeypot_trip({"name": "Alice"})


def test_list_get_update_delete_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    _seed_project(tmp_path, "good-co")
    rec = forms_mod.save_submission("good-co", {"name": "Alice", "msg": "Hi"})
    rows = forms_mod.list_submissions("good-co")
    assert len(rows) == 1
    fetched = forms_mod.get_submission("good-co", rec.id)
    assert fetched["fields"]["name"] == "Alice"
    forms_mod.update_submission("good-co", rec.id, {"read": True})
    assert forms_mod.get_submission("good-co", rec.id)["read"] is True
    # Non-allowlisted patch keys are ignored — defensive
    forms_mod.update_submission("good-co", rec.id, {"fields": {"injected": "x"}})
    assert "injected" not in forms_mod.get_submission("good-co", rec.id)["fields"]
    forms_mod.delete_submission("good-co", rec.id)
    assert forms_mod.list_submissions("good-co") == []


def test_inbox_summary(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    _seed_project(tmp_path, "good-co")
    forms_mod.save_submission("good-co", {"x": "y"})
    forms_mod.save_submission("good-co", {"a": "b"})
    s = forms_mod.inbox_summary("good-co")
    assert s["total"] == 2
    assert s["unread"] == 2


# ---- HTTP integration ---------------------------------------------------

def test_submit_writes_to_inbox(engine_server):
    out = engine_server["output"]
    _seed_project(out, "good-co")
    status, body = _request("POST", engine_server["base"], "/api/forms/good-co", {
        "name": "Alice", "email": "alice@example.com", "message": "Hello",
    })
    assert status == 200
    assert body["ok"] is True
    inbox = out / "good-co" / "inbox"
    files = list(inbox.glob("*.json"))
    assert len(files) == 1


def test_submit_404_for_unknown_project(engine_server):
    status, body = _request("POST", engine_server["base"], "/api/forms/ghost", {"x": "y"})
    assert status == 404


def test_submit_honeypot_swallowed_silently(engine_server):
    out = engine_server["output"]
    _seed_project(out, "good-co")
    status, body = _request("POST", engine_server["base"], "/api/forms/good-co", {
        "name": "Alice",
        forms_mod.HONEYPOT_FIELD: "bot-was-here",
    })
    assert status == 200
    assert body["ok"] is True
    # No inbox file written
    inbox = out / "good-co" / "inbox"
    assert not inbox.exists() or list(inbox.glob("*.json")) == []


def test_list_inbox_returns_submissions(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(engine_server["base"], "owner@example.com", "valid-password")
    _seed_project(out, "good-co", owner_id=uid)
    _request("POST", engine_server["base"], "/api/forms/good-co", {"name": "A"})
    _request("POST", engine_server["base"], "/api/forms/good-co", {"name": "B"})
    status, body = _request("GET", engine_server["base"], "/api/projects/good-co/inbox", headers={"Cookie": cookie})
    assert status == 200
    assert body["count"] == 2
    assert body["unread"] == 2


def test_list_inbox_401_when_signed_out(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(engine_server["base"], "owner@example.com", "valid-password")
    _seed_project(out, "good-co", owner_id=uid)
    status, body = _request("GET", engine_server["base"], "/api/projects/good-co/inbox")
    assert status == 401


def test_list_inbox_403_when_signed_in_as_other_user(engine_server):
    """Owner-check regression: other users must NOT read someone's inbox."""
    out = engine_server["output"]
    _, owner_id = _signup_get_cookie_and_id(engine_server["base"], "owner@example.com", "valid-password")
    other_cookie, _ = _signup_get_cookie_and_id(engine_server["base"], "snoop@example.com", "valid-password")
    _seed_project(out, "good-co", owner_id=owner_id)
    status, body = _request("GET", engine_server["base"],
                            "/api/projects/good-co/inbox",
                            headers={"Cookie": other_cookie})
    assert status == 403


def test_get_inbox_item_round_trip(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(engine_server["base"], "owner@example.com", "valid-password")
    _seed_project(out, "good-co", owner_id=uid)
    _, sub = _request("POST", engine_server["base"], "/api/forms/good-co", {"name": "Alice"})
    sub_id = sub["id"]
    status, body = _request("GET", engine_server["base"], f"/api/projects/good-co/inbox/{sub_id}",
                            headers={"Cookie": cookie})
    assert status == 200
    assert body["fields"]["name"] == "Alice"


def test_mark_read_then_list_shows_zero_unread(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(engine_server["base"], "owner@example.com", "valid-password")
    _seed_project(out, "good-co", owner_id=uid)
    _, sub = _request("POST", engine_server["base"], "/api/forms/good-co", {"name": "Alice"})
    status, body = _request("POST", engine_server["base"], f"/api/projects/good-co/inbox/{sub['id']}/read", {},
                            headers={"Cookie": cookie})
    assert status == 200
    assert body["read"] is True
    _, listing = _request("GET", engine_server["base"], "/api/projects/good-co/inbox", headers={"Cookie": cookie})
    assert listing["unread"] == 0


def test_delete_inbox_item(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(engine_server["base"], "owner@example.com", "valid-password")
    _seed_project(out, "good-co", owner_id=uid)
    _, sub = _request("POST", engine_server["base"], "/api/forms/good-co", {"name": "Alice"})
    status, _ = _request("DELETE", engine_server["base"], f"/api/projects/good-co/inbox/{sub['id']}",
                         headers={"Cookie": cookie})
    assert status == 200
    _, listing = _request("GET", engine_server["base"], "/api/projects/good-co/inbox", headers={"Cookie": cookie})
    assert listing["count"] == 0


def test_submit_rejects_oversized_payload(engine_server):
    _seed_project(engine_server["output"], "good-co")
    # 32KB payload — twice the limit
    big = {"x": "a" * (32 * 1024)}
    status, body = _request("POST", engine_server["base"], "/api/forms/good-co", big)
    assert status == 413


def test_submit_rate_limited_after_burst(engine_server, monkeypatch):
    """Per-IP burst limiter kicks in after ~10 rapid submissions."""
    # The shared limiter is module-state; reset for test isolation.
    from pebble.security import forms_submit_limiter
    forms_submit_limiter._buckets.clear()
    _seed_project(engine_server["output"], "good-co")
    statuses = []
    for i in range(15):
        s, _ = _request("POST", engine_server["base"], "/api/forms/good-co", {"i": str(i)})
        statuses.append(s)
    # Some early ones succeed, eventually we see 429
    assert 429 in statuses
