import json
from pathlib import Path

import pytest

import scripts.promote_example as promote


def _make_fake_build(tmp_path, slug="tidewater-plumbing"):
    out = tmp_path / "output" / slug
    site = out / "site"
    (site / "app").mkdir(parents=True)
    (site / "app" / "page.tsx").write_text(
        "export default function Page(){return null;}", encoding="utf-8"
    )
    # noise that must be excluded
    (site / "node_modules" / "react").mkdir(parents=True)
    (site / "node_modules" / "react" / "index.js").write_text("// noise", encoding="utf-8")
    (site / ".next" / "cache").mkdir(parents=True)
    (site / ".next" / "cache" / "junk").write_text("noise", encoding="utf-8")
    (out / "brief.json").write_text(
        json.dumps({"business_name": "Tidewater Plumbing Co.", "industry": "plumber"}),
        encoding="utf-8",
    )
    (out / "build_meta.json").write_text(
        json.dumps({"engine_version": "v2", "block_picks": ["library/a", "library/b", "library/c"]}),
        encoding="utf-8",
    )
    return out


def _make_examples_dirs(tmp_path):
    examples = tmp_path / "pebble" / "examples"
    examples.mkdir(parents=True)
    manifest = tmp_path / "pebble" / "example_gallery.json"
    manifest.write_text(
        json.dumps({"schema_version": "1.0", "examples": []}),
        encoding="utf-8",
    )
    return examples, manifest


def _wire(monkeypatch, tmp_path, examples, manifest):
    monkeypatch.setattr(promote, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(promote, "EXAMPLES_DIR", examples)
    monkeypatch.setattr(promote, "MANIFEST", manifest)
    monkeypatch.setattr(
        promote, "capture_thumbnail",
        lambda slug, site_dir: f"templates-preview/{slug}.png",
    )


def test_promote_moves_site_and_appends_manifest(tmp_path, monkeypatch):
    _make_fake_build(tmp_path)
    examples, manifest = _make_examples_dirs(tmp_path)
    _wire(monkeypatch, tmp_path, examples, manifest)

    promote.promote("tidewater-plumbing", vibe="trade-pro")

    # site copied
    assert (examples / "tidewater-plumbing" / "site" / "app" / "page.tsx").exists()
    # brief carried forward
    assert (examples / "tidewater-plumbing" / "brief.json").exists()
    # exclusions respected
    assert not (examples / "tidewater-plumbing" / "site" / "node_modules").exists()
    assert not (examples / "tidewater-plumbing" / "site" / ".next").exists()

    data = json.loads(manifest.read_text(encoding="utf-8"))
    slugs = {e["slug"] for e in data["examples"]}
    assert "tidewater-plumbing" in slugs
    entry = next(e for e in data["examples"] if e["slug"] == "tidewater-plumbing")
    assert entry["vibe"] == "trade-pro"
    assert entry["industry"] == "plumber"
    assert entry["name"] == "Tidewater Plumbing Co."
    assert entry["source_dir"] == "pebble/examples/tidewater-plumbing"
    assert entry["kind"] == "example_build"
    assert entry["sections"] == 3  # from block_picks length
    assert entry["hero_image"]  # non-empty


def test_promote_is_idempotent(tmp_path, monkeypatch):
    _make_fake_build(tmp_path)
    examples, manifest = _make_examples_dirs(tmp_path)
    _wire(monkeypatch, tmp_path, examples, manifest)

    promote.promote("tidewater-plumbing", vibe="trade-pro")
    # second promote of same slug REPLACES, doesn't duplicate
    promote.promote("tidewater-plumbing", vibe="trade-pro")

    data = json.loads(manifest.read_text(encoding="utf-8"))
    matching = [e for e in data["examples"] if e["slug"] == "tidewater-plumbing"]
    assert len(matching) == 1


def test_promote_unknown_slug_raises(tmp_path, monkeypatch):
    examples, manifest = _make_examples_dirs(tmp_path)
    _wire(monkeypatch, tmp_path, examples, manifest)

    with pytest.raises((FileNotFoundError, ValueError)):
        promote.promote("nonexistent-slug", vibe="trade-pro")
