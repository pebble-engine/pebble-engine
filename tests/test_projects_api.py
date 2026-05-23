"""HTTP-shape tests for the new project/history/refine/visual-edit endpoints.

These tests use a synthetic FakeHandler that captures the JSON response —
no real socket. They verify request validation + the data-shape contract
that the v3 UI will rely on.
"""
from __future__ import annotations

import json
import time
from io import BytesIO
from pathlib import Path

import pytest

import pebble.engagement as engagement_mod
import pebble.history as history_mod
import pebble.security as security_mod
import pebble.server.projects as projects
import pebble.server.refine as refine
import pebble.server.visual_edit as visual_edit


class FakeHandler:
    """Minimal stand-in for the HTTP handler — captures responses, exposes
    headers + body to the module under test."""
    def __init__(self, body: dict | None = None, content_length: int | None = None):
        raw = json.dumps(body).encode("utf-8") if body is not None else b""
        self.rfile = BytesIO(raw)
        self.headers = {"Content-Length": str(len(raw) if content_length is None else content_length)}
        self.status: int | None = None
        self.json_body: dict | None = None

    def _json(self, status: int, payload: dict):
        self.status = status
        self.json_body = payload


@pytest.fixture
def fake_output(tmp_path, monkeypatch):
    """Redirect all OUTPUT_DIR references in the modules under test.

    Also short-circuits ``require_project_owner`` so legacy FakeHandler
    tests (no real cookies) keep working. The 2026-05-15 evening security
    pass added auth gates to refine / visual-edit / rollback / history /
    star endpoints; the existing tests were written before that. Each
    test still exercises the JSON contract; auth-specific behavior is
    covered in tests/test_security.py and the HTTP e2e files.
    """
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(history_mod, "OUTPUT_DIR", out)
    monkeypatch.setattr(security_mod, "_output_dir", lambda: out)
    # Patch the _engine() lookups in our server modules so they pick up the
    # tmp output too. Easier than mocking the real engine import.
    class FakeEngine:
        OUTPUT_DIR = out
    monkeypatch.setattr(projects, "_engine", lambda: FakeEngine)
    monkeypatch.setattr(refine,   "_engine", lambda: FakeEngine)
    monkeypatch.setattr(visual_edit, "_engine", lambda: FakeEngine)
    # Bypass the auth gate — tests focus on the JSON contract. Auth
    # behavior is covered separately. Preserves the gate's *non-auth*
    # responsibilities: bad slug → 400, missing project → 404. The
    # ownership check itself is what we short-circuit.
    def bypass(handler, slug):
        if not security_mod.is_valid_slug(slug):
            handler._json(400, {"error": "invalid project slug"})
            return None
        if not (out / slug).exists():
            handler._json(404, {"error": f"project not found: {slug}"})
            return None
        return "test-user"
    monkeypatch.setattr(security_mod, "require_project_owner", bypass)
    monkeypatch.setattr(projects, "require_project_owner", bypass)
    monkeypatch.setattr(refine, "require_project_owner", bypass)
    monkeypatch.setattr(visual_edit, "require_project_owner", bypass)
    # Phase 58e (2026-05-22) — /api/projects + /api/usage now require
    # an authenticated user (used to fall through to "show all" on
    # anon callers, which was a leak). The JSON-contract tests below
    # don't pass auth headers, so short-circuit resolve_user_id too
    # — the same way require_project_owner is bypassed above. Auth-
    # specific behavior is exercised in test_security.py + test_http_e2e.py.
    monkeypatch.setattr(security_mod, "resolve_user_id", lambda h: "test-user")
    monkeypatch.setattr(projects, "resolve_user_id", lambda h: "test-user")
    # Phase 54a (2026-05-23) — `colors` and the LLM refinements call
    # would_exceed_quota() before doing any work. "test-user" has no real
    # plan, so the gate would 402 every refinement. Bypass it the same way
    # require_project_owner is bypassed; plan-gate behavior is exercised
    # in tests/test_user_plan.py.
    monkeypatch.setattr(refine, "would_exceed_quota",
                        lambda uid, ev_kind, lim_key: (False, 0, 999_999))
    monkeypatch.setattr(refine, "increment_usage", lambda uid, ev_kind: None)
    # Isolate engagement storage per test (T17). Without this every test
    # would append to a shared output/.engagement/ dir.
    monkeypatch.setattr(engagement_mod, "_engagement_dir", lambda: out / ".engagement")
    return out


def _seed_site(output: Path, slug: str, files: dict[str, str]) -> Path:
    site = output / slug / "site"
    site.mkdir(parents=True, exist_ok=True)
    for rel, content in files.items():
        p = site / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return site


# ---- /api/projects ---------------------------------------------------------

def test_list_projects_empty(fake_output):
    h = FakeHandler()
    projects.run_list_projects(h)
    assert h.status == 200
    assert h.json_body == {"projects": [], "count": 0}


def test_list_projects_returns_brief_and_meta(fake_output):
    slug = "good-co"
    (fake_output / slug).mkdir()
    (fake_output / slug / "brief.json").write_text(json.dumps({
        "business_name": "Good Co",
        "business_type": "bakery",
        "_design_dna": "swiss_magazine",
    }))
    (fake_output / slug / "build_meta.json").write_text(json.dumps({
        "built_at": "2026-05-14T12:00:00",
    }))
    _seed_site(fake_output, slug, {"app/page.tsx": "x", "package.json": "y"})

    h = FakeHandler()
    projects.run_list_projects(h)
    assert h.status == 200
    assert h.json_body["count"] == 1
    p = h.json_body["projects"][0]
    assert p["slug"] == slug
    assert p["business_name"] == "Good Co"
    assert p["business_type"] == "bakery"
    assert p["file_count"] == 2
    assert p["starred"] is False
    assert p["preview_url"] == "/preview/good-co/"


def test_list_projects_skips_non_project_dirs(fake_output):
    # research_cache is in the output dir but isn't a project
    (fake_output / "research_cache").mkdir()
    (fake_output / "research_cache" / "bakery.md").write_text("notes")
    h = FakeHandler()
    projects.run_list_projects(h)
    assert h.json_body["count"] == 0


def test_list_projects_orders_newest_first(fake_output):
    for i, slug in enumerate(["older", "newer"]):
        (fake_output / slug).mkdir()
        (fake_output / slug / "brief.json").write_text(json.dumps({"business_name": slug}))
        (fake_output / slug / "build_meta.json").write_text(json.dumps({
            "built_at": f"2026-05-{10 + i:02d}T00:00:00",
        }))
        _seed_site(fake_output, slug, {"a.txt": "x"})
    h = FakeHandler()
    projects.run_list_projects(h)
    slugs = [p["slug"] for p in h.json_body["projects"]]
    assert slugs == ["newer", "older"]


# ---- /api/projects/<slug>/history -----------------------------------------

def test_get_history_404_for_unknown_project(fake_output):
    h = FakeHandler()
    projects.run_get_history(h, "does-not-exist")
    assert h.status == 404


def test_get_history_returns_snapshots(fake_output):
    slug = "p1"
    _seed_site(fake_output, slug, {"a.txt": "v1"})
    history_mod.snapshot_site(slug, reason="generate")
    time.sleep(1.05)
    (fake_output / slug / "site" / "a.txt").write_text("v2", encoding="utf-8")
    history_mod.snapshot_site(slug, reason="refine-friendlier")

    h = FakeHandler()
    projects.run_get_history(h, slug)
    assert h.status == 200
    assert h.json_body["slug"] == slug
    assert h.json_body["count"] == 2
    assert h.json_body["snapshots"][0]["reason"] == "refine-friendlier"


# ---- /api/rollback ---------------------------------------------------------

def test_rollback_restores_old_content(fake_output):
    slug = "p1"
    _seed_site(fake_output, slug, {"a.txt": "ORIGINAL"})
    history_mod.snapshot_site(slug, reason="generate")
    time.sleep(1.05)
    (fake_output / slug / "site" / "a.txt").write_text("MUTATED", encoding="utf-8")

    snapshot_id = history_mod.list_history(slug)[0].snapshot_id
    h = FakeHandler(body={"slug": slug, "snapshot_id": snapshot_id})
    projects.run_rollback(h)
    assert h.status == 200
    assert h.json_body["files_restored"] >= 1
    assert (fake_output / slug / "site" / "a.txt").read_text() == "ORIGINAL"


def test_rollback_validates_required_fields(fake_output):
    h = FakeHandler(body={"slug": "p1"})  # missing snapshot_id
    projects.run_rollback(h)
    assert h.status == 400


def test_rollback_404_for_unknown_snapshot(fake_output):
    _seed_site(fake_output, "p1", {"a.txt": "x"})
    h = FakeHandler(body={"slug": "p1", "snapshot_id": "20990101T000000-bogus"})
    projects.run_rollback(h)
    assert h.status == 404


# ---- /api/projects/<slug>/star --------------------------------------------

def test_toggle_star_creates_sentinel_on_first_call(fake_output):
    slug = "p1"
    (fake_output / slug).mkdir()
    _seed_site(fake_output, slug, {"a.txt": "x"})
    assert not (fake_output / slug / ".starred").exists()
    h = FakeHandler()
    projects.run_toggle_star(h, slug)
    assert h.status == 200
    assert h.json_body["starred"] is True
    assert (fake_output / slug / ".starred").exists()


def test_toggle_star_unstars_on_second_call(fake_output):
    slug = "p1"
    (fake_output / slug).mkdir()
    _seed_site(fake_output, slug, {"a.txt": "x"})
    (fake_output / slug / ".starred").touch()
    h = FakeHandler()
    projects.run_toggle_star(h, slug)
    assert h.json_body["starred"] is False
    assert not (fake_output / slug / ".starred").exists()


# ---- /api/refine (deterministic) ------------------------------------------

def test_refine_validates_required_fields(fake_output):
    h = FakeHandler(body={"slug": "p1"})  # missing refinement_id
    refine.run_refine(h)
    assert h.status == 400


def test_refine_404_for_unknown_site(fake_output):
    h = FakeHandler(body={"slug": "nope", "refinement_id": "simpler"})
    refine.run_refine(h)
    assert h.status == 404


def test_refine_simpler_is_deterministic_and_free(fake_output):
    slug = "p1"
    _seed_site(fake_output, slug, {
        "app/globals.css": "body { background: #FF6633; color: #111; }\n",
    })
    h = FakeHandler(body={"slug": slug, "refinement_id": "simpler"})
    refine.run_refine(h)
    assert h.status == 200
    assert h.json_body["kind"] == "deterministic"
    assert h.json_body["billable"] is False
    # The bright orange should have been toned down (matched by the rule).
    assert "#FF6633" not in (fake_output / slug / "site" / "app" / "globals.css").read_text()


def test_refine_colors_rotates_palette(fake_output):
    slug = "p1"
    _seed_site(fake_output, slug, {
        "app/globals.css": "body { color: #111111; background: #222222; }",
    })
    h = FakeHandler(body={"slug": slug, "refinement_id": "colors"})
    refine.run_refine(h)
    assert h.status == 200
    # 2026-05-19: "colors" repriced as billable ("Magic Palette Shift").
    # Mechanical execution but high perceived value — giving it away
    # devalued the DNA system. Per NLM adversarial pricing review.
    assert h.json_body["billable"] is True
    assert h.json_body["kind"] == "deterministic"  # still no LLM call
    new = (fake_output / slug / "site" / "app" / "globals.css").read_text()
    assert "#111111" not in new  # at least one hex should have changed


def test_refine_creates_history_snapshot(fake_output):
    slug = "p1"
    _seed_site(fake_output, slug, {"app/globals.css": "body { color: #ff0000; }\n"})
    h = FakeHandler(body={"slug": slug, "refinement_id": "simpler"})
    refine.run_refine(h)
    assert h.json_body["snapshot_id"] is not None
    snaps = history_mod.list_history(slug)
    assert any("simpler" in s.reason or s.reason == "refine-simpler" for s in snaps)


# ---- /api/visual-edit ------------------------------------------------------

def test_visual_edit_text_replaces_jsx_text(fake_output):
    slug = "p1"
    _seed_site(fake_output, slug, {
        "app/page.tsx": (
            'import { Hero } from "@/components/sections/Hero";\n'
            'export default function P() {\n'
            '  return <main><h1>Welcome to my bakery</h1></main>;\n'
            '}'
        ),
    })
    h = FakeHandler(body={
        "slug": slug,
        "op":   "text",
        "original_text": "Welcome to my bakery",
        "new_text":      "Hi, I'm a baker",
    })
    visual_edit.run_visual_edit(h)
    assert h.status == 200
    assert h.json_body["billable"] is False
    content = (fake_output / slug / "site" / "app" / "page.tsx").read_text()
    assert "Hi, I'm a baker" in content
    assert "Welcome to my bakery" not in content


def test_visual_edit_text_skips_import_lines(fake_output):
    """A literal that happens to appear in an import statement should not be
    rewritten — that's a structural change, not a visual edit."""
    slug = "p1"
    _seed_site(fake_output, slug, {
        "app/page.tsx": (
            'import { Brand } from "@/lib/Brand";  // Brand is a real component name\n'
            'export default function P() { return <main><p>Brand</p></main>; }'
        ),
    })
    h = FakeHandler(body={"slug": slug, "op": "text", "original_text": "Brand", "new_text": "Studio"})
    visual_edit.run_visual_edit(h)
    content = (fake_output / slug / "site" / "app" / "page.tsx").read_text()
    # import line still says Brand
    assert "import { Brand }" in content
    # JSX <p>Brand</p> should now be <p>Studio</p>
    assert "<p>Studio</p>" in content


def test_visual_edit_validates_op(fake_output):
    h = FakeHandler(body={"slug": "p1", "op": "delete-everything"})
    visual_edit.run_visual_edit(h)
    assert h.status == 400


def test_visual_edit_color_requires_valid_hex(fake_output):
    _seed_site(fake_output, "p1", {"app/globals.css": "body { color: #000000; }"})
    h = FakeHandler(body={"slug": "p1", "op": "color", "new_color": "blue"})
    visual_edit.run_visual_edit(h)
    assert h.status == 400


def test_visual_edit_snapshots_before_changing(fake_output):
    _seed_site(fake_output, "p1", {"app/page.tsx": "export default function P() { return <main>Hello</main>; }"})
    h = FakeHandler(body={"slug": "p1", "op": "text", "original_text": "Hello", "new_text": "Hi"})
    visual_edit.run_visual_edit(h)
    assert h.json_body["snapshot_id"]
    assert len(history_mod.list_history("p1")) == 1


# ---- T17: engagement wiring + privacy regression --------------------------

def test_visual_edit_logs_engagement_event_on_success(fake_output):
    """visual_edit success path must call engagement.log_event with
    the bypass fixture's user ('test-user') and the canonical event name."""
    _seed_site(fake_output, "p1", {"app/page.tsx": "export default function P() { return <main>Hello</main>; }"})
    h = FakeHandler(body={"slug": "p1", "op": "text", "original_text": "Hello", "new_text": "Hi"})
    visual_edit.run_visual_edit(h)
    assert h.status == 200
    events = engagement_mod.read_user_events("test-user")
    assert len(events) == 1
    assert events[0]["event"] == "visual_edit_used"


def test_visual_edit_does_not_log_engagement_on_validation_failure(fake_output):
    """Failed validations (bad op) must NOT log an event — engagement counts
    successful actions, not error replies."""
    h = FakeHandler(body={"slug": "p1", "op": "delete-everything"})
    visual_edit.run_visual_edit(h)
    assert h.status == 400
    assert engagement_mod.read_user_events("test-user") == []


def test_visual_edit_engagement_never_contains_content(fake_output):
    """PRIVACY REGRESSION — log files must contain ONLY {event, timestamp}.
    Run a visual-edit with sensitive-looking text and assert no leakage."""
    sensitive_text = "Hello-secret-marker-zxyq"
    _seed_site(fake_output, "p1", {"app/page.tsx": f"export default function P() {{ return <main>{sensitive_text}</main>; }}"})
    h = FakeHandler(body={"slug": "p1", "op": "text", "original_text": sensitive_text, "new_text": "Hi-new-marker"})
    visual_edit.run_visual_edit(h)
    log_file = fake_output / ".engagement" / "test-user.jsonl"
    assert log_file.exists()
    text = log_file.read_text(encoding="utf-8")
    assert sensitive_text not in text
    assert "Hi-new-marker" not in text
    # The event line itself must contain exactly two keys.
    row = json.loads(text.splitlines()[0])
    assert set(row.keys()) == {"event", "timestamp"}


def test_project_star_logs_engagement_event(fake_output):
    """Toggling a project's star fires `project_starred` (regardless of
    direction — engagement cares about variety not state)."""
    (fake_output / "p1").mkdir()
    h = FakeHandler(body={"starred": True})
    projects.run_toggle_star(h, "p1")
    assert h.status == 200
    events = engagement_mod.read_user_events("test-user")
    assert any(e["event"] == "project_starred" for e in events)


def test_project_delete_logs_engagement_event(fake_output):
    (fake_output / "p1").mkdir()
    (fake_output / "p1" / "brief.json").write_text('{"business_name":"p1"}')
    h = FakeHandler()
    projects.run_delete_project(h, "p1")
    assert h.status == 200
    events = engagement_mod.read_user_events("test-user")
    assert any(e["event"] == "project_deleted" for e in events)


# ---- /api/projects/<slug> (single-project state) ----------------------------

def test_get_project_state_returns_brief_plan_meta(fake_output):
    """The new GET /api/projects/<slug> bundles everything a workspace
    needs to resume a project: slug + brief + plan + build_meta."""
    slug = "good-co"
    (fake_output / slug).mkdir()
    (fake_output / slug / "brief.json").write_text(json.dumps({
        "business_name": "Good Co",
        "business_type": "bakery",
        "_design_dna": "swiss_magazine",
    }), encoding="utf-8")
    (fake_output / slug / "plan.json").write_text(json.dumps({
        "name": "Good Co",
        "audience": "local",
    }), encoding="utf-8")
    (fake_output / slug / "build_meta.json").write_text(json.dumps({
        "built_at": "2026-05-14T12:00:00",
        "model": "qwen/qwen3.6-plus",
    }), encoding="utf-8")
    _seed_site(fake_output, slug, {"app/page.tsx": "x"})

    h = FakeHandler()
    projects.run_get_project_state(h, slug)
    assert h.status == 200
    body = h.json_body
    assert body["slug"] == slug
    assert body["brief"]["business_name"] == "Good Co"
    assert body["plan"]["name"] == "Good Co"
    assert body["build_meta"]["built_at"] == "2026-05-14T12:00:00"


def test_get_project_state_404_for_unknown(fake_output):
    h = FakeHandler()
    projects.run_get_project_state(h, "does-not-exist")
    assert h.status == 404


def test_get_project_state_handles_missing_plan_gracefully(fake_output):
    """Some old projects don't have plan.json yet. Return null for plan
    rather than 500."""
    slug = "ancient"
    (fake_output / slug).mkdir()
    (fake_output / slug / "brief.json").write_text(json.dumps({"business_name": "Ancient"}))
    _seed_site(fake_output, slug, {"app/page.tsx": "x"})

    h = FakeHandler()
    projects.run_get_project_state(h, slug)
    assert h.status == 200
    assert h.json_body["plan"] is None
    assert h.json_body["build_meta"] is None  # also missing


def test_get_project_state_401_when_no_auth(tmp_path, monkeypatch):
    """Pin the auth-gate behavior at the unit level. The fake_output
    fixture bypasses require_project_owner for JSON-contract tests;
    here we undo that to confirm the handler actually 401s on no auth."""
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(history_mod, "OUTPUT_DIR", out)
    monkeypatch.setattr(security_mod, "_output_dir", lambda: out)
    class FakeEngine:
        OUTPUT_DIR = out
    monkeypatch.setattr(projects, "_engine", lambda: FakeEngine)

    # Restore the real require_project_owner (undo the fixture bypass).
    # We import and use the actual function from security module.
    from pebble.security import require_project_owner as real_require
    monkeypatch.setattr(projects, "require_project_owner", real_require)

    # Seed a real project so we get past the 404-doesn't-exist check
    slug = "good-co"
    (out / slug).mkdir()
    (out / slug / "brief.json").write_text(json.dumps({"business_name": "Good Co"}),
                                          encoding="utf-8")
    _seed_site(out, slug, {"app/page.tsx": "x"})

    h = FakeHandler()
    projects.run_get_project_state(h, slug)
    # No Authorization header on FakeHandler, no cookie — should 401
    assert h.status == 401
