"""Tests for custom domain wiring.

The Cloudflare-attached paths are not exercised here (they need real
creds). We test:

- Host normalization + validation
- File-backed state (read/write/clear)
- HTTP endpoints (GET / POST / DELETE) when Cloudflare is not configured —
  status stays ``pending`` with CNAME instructions returned to the user.
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
import pebble.domain as domain_mod
import pebble.security as security_mod
import pebble.server.domain as domain_server
import pebble.server.projects as projects_server


@pytest.fixture(autouse=True)
def _clean_cloudflare_env(monkeypatch):
    """Every test in this module assumes Cloudflare is NOT configured —
    the engine_server fixture clears it too, but unit tests that don't
    use the fixture need their own scrub now that .env has real keys."""
    monkeypatch.delenv("CLOUDFLARE_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)


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
    monkeypatch.setattr(security_mod, "_output_dir", lambda: out)
    monkeypatch.delenv("CLOUDFLARE_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)
    # Phase 54a — custom domains require Starter+. These tests predate
    # the gate; bypass at the call site so they keep exercising the
    # domain-attach contract. Dedicated 402 test lives separately.
    monkeypatch.setattr(domain_server, "get_limit", lambda uid, key: 1)

    # Auth gate bypass — see test_publish.py / test_http_e2e.py for the
    # rationale. Existing tests target the JSON contract; the auth gate
    # itself is covered by test_security.py.
    def bypass(handler, slug):
        if not security_mod.is_valid_slug(slug):
            handler._json(400, {"error": "invalid project slug"})
            return None
        if not (out / slug).exists():
            handler._json(404, {"error": f"project not found: {slug}"})
            return None
        return "test-user"
    monkeypatch.setattr(domain_server,   "require_project_owner", bypass)
    monkeypatch.setattr(projects_server, "require_project_owner", bypass)

    port = _find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), pebble_engine.PebbleHandler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    time.sleep(0.1)
    try:
        yield {"base": f"http://127.0.0.1:{port}", "output": out, "server": server}
    finally:
        server.shutdown()
        server.server_close()


def _request(method: str, base: str, path: str, body: dict | None = None) -> tuple[int, dict | str]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(f"{base}{path}", data=data, headers=headers, method=method)
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
    (project / "site" / "app").mkdir()
    (project / "site" / "app" / "page.tsx").write_text("x")
    return project


# ---- normalize_host -----------------------------------------------------

def test_normalize_host_lowercases_and_strips_scheme():
    assert domain_mod.normalize_host("HTTPS://Example.com/") == "example.com"
    assert domain_mod.normalize_host("  HTTP://www.foo.io:443/path  ") == "www.foo.io"


def test_normalize_host_rejects_bad_input():
    for bad in ["", "   ", "no-dot", "spaces in.com", "x_y.com", "-bad.com", ".com"]:
        with pytest.raises(domain_mod.DomainError):
            domain_mod.normalize_host(bad)


def test_normalize_host_accepts_subdomains_and_hyphens():
    assert domain_mod.normalize_host("foo.example.co.uk") == "foo.example.co.uk"
    assert domain_mod.normalize_host("good-co.com") == "good-co.com"


# ---- cname helpers ------------------------------------------------------

def test_cname_target_is_slugified_project_name():
    assert domain_mod.cname_target_for("Good Co!") == "pebble-good-co.pages.dev"
    assert domain_mod.cname_target_for("yoga") == "pebble-yoga.pages.dev"


def test_cname_instructions_is_paste_ready():
    msg = domain_mod.cname_instructions("example.com", "pebble-yoga.pages.dev")
    assert msg == "example.com CNAME pebble-yoga.pages.dev"


# ---- set/read/clear -----------------------------------------------------

def test_set_domain_persists_record_when_cloudflare_off(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    monkeypatch.delenv("CLOUDFLARE_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)
    _seed_project(tmp_path, "good-co")

    rec = domain_mod.set_domain("good-co", "EXAMPLE.com")
    assert rec.host == "example.com"
    assert rec.status == "pending"
    assert rec.cname_target == "pebble-good-co.pages.dev"
    assert rec.cname_record == "example.com CNAME pebble-good-co.pages.dev"

    state = domain_mod.read_domain("good-co")
    assert state["host"] == "example.com"
    assert state["status"] == "pending"


def test_remove_domain_clears_record(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    _seed_project(tmp_path, "good-co")
    domain_mod.set_domain("good-co", "example.com")
    prev = domain_mod.remove_domain("good-co")
    assert prev["host"] == "example.com"
    assert domain_mod.read_domain("good-co") is None


def test_remove_domain_when_none_set(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    _seed_project(tmp_path, "good-co")
    assert domain_mod.remove_domain("good-co") is None


# ---- HTTP integration ---------------------------------------------------

def test_get_domain_404_for_missing_project(engine_server):
    status, body = _request("GET", engine_server["base"], "/api/projects/nope/domain")
    assert status == 404


def test_get_domain_returns_null_when_unset(engine_server):
    _seed_project(engine_server["output"], "good-co")
    status, body = _request("GET", engine_server["base"], "/api/projects/good-co/domain")
    assert status == 200
    assert body["slug"] == "good-co"
    assert body["domain"] is None
    assert body["cloudflare_configured"] is False
    assert "CLOUDFLARE_API_TOKEN" in (body["cloudflare_setup_md"] or "")


def test_post_then_get_round_trip(engine_server):
    _seed_project(engine_server["output"], "good-co")
    status, body = _request("POST", engine_server["base"],
                            "/api/projects/good-co/domain",
                            {"host": "example.com"})
    assert status == 200
    assert body["domain"]["host"] == "example.com"
    assert body["domain"]["status"] == "pending"
    assert body["domain"]["cname_record"] == "example.com CNAME pebble-good-co.pages.dev"

    status, body = _request("GET", engine_server["base"], "/api/projects/good-co/domain")
    assert status == 200
    assert body["domain"]["host"] == "example.com"


def test_post_rejects_bad_host(engine_server):
    _seed_project(engine_server["output"], "good-co")
    status, body = _request("POST", engine_server["base"],
                            "/api/projects/good-co/domain",
                            {"host": "no-tld"})
    assert status == 400


def test_post_404_for_missing_project(engine_server):
    status, body = _request("POST", engine_server["base"],
                            "/api/projects/nope/domain",
                            {"host": "example.com"})
    assert status == 404


def test_delete_domain_round_trip(engine_server):
    _seed_project(engine_server["output"], "good-co")
    _request("POST", engine_server["base"], "/api/projects/good-co/domain",
             {"host": "example.com"})
    status, body = _request("DELETE", engine_server["base"], "/api/projects/good-co/domain")
    assert status == 200
    assert body["removed"]["host"] == "example.com"
    # Get returns null again
    status, body = _request("GET", engine_server["base"], "/api/projects/good-co/domain")
    assert body["domain"] is None


def test_delete_domain_404_when_none_attached(engine_server):
    _seed_project(engine_server["output"], "good-co")
    status, body = _request("DELETE", engine_server["base"], "/api/projects/good-co/domain")
    assert status == 404


def test_dashboard_summary_includes_domain_after_attach(engine_server):
    _seed_project(engine_server["output"], "good-co")
    _request("POST", engine_server["base"], "/api/projects/good-co/domain",
             {"host": "example.com"})
    status, body = _request("GET", engine_server["base"], "/api/projects")
    assert status == 200
    proj = next(p for p in body["projects"] if p["slug"] == "good-co")
    assert proj["domain"]["host"] == "example.com"
    assert proj["domain"]["status"] == "pending"
