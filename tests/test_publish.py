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
import pebble.security as security_mod
import pebble.server.publish as publish_server
import pebble.server.projects as projects_server


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
    monkeypatch.setattr(security_mod, "_output_dir", lambda: out)
    # The 2026-05-15 evening security pass added require_project_owner
    # to publish + project-mutation endpoints. These pre-existing tests
    # exercise the JSON contract through the real HTTP server WITHOUT
    # session cookies; bypass the gate here so they keep working. Auth
    # behavior is covered separately in test_security.py +
    # test_http_e2e.py.
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


def _get(base: str, path: str, cookie: str | None = None) -> tuple[int, dict | str, dict]:
    # Phase 58e (2026-05-22) — added optional cookie for the /api/projects
    # dashboard-listing tests that now require auth.
    req = urllib.request.Request(f"{base}{path}",
                                  headers={"Cookie": cookie} if cookie else {})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            headers = dict(resp.headers.items())
            try: return resp.status, json.loads(data.decode("utf-8")), headers
            except Exception: return resp.status, data, headers
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(body_text), dict(e.headers.items() if e.headers else {})
        except Exception: return e.code, body_text, {}


def _signup_and_get_cookie(base: str, email: str = "u@example.com",
                           password: str = "valid-password") -> str:
    """Sign up via the legacy auth endpoint and extract the session cookie.

    Used for tests that need to hit signed-in-only endpoints like the
    dashboard listing (/api/projects) without needing a real Supabase
    instance.
    """
    data = json.dumps({"email": email, "password": password}).encode("utf-8")
    req = urllib.request.Request(f"{base}/api/auth/signup", data=data,
                                  headers={"Content-Type": "application/json"},
                                  method="POST")
    with urllib.request.urlopen(req, timeout=5) as resp:
        sc = resp.headers.get("Set-Cookie") or ""
    # First semicolon-separated chunk is the name=value pair we want.
    return sc.split(";", 1)[0] if sc else ""


def _signup_and_stamp_owner(base: str, output: Path, slug: str) -> str:
    cookie = _signup_and_get_cookie(base)
    req = urllib.request.Request(f"{base}/api/auth/me", headers={"Cookie": cookie})
    with urllib.request.urlopen(req, timeout=5) as resp:
        uid = json.loads(resp.read().decode("utf-8"))["user"]["id"]
    brief_path = output / slug / "brief.json"
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    brief["_user_id"] = uid
    brief_path.write_text(json.dumps(brief), encoding="utf-8")
    return cookie


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
    cookie = _signup_and_stamp_owner(engine_server["base"], out, "good-co")
    status, body, _ = _get(engine_server["base"], "/api/projects", cookie=cookie)
    assert status == 200
    assert body["count"] == 1
    proj = body["projects"][0]
    assert proj["publish"] is not None
    assert proj["publish"]["kind"] == "zip"
    assert proj["publish"]["url"].endswith("/dist.zip")


# ---- Free-plan publish limit ------------------------------------------------

def _seed_published(out: Path, slug: str, user_id: str = "test-user") -> None:
    """Create a project that is already published (has a publish.json)."""
    site = out / slug / "site" / "app"
    site.mkdir(parents=True)
    (site / "page.tsx").write_text("x", encoding="utf-8")
    (out / slug / "brief.json").write_text(
        json.dumps({"_user_id": user_id, "business_name": slug}), encoding="utf-8"
    )
    (out / slug / "publish.json").write_text(
        json.dumps({"kind": "zip", "url": f"/dist/{slug}/dist.zip",
                    "deployed_at": "2026-01-01T00:00:00+00:00"}), encoding="utf-8"
    )


def test_free_user_blocked_at_publish_limit(engine_server):
    out = engine_server["output"]
    # Two already-published sites for the same user.
    _seed_published(out, "site-one", user_id="test-user")
    _seed_published(out, "site-two", user_id="test-user")
    # Third site — not yet published.
    _seed_project(out, "site-three", {"app/page.tsx": "x"},
                  brief={"_user_id": "test-user", "business_name": "Three"})
    status, body = _post(engine_server["base"], "/api/publish", {"slug": "site-three"})
    assert status == 402
    assert "upgrade" in body.get("error", "").lower() or "upgrade_url" in body


def test_free_user_can_republish_existing_published_site(engine_server):
    out = engine_server["output"]
    # Two already-published sites.
    _seed_published(out, "site-one", user_id="test-user")
    _seed_published(out, "site-two", user_id="test-user")
    # Re-publishing site-two (already counted, so still within limit).
    status, _body = _post(engine_server["base"], "/api/publish", {"slug": "site-two"})
    assert status == 200  # allowed — not a new site


def test_subscriber_can_publish_beyond_free_limit(engine_server):
    out = engine_server["output"]
    # Two already-published sites.
    _seed_published(out, "site-one", user_id="test-user")
    _seed_published(out, "site-two", user_id="test-user")
    # Write an active subscription sentinel for test-user.
    sub_dir = out / ".users" / "test-user"
    sub_dir.mkdir(parents=True)
    (sub_dir / "subscription.json").write_text(
        json.dumps({"status": "active", "plan": "starter"}), encoding="utf-8"
    )
    # Third site — should be allowed for subscriber.
    _seed_project(out, "site-three", {"app/page.tsx": "x"},
                  brief={"_user_id": "test-user", "business_name": "Three"})
    status, _body = _post(engine_server["base"], "/api/publish", {"slug": "site-three"})
    assert status == 200


# ---- Intent sentinel tests (TOCTOU fix) ----------------------------------------

def test_publish_intent_counts_toward_limit(tmp_path, monkeypatch):
    """A .publish_intent file for another slug must block a third publish."""
    import pebble.server.publish as srv
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)

    _seed_published(tmp_path, "site-one", user_id="u1")
    # Simulate an in-flight publish for site-two (intent written, upload pending).
    (tmp_path / "site-two").mkdir(parents=True)
    (tmp_path / "site-two" / "brief.json").write_text(
        json.dumps({"_user_id": "u1", "business_name": "Two"}), encoding="utf-8"
    )
    (tmp_path / "site-two" / ".publish_intent").touch()

    # Now site-three wants to publish — should be blocked at limit=2.
    count = srv._count_published_sites("u1", exclude_slug="site-three")
    assert count == 2


def test_publish_intent_cleared_after_successful_zip(engine_server):
    """After a successful ZIP publish, .publish_intent must not remain."""
    out = engine_server["output"]
    _seed_project(out, "my-site", {"app/page.tsx": "x"},
                  brief={"_user_id": "test-user", "business_name": "My"})
    status, _ = _post(engine_server["base"], "/api/publish", {"slug": "my-site"})
    assert status == 200
    assert not (out / "my-site" / ".publish_intent").exists()


def test_concurrent_free_tier_publishes_cant_both_succeed(engine_server):
    """Two simultaneous publish requests for different slugs by the same free
    user — when already at limit-1 — must result in exactly one 200 and one 402.
    """
    out = engine_server["output"]
    _seed_published(out, "site-one", user_id="test-user")
    _seed_project(out, "site-two", {"app/page.tsx": "x"},
                  brief={"_user_id": "test-user", "business_name": "Two"})
    _seed_project(out, "site-three", {"app/page.tsx": "x"},
                  brief={"_user_id": "test-user", "business_name": "Three"})

    results: list[int] = []
    lock = threading.Lock()

    def do_publish(slug: str) -> None:
        status, _ = _post(engine_server["base"], "/api/publish", {"slug": slug})
        with lock:
            results.append(status)

    t2 = threading.Thread(target=do_publish, args=("site-two",))
    t3 = threading.Thread(target=do_publish, args=("site-three",))
    t2.start(); t3.start()
    t2.join(); t3.join()

    results.sort()
    assert results == [200, 402], (
        f"Expected one 200 and one 402 for concurrent free-tier publishes, got {results}"
    )
