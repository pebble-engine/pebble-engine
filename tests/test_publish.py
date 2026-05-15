"""Unit + HTTP integration tests for the publish flow.

The Cloudflare API path requires real creds + the optional ``blake3``
package — we don't exercise it here. The ZIP fallback is the testable
shape for now.
"""
from __future__ import annotations

import io
import json
import os
import socket
import threading
import time
import urllib.error
import urllib.request
import zipfile
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import pebble_engine
import pebble.history as history_mod
import pebble.publish as publish_mod


# ---- helpers reused from the e2e style ----------------------------------

def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def engine_server(tmp_path, monkeypatch):
    """Spin up the real PebbleHandler bound to a tmp output dir."""
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.setattr(history_mod, "OUTPUT_DIR", out)
    # Belt-and-suspenders: ensure cloudflare envs aren't accidentally
    # set from the developer's actual shell.
    monkeypatch.delenv("CLOUDFLARE_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)

    port = _find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), pebble_engine.PebbleHandler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    try:
        yield {"base": f"http://127.0.0.1:{port}", "output": out, "server": server}
    finally:
        server.shutdown()
        server.server_close()


def _post(base: str, path: str, body: dict | None = None) -> tuple[int, dict | str]:
    data = json.dumps(body or {}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body_text = resp.read().decode("utf-8", errors="replace")
            try: return resp.status, json.loads(body_text)
            except Exception: return resp.status, body_text
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(body_text)
        except Exception: return e.code, body_text


def _get(base: str, path: str) -> tuple[int, dict | str, dict]:
    try:
        with urllib.request.urlopen(f"{base}{path}", timeout=10) as resp:
            data = resp.read()
            headers = dict(resp.headers.items())
            try: return resp.status, json.loads(data.decode("utf-8")), headers
            except Exception: return resp.status, data, headers
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(body_text), dict(e.headers.items() if e.headers else {})
        except Exception: return e.code, body_text, {}


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


# ---- pebble.publish unit tests ------------------------------------------

def test_package_zip_includes_site_files(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    _seed_project(tmp_path, "good-co", {
        "app/page.tsx": "<p>Hi</p>",
        "package.json": '{"name":"good-co"}',
    })
    zip_path, files, byts = publish_mod.package_zip("good-co")
    assert zip_path.exists()
    assert files == 2
    assert byts > 0
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
    assert "app/page.tsx" in names
    assert "package.json" in names


def test_package_zip_excludes_node_modules_and_secrets(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    _seed_project(tmp_path, "good-co", {
        "package.json":               '{"name":"good-co"}',
        "node_modules/react/index.js": "//npm",
        ".next/cache/foo.bin":         "binary",
        ".env":                        "SECRET=value",
        ".pebble-ids.json":            "{}",
    })
    zip_path, files, byts = publish_mod.package_zip("good-co")
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
    assert "package.json" in names
    assert all("node_modules" not in n for n in names)
    assert all(".next" not in n for n in names)
    assert ".env" not in names
    assert ".pebble-ids.json" not in names


def test_package_zip_raises_when_no_site(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    (tmp_path / "ghost").mkdir()
    with pytest.raises(publish_mod.PublishError):
        publish_mod.package_zip("ghost")


def test_package_zip_raises_when_only_excluded_files(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    _seed_project(tmp_path, "only-secrets", {
        ".env":                       "x",
        "node_modules/foo/index.js":  "y",
    })
    with pytest.raises(publish_mod.PublishError):
        publish_mod.package_zip("only-secrets")


def test_slug_to_project_name_normalizes():
    assert publish_mod.slug_to_project_name("Good Co!") == "pebble-good-co"
    assert publish_mod.slug_to_project_name("---weird---") == "pebble-weird"
    assert publish_mod.slug_to_project_name("") == "pebble-site"
    name = publish_mod.slug_to_project_name("x" * 200)
    assert len(name) <= 58
    assert name.startswith("pebble-")


def test_cloudflare_configured_reflects_env(monkeypatch):
    monkeypatch.delenv("CLOUDFLARE_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)
    assert publish_mod.cloudflare_configured() is False
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "acct123")
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok456")
    assert publish_mod.cloudflare_configured() is True


def test_cloudflare_setup_checklist_paste_ready():
    md = publish_mod.cloudflare_setup_checklist()
    # The user should see actionable steps with the env var names.
    assert "CLOUDFLARE_ACCOUNT_ID" in md
    assert "CLOUDFLARE_API_TOKEN" in md
    assert "https://dash.cloudflare.com" in md


def test_state_write_and_read_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    _seed_project(tmp_path, "good-co", {"package.json": "{}"})
    result = publish_mod.PublishResult(
        slug="good-co",
        kind="zip",
        url="/dist/good-co/dist.zip",
        deployed_at="2026-05-14T22:00:00Z",
        bytes_published=42,
        files_published=1,
    )
    publish_mod.write_publish_state("good-co", result)
    state = publish_mod.read_publish_state("good-co")
    assert state["kind"] == "zip"
    assert state["url"].endswith("/dist.zip")
    history = publish_mod.read_publish_history("good-co")
    assert len(history) == 1


# ---- HTTP integration ---------------------------------------------------

def test_publish_returns_404_for_missing_project(engine_server):
    status, body = _post(engine_server["base"], "/api/publish", {"slug": "nope"})
    assert status == 404


def test_publish_requires_slug(engine_server):
    status, body = _post(engine_server["base"], "/api/publish", {})
    assert status == 400


def test_publish_rejects_unknown_dest(engine_server):
    _seed_project(engine_server["output"], "good-co", {"app/page.tsx": "x"})
    status, body = _post(engine_server["base"], "/api/publish", {"slug": "good-co", "dest": "ftp"})
    assert status == 400


def test_publish_zip_round_trip(engine_server):
    out = engine_server["output"]
    _seed_project(out, "good-co", {
        "app/page.tsx": "<p>Hi</p>",
        "package.json": '{"name":"good-co"}',
    })

    # Publish (defaults to auto → zip because CF not configured)
    status, body = _post(engine_server["base"], "/api/publish", {"slug": "good-co"})
    assert status == 200, body
    assert body["kind"] == "zip"
    assert body["url"] == "/dist/good-co/dist.zip"
    assert body["files_published"] == 2
    assert body["snapshot_id"]  # snapshot was created
    assert body["cloudflare_setup_md"]  # checklist is included on zip fallback
    assert body["note"]                  # honest note about why it's a zip

    # The zip file exists on disk
    zip_path = out / "good-co" / "dist.zip"
    assert zip_path.exists()

    # Download via /dist/<slug>/dist.zip
    status, data, headers = _get(engine_server["base"], "/dist/good-co/dist.zip")
    assert status == 200
    assert headers.get("Content-Type") == "application/zip"
    assert b"PK" == data[:2]  # zip magic number
    # Verify it's a valid zip with our files
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = set(zf.namelist())
    assert "app/page.tsx" in names
    assert "package.json" in names


def test_publish_state_endpoint_returns_current_after_publish(engine_server):
    _seed_project(engine_server["output"], "good-co", {"app/page.tsx": "x"})
    _, body = _post(engine_server["base"], "/api/publish", {"slug": "good-co"})
    assert body["kind"] == "zip"
    status, state, _ = _get(engine_server["base"], "/api/projects/good-co/publish")
    assert status == 200
    assert state["slug"] == "good-co"
    assert state["current"]["kind"] == "zip"
    assert len(state["history"]) == 1


def test_publish_state_404_for_missing_project(engine_server):
    status, body, _ = _get(engine_server["base"], "/api/projects/nope/publish")
    assert status == 404


def test_dist_404_when_not_published(engine_server):
    _seed_project(engine_server["output"], "good-co", {"app/page.tsx": "x"})
    status, body, _ = _get(engine_server["base"], "/dist/good-co/dist.zip")
    assert status == 404


def test_dist_rejects_path_traversal(engine_server):
    status, body, _ = _get(engine_server["base"], "/dist/..%2Fother/dist.zip")
    # urllib normalizes URL-encoded segments differently; the explicit
    # check via path parts rejects empty / dot paths regardless.
    assert status == 404


def test_publish_force_cloudflare_returns_400_without_keys(engine_server):
    _seed_project(engine_server["output"], "good-co", {"app/page.tsx": "x"})
    status, body = _post(engine_server["base"], "/api/publish",
                         {"slug": "good-co", "dest": "cloudflare"})
    assert status == 400
    assert "cloudflare_setup_md" in body


def test_publish_snapshots_site_before_zipping(engine_server):
    out = engine_server["output"]
    _seed_project(out, "good-co", {"app/page.tsx": "ORIGINAL"})
    _, body = _post(engine_server["base"], "/api/publish", {"slug": "good-co"})
    assert body["snapshot_id"]
    snap_dir = out / "good-co" / "history" / body["snapshot_id"]
    assert snap_dir.exists()
    # Snapshot captured the page.tsx file
    assert (snap_dir / "site" / "app" / "page.tsx").read_text() == "ORIGINAL"


def test_dashboard_summary_includes_publish_after_publishing(engine_server):
    out = engine_server["output"]
    _seed_project(out, "good-co", {"app/page.tsx": "x"},
                  brief={"business_name": "Good Co"})
    _post(engine_server["base"], "/api/publish", {"slug": "good-co"})
    status, body, _ = _get(engine_server["base"], "/api/projects")
    assert status == 200
    assert body["count"] == 1
    proj = body["projects"][0]
    assert proj["publish"] is not None
    assert proj["publish"]["kind"] == "zip"
    assert proj["publish"]["url"].endswith("/dist.zip")
