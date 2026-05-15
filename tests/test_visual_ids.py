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
    repair_mangled_files,
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


# ---- JSX expression containers (the > inside =>, {{...}}, etc) ------------
#
# Regression for the 2026-05-15 Navbar bug: the old regex matched
# `\s[^<>]*?` for attrs, which mistakes the `>` inside an arrow function
# `() =>` for the tag close. The injection then sliced through the arrow,
# producing `onClick={() = data-pebble-id="pb-..."> doStuff()}` and
# crashing the next dev compile with "Expected '</', got '='".


def test_inject_preserves_arrow_function_in_onclick(site):
    """The bug: `onClick={() => setOpen(true)}` got mangled to
    `onClick={() = data-pebble-id="pb-xxx"> setOpen(true)}`."""
    src = (
        'export default function X(){\n'
        '  return <button className="x" onClick={() => setOpen(true)}>Go</button>;\n'
        '}\n'
    )
    (site / "page.tsx").write_text(src, encoding="utf-8")
    inject_pebble_ids(site)
    out = (site / "page.tsx").read_text(encoding="utf-8")
    # The arrow function must survive untouched.
    assert "() => setOpen(true)" in out
    # The data-pebble-id must land OUTSIDE the arrow, before the real tag close.
    assert 'onClick={() => setOpen(true)}' in out
    # The tag still gets a pebble-id (just at the right spot).
    assert "data-pebble-id=" in out


def test_inject_preserves_arrow_function_with_param(site):
    """Variant with a parameter: ``(e) => fn(e)``."""
    src = '<button onClick={(e) => handle(e)}>X</button>'
    (site / "page.tsx").write_text(src, encoding="utf-8")
    inject_pebble_ids(site)
    out = (site / "page.tsx").read_text(encoding="utf-8")
    assert "(e) => handle(e)" in out


def test_inject_preserves_nested_braces_in_style_prop(site):
    """``style={{color: "red"}}`` has nested braces; the scanner must
    track depth, not bail at the first ``}``."""
    src = '<p style={{color: "red", fontSize: 14}}>Hi</p>'
    (site / "page.tsx").write_text(src, encoding="utf-8")
    inject_pebble_ids(site)
    out = (site / "page.tsx").read_text(encoding="utf-8")
    assert '{{color: "red", fontSize: 14}}' in out


def test_inject_handles_gt_inside_quoted_attribute_value(site):
    """``>`` inside a quoted attr (e.g. URL with a query string) shouldn't
    close the tag early."""
    src = '<a href="https://example.com/?q=>foo">link</a>'
    (site / "page.tsx").write_text(src, encoding="utf-8")
    inject_pebble_ids(site)
    out = (site / "page.tsx").read_text(encoding="utf-8")
    assert 'href="https://example.com/?q=>foo"' in out


def test_inject_handles_template_literal_in_classname(site):
    """``className={`flex ${cond && 'on'}`}`` uses template literals;
    backticks must be treated as string delimiters."""
    src = "<span className={`flex ${active && 'on'}`}>Hi</span>"
    (site / "page.tsx").write_text(src, encoding="utf-8")
    inject_pebble_ids(site)
    out = (site / "page.tsx").read_text(encoding="utf-8")
    assert "${active && 'on'}" in out


def test_inject_handles_multiline_attrs_with_arrow(site):
    """The original Navbar case: multi-line attrs, arrow function in
    onClick, tag close on its own line."""
    src = (
        '<button\n'
        '  className="md:hidden p-2"\n'
        '  onClick={() => setIsMobileMenuOpen(true)}\n'
        '  aria-label="Open Menu"\n'
        '>X</button>\n'
    )
    (site / "page.tsx").write_text(src, encoding="utf-8")
    inject_pebble_ids(site)
    out = (site / "page.tsx").read_text(encoding="utf-8")
    # Arrow intact
    assert "onClick={() => setIsMobileMenuOpen(true)}" in out
    # aria-label still present at the right position
    assert 'aria-label="Open Menu"' in out
    # Tag still got a pebble-id
    assert "data-pebble-id=" in out


# ---- repair_mangled_files (recovery for sites built before the fix) -------

def test_repair_restores_arrow_in_corrupted_file(site):
    """The exact pattern Marc hit in his Navbar.tsx — repair must
    restore the arrow and the file must then compile."""
    corrupted = (
        'export default function Nav(){\n'
        '  return <button\n'
        '    className="md:hidden p-2"\n'
        '    onClick={() = data-pebble-id="pb-613d12"> setIsMobileMenuOpen(true)}\n'
        '    aria-label="Open Menu"\n'
        '  >X</button>;\n'
        '}\n'
    )
    (site / "Navbar.tsx").write_text(corrupted, encoding="utf-8")
    n = repair_mangled_files(site)
    assert n == 1
    out = (site / "Navbar.tsx").read_text(encoding="utf-8")
    assert "onClick={() => setIsMobileMenuOpen(true)}" in out
    # The broken pebble-id is dropped; the next inject will add a fresh one.
    assert "pb-613d12" not in out


def test_repair_prunes_orphan_manifest_entries(site):
    """After repair, the orphaned manifest entries are removed so the
    next inject doesn't think the tag is still tagged."""
    corrupted = '<button onClick={() = data-pebble-id="pb-aabbcc"> doX()}>X</button>'
    (site / "page.tsx").write_text(corrupted, encoding="utf-8")
    # Seed a manifest as if the corrupt inject had run.
    (site / ".pebble-ids.json").write_text(
        json.dumps({"pb-aabbcc": {"file": "page.tsx", "tag": "button", "original_text": ""}}),
        encoding="utf-8",
    )
    repair_mangled_files(site)
    manifest = load_manifest(site)
    assert "pb-aabbcc" not in manifest


def test_repair_is_noop_on_clean_files(site):
    """No mangled patterns → no rewrites, no orphan pruning."""
    (site / "page.tsx").write_text(
        '<button onClick={() => doX()}>X</button>',
        encoding="utf-8",
    )
    assert repair_mangled_files(site) == 0


def test_repair_then_reinject_yields_working_pebble_id(site):
    """End-to-end: corrupt input → repair → inject_pebble_ids = a clean
    file with a proper data-pebble-id on the button."""
    corrupted = '<button onClick={() = data-pebble-id="pb-aabbcc"> doX()}>X</button>'
    (site / "page.tsx").write_text(corrupted, encoding="utf-8")
    repair_mangled_files(site)
    manifest = inject_pebble_ids(site)
    out = (site / "page.tsx").read_text(encoding="utf-8")
    # Arrow restored, fresh pebble-id at a valid position.
    assert "onClick={() => doX()}" in out
    assert "data-pebble-id=" in out
    # Old id gone, new id present.
    assert "pb-aabbcc" not in out
    assert any(pid.startswith("pb-") for pid in manifest)


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
