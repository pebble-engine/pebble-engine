"""Unit + HTTP integration tests for Phase 44 instant subdomain publish.

The instant publish flow is interesting in three places:

1. Subdomain validation + reserved-name list (pure-function tests).
2. The sentinel write/read round-trip + uniqueness behaviour.
3. End-to-end through the real HTTP server: POST creates the sentinel,
   GET reads it, DELETE removes it, and a request with
   ``Host: <subdomain>.<public-domain>`` is routed to the preview handler.
"""
from __future__ import annotations

import http.client
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
import pebble.security as security_mod
import pebble.server.publish as publish_server
import pebble.server.publish_instant as instant_mod
import pebble.server.projects as projects_server


# ---- helpers ------------------------------------------------------------

def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def engine_server(tmp_path, monkeypatch):
    """Boot the real PebbleHandler with auth bypassed + a temp OUTPUT_DIR.

    Mirrors the convention in test_publish.py — we exercise the JSON
    contract through the real server but without session cookies. The
    authn / authz behaviour itself is covered by test_security.py.
    """
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.setattr(history_mod, "OUTPUT_DIR", out)
    monkeypatch.setattr(security_mod, "_output_dir", lambda: out)

    def bypass(handler, slug):
        if not security_mod.is_valid_slug(slug):
            handler._json(400, {"error": "invalid project slug"})
            return None
        if not (out / slug).exists():
            handler._json(404, {"error": f"project not found: {slug}"})
            return None
        return "test-user"

    monkeypatch.setattr(publish_server,  "require_project_owner", bypass)
    monkeypatch.setattr(projects_server, "require_project_owner", bypass)
    monkeypatch.setattr(instant_mod,     "require_project_owner", bypass)
    monkeypatch.setenv("PEBBLE_PUBLIC_DOMAIN", "pebbleapp.test")
    monkeypatch.setenv("PEBBLE_PUBLIC_SCHEME", "http")
    monkeypatch.delenv("CLOUDFLARE_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)

    port = _find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), pebble_engine.PebbleHandler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    try:
        yield {"base": f"http://127.0.0.1:{port}", "output": out, "port": port}
    finally:
        server.shutdown()
        server.server_close()


def _post(base: str, path: str, body: dict | None = None) -> tuple[int, dict | str]:
    data = json.dumps(body or {}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}{path}", data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            try: return resp.status, json.loads(text)
            except Exception: return resp.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except Exception: return e.code, text


def _delete(base: str, path: str, body: dict | None = None) -> tuple[int, dict | str]:
    data = json.dumps(body or {}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}{path}", data=data,
        headers={"Content-Type": "application/json"}, method="DELETE",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            try: return resp.status, json.loads(text)
            except Exception: return resp.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except Exception: return e.code, text


def _get(base: str, path: str, host_header: str | None = None) -> tuple[int, dict | str | bytes, dict]:
    req = urllib.request.Request(f"{base}{path}")
    if host_header:
        req.add_header("Host", host_header)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            headers = dict(resp.headers.items())
            try:
                return resp.status, json.loads(data.decode("utf-8")), headers
            except Exception:
                return resp.status, data, headers
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text), dict(e.headers.items() if e.headers else {})
        except Exception: return e.code, text, {}


def _seed_project(output: Path, slug: str, html: str = "<h1>Hi</h1>") -> Path:
    project = output / slug
    project.mkdir()
    site = project / "site"
    site.mkdir()
    (site / "index.html").write_text(
        f"<!doctype html><html><body>{html}</body></html>",
        encoding="utf-8",
    )
    return project


# ---- pure-function tests ------------------------------------------------

def test_is_valid_subdomain_accepts_normal_names():
    assert instant_mod.is_valid_subdomain("bakery")
    assert instant_mod.is_valid_subdomain("good-co")
    assert instant_mod.is_valid_subdomain("a1")
    assert instant_mod.is_valid_subdomain("x" * 63)


def test_is_valid_subdomain_rejects_too_short_or_long():
    assert not instant_mod.is_valid_subdomain("")
    assert not instant_mod.is_valid_subdomain("a")
    assert not instant_mod.is_valid_subdomain("x" * 64)


def test_is_valid_subdomain_rejects_bad_characters():
    assert not instant_mod.is_valid_subdomain("Bakery")           # uppercase
    assert not instant_mod.is_valid_subdomain("good_co")          # underscore
    assert not instant_mod.is_valid_subdomain("good.co")          # dot
    assert not instant_mod.is_valid_subdomain("-bakery")          # leading hyphen
    assert not instant_mod.is_valid_subdomain("bakery-")          # trailing hyphen
    assert not instant_mod.is_valid_subdomain("baker y")          # space


def test_is_valid_subdomain_rejects_reserved_names():
    for name in ("www", "api", "app", "admin", "pricing", "auth", "login"):
        assert not instant_mod.is_valid_subdomain(name), f"{name} should be reserved"


def test_slug_to_subdomain_normalizes_underscores():
    # Legacy slugs with underscores get hyphenated for DNS safety.
    assert instant_mod._slug_to_subdomain("good_co") == "good-co"
    assert instant_mod._slug_to_subdomain("under__score") == "under-score"
    assert instant_mod._slug_to_subdomain("alreadyok") == "alreadyok"


def test_lookup_published_slug_resolves_host_header(tmp_path, monkeypatch):
    out = tmp_path / "output"; out.mkdir()
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.setenv("PEBBLE_PUBLIC_DOMAIN", "pebbleapp.test")
    # Seed a project + sentinel.
    (out / "bakery").mkdir()
    (out / "bakery" / "published.json").write_text(
        json.dumps({"slug": "bakery", "subdomain": "bakery"}),
        encoding="utf-8",
    )
    assert instant_mod.lookup_published_slug_by_subdomain("bakery.pebbleapp.test") == "bakery"
    assert instant_mod.lookup_published_slug_by_subdomain("bakery.pebbleapp.test:443") == "bakery"
    assert instant_mod.lookup_published_slug_by_subdomain("BAKERY.PEBBLEAPP.TEST") == "bakery"


def test_lookup_published_slug_rejects_apex_and_unknown(tmp_path, monkeypatch):
    out = tmp_path / "output"; out.mkdir()
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.setenv("PEBBLE_PUBLIC_DOMAIN", "pebbleapp.test")
    # Apex domain itself never resolves (that's the marketing site).
    assert instant_mod.lookup_published_slug_by_subdomain("pebbleapp.test") is None
    # Unknown subdomain.
    assert instant_mod.lookup_published_slug_by_subdomain("ghost.pebbleapp.test") is None
    # Different domain entirely.
    assert instant_mod.lookup_published_slug_by_subdomain("bakery.othersite.com") is None
    # Multi-level subdomain (should never resolve — wildcard cert only).
    (out / "bakery").mkdir()
    (out / "bakery" / "published.json").write_text(
        json.dumps({"slug": "bakery", "subdomain": "bakery"}),
        encoding="utf-8",
    )
    assert instant_mod.lookup_published_slug_by_subdomain("evil.bakery.pebbleapp.test") is None


def test_lookup_returns_none_when_env_unset(tmp_path, monkeypatch):
    out = tmp_path / "output"; out.mkdir()
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.delenv("PEBBLE_PUBLIC_DOMAIN", raising=False)
    (out / "bakery").mkdir()
    (out / "bakery" / "published.json").write_text(
        json.dumps({"slug": "bakery", "subdomain": "bakery"}),
        encoding="utf-8",
    )
    # No env config => instant publish disabled => no subdomain ever matches.
    assert instant_mod.lookup_published_slug_by_subdomain("bakery.pebbleapp.test") is None


def test_allocate_subdomain_suffixes_on_collision(tmp_path, monkeypatch):
    out = tmp_path / "output"; out.mkdir()
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.setenv("PEBBLE_PUBLIC_DOMAIN", "pebbleapp.test")
    # Pre-existing project owns "bakery".
    (out / "first").mkdir()
    (out / "first" / "published.json").write_text(
        json.dumps({"slug": "first", "subdomain": "bakery"}),
        encoding="utf-8",
    )
    # Second project should get "bakery-2".
    assert instant_mod._allocate_subdomain("bakery", exclude_slug="second") == "bakery-2"
    # The same project asking for ITS OWN subdomain gets it back.
    assert instant_mod._allocate_subdomain("bakery", exclude_slug="first") == "bakery"


# ---- HTTP integration tests --------------------------------------------

def test_publish_instant_creates_sentinel_and_returns_url(engine_server):
    base = engine_server["base"]
    out = engine_server["output"]
    _seed_project(out, "bakery")

    status, body = _post(base, "/api/publish/instant", {"slug": "bakery"})
    assert status == 200
    assert body["slug"] == "bakery"
    assert body["subdomain"] == "bakery"
    assert body["url"] == "http://bakery.pebbleapp.test"
    assert body["kind"] == "instant"
    assert body["snapshot_id"]

    sentinel = out / "bakery" / "published.json"
    assert sentinel.exists()
    data = json.loads(sentinel.read_text("utf-8"))
    assert data["subdomain"] == "bakery"
    assert data["user_id"] == "test-user"


def test_publish_instant_rejects_invalid_slug(engine_server):
    status, body = _post(engine_server["base"], "/api/publish/instant", {"slug": "../etc"})
    assert status == 400


def test_publish_instant_404s_on_missing_project(engine_server):
    status, _ = _post(engine_server["base"], "/api/publish/instant", {"slug": "ghost"})
    assert status == 404


def test_publish_instant_500s_when_env_unset(engine_server, monkeypatch):
    monkeypatch.delenv("PEBBLE_PUBLIC_DOMAIN", raising=False)
    out = engine_server["output"]
    _seed_project(out, "bakery")
    status, body = _post(engine_server["base"], "/api/publish/instant", {"slug": "bakery"})
    assert status == 500
    assert "PEBBLE_PUBLIC_DOMAIN" in body["error"]


def test_publish_instant_rejects_reserved_subdomain(engine_server):
    out = engine_server["output"]
    _seed_project(out, "bakery")
    status, body = _post(
        engine_server["base"],
        "/api/publish/instant",
        {"slug": "bakery", "subdomain": "admin"},
    )
    assert status == 400
    assert "Invalid subdomain" in body["error"]


def test_publish_instant_idempotent_keeps_subdomain(engine_server):
    out = engine_server["output"]
    _seed_project(out, "bakery")
    _post(engine_server["base"], "/api/publish/instant", {"slug": "bakery"})
    # Second publish without an explicit subdomain returns the original one.
    status, body = _post(engine_server["base"], "/api/publish/instant", {"slug": "bakery"})
    assert status == 200
    assert body["subdomain"] == "bakery"


def test_get_published_state_reads_sentinel(engine_server):
    out = engine_server["output"]
    _seed_project(out, "bakery")
    _post(engine_server["base"], "/api/publish/instant", {"slug": "bakery"})

    status, body, _ = _get(engine_server["base"], "/api/projects/bakery/published")
    assert status == 200
    assert body["published"] is True
    assert body["subdomain"] == "bakery"
    assert body["url"] == "http://bakery.pebbleapp.test"


def test_get_published_state_reports_unpublished(engine_server):
    out = engine_server["output"]
    _seed_project(out, "bakery")
    status, body, _ = _get(engine_server["base"], "/api/projects/bakery/published")
    assert status == 200
    assert body["published"] is False


def test_unpublish_instant_removes_sentinel(engine_server):
    out = engine_server["output"]
    _seed_project(out, "bakery")
    _post(engine_server["base"], "/api/publish/instant", {"slug": "bakery"})
    assert (out / "bakery" / "published.json").exists()

    status, body = _delete(engine_server["base"], "/api/publish/instant", {"slug": "bakery"})
    assert status == 200
    assert body["was_published"] is True
    assert not (out / "bakery" / "published.json").exists()


def test_unpublish_idempotent(engine_server):
    out = engine_server["output"]
    _seed_project(out, "bakery")
    # Unpublish without ever publishing — should still 200.
    status, body = _delete(engine_server["base"], "/api/publish/instant", {"slug": "bakery"})
    assert status == 200
    assert body["was_published"] is False


def test_subdomain_host_header_routes_to_preview(engine_server):
    """End-to-end: Host header alone should resolve to the project's index.html.

    This is the entire point of instant publish — open
    ``http://bakery.pebbleapp.test:<port>/`` and get the project's HTML.
    """
    out = engine_server["output"]
    _seed_project(out, "bakery", html="<h1>Bakery is live</h1>")
    _post(engine_server["base"], "/api/publish/instant", {"slug": "bakery"})

    # Request "/" but with the published subdomain in the Host header.
    # _get's host_header param spoofs it; the engine reads it from
    # self.headers["Host"] and routes via _route_subdomain_get.
    port = engine_server["port"]
    status, data, headers = _get(
        engine_server["base"], "/",
        host_header=f"bakery.pebbleapp.test:{port}",
    )
    assert status == 200
    body = data.decode("utf-8") if isinstance(data, bytes) else (
        data if isinstance(data, str) else json.dumps(data)
    )
    assert "Bakery is live" in body
    # Public mode must NOT inject the visual-edit bridge.
    assert "pebble-bridge" not in body
    # Public cache header (not no-store).
    assert "public" in headers.get("Cache-Control", "").lower()


def test_subdomain_host_does_not_intercept_api_routes(engine_server):
    """Even on a subdomain, /api/* must keep working (forms, analytics)."""
    out = engine_server["output"]
    _seed_project(out, "bakery")
    _post(engine_server["base"], "/api/publish/instant", {"slug": "bakery"})

    port = engine_server["port"]
    status, body, _ = _get(
        engine_server["base"], "/api/health",
        host_header=f"bakery.pebbleapp.test:{port}",
    )
    assert status == 200
    assert isinstance(body, dict) and "model" in body  # /api/health response shape


def test_workspace_host_still_shows_bridge(engine_server):
    """Workspace-iframe path (Host = engine, /preview/<slug>) keeps the bridge."""
    out = engine_server["output"]
    _seed_project(out, "bakery", html="<h1>Iframe view</h1>")
    _post(engine_server["base"], "/api/publish/instant", {"slug": "bakery"})

    status, data, headers = _get(engine_server["base"], "/preview/bakery/")
    assert status == 200
    body = data.decode("utf-8") if isinstance(data, bytes) else (
        data if isinstance(data, str) else json.dumps(data)
    )
    assert "Iframe view" in body
    # Workspace iframe = bridge injected.
    assert "pebble-bridge" in body
    # No-store on the workspace path so edits are visible immediately.
    cache = headers.get("Cache-Control", "").lower()
    assert "no-store" in cache or "no-cache" in cache
