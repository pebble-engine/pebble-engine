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


def test_activity_feed_empty_when_no_history(engine_server):
    _seed_project(engine_server["output"], "good-co", {"app/page.tsx": "x"})
    status, body = _get(engine_server["base"], "/api/activity")
    assert status == 200
    assert body["count"] == 0


def test_activity_feed_lists_snapshots_newest_first(engine_server):
    out = engine_server["output"]
    _seed_project(out, "good-co", {"app/page.tsx": "ORIGINAL"},
                  brief={"business_name": "Good Co"})
    history_mod.snapshot_site("good-co", reason="generate", source="POST /api/generate")
    time.sleep(1.05)
    history_mod.snapshot_site("good-co", reason="refine-friendlier", source="POST /api/refine")
    status, body = _get(engine_server["base"], "/api/activity")
    assert status == 200
    assert body["count"] == 2
    # Newest first
    assert body["activity"][0]["reason"] == "refine-friendlier"
    assert body["activity"][1]["reason"] == "generate"
    assert body["activity"][0]["business_name"] == "Good Co"


def test_signup_writes_welcome_email_to_outbox(engine_server):
    base = engine_server["base"]
    out = engine_server["output"]
    status, _body, _ = _post_with_cookie(base, "/api/auth/signup", {
        "email": "alice@example.com", "password": "valid-password",
    })
    assert status == 201
    # FileSender wrote an .eml under output/.email_outbox/
    outbox = out / ".email_outbox"
    assert outbox.exists()
    files = list(outbox.glob("*.eml"))
    assert len(files) == 1
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
    # Parse the .eml with the modern email policy so we get the decoded
    # body instead of quoted-printable-wrapped raw bytes.
    import email.policy as _email_policy
    outbox = out / ".email_outbox"
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
    """Anonymous projects show to everyone; user-stamped projects only show
    to their owner."""
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

    # User A sees their site + anonymous, not B's
    req = urllib.request.Request(f"{base}/api/projects", headers={"Cookie": cookie_a})
    with urllib.request.urlopen(req, timeout=5) as r:
        listing = json.loads(r.read().decode("utf-8"))
    slugs = {p["slug"] for p in listing["projects"]}
    assert "anon-site" in slugs
    assert "a-site" in slugs
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


# ---- /api/usage ---------------------------------------------------------

def test_usage_empty_when_no_projects(engine_server):
    status, body = _get(engine_server["base"], "/api/usage")
    assert status == 200
    assert body["projects"] == 0
    assert body["total_estimated_cost_usd"] == 0
    assert body["by_project"] == []


def test_usage_aggregates_build_meta(engine_server):
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

    status, body = _get(engine_server["base"], "/api/usage")
    assert status == 200
    assert body["projects"] == 2
    assert body["total_input_tokens"] == 13000
    assert body["total_output_tokens"] == 7000
    assert body["total_estimated_cost_usd"] == pytest.approx(0.05125, rel=1e-3)
    # Newer build comes first
    assert body["by_project"][0]["slug"] == "p2"


def test_usage_skips_projects_without_build_meta(engine_server):
    out = engine_server["output"]
    _seed_project(out, "still-cooking", {"app/page.tsx": "x"})  # no build_meta.json
    status, body = _get(engine_server["base"], "/api/usage")
    assert body["projects"] == 0


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
