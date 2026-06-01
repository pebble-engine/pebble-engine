"""Tests for the free "pick-from" example gallery (/api/examples + clone).

The 15 v2 example sites are offered as starting points. Cloning is a pure
filesystem copy — no LLM — that drops a complete built site into the user's
account. These tests assert the list contract, the clone copy + stamping, and
the error paths, using a tmp OUTPUT_DIR and a fake example source on disk.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pebble.server import examples as ex


# ---------------------------------------------------------------------------
# Manifest / list
# ---------------------------------------------------------------------------

def test_real_manifest_lists_fifteen_examples():
    """The committed manifest ships the full gallery."""
    reg = ex.load_examples()
    assert reg.get("examples"), "example_gallery.json must list examples"
    assert len(reg["examples"]) == 15
    for e in reg["examples"]:
        assert e["slug"] and e["name"] and e["vibe"]
        assert e["hero_image"].startswith("http")  # real preview image
        # committed source location so the gallery works on a fresh deploy
        assert e["source_dir"].startswith("pebble/examples/")
        assert (Path(__file__).resolve().parents[1] / e["source_dir"] / "site").is_dir()


def test_list_examples_strips_internal_source_dir():
    handler = MagicMock()
    ex.run_list_examples(handler)
    status, body = handler._json.call_args[0]
    assert status == 200
    assert body["count"] == len(body["examples"]) >= 1
    # the engine-internal source path must NOT leak to the public list
    assert all("source_dir" not in e for e in body["examples"])
    assert all("name" in e and "vibe" in e for e in body["examples"])


# ---------------------------------------------------------------------------
# Clone
# ---------------------------------------------------------------------------

def _fake_example_on_disk(tmp_path: Path) -> dict:
    """Create a minimal fake example site under a repo-rooted source dir."""
    src = tmp_path / "output" / "demo-example"
    site = src / "site"
    (site / "components" / "sections").mkdir(parents=True)
    (site / "app").mkdir(parents=True)
    (site / "components" / "sections" / "Section00.tsx").write_text("export default function H(){return null}", encoding="utf-8")
    (site / "app" / "page.tsx").write_text("export default function P(){return null}", encoding="utf-8")
    (site / "next.config.mjs").write_text("/** @type {import('next').NextConfig} */\nexport default {};\n", encoding="utf-8")
    # build artifacts that must NOT be copied
    (site / "node_modules").mkdir()
    (site / "node_modules" / "junk.js").write_text("x", encoding="utf-8")
    (src / "brief.json").write_text(json.dumps({"business_name": "Demo Co", "industry": "bakery", "_vibe": "warm-craft"}), encoding="utf-8")
    return {"slug": "demo-example", "name": "Demo Co", "industry": "bakery",
            "vibe": "warm-craft", "hero_image": "http://x/y.jpg",
            "source_dir": "output/demo-example", "kind": "example_build"}


def _make_handler(body: dict) -> MagicMock:
    raw = json.dumps(body).encode("utf-8")
    h = MagicMock()
    h.headers = {"Content-Length": str(len(raw))}
    h.rfile.read.return_value = raw
    return h


def _wire(monkeypatch, tmp_path: Path, example: dict):
    out = tmp_path / "out"
    out.mkdir()
    # repo root → tmp_path so source_dir "output/demo-example" resolves to our fake
    monkeypatch.setattr(ex, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(ex, "get_example", lambda s: example if s == example["slug"] else None)

    fake_engine = MagicMock()
    fake_engine.OUTPUT_DIR = out
    fake_engine.MAX_REQUEST_BYTES = 5_000_000
    fake_engine._slugify = lambda n: n.lower().replace(" ", "-").replace("&", "and")
    fake_engine._resolve_user_id = lambda h: None
    monkeypatch.setattr("pebble.server.build._engine", lambda: fake_engine)
    # bypass the per-IP rate limiter
    monkeypatch.setattr(ex.generate_limiter, "allow", lambda ip: True)
    return out


def test_clone_copies_site_and_stamps_meta(tmp_path, monkeypatch):
    example = _fake_example_on_disk(tmp_path)
    out = _wire(monkeypatch, tmp_path, example)

    handler = _make_handler({"example_slug": "demo-example", "business_name": "My Bakery"})
    ex.run_clone_example(handler)

    status, body = handler._json.call_args[0]
    assert status == 200
    assert body["ok"] is True
    assert body["slug"] == "my-bakery"          # slug from provided name
    assert body["cloned_from"] == "demo-example"
    assert body["billable"] is False

    site = out / "my-bakery" / "site"
    assert (site / "app" / "page.tsx").exists()
    assert (site / "components" / "sections" / "Section00.tsx").exists()
    # build artifacts excluded
    assert not (site / "node_modules").exists()

    brief = json.loads((out / "my-bakery" / "brief.json").read_text())
    assert brief["business_name"] == "My Bakery"   # name override applied
    assert brief["_cloned_from"] == "demo-example"
    meta = json.loads((out / "my-bakery" / "build_meta.json").read_text())
    assert meta["engine_version"] == "v2"
    assert meta["cloned_from"] == "demo-example"
    assert meta["billable"] is False


def test_clone_without_name_uses_copy_suffix_and_autosuffixes(tmp_path, monkeypatch):
    example = _fake_example_on_disk(tmp_path)
    out = _wire(monkeypatch, tmp_path, example)
    # pre-create the default target so the clone must auto-suffix
    (out / "demo-example-copy").mkdir()

    handler = _make_handler({"example_slug": "demo-example"})
    ex.run_clone_example(handler)
    status, body = handler._json.call_args[0]
    assert status == 200
    assert body["slug"] == "demo-example-copy-2"   # collision → -2


def test_clone_unknown_example_404(tmp_path, monkeypatch):
    example = _fake_example_on_disk(tmp_path)
    _wire(monkeypatch, tmp_path, example)
    handler = _make_handler({"example_slug": "does-not-exist"})
    ex.run_clone_example(handler)
    status, body = handler._json.call_args[0]
    assert status == 404
    assert "unknown" in body["error"].lower()


def test_clone_empty_body_400(tmp_path, monkeypatch):
    example = _fake_example_on_disk(tmp_path)
    _wire(monkeypatch, tmp_path, example)
    handler = MagicMock()
    handler.headers = {"Content-Length": "0"}
    ex.run_clone_example(handler)
    status, body = handler._json.call_args[0]
    assert status == 400
