"""Tests for pebble.visual_ids — pebble-id injection + manifest + lookup."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pebble.visual_ids import (
    inject_pebble_ids,
    load_manifest,
    find_tag_open,
    find_element_span,
)


@pytest.fixture
def site(tmp_path) -> Path:
    """Fresh per-test site directory."""
    s = tmp_path / "site"
    s.mkdir()
    return s


# ---- inject_pebble_ids -----------------------------------------------------

def test_inject_into_empty_dir_returns_empty_manifest(site):
    assert inject_pebble_ids(site) == {}
    assert (site / ".pebble-ids.json").exists()


def test_inject_into_missing_dir_returns_empty(tmp_path):
    assert inject_pebble_ids(tmp_path / "does-not-exist") == {}


def test_inject_html_tags_adds_data_attrs(site):
    (site / "index.html").write_text(
        "<html><body><h1>Hello</h1><p>World</p></body></html>",
        encoding="utf-8",
    )
    manifest = inject_pebble_ids(site)
    content = (site / "index.html").read_text(encoding="utf-8")

    assert len(manifest) == 2
    assert content.count("data-pebble-id=") == 2
    for pid, entry in manifest.items():
        assert pid.startswith("pb-") and len(pid) == 9
        assert entry["file"] == "index.html"
        assert entry["tag"] in {"h1", "p"}


def test_inject_jsx_tags_adds_data_attrs(site):
    (site / "page.tsx").write_text(
        'export default function Page() { return <div><h1 className="x">Hi</h1><button>Go</button></div>; }',
        encoding="utf-8",
    )
    manifest = inject_pebble_ids(site)
    content = (site / "page.tsx").read_text(encoding="utf-8")

    # h1 and button are TARGET_TAGS, div is not.
    assert len(manifest) == 2
    assert content.count("data-pebble-id=") == 2
    # className is preserved on the h1.
    assert 'className="x"' in content


def test_inject_skips_tags_with_existing_id(site):
    pre = '<p data-pebble-id="pb-123abc">A</p><p>B</p>'
    (site / "index.html").write_text(pre, encoding="utf-8")
    manifest = inject_pebble_ids(site)

    # Manifest only contains the newly-injected id for the second <p>.
    assert len(manifest) == 1
    content = (site / "index.html").read_text(encoding="utf-8")
    assert 'pb-123abc' in content
    assert content.count("data-pebble-id=") == 2


def test_inject_is_idempotent(site):
    (site / "index.html").write_text("<h1>Hello</h1><h2>World</h2>", encoding="utf-8")
    first = inject_pebble_ids(site)
    first_content = (site / "index.html").read_text(encoding="utf-8")

    second = inject_pebble_ids(site)
    second_content = (site / "index.html").read_text(encoding="utf-8")

    assert set(first.keys()) == set(second.keys())
    assert first_content == second_content


def test_inject_prunes_orphans(site):
    (site / "a.html").write_text("<p>A</p>", encoding="utf-8")
    (site / "b.html").write_text("<p>B</p>", encoding="utf-8")
    manifest1 = inject_pebble_ids(site)
    assert len(manifest1) == 2

    # Delete one file and re-inject; the entry for it should be pruned.
    (site / "a.html").unlink()
    manifest2 = inject_pebble_ids(site)
    assert len(manifest2) == 1
    assert all(entry["file"] == "b.html" for entry in manifest2.values())


def test_inject_writes_manifest_to_dot_pebble_ids_json(site):
    (site / "x.html").write_text("<h1>X</h1>", encoding="utf-8")
    inject_pebble_ids(site)
    data = json.loads((site / ".pebble-ids.json").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert len(data) == 1


def test_inject_skips_non_target_tags(site):
    (site / "index.html").write_text(
        "<div><section><nav><h1>Title</h1></nav></section></div>",
        encoding="utf-8",
    )
    manifest = inject_pebble_ids(site)
    # Only the h1 is a TARGET_TAG.
    assert len(manifest) == 1
    assert list(manifest.values())[0]["tag"] == "h1"


def test_inject_preserves_existing_text_in_file(site):
    (site / "index.html").write_text(
        "<!doctype html><html><body><h1>Hello</h1></body></html>",
        encoding="utf-8",
    )
    inject_pebble_ids(site)
    content = (site / "index.html").read_text(encoding="utf-8")
    assert "<!doctype html>" in content
    assert ">Hello</h1>" in content


# ---- load_manifest ---------------------------------------------------------

def test_load_manifest_missing_returns_empty(site):
    assert load_manifest(site) == {}


def test_load_manifest_corrupt_returns_empty(site):
    (site / ".pebble-ids.json").write_text("{not json", encoding="utf-8")
    assert load_manifest(site) == {}


def test_load_manifest_non_dict_returns_empty(site):
    (site / ".pebble-ids.json").write_text("[1,2,3]", encoding="utf-8")
    assert load_manifest(site) == {}


def test_load_manifest_valid_roundtrip(site):
    (site / "index.html").write_text("<h1>Hi</h1>", encoding="utf-8")
    written = inject_pebble_ids(site)
    loaded = load_manifest(site)
    assert loaded == written


# ---- find_tag_open ---------------------------------------------------------

def test_find_tag_open_simple():
    text = '<p data-pebble-id="pb-abc123">Hello</p>'
    span = find_tag_open(text, "pb-abc123")
    assert span is not None
    open_start, open_end = span
    assert text[open_start:open_end] == '<p data-pebble-id="pb-abc123">'


def test_find_tag_open_with_other_attrs():
    text = '<a href="/x" data-pebble-id="pb-foo" className="link">go</a>'
    span = find_tag_open(text, "pb-foo")
    assert span is not None
    open_start, open_end = span
    assert text[open_start:open_end].startswith("<a ")
    assert text[open_start:open_end].endswith(">")


def test_find_tag_open_missing_returns_none():
    text = '<p data-pebble-id="pb-other">x</p>'
    assert find_tag_open(text, "pb-missing") is None


# ---- find_element_span -----------------------------------------------------

def test_find_element_span_simple():
    text = '<p data-pebble-id="pb-x">Hello</p>'
    span = find_element_span(text, "pb-x")
    assert span is not None
    open_start, open_end, close_start, close_end = span
    assert text[open_start:open_end] == '<p data-pebble-id="pb-x">'
    assert text[open_end:close_start] == "Hello"
    assert text[close_start:close_end] == "</p>"


def test_find_element_span_handles_nested_same_tag():
    text = '<span data-pebble-id="pb-outer">A <span>nested</span> B</span>'
    span = find_element_span(text, "pb-outer")
    assert span is not None
    _, open_end, close_start, _ = span
    assert text[open_end:close_start] == "A <span>nested</span> B"


def test_find_element_span_self_closing():
    text = '<img data-pebble-id="pb-img" src="x.png"/>'
    span = find_element_span(text, "pb-img")
    assert span is not None
    open_start, open_end, close_start, close_end = span
    assert open_end == close_start == close_end
    assert text[open_start:open_end].endswith("/>")


def test_find_element_span_unmatched_returns_none():
    text = '<p data-pebble-id="pb-x">unclosed'
    assert find_element_span(text, "pb-x") is None
