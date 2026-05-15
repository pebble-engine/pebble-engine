"""Tests for first-party privacy analytics."""
from __future__ import annotations

import json
import socket
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import pebble_engine
import pebble.history as history_mod
import pebble.analytics as analytics_mod


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


def _seed_project(output: Path, slug: str) -> Path:
    project = output / slug
    project.mkdir()
    (project / "site").mkdir()
    (project / "site" / "page.tsx").write_text("x")
    return project


# ---- pebble.analytics unit tests ----------------------------------------

def test_normalize_path_strips_query_and_fragment():
    assert analytics_mod._normalize_path("/about?utm=email#contact") == "/about"
    assert analytics_mod._normalize_path("") == "/"
    assert analytics_mod._normalize_path("") == "/"
    # Cap on length
    long_p = "/" + "x" * 1000
    assert len(analytics_mod._normalize_path(long_p)) == analytics_mod.MAX_PATH_LEN


def test_referrer_host_just_returns_host():
    assert analytics_mod._referrer_host("https://news.example.com/path?q=1") == "news.example.com"
    assert analytics_mod._referrer_host(None) == ""
    assert analytics_mod._referrer_host("") == ""


def test_visitor_hour_hash_is_stable_within_hour():
    when = datetime(2026, 5, 14, 22, 15, 0, tzinfo=timezone.utc)
    h1 = analytics_mod._visitor_hour_hash("203.0.113.1", "UA-X", when)
    h2 = analytics_mod._visitor_hour_hash("203.0.113.1", "UA-X", when)
    assert h1 == h2 and len(h1) == 16


def test_visitor_hour_hash_rotates_each_hour():
    a = datetime(2026, 5, 14, 22, 59, 59, tzinfo=timezone.utc)
    b = datetime(2026, 5, 14, 23, 0, 1,  tzinfo=timezone.utc)
    h_a = analytics_mod._visitor_hour_hash("203.0.113.1", "UA", a)
    h_b = analytics_mod._visitor_hour_hash("203.0.113.1", "UA", b)
    assert h_a != h_b


def test_record_appends_event(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    _seed_project(tmp_path, "good-co")
    ok = analytics_mod.record_page_view("good-co", path="/about", ip="203.0.113.42", user_agent="UA")
    assert ok is True
    files = list((tmp_path / "good-co" / "analytics").glob("*.jsonl"))
    assert len(files) == 1


def test_summarize_aggregates(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    _seed_project(tmp_path, "good-co")
    for _ in range(3):
        analytics_mod.record_page_view("good-co", path="/", ip="203.0.113.1", user_agent="A")
    analytics_mod.record_page_view("good-co", path="/about", ip="203.0.113.2", user_agent="A",
                                   referrer="https://example.com/blog")

    s = analytics_mod.summarize("good-co", days=2)
    assert s["total_views"] == 4
    assert s["approx_visitors"] >= 2
    paths = {p["path"]: p["views"] for p in s["top_paths"]}
    assert paths.get("/") == 3
    assert paths.get("/about") == 1
    refs = {r["host"]: r["views"] for r in s["top_referrer_hosts"]}
    assert refs.get("example.com") == 1


# ---- HTTP integration ---------------------------------------------------

def test_track_records_and_summary_returns(engine_server):
    out = engine_server["output"]
    _seed_project(out, "good-co")
    status, body = _request("POST", engine_server["base"], "/api/track/good-co",
                            {"path": "/about", "referrer": "https://x.com/post"})
    assert status == 200
    assert body["recorded"] is True

    status, summary = _request("GET", engine_server["base"], "/api/projects/good-co/analytics")
    assert status == 200
    assert summary["total_views"] >= 1
    assert summary["top_paths"][0]["path"] == "/about"


def test_track_ok_even_for_unknown_project(engine_server):
    # /api/track is fire-and-forget — must not break sites if Pebble can't find them
    status, body = _request("POST", engine_server["base"], "/api/track/ghost", {"path": "/"})
    assert status == 200
    assert body["recorded"] is False


def test_summary_404_for_unknown_project(engine_server):
    status, body = _request("GET", engine_server["base"], "/api/projects/ghost/analytics")
    assert status == 404


def test_track_never_stores_raw_ip(engine_server):
    out = engine_server["output"]
    _seed_project(out, "good-co")
    _request("POST", engine_server["base"], "/api/track/good-co", {"path": "/"})
    files = list((out / "good-co" / "analytics").glob("*.jsonl"))
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8")
    # The raw IP must never appear in any event.
    assert "127.0.0.1" not in content
    # But a visitor_hour hash should
    line = content.splitlines()[0]
    event = json.loads(line)
    assert event["visitor_hour"] and len(event["visitor_hour"]) == 16
