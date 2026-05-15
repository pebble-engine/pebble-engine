"""End-to-end HTTP integration tests against a real Pebble engine instance.

Boots the engine on a random port in a background thread, fires real HTTP
requests, asserts on the responses. This catches issues the unit tests
can't: route wiring, request body parsing, response shape under the
wire, and the visual-edit bridge injection into HTML responses.

Heavy by smoke-test standards (each test starts/stops an HTTP server)
but cheap by full-build standards (no LLM calls; the build/generate
routes aren't exercised here, only the cheap ones).
"""
from __future__ import annotations

import json
import socket
import threading
import time
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import pebble_engine
import pebble.history as history_mod


def _find_free_port() -> int:
    """Ask the OS for an ephemeral port. Race-free enough for tests."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def engine_server(tmp_path, monkeypatch):
    """Spin up the real PebbleHandler bound to a tmp output dir on a
    random port. Yields ``base_url`` ending in no slash. Tears down on
    exit."""
    # Redirect all output paths to tmp so we don't touch the real tree.
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.setattr(history_mod, "OUTPUT_DIR", out)

    port = _find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), pebble_engine.PebbleHandler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    # Brief warm-up so the listener is fully ready
    time.sleep(0.1)
    try:
        yield {
            "base":   f"http://127.0.0.1:{port}",
            "output": out,
            "server": server,
        }
    finally:
        server.shutdown()
        server.server_close()


def _get(base: str, path: str) -> tuple[int, dict | str]:
    try:
        with urllib.request.urlopen(f"{base}{path}", timeout=5) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try: return resp.status, json.loads(body)
            except Exception: return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(body)
        except Exception: return e.code, body


def _post(base: str, path: str, body: dict | None = None) -> tuple[int, dict | str]:
    data = json.dumps(body or {}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body_text = resp.read().decode("utf-8", errors="replace")
            try: return resp.status, json.loads(body_text)
            except Exception: return resp.status, body_text
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(body_text)
        except Exception: return e.code, body_text


def _seed_project(output: Path, slug: str, files: dict[str, str], brief: dict | None = None) -> Path:
    project = output / slug
    project.mkdir()
    site = project / "site"
    site.mkdir()
    for rel, content in files.items():
        p = site / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    if brief is not None:
        (project / "brief.json").write_text(json.dumps(brief), encoding="utf-8")
    return project


# ---- /api/health --------------------------------------------------------

def test_health_returns_engine_status(engine_server):
    status, body = _get(engine_server["base"], "/api/health")
    assert status == 200
    assert isinstance(body, dict)
    assert "engine_ok" in body
    assert "llm_ready" in body


# ---- /api/projects ------------------------------------------------------

def test_list_projects_empty_initially(engine_server):
    status, body = _get(engine_server["base"], "/api/projects")
    assert status == 200
    assert body["count"] == 0


def test_list_projects_returns_seeded_project(engine_server):
    _seed_project(
        engine_server["output"],
        "good-co",
        {"app/page.tsx": "x", "package.json": "y"},
        brief={"business_name": "Good Co", "business_type": "bakery"},
    )
    status, body = _get(engine_server["base"], "/api/projects")
    assert status == 200
    assert body["count"] == 1
    p = body["projects"][0]
    assert p["slug"] == "good-co"
    assert p["business_name"] == "Good Co"
    assert p["business_type"] == "bakery"
    assert p["file_count"] == 2
    assert p["starred"] is False


# ---- /api/projects/<slug>/star ------------------------------------------

def test_star_toggle_flips_state(engine_server):
    _seed_project(engine_server["output"], "good-co", {"app/page.tsx": "x"})
    status, body = _post(engine_server["base"], "/api/projects/good-co/star")
    assert status == 200
    assert body["starred"] is True
    status, body = _post(engine_server["base"], "/api/projects/good-co/star")
    assert body["starred"] is False


def test_star_404_for_unknown_project(engine_server):
    status, body = _post(engine_server["base"], "/api/projects/nope/star")
    assert status == 404


# ---- /api/projects/<slug>/history ---------------------------------------

def test_history_empty_initially(engine_server):
    _seed_project(engine_server["output"], "good-co", {"app/page.tsx": "x"})
    status, body = _get(engine_server["base"], "/api/projects/good-co/history")
    assert status == 200
    assert body["slug"] == "good-co"
    assert body["count"] == 0
    assert body["snapshots"] == []


def test_history_404_for_unknown_project(engine_server):
    status, body = _get(engine_server["base"], "/api/projects/nope/history")
    assert status == 404


# ---- /api/rollback ------------------------------------------------------

def test_rollback_round_trip(engine_server):
    out = engine_server["output"]
    base = engine_server["base"]
    _seed_project(out, "good-co", {"app/page.tsx": "ORIGINAL"})
    # Snapshot via direct call (simulating what /api/generate would do)
    history_mod.snapshot_site("good-co", reason="generate")
    time.sleep(1.05)
    # Mutate
    (out / "good-co" / "site" / "app" / "page.tsx").write_text("MUTATED", encoding="utf-8")

    # Get history → pick snapshot → rollback
    status, hist = _get(base, "/api/projects/good-co/history")
    assert status == 200
    snapshot_id = hist["snapshots"][0]["snapshot_id"]
    status, body = _post(base, "/api/rollback", {"slug": "good-co", "snapshot_id": snapshot_id})
    assert status == 200
    assert body["files_restored"] >= 1
    assert (out / "good-co" / "site" / "app" / "page.tsx").read_text() == "ORIGINAL"


# ---- /api/refine (deterministic only — LLM-backed needs real key) -------

def test_refine_simpler_is_free_and_changes_files(engine_server):
    out = engine_server["output"]
    _seed_project(out, "good-co", {"app/globals.css": "body { color: #FF1234; }"})
    status, body = _post(engine_server["base"], "/api/refine", {
        "slug": "good-co",
        "refinement_id": "simpler",
    })
    assert status == 200
    assert body["billable"] is False
    assert body["kind"] == "deterministic"
    assert body["snapshot_id"]  # snapshot created
    assert "#FF1234" not in (out / "good-co" / "site" / "app" / "globals.css").read_text()


def test_refine_rejects_unknown_refinement_id(engine_server):
    _seed_project(engine_server["output"], "good-co", {"app/globals.css": "body {}"})
    status, body = _post(engine_server["base"], "/api/refine", {
        "slug": "good-co",
        "refinement_id": "explode-the-universe",
    })
    assert status == 400


def test_refine_404_for_missing_site(engine_server):
    status, body = _post(engine_server["base"], "/api/refine", {
        "slug": "nope",
        "refinement_id": "simpler",
    })
    assert status == 404


# ---- /api/visual-edit ---------------------------------------------------

def test_visual_edit_text_op(engine_server):
    out = engine_server["output"]
    _seed_project(out, "good-co", {
        "app/page.tsx": (
            'export default function P() {\n'
            '  return <main><h1>Welcome to my bakery</h1></main>;\n'
            '}'
        ),
    })
    status, body = _post(engine_server["base"], "/api/visual-edit", {
        "slug": "good-co",
        "op": "text",
        "original_text": "Welcome to my bakery",
        "new_text": "Hi, I'm a baker",
    })
    assert status == 200
    assert body["billable"] is False
    content = (out / "good-co" / "site" / "app" / "page.tsx").read_text()
    assert "Hi, I'm a baker" in content


def test_visual_edit_rejects_bad_op(engine_server):
    _seed_project(engine_server["output"], "good-co", {"app/page.tsx": "x"})
    status, body = _post(engine_server["base"], "/api/visual-edit", {
        "slug": "good-co",
        "op": "drop-tables",
    })
    assert status == 400


# ---- /preview/<slug>/ bridge injection ----------------------------------

def test_preview_html_gets_bridge_script_injected(engine_server):
    """The visual-edit bridge must auto-inject into any HTML served from
    /preview/<slug>/* so the click-to-edit flow works without the
    generated site knowing about it."""
    _seed_project(engine_server["output"], "good-co", {
        "index.html": "<!doctype html><html><body><h1>Hi</h1></body></html>",
    })
    status, body = _get(engine_server["base"], "/preview/good-co/index.html")
    assert status == 200
    assert isinstance(body, str)
    assert '<script id="pebble-bridge">' in body
    # Bridge must run BEFORE </body> close
    assert body.index('<script id="pebble-bridge">') < body.index("</body>")
    # And carry the click handler
    assert "pebble-select" in body


def test_preview_non_html_files_pass_through(engine_server):
    """CSS, JS, etc. served from /preview/ should NOT get the bridge —
    injection is only for HTML."""
    _seed_project(engine_server["output"], "good-co", {
        "app/globals.css": "body { color: red; }",
    })
    status, body = _get(engine_server["base"], "/preview/good-co/app/globals.css")
    assert status == 200
    assert "pebble-bridge" not in body
