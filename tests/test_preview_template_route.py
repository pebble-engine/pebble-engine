"""HTTP-level tests for /preview-template/<id>/... — the engine route
that serves pre-built static previews of cinematic_* templates from
pebble/templates/<id>/out/."""
from __future__ import annotations

import socket
import threading
import time
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import pebble_engine


REPO_ROOT = Path(__file__).resolve().parents[1]


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _get(base: str, path: str) -> tuple[int, bytes, dict[str, str]]:
    try:
        with urllib.request.urlopen(f"{base}{path}", timeout=5) as resp:
            return resp.status, resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


@pytest.fixture(scope="module")
def engine_base():
    port = _find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), pebble_engine.PebbleHandler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()


def test_preview_template_serves_index_when_path_is_directory(engine_base):
    """Bare /preview-template/<id>/ resolves to out/index.html."""
    out_index = REPO_ROOT / "pebble/templates/cinematic_hero/out/index.html"
    if not out_index.is_file():
        pytest.skip("Run `python -m pebble.templates.export cinematic_hero` first")
    status, body, headers = _get(engine_base, "/preview-template/cinematic_hero/")
    assert status == 200
    assert b"<html" in body.lower() or b"<!doctype" in body.lower()
    assert headers.get("Content-Type", "").startswith("text/html")


def test_preview_template_404s_unknown_template(engine_base):
    status, body, _ = _get(engine_base, "/preview-template/no_such_template/")
    assert status == 404


def test_preview_template_400s_invalid_template_id(engine_base):
    """Template IDs are lowercased alphanumeric+underscore. Reject anything else."""
    status, _, _ = _get(engine_base, "/preview-template/Bad-Name!/")
    assert status == 400


def test_preview_template_rejects_path_traversal(engine_base):
    """Walking out of the template dir must not leak filesystem contents."""
    status, _, _ = _get(engine_base, "/preview-template/cinematic_hero/../../../README.md")
    # Either resolved-out-of-bounds (403) or normalised by HTTP and 404. Both safe.
    assert status in (400, 403, 404)


def test_preview_template_404s_when_out_dir_missing(engine_base, monkeypatch, tmp_path):
    """If a template exists but hasn't been exported yet, return 404 with a hint."""
    # Use a sentinel template that's in the registry but whose out/ we KNOW doesn't exist.
    # cinematic_landscaper is a good candidate IF it hasn't been exported yet — check first.
    skin_out = REPO_ROOT / "pebble/templates/cinematic_landscaper/out"
    if skin_out.is_dir():
        pytest.skip("cinematic_landscaper has been exported; this test needs an unexported template")
    status, body, _ = _get(engine_base, "/preview-template/cinematic_landscaper/")
    assert status == 404
    # Optional: verify the operator-facing hint mentions the export command
    body_text = body.decode("utf-8", errors="replace")
    assert "export" in body_text.lower()
