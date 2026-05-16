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


# ---------------------------------------------------------------------------
# Outbound webhook config — Track 4 (2026-05-16)
# ---------------------------------------------------------------------------

def test_webhook_config_starts_unconfigured(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(
        engine_server["base"], "wh1@example.com", "valid-password")
    _seed_project(out, "wh-co", owner_id=uid)
    status, body = _request(
        "GET", engine_server["base"], "/api/projects/wh-co/forms/webhook",
        headers={"Cookie": cookie},
    )
    assert status == 200
    assert body["configured"] is False
    assert body["webhook"] is None


def test_webhook_config_set_and_get(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(
        engine_server["base"], "wh2@example.com", "valid-password")
    _seed_project(out, "wh-co", owner_id=uid)
    status, body = _request(
        "POST", engine_server["base"], "/api/projects/wh-co/forms/webhook",
        body={"url": "https://hooks.zapier.com/abc"},
        headers={"Cookie": cookie},
    )
    assert status == 200
    assert body["configured"] is True
    assert body["webhook"]["url"] == "https://hooks.zapier.com/abc"
    # Round-trip GET
    status2, body2 = _request(
        "GET", engine_server["base"], "/api/projects/wh-co/forms/webhook",
        headers={"Cookie": cookie},
    )
    assert body2["webhook"]["url"] == "https://hooks.zapier.com/abc"


def test_webhook_config_rejects_bad_scheme(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(
        engine_server["base"], "wh3@example.com", "valid-password")
    _seed_project(out, "wh-co", owner_id=uid)
    status, body = _request(
        "POST", engine_server["base"], "/api/projects/wh-co/forms/webhook",
        body={"url": "ftp://example.com/hook"},
        headers={"Cookie": cookie},
    )
    assert status == 400


def test_webhook_config_delete(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(
        engine_server["base"], "wh4@example.com", "valid-password")
    _seed_project(out, "wh-co", owner_id=uid)
    _request("POST", engine_server["base"], "/api/projects/wh-co/forms/webhook",
             body={"url": "https://example.com/hook"}, headers={"Cookie": cookie})
    status, body = _request(
        "DELETE", engine_server["base"], "/api/projects/wh-co/forms/webhook",
        headers={"Cookie": cookie},
    )
    assert status == 200
    assert body["removed"] is True
    # Subsequent GET confirms gone
    _, body2 = _request(
        "GET", engine_server["base"], "/api/projects/wh-co/forms/webhook",
        headers={"Cookie": cookie},
    )
    assert body2["configured"] is False


def test_webhook_config_requires_auth(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(
        engine_server["base"], "wh5@example.com", "valid-password")
    _seed_project(out, "wh-co", owner_id=uid)
    # GET without cookie
    status, _ = _request("GET", engine_server["base"], "/api/projects/wh-co/forms/webhook")
    assert status == 401
    # POST without cookie
    status, _ = _request("POST", engine_server["base"], "/api/projects/wh-co/forms/webhook",
                         body={"url": "https://example.com/hook"})
    assert status == 401
    # DELETE without cookie
    status, _ = _request("DELETE", engine_server["base"], "/api/projects/wh-co/forms/webhook")
    assert status == 401


def test_webhook_config_blocks_other_users(engine_server):
    """Owner-A configures a webhook; Owner-B signed in as a different
    user gets a 403."""
    out = engine_server["output"]
    cookie_a, uid_a = _signup_get_cookie_and_id(
        engine_server["base"], "owner-a@example.com", "valid-password")
    _seed_project(out, "wh-co", owner_id=uid_a)
    cookie_b, _ = _signup_get_cookie_and_id(
        engine_server["base"], "owner-b@example.com", "valid-password")
    status, _ = _request("GET", engine_server["base"], "/api/projects/wh-co/forms/webhook",
                         headers={"Cookie": cookie_b})
    assert status == 403


def test_submit_fires_webhook_when_configured(engine_server, monkeypatch):
    """End-to-end: configure a webhook, submit a form, and observe the
    delivery thread invoke post_webhook with the right payload."""
    import time as _time
    from pebble import forms_webhook as fw
    from pebble.security import forms_submit_limiter

    fw._reset_rate_limiter_for_tests()
    forms_submit_limiter._buckets.clear()
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(
        engine_server["base"], "wh6@example.com", "valid-password")
    _seed_project(out, "wh-co", owner_id=uid)
    _request("POST", engine_server["base"], "/api/projects/wh-co/forms/webhook",
             body={"url": "https://hooks.zapier.com/abc"}, headers={"Cookie": cookie})

    captured = {}
    def fake_post(url, payload, **kwargs):
        captured["url"] = url
        captured["payload"] = payload
        return True, None
    # Patch the post_webhook the forms_webhook module imported into its
    # namespace (not pebble.url_fetch.post_webhook directly — the
    # module-local reference is what deliver() uses).
    monkeypatch.setattr("pebble.forms_webhook.post_webhook", fake_post)

    _request("POST", engine_server["base"], "/api/forms/wh-co",
             {"name": "Alice", "message": "Hi"})

    # The delivery runs on a daemon thread — give it a beat to land.
    for _ in range(20):
        if captured:
            break
        _time.sleep(0.05)
    assert captured.get("url") == "https://hooks.zapier.com/abc"
    assert captured["payload"]["event"] == "form.submitted"
    assert captured["payload"]["project"] == "wh-co"
    assert captured["payload"]["submission"]["fields"]["name"] == "Alice"


def test_submit_succeeds_even_when_webhook_fails(engine_server, monkeypatch):
    """The inbox is the source of truth — a webhook failure must NOT
    affect the form-submit response or the inbox write."""
    from pebble import forms_webhook as fw
    from pebble.security import forms_submit_limiter
    fw._reset_rate_limiter_for_tests()
    forms_submit_limiter._buckets.clear()
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(
        engine_server["base"], "wh7@example.com", "valid-password")
    _seed_project(out, "wh-co", owner_id=uid)
    _request("POST", engine_server["base"], "/api/projects/wh-co/forms/webhook",
             body={"url": "https://broken.example/hook"}, headers={"Cookie": cookie})

    monkeypatch.setattr("pebble.forms_webhook.post_webhook",
                        lambda *_a, **_k: (False, "HTTP 503"))

    status, body = _request("POST", engine_server["base"], "/api/forms/wh-co",
                             {"name": "Alice"})
    assert status == 200
    assert body["ok"] is True
    # Inbox file written despite webhook failure
    inbox = out / "wh-co" / "inbox"
    assert any(inbox.glob("*.json"))


def test_submit_works_when_no_webhook_configured(engine_server, monkeypatch):
    """No webhook URL — form submit must NOT spawn any outbound call.
    Regression guard against accidentally always-firing the delivery
    thread."""
    from pebble import forms_webhook as fw
    from pebble.security import forms_submit_limiter
    fw._reset_rate_limiter_for_tests()
    forms_submit_limiter._buckets.clear()

    out = engine_server["output"]
    _seed_project(out, "no-webhook-co")
    called = {"yes": False}
    def trip(*_a, **_kw):
        called["yes"] = True
        return True, None
    monkeypatch.setattr("pebble.forms_webhook.post_webhook", trip)

    status, body = _request("POST", engine_server["base"], "/api/forms/no-webhook-co",
                             {"name": "Bob"})
    assert status == 200
    # Give the daemon thread a moment in case something fires.
    import time as _time
    _time.sleep(0.15)
    assert called["yes"] is False


# ---------------------------------------------------------------------------
# Autoresponder config — Track 5 (2026-05-16)
# ---------------------------------------------------------------------------

def test_autoresponder_starts_with_defaults(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(
        engine_server["base"], "ar1@example.com", "valid-password")
    _seed_project(out, "ar-co", owner_id=uid)
    status, body = _request(
        "GET", engine_server["base"], "/api/projects/ar-co/forms/autoresponder",
        headers={"Cookie": cookie},
    )
    assert status == 200
    assert body["autoresponder"]["enabled"] is False
    assert body["autoresponder"]["subject"]  # default subject populated
    assert body["autoresponder"]["reply_field"] == "email"


def test_autoresponder_enable_and_save_custom(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(
        engine_server["base"], "ar2@example.com", "valid-password")
    _seed_project(out, "ar-co", owner_id=uid)
    status, body = _request(
        "POST", engine_server["base"], "/api/projects/ar-co/forms/autoresponder",
        body={
            "enabled": True,
            "subject": "Thanks for reaching out, {{ name }}",
            "body":    "Hi {{ name }} — we got it.",
        },
        headers={"Cookie": cookie},
    )
    assert status == 200
    assert body["autoresponder"]["enabled"] is True
    assert body["autoresponder"]["subject"] == "Thanks for reaching out, {{ name }}"


def test_autoresponder_post_requires_enabled_bool(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(
        engine_server["base"], "ar3@example.com", "valid-password")
    _seed_project(out, "ar-co", owner_id=uid)
    status, body = _request(
        "POST", engine_server["base"], "/api/projects/ar-co/forms/autoresponder",
        body={"subject": "no enabled flag"},
        headers={"Cookie": cookie},
    )
    assert status == 400
    assert "enabled" in body["error"].lower()


def test_autoresponder_rejects_invalid_types(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(
        engine_server["base"], "ar4@example.com", "valid-password")
    _seed_project(out, "ar-co", owner_id=uid)
    status, body = _request(
        "POST", engine_server["base"], "/api/projects/ar-co/forms/autoresponder",
        body={"enabled": True, "subject": 42},  # subject must be string
        headers={"Cookie": cookie},
    )
    assert status == 400


def test_autoresponder_delete(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(
        engine_server["base"], "ar5@example.com", "valid-password")
    _seed_project(out, "ar-co", owner_id=uid)
    _request("POST", engine_server["base"], "/api/projects/ar-co/forms/autoresponder",
             body={"enabled": True}, headers={"Cookie": cookie})
    status, body = _request(
        "DELETE", engine_server["base"], "/api/projects/ar-co/forms/autoresponder",
        headers={"Cookie": cookie},
    )
    assert status == 200
    assert body["removed"] is True
    _, body2 = _request(
        "GET", engine_server["base"], "/api/projects/ar-co/forms/autoresponder",
        headers={"Cookie": cookie},
    )
    # After delete, config reverts to defaults (enabled=false)
    assert body2["autoresponder"]["enabled"] is False


def test_autoresponder_requires_auth(engine_server):
    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(
        engine_server["base"], "ar6@example.com", "valid-password")
    _seed_project(out, "ar-co", owner_id=uid)
    for verb, body in (("GET", None), ("POST", {"enabled": True}), ("DELETE", None)):
        status, _ = _request(verb, engine_server["base"],
                             "/api/projects/ar-co/forms/autoresponder",
                             body=body)
        assert status == 401, f"{verb} should require auth, got {status}"


def test_autoresponder_blocks_other_users(engine_server):
    out = engine_server["output"]
    cookie_a, uid_a = _signup_get_cookie_and_id(
        engine_server["base"], "ar-a@example.com", "valid-password")
    _seed_project(out, "ar-co", owner_id=uid_a)
    cookie_b, _ = _signup_get_cookie_and_id(
        engine_server["base"], "ar-b@example.com", "valid-password")
    status, _ = _request(
        "GET", engine_server["base"], "/api/projects/ar-co/forms/autoresponder",
        headers={"Cookie": cookie_b},
    )
    assert status == 403


def test_submit_fires_autoresponse_when_enabled(engine_server, monkeypatch):
    """End-to-end: enable autoresponder, submit a form with an email
    field, observe send_async called with the rendered message."""
    import time as _time
    from concurrent.futures import Future
    from pebble import forms_autoresponder as ar, forms_webhook as fw
    from pebble.security import forms_submit_limiter
    ar._reset_rate_limiter_for_tests()
    fw._reset_rate_limiter_for_tests()
    forms_submit_limiter._buckets.clear()

    out = engine_server["output"]
    cookie, uid = _signup_get_cookie_and_id(
        engine_server["base"], "ar7@example.com", "valid-password")
    _seed_project(out, "ar-co", owner_id=uid)
    _request("POST", engine_server["base"], "/api/projects/ar-co/forms/autoresponder",
             body={"enabled": True, "subject": "Thanks {{ name }}!",
                   "body": "Hi {{ name }}, we got your note."},
             headers={"Cookie": cookie})

    captured = {}
    def fake_send(message, *_a, **_k):
        captured["to"] = message.to
        captured["subject"] = message.subject
        captured["text"] = message.text
        f: Future = Future()
        f.set_result({"ok": True, "provider": "fake", "id": "x"})
        return f
    monkeypatch.setattr("pebble.forms_autoresponder.send_async", fake_send)

    _request("POST", engine_server["base"], "/api/forms/ar-co",
             {"name": "Marc", "email": "marc@example.com", "message": "Hi"})

    for _ in range(20):
        if captured:
            break
        _time.sleep(0.05)
    assert captured.get("to") == "marc@example.com"
    assert captured["subject"] == "Thanks Marc!"
    assert "Hi Marc" in captured["text"]


def test_submit_no_autoresponse_when_disabled(engine_server, monkeypatch):
    """Default config is disabled — no email should fire."""
    import time as _time
    from pebble import forms_autoresponder as ar, forms_webhook as fw
    from pebble.security import forms_submit_limiter
    ar._reset_rate_limiter_for_tests()
    fw._reset_rate_limiter_for_tests()
    forms_submit_limiter._buckets.clear()

    out = engine_server["output"]
    _seed_project(out, "ar-co")
    called = {"yes": False}
    monkeypatch.setattr("pebble.forms_autoresponder.send_async",
                        lambda *_a, **_k: called.update({"yes": True}))
    _request("POST", engine_server["base"], "/api/forms/ar-co",
             {"name": "Bob", "email": "bob@example.com"})
    _time.sleep(0.15)
    assert called["yes"] is False
