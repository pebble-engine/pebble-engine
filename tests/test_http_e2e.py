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
import pebble.security as security_mod
import pebble.server.projects as projects_server
import pebble.server.refine as refine_server
import pebble.server.visual_edit as visual_edit_server
import pebble.server.publish as publish_server
import pebble.server.domain as domain_server
import pebble.server.blocks as blocks_server


def _find_free_port() -> int:
    """Ask the OS for an ephemeral port. Race-free enough for tests."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(autouse=True)
def _scrub_vendor_env(monkeypatch):
    """Force every test in this module onto the dev-default email
    sender + unconfigured Cloudflare. .env now ships with real keys
    for both Resend and Cloudflare; without this scrub, get_sender()
    returns ResendSender and the welcome / reset email tests stop
    seeing files in the outbox because the prod sender raises before
    the FileSender audit-copy gets written. Same pattern as the
    Cloudflare autouse scrub commit a9bfd7d added to test_domain.py."""
    for var in (
        "PEBBLE_EMAIL_PROVIDER",
        "PEBBLE_EMAIL_RESEND_KEY",
        "RESEND_API_KEY",
        "PEBBLE_EMAIL_POSTMARK_TOKEN",
        "PEBBLE_EMAIL_SENDGRID_KEY",
        "CLOUDFLARE_ACCOUNT_ID",
        "CLOUDFLARE_API_TOKEN",
    ):
        monkeypatch.delenv(var, raising=False)


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
    monkeypatch.setattr(security_mod, "_output_dir", lambda: out)

    # The 2026-05-15 evening NLM pass added require_project_owner to
    # publish + refine + visual-edit + rollback + history + star + delete.
    # Pre-existing tests in this file exercise the JSON contract through
    # the real HTTP server WITHOUT cookies; bypass the auth check so they
    # keep working. (Auth coverage lives in test_security.py +
    # test_blocks.py.)
    def bypass(handler, slug):
        if not security_mod.is_valid_slug(slug):
            handler._json(400, {"error": "invalid project slug"})
            return None
        if not (out / slug).exists():
            handler._json(404, {"error": f"project not found: {slug}"})
            return None
        return "test-user"
    for mod in (projects_server, refine_server, visual_edit_server,
                publish_server, domain_server, blocks_server):
        monkeypatch.setattr(mod, "require_project_owner", bypass)

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

def test_health_returns_engine_status(engine_server, monkeypatch):
    monkeypatch.delenv("VERCEL_TOKEN", raising=False)
    status, body = _get(engine_server["base"], "/api/health")
    assert status == 200
    assert isinstance(body, dict)
    assert "engine_ok" in body
    assert "llm_ready" in body
    assert body.get("preview_backend") == "local"
    assert body.get("vercel_configured") is False
    assert body.get("preview_prod_ready") is False


def test_health_reports_vercel_preview_ready(engine_server, monkeypatch):
    monkeypatch.setenv("PEBBLE_PREVIEW_BACKEND", "vercel")
    monkeypatch.setenv("VERCEL_TOKEN", "tok")
    status, body = _get(engine_server["base"], "/api/health")
    assert status == 200
    assert body["preview_backend"] == "vercel"
    assert body["vercel_configured"] is True
    assert body["preview_prod_ready"] is True


# ---- /api/community ---------------------------------------------------

def test_community_feed_is_public(engine_server):
    status, body = _get(engine_server["base"], "/api/community/feed")
    assert status == 200
    assert isinstance(body, dict)
    assert "events" in body
    assert "count" in body
    assert isinstance(body["events"], list)


def test_community_stats_is_public(engine_server):
    status, body = _get(engine_server["base"], "/api/community/stats")
    assert status == 200
    assert isinstance(body, dict)
    assert "stats" in body or body.get("fallback") is True


def test_launchpad_showcase_is_public(engine_server):
    status, body = _get(engine_server["base"], "/api/launchpad/showcase")
    assert status == 200
    assert isinstance(body, dict)
    assert "entries" in body
    assert "count" in body
    assert isinstance(body["entries"], list)


# ---- /api/projects ------------------------------------------------------

def test_list_projects_401_when_signed_out(engine_server):
    """Phase 58e regression pin (2026-05-22) — /api/projects used to fall
    through to "show all projects" for anon callers, which leaked every
    user's slug + business_name + inbox counts. Must 401 instead."""
    status, _ = _get(engine_server["base"], "/api/projects")
    assert status == 401


def test_list_projects_empty_initially(engine_server):
    cookie = _signin(engine_server["base"], "u@example.com", "valid-password")
    status, body = _get_with_cookie(engine_server["base"], "/api/projects", cookie=cookie)
    assert status == 200
    assert body["count"] == 0


def test_list_projects_returns_seeded_project(engine_server):
    base = engine_server["base"]
    cookie = _signin(base, "u@example.com", "valid-password")
    # Resolve the caller's id so the seeded project is OWNED by them — a
    # signed-in user only sees their own projects (unclaimed are excluded).
    req_me = urllib.request.Request(f"{base}/api/auth/me", headers={"Cookie": cookie})
    with urllib.request.urlopen(req_me, timeout=5) as r:
        uid = json.loads(r.read().decode("utf-8"))["user"]["id"]
    _seed_project(
        engine_server["output"],
        "good-co",
        {"app/page.tsx": "x", "package.json": "y"},
        brief={"business_name": "Good Co", "business_type": "bakery", "_user_id": uid},
    )
    status, body = _get_with_cookie(engine_server["base"], "/api/projects", cookie=cookie)
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


# ---- /api/visual-edit — surgical (pebble_id manifest) path --------------

def _seed_with_manifest(out: Path, slug: str, files: dict[str, str], manifest: dict) -> Path:
    """Seed a project AND drop a .pebble-ids.json so the surgical path
    activates without running the full /api/generate pipeline."""
    project = _seed_project(out, slug, files)
    site = project / "site"
    (site / ".pebble-ids.json").write_text(json.dumps(manifest), encoding="utf-8")
    return project


def test_visual_edit_text_surgical_uses_manifest(engine_server):
    out = engine_server["output"]
    _seed_with_manifest(out, "good-co", {
        "index.html": '<h1 data-pebble-id="pb-aaa111">Welcome</h1><p>Other</p>',
    }, {
        "pb-aaa111": {"file": "index.html", "tag": "h1", "original_text": "Welcome"},
    })
    status, body = _post(engine_server["base"], "/api/visual-edit", {
        "slug":          "good-co",
        "op":            "text",
        "pebble_id":     "pb-aaa111",
        "original_text": "Welcome",
        "new_text":      "Hello world",
    })
    assert status == 200
    assert body["billable"] is False
    assert body["used_manifest"] is True
    content = (out / "good-co" / "site" / "index.html").read_text(encoding="utf-8")
    assert ">Hello world</h1>" in content
    assert "<p>Other</p>" in content   # untouched


def test_visual_edit_color_surgical_upserts_html_style(engine_server):
    out = engine_server["output"]
    _seed_with_manifest(out, "good-co", {
        "index.html": '<h1 data-pebble-id="pb-bbb222">Title</h1>',
    }, {
        "pb-bbb222": {"file": "index.html", "tag": "h1", "original_text": "Title"},
    })
    status, body = _post(engine_server["base"], "/api/visual-edit", {
        "slug":      "good-co",
        "op":        "color",
        "pebble_id": "pb-bbb222",
        "new_color": "#ff0000",
    })
    assert status == 200
    assert body["used_manifest"] is True
    content = (out / "good-co" / "site" / "index.html").read_text(encoding="utf-8")
    assert 'style="color: #ff0000' in content


def test_visual_edit_color_surgical_upserts_jsx_style(engine_server):
    out = engine_server["output"]
    _seed_with_manifest(out, "good-co", {
        "app/page.tsx": (
            'export default function P() {\n'
            '  return <h1 data-pebble-id="pb-ccc333">Hi</h1>;\n'
            '}'
        ),
    }, {
        "pb-ccc333": {"file": "app/page.tsx", "tag": "h1", "original_text": "Hi"},
    })
    status, body = _post(engine_server["base"], "/api/visual-edit", {
        "slug":      "good-co",
        "op":        "color",
        "pebble_id": "pb-ccc333",
        "new_color": "#00aa55",
    })
    assert status == 200
    content = (out / "good-co" / "site" / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "color: '#00aa55'" in content


def test_visual_edit_font_size_surgical_uses_new_font_size(engine_server):
    out = engine_server["output"]
    _seed_with_manifest(out, "good-co", {
        "index.html": '<h1 data-pebble-id="pb-ddd444">Big</h1>',
    }, {
        "pb-ddd444": {"file": "index.html", "tag": "h1", "original_text": "Big"},
    })
    status, body = _post(engine_server["base"], "/api/visual-edit", {
        "slug":          "good-co",
        "op":            "font-size",
        "pebble_id":     "pb-ddd444",
        "new_font_size": "28px",
        "delta":         0,
    })
    assert status == 200
    assert body["used_manifest"] is True
    content = (out / "good-co" / "site" / "index.html").read_text(encoding="utf-8")
    assert "font-size: 28px" in content


# ---- /api/auth/* end-to-end ---------------------------------------------

def _post_with_cookie(base: str, path: str, body: dict, cookie: str | None = None) -> tuple[int, dict | str, str | None]:
    """Like _post, but returns the Set-Cookie response header too."""
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if cookie:
        headers["Cookie"] = cookie
    req = urllib.request.Request(f"{base}{path}", data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body_text = resp.read().decode("utf-8", errors="replace")
            try: json_body = json.loads(body_text)
            except Exception: json_body = body_text
            return resp.status, json_body, resp.headers.get("Set-Cookie")
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        try: json_body = json.loads(body_text)
        except Exception: json_body = body_text
        return e.code, json_body, e.headers.get("Set-Cookie")


def _extract_cookie(set_cookie_header: str | None) -> str:
    """Pull the name=value pair out of a Set-Cookie so we can re-send it."""
    if not set_cookie_header:
        return ""
    return set_cookie_header.split(";", 1)[0].strip()


def _signin(base: str, email: str, password: str) -> str:
    """Sign up and return the session cookie."""
    _, _, sc = _post_with_cookie(base, "/api/auth/signup", {"email": email, "password": password})
    return _extract_cookie(sc)


def _get_with_cookie(base: str, path: str, cookie: str | None = None) -> tuple[int, dict | str]:
    headers = {"Cookie": cookie} if cookie else {}
    req = urllib.request.Request(f"{base}{path}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try: return resp.status, json.loads(body)
            except Exception: return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(body)
        except Exception: return e.code, body


def test_activity_feed_401_when_signed_out(engine_server):
    status, body = _get(engine_server["base"], "/api/activity")
    assert status == 401


def test_activity_feed_empty_when_no_history(engine_server):
    cookie = _signin(engine_server["base"], "u@example.com", "valid-password")
    _seed_project(engine_server["output"], "good-co", {"app/page.tsx": "x"})
    status, body = _get_with_cookie(engine_server["base"], "/api/activity", cookie=cookie)
    assert status == 200
    assert body["count"] == 0


def test_activity_feed_lists_snapshots_newest_first(engine_server):
    out = engine_server["output"]
    cookie = _signin(engine_server["base"], "u@example.com", "valid-password")
    _seed_project(out, "good-co", {"app/page.tsx": "ORIGINAL"},
                  brief={"business_name": "Good Co"})
    history_mod.snapshot_site("good-co", reason="generate", source="POST /api/generate")
    time.sleep(1.05)
    history_mod.snapshot_site("good-co", reason="refine-friendlier", source="POST /api/refine")
    status, body = _get_with_cookie(engine_server["base"], "/api/activity", cookie=cookie)
    assert status == 200
    assert body["count"] == 2
    # Newest first
    assert body["activity"][0]["reason"] == "refine-friendlier"
    assert body["activity"][1]["reason"] == "generate"
    assert body["activity"][0]["business_name"] == "Good Co"


def _wait_for_email(outbox: Path, predicate, *, timeout: float = 3.0) -> list:
    """Poll outbox until at least one .eml matches predicate, or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        files = [f for f in outbox.glob("*.eml") if predicate(f)]
        if files:
            return files
        time.sleep(0.05)
    return []


def test_signup_writes_welcome_email_to_outbox(engine_server):
    base = engine_server["base"]
    out = engine_server["output"]
    status, _body, _ = _post_with_cookie(base, "/api/auth/signup", {
        "email": "alice@example.com", "password": "valid-password",
    })
    assert status == 201
    # Welcome email is sent async — wait for the .eml to land.
    outbox = out / ".email_outbox"
    files = _wait_for_email(outbox, lambda f: "alice" in f.name)
    assert files, "welcome email never arrived in outbox"
    contents = files[0].read_text(encoding="utf-8", errors="replace")
    assert "alice@example.com" in contents
    assert "Welcome" in contents


def test_forgot_reset_round_trip(engine_server):
    """Real e2e: signup → forgot → grab token from .eml → reset → login as new password."""
    import email as _email
    import re as _re
    base = engine_server["base"]
    out = engine_server["output"]
    # 1) Signup
    _post(base, "/api/auth/signup", {"email": "user@example.com", "password": "old-pass-123"})

    # 2) Forgot — generates a reset token + writes the reset email
    status, body = _post(base, "/api/auth/forgot", {"email": "user@example.com"})
    assert status == 200
    assert body["sent"] is True

    # 3) The reset URL was written to the outbox; pull the token out.
    # Reset email is sent async — wait for it to land, then parse with
    # the modern email policy so quoted-printable soft-line-breaks don't
    # corrupt the token.
    import email.policy as _email_policy
    outbox = out / ".email_outbox"
    _wait_for_email(outbox, lambda f: "reset" in f.read_text(encoding="utf-8", errors="ignore").lower())
    reset_emails: list = []
    for f in outbox.glob("*.eml"):
        msg = _email.message_from_bytes(f.read_bytes(), policy=_email_policy.default)
        subj = str(msg.get("Subject") or "")
        if "reset" in subj.lower():
            reset_emails.append(msg)
    assert reset_emails, "no reset email landed in outbox"

    # Walk the multipart and pick text/plain (avoids HTML-attribute hits)
    body_str = ""
    for part in reset_emails[-1].walk():
        if part.get_content_type() == "text/plain":
            try:
                body_str = part.get_content()
                break
            except Exception:
                pass
    m = _re.search(r"token=([A-Za-z0-9_-]+)", body_str)
    assert m, f"no token found in reset email; body was: {body_str!r}"
    token = m.group(1)

    # 4) Reset
    status, body = _post(base, "/api/auth/reset", {"token": token, "password": "brand-new-pass-456"})
    assert status == 200
    assert body["user"]["email"] == "user@example.com"

    # 5) Old password fails; new password works
    status, _, _ = _post_with_cookie(base, "/api/auth/login", {
        "email": "user@example.com", "password": "old-pass-123",
    })
    assert status == 401
    status, _, _ = _post_with_cookie(base, "/api/auth/login", {
        "email": "user@example.com", "password": "brand-new-pass-456",
    })
    assert status == 200

    # 6) Replay of the same token is blocked
    status, body = _post(base, "/api/auth/reset", {"token": token, "password": "another-pass-789"})
    assert status == 400


def test_forgot_for_unknown_email_returns_200_but_sent_false(engine_server):
    status, body = _post(engine_server["base"], "/api/auth/forgot", {"email": "ghost@example.com"})
    assert status == 200
    # We tell the test sender what happened — production-side it's an honest "ok"
    assert body["sent"] is False


def test_reset_with_bad_token_400(engine_server):
    status, body = _post(engine_server["base"], "/api/auth/reset", {
        "token": "not-a-real-token", "password": "valid-pass-123",
    })
    assert status == 400


def test_auth_signup_login_me_logout_flow(engine_server):
    base = engine_server["base"]

    # Signup
    status, body, set_cookie = _post_with_cookie(base, "/api/auth/signup", {
        "email": "qwen@example.com", "password": "valid-password",
    })
    assert status == 201
    assert body["user"]["email"] == "qwen@example.com"
    assert "pebble_session=" in (set_cookie or "")
    cookie = _extract_cookie(set_cookie)

    # /me with the cookie returns the user
    req = urllib.request.Request(f"{base}/api/auth/me", headers={"Cookie": cookie})
    with urllib.request.urlopen(req, timeout=5) as resp:
        me = json.loads(resp.read().decode("utf-8"))
    assert me["user"]["email"] == "qwen@example.com"

    # Logout revokes
    status, _, _ = _post_with_cookie(base, "/api/auth/logout", {}, cookie=cookie)
    assert status == 200

    # /me without re-auth returns 401
    req = urllib.request.Request(f"{base}/api/auth/me", headers={"Cookie": cookie})
    try:
        urllib.request.urlopen(req, timeout=5)
        assert False, "expected 401"
    except urllib.error.HTTPError as e:
        assert e.code == 401


def test_auth_login_wrong_password_returns_401(engine_server):
    base = engine_server["base"]
    _post_with_cookie(base, "/api/auth/signup", {"email": "ravi@example.com", "password": "right-password"})
    status, body, _ = _post_with_cookie(base, "/api/auth/login", {
        "email": "ravi@example.com", "password": "wrong-password",
    })
    assert status == 401


def test_projects_list_filters_by_logged_in_user(engine_server):
    """A signed-in user sees ONLY their own projects. Unclaimed/anonymous
    projects (no _user_id) are NOT shown — the 2026-05-26 P0 fix: brand-new
    users were landing on a dashboard pre-filled with stray legacy builds."""
    base = engine_server["base"]
    out = engine_server["output"]

    # User A signs up
    _, _, cookie_a_header = _post_with_cookie(base, "/api/auth/signup", {
        "email": "owner-a@example.com", "password": "valid-password",
    })
    cookie_a = _extract_cookie(cookie_a_header)

    # User B signs up
    _, _, cookie_b_header = _post_with_cookie(base, "/api/auth/signup", {
        "email": "owner-b@example.com", "password": "valid-password",
    })
    cookie_b = _extract_cookie(cookie_b_header)

    # Resolve A's id via /me
    req_me = urllib.request.Request(f"{base}/api/auth/me", headers={"Cookie": cookie_a})
    with urllib.request.urlopen(req_me, timeout=5) as r:
        owner_a_id = json.loads(r.read().decode("utf-8"))["user"]["id"]

    # Seed three projects: anonymous, A's, B's
    _seed_project(out, "anon-site", {"index.html": "x"}, brief={"business_name": "Anon"})
    _seed_project(out, "a-site", {"index.html": "x"}, brief={"business_name": "A's", "_user_id": owner_a_id})
    _seed_project(out, "b-site", {"index.html": "x"}, brief={"business_name": "B's", "_user_id": "some-other-id"})

    # User A sees ONLY their own site — not the anonymous one, not B's.
    req = urllib.request.Request(f"{base}/api/projects", headers={"Cookie": cookie_a})
    with urllib.request.urlopen(req, timeout=5) as r:
        listing = json.loads(r.read().decode("utf-8"))
    slugs = {p["slug"] for p in listing["projects"]}
    assert "a-site" in slugs
    assert "anon-site" not in slugs   # unclaimed must NOT leak (2026-05-26 P0)
    assert "b-site" not in slugs


def test_visual_edit_falls_back_when_pebble_id_unknown(engine_server):
    """An unknown pebble_id should not error — should fall back to the
    legacy substring/heuristic path so older builds keep working."""
    out = engine_server["output"]
    _seed_with_manifest(out, "good-co", {
        "index.html": "<h1>Welcome</h1>",
    }, manifest={})
    status, body = _post(engine_server["base"], "/api/visual-edit", {
        "slug":          "good-co",
        "op":            "text",
        "pebble_id":     "pb-nonexistent",
        "original_text": "Welcome",
        "new_text":      "Hello",
    })
    assert status == 200
    assert body["used_manifest"] is False
    content = (out / "good-co" / "site" / "index.html").read_text(encoding="utf-8")
    assert "Hello" in content


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


def test_preview_vercel_backend_shows_splash_without_deployment(engine_server, monkeypatch):
    """When PEBBLE_PREVIEW_BACKEND=vercel and no .vercel-preview.json exists,
    Railway must NOT fall through to npm warmup — show the splash instead."""
    monkeypatch.setenv("PEBBLE_PREVIEW_BACKEND", "vercel")
    _seed_project(engine_server["output"], "bakery-co", {
        "site/package.json": '{"name":"bakery-co","scripts":{"dev":"next dev"}}',
        "site/app/page.tsx": "export default ()=>null",
    })
    status, body = _get(engine_server["base"], "/preview/bakery-co/")
    assert status == 200
    assert isinstance(body, str)
    assert "pebble-bridge" not in body  # splash, not proxied HTML
    assert "refresh" in body.lower() or "warming" in body.lower()


# ---- /api/migrate -------------------------------------------------------

def test_migrate_validates_url(engine_server):
    status, body = _post(engine_server["base"], "/api/migrate", {"url": ""})
    assert status == 400


def test_migrate_returns_partial_brief_for_simulated_html(engine_server, monkeypatch):
    """Patch the fetcher so the test doesn't depend on the network."""
    import pebble.migrate as migrate
    html = (
        "<!doctype html><html><head>"
        "<title>Wildflower Bakery — Brooklyn's freshest sourdough</title>"
        "<meta name='description' content='Hand-kneaded sourdough in Park Slope.'>"
        "</head><body><h1>Welcome</h1><p>Phone (212) 555-7777</p></body></html>"
    )
    monkeypatch.setattr(migrate, "_fetch_url", lambda url: ("https://example.com/", html, len(html), None))

    status, body = _post(engine_server["base"], "/api/migrate", {"url": "https://example.com"})
    assert status == 200
    assert body["ok"] is True
    assert body["brief_partial"]["business_name"] == "Wildflower Bakery"
    assert body["brief_partial"]["business_type"] == "bakery"
    assert "Park Slope" in body["brief_partial"]["extra_context"]


def test_migrate_reports_fetch_error_as_200_with_error_field(engine_server, monkeypatch):
    import pebble.migrate as migrate
    monkeypatch.setattr(migrate, "_fetch_url", lambda url: ("", "", 0, "HTTP 503"))
    status, body = _post(engine_server["base"], "/api/migrate", {"url": "https://example.com"})
    # We return 200 with error filled in so the UI can render whatever
    # partial extract we got (here: nothing) without treating it as a hard fail.
    assert status == 200
    assert body["ok"] is False
    assert body["error"] == "HTTP 503"


# ---- /api/inspire -------------------------------------------------------

def test_inspire_validates_url(engine_server):
    status, body = _post(engine_server["base"], "/api/inspire", {"url": ""})
    assert status == 400


def test_inspire_returns_palette_and_dna_for_simulated_html(engine_server, monkeypatch):
    """Patch the safe fetcher so the test doesn't need network or
    SSRF-relevant DNS resolution."""
    import pebble.inspire as inspire
    html = (
        "<!doctype html><html><head>"
        "<title>Sage Studio — Considered work</title>"
        "<style>"
        "body{background:#faf8f3;color:#0e0e10;font-family:'Cormorant Garamond',serif}"
        "h1{color:#5e7a6e}"
        "p{font-family:'Inter Tight',sans-serif}"
        "</style></head><body>"
        "<h1>Quiet authority for considered work.</h1>"
        "<p>We design with intent.</p>"
        "</body></html>"
    )
    monkeypatch.setattr(
        inspire, "_fetch_url_safe",
        lambda url: ("https://sage.example", html, len(html), None),
    )
    status, body = _post(engine_server["base"], "/api/inspire", {"url": "https://sage.example"})
    assert status == 200
    assert body["ok"] is True
    assert body["extract"]["palette"]["background"] == "#faf8f3"
    assert body["extract"]["palette"]["primary"] == "#0e0e10"
    assert body["extract"]["suggested_dna"]["id"]
    assert body["brief_partial"]["_inspire_dna_hint"]
    # business facts are migrate.py's job — must NOT leak into inspire output
    assert "business_name" not in body["brief_partial"]


def test_inspire_reports_fetch_error_as_200_with_error_field(engine_server, monkeypatch):
    import pebble.inspire as inspire
    monkeypatch.setattr(inspire, "_fetch_url_safe",
                        lambda url: ("", "", 0, "host resolves to a private or blocked address"))
    status, body = _post(engine_server["base"], "/api/inspire",
                         {"url": "http://localhost/admin"})
    assert status == 200
    assert body["ok"] is False
    assert "private" in body["error"]


def test_inspire_rate_limits_after_burst(engine_server, monkeypatch):
    """6 burst budget — a fast 7th request from the same IP must 429.
    Reset the limiter after to avoid leaking state to other tests."""
    import pebble.inspire as inspire
    from pebble.security import inspire_fetch_limiter
    monkeypatch.setattr(
        inspire, "_fetch_url_safe",
        lambda url: ("https://x.example", "<html></html>", 13, None),
    )
    inspire_fetch_limiter.reset("127.0.0.1")
    last_status = None
    for _ in range(7):
        last_status, last_body = _post(
            engine_server["base"], "/api/inspire", {"url": "https://x.example"},
        )
    assert last_status == 429
    assert "too many" in last_body["error"]
    inspire_fetch_limiter.reset("127.0.0.1")


def test_inspire_rejects_oversized_body(engine_server):
    """The /api/inspire body is just { url }; nothing legitimate is over 4 KB.
    A 50 KB body indicates abuse and should be rejected before we try to parse."""
    big_payload = {"url": "https://example.com", "junk": "x" * 60_000}
    status, _ = _post(engine_server["base"], "/api/inspire", big_payload)
    assert status == 400


# ---- /api/usage ---------------------------------------------------------

def test_usage_401_when_signed_out(engine_server):
    """Phase 58e regression pin (2026-05-22) — /api/usage used to
    aggregate every project regardless of caller, exposing every user's
    slugs + token counts + cost data. Must 401 instead."""
    status, _ = _get(engine_server["base"], "/api/usage")
    assert status == 401


def test_usage_empty_when_no_projects(engine_server):
    cookie = _signin(engine_server["base"], "u@example.com", "valid-password")
    status, body = _get_with_cookie(engine_server["base"], "/api/usage", cookie=cookie)
    assert status == 200
    assert body["projects"] == 0
    assert body["total_estimated_cost_usd"] == 0
    assert body["by_project"] == []


def test_usage_aggregates_build_meta(engine_server):
    cookie = _signin(engine_server["base"], "u@example.com", "valid-password")
    out = engine_server["output"]
    _seed_project(out, "p1", {"app/page.tsx": "x"})
    (out / "p1" / "build_meta.json").write_text(json.dumps({
        "built_at": "2026-05-14T12:00:00",
        "model": "gemini-3.1-pro-preview",
        "billable": True,
        "tokens_used": {"input": 5000, "output": 3000},
        "estimated_cost_usd": 0.02125,
    }), encoding="utf-8")
    _seed_project(out, "p2", {"app/page.tsx": "x"})
    (out / "p2" / "build_meta.json").write_text(json.dumps({
        "built_at": "2026-05-14T13:00:00",
        "model": "gemini-3.1-pro-preview",
        "billable": True,
        "tokens_used": {"input": 8000, "output": 4000},
        "estimated_cost_usd": 0.030,
    }), encoding="utf-8")

    status, body = _get_with_cookie(engine_server["base"], "/api/usage", cookie=cookie)
    assert status == 200
    assert body["projects"] == 2
    assert body["total_input_tokens"] == 13000
    assert body["total_output_tokens"] == 7000
    assert body["total_estimated_cost_usd"] == pytest.approx(0.05125, rel=1e-3)
    # Newer build comes first
    assert body["by_project"][0]["slug"] == "p2"


def test_usage_skips_projects_without_build_meta(engine_server):
    cookie = _signin(engine_server["base"], "u@example.com", "valid-password")
    out = engine_server["output"]
    _seed_project(out, "still-cooking", {"app/page.tsx": "x"})  # no build_meta.json
    status, body = _get_with_cookie(engine_server["base"], "/api/usage", cookie=cookie)
    assert body["projects"] == 0


def test_usage_filters_other_users_projects(engine_server):
    """Phase 58e (2026-05-22) — usage is now per-caller. A project
    owned by another user must not appear in the caller's aggregation."""
    cookie = _signin(engine_server["base"], "alice@example.com", "valid-password")
    out = engine_server["output"]
    # Alice's project
    _seed_project(out, "alice-co", {"app/page.tsx": "x"},
                  brief={"business_name": "Alice", "_user_id": "ALICE_PLACEHOLDER"})
    (out / "alice-co" / "build_meta.json").write_text(json.dumps({
        "built_at": "2026-05-22T12:00:00",
        "billable": True,
        "tokens_used": {"input": 1000, "output": 1000},
        "estimated_cost_usd": 0.005,
    }), encoding="utf-8")
    # Stranger's project — owner is a fixed other id, never alice
    _seed_project(out, "stranger-co", {"app/page.tsx": "x"},
                  brief={"business_name": "Stranger", "_user_id": "OTHER_USER_ID"})
    (out / "stranger-co" / "build_meta.json").write_text(json.dumps({
        "built_at": "2026-05-22T12:00:00",
        "billable": True,
        "tokens_used": {"input": 9999, "output": 9999},
        "estimated_cost_usd": 99.99,
    }), encoding="utf-8")
    status, body = _get_with_cookie(engine_server["base"], "/api/usage", cookie=cookie)
    assert status == 200
    # Stranger's project must not appear or contribute to the total
    slugs = [r["slug"] for r in body["by_project"]]
    assert "stranger-co" not in slugs
    assert body["total_estimated_cost_usd"] < 1.0  # nowhere near 99.99


# ---- DELETE /api/projects/<slug> ----------------------------------------

def _delete(base: str, path: str) -> tuple[int, dict | str]:
    req = urllib.request.Request(f"{base}{path}", method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body_text = resp.read().decode("utf-8", errors="replace")
            try: return resp.status, json.loads(body_text)
            except Exception: return resp.status, body_text
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(body_text)
        except Exception: return e.code, body_text


def test_delete_project_removes_directory(engine_server):
    out = engine_server["output"]
    _seed_project(out, "to-delete", {"app/page.tsx": "x"})
    assert (out / "to-delete").exists()
    status, body = _delete(engine_server["base"], "/api/projects/to-delete")
    assert status == 200
    assert body["deleted"] is True
    assert not (out / "to-delete").exists()


def test_delete_project_404_for_unknown(engine_server):
    status, _ = _delete(engine_server["base"], "/api/projects/never-existed")
    assert status == 404


def test_delete_rejects_subroute_paths(engine_server):
    """DELETE /api/projects/<slug>/history should NOT delete — it's a GET route."""
    _seed_project(engine_server["output"], "good-co", {"app/page.tsx": "x"})
    status, _ = _delete(engine_server["base"], "/api/projects/good-co/history")
    assert status == 404
    # Project should still be there
    assert (engine_server["output"] / "good-co").exists()


# ---- /api/projects/<slug> (single-project state) ----------------------------

def test_get_project_state_bundles_brief_plan_meta(engine_server):
    """E2E sanity check — the new endpoint serves the full bundled
    state through the real HTTP server. Auth-gate behavior is covered
    by the unit tests in test_projects_api.py (which exercise
    require_project_owner) and by the engine_server fixture which
    bypasses auth for JSON-contract testing."""
    out = engine_server["output"]
    _seed_project(out, "good-co", {"app/page.tsx": "x"},
                  brief={"business_name": "Good Co", "business_type": "bakery"})
    # Write plan and build_meta (would be written by /api/generate)
    (out / "good-co" / "plan.json").write_text(
        json.dumps({"name": "Good Co", "audience": "local"}), encoding="utf-8"
    )
    (out / "good-co" / "build_meta.json").write_text(
        json.dumps({"built_at": "2026-05-14T12:00:00", "model": "qwen/qwen3.6-plus"}),
        encoding="utf-8",
    )
    status, body = _get(engine_server["base"], "/api/projects/good-co")
    assert status == 200
    assert body["slug"] == "good-co"
    assert body["brief"]["business_name"] == "Good Co"
    assert body["plan"]["name"] == "Good Co"
    assert body["build_meta"]["built_at"] == "2026-05-14T12:00:00"


def test_get_project_state_404_for_unknown_slug(engine_server):
    """Missing project dir → 404 regardless of auth (require_project_owner
    emits the 404 before ownership is even checked)."""
    status, _ = _get(engine_server["base"], "/api/projects/does-not-exist")
    assert status == 404
