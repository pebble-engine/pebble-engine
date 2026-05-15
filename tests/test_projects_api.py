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

import pebble.history as history_mod
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
    """Redirect all OUTPUT_DIR references in the modules under test."""
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(history_mod, "OUTPUT_DIR", out)
    # Patch the _engine() lookups in our server modules so they pick up the
    # tmp output too. Easier than mocking the real engine import.
    class FakeEngine:
        OUTPUT_DIR = out
    monkeypatch.setattr(projects, "_engine", lambda: FakeEngine)
    monkeypatch.setattr(refine,   "_engine", lambda: FakeEngine)
    monkeypatch.setattr(visual_edit, "_engine", lambda: FakeEngine)
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
    assert h.json_body["billable"] is False
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
