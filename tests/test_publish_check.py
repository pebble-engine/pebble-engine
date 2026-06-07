"""Tests for pebble.publish_check — the publish-time transparency guard.

It scans a generated site for leftover placeholders / sample content
([BUSINESS PHONE], bracketed "[Add a review…]" slots, sample-review
phrases) so the publish flow can warn a non-technical owner BEFORE they
ship fake-looking or unfinished content. The point: transparency that
doesn't depend on the owner reading a reminder — and a trust feature
Lovable doesn't have.

Design:
- find_placeholders(text, loose=...) — loose=True applies the generic
  bracket pattern (for content/*.ts data files where brackets are always
  placeholders); loose=False matches only explicit contact tokens +
  sample phrases (for .tsx/.ts code files, to avoid flagging array
  destructuring like `const [a, b] = ...`).
- scan_site(site_dir) — walks the build, applies the right mode per file.
- publish_readiness(site_dir) — {ready, count, items, message}.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from pebble import publish_check as pc


# ---- find_placeholders ------------------------------------------------ #

def test_finds_explicit_contact_token_in_loose_and_strict():
    for loose in (True, False):
        hits = pc.find_placeholders('phone: "[BUSINESS PHONE]"', loose=loose)
        assert any(h["token"] == "[BUSINESS PHONE]" for h in hits)
        assert any(h["kind"] == "contact" for h in hits)


def test_loose_finds_generic_bracket_placeholder():
    hits = pc.find_placeholders('"[Add a review from a happy customer]"', loose=True)
    assert any("Add a review" in h["token"] for h in hits)


def test_strict_does_not_flag_code_destructuring():
    # In a .tsx code file, array destructuring must NOT be flagged.
    code = "const [open, setOpen] = useState(false);\nconst x = arr[0];"
    hits = pc.find_placeholders(code, loose=False)
    assert hits == []


def test_loose_does_not_flag_short_code_brackets():
    # Even in loose mode, single-letter / numeric brackets aren't placeholders.
    assert pc.find_placeholders("x = a[0]; y = b[i];", loose=True) == []


def test_detects_sample_phrases_case_insensitive():
    for phrase in ("Replace me", "your happy customer", "SAMPLE REVIEW", "Lorem ipsum"):
        hits = pc.find_placeholders(f"text {phrase} here", loose=False)
        assert hits, f"expected to flag sample phrase {phrase!r}"
        assert any(h["kind"] == "sample" for h in hits)


def test_clean_copy_produces_no_hits():
    clean = 'export const HERO = "Pest control that respects your home.";'
    assert pc.find_placeholders(clean, loose=True) == []


def test_detects_metric_placeholders_both_modes():
    # The exact labeled placeholders the content-swap prompt emits for
    # missing social-proof numbers ([rating], [# of reviews]).
    for loose in (True, False):
        for txt in ('export const RATING_VALUE = "[rating]";',
                    'export const RATING_COUNT = "[# of reviews]";'):
            hits = pc.find_placeholders(txt, loose=loose)
            assert hits, f"missed metric placeholder in {txt!r} (loose={loose})"


def test_skips_convention_comment_lines():
    # site.ts ships a JSDoc convention doc that literally says
    # "[SQUARE BRACKETS]" — that's documentation, not content. Must NOT flag.
    doc = " * Convention for unknown data: use placeholder strings in [SQUARE BRACKETS]."
    assert pc.find_placeholders(doc, loose=True) == []
    assert pc.find_placeholders("// TODO: handle [edge case] here", loose=True) == []


# ---- scan_site + publish_readiness ------------------------------------ #

def _make_site(tmp_path: Path, files: dict[str, str]) -> Path:
    site = tmp_path / "site"
    for rel, body in files.items():
        p = site / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    return site


def test_scan_site_flags_content_brackets_and_contact_tokens(tmp_path):
    site = _make_site(tmp_path, {
        "content/site.ts": 'export const PHONE = "[BUSINESS PHONE]";\n'
                            'export const REVIEW = "[Add your best customer review here]";',
        "components/sections/Hero.tsx": "const [open, setOpen] = useState(false);",  # must NOT flag
    })
    items = pc.scan_site(site)
    tokens = [i["token"] for i in items]
    assert any("BUSINESS PHONE" in t for t in tokens)
    assert any("Add your best customer review" in t for t in tokens)
    # destructuring in the tsx file is not a placeholder
    assert not any("open" in t for t in tokens)
    # every item carries file + line
    assert all("file" in i and "line" in i for i in items)


def test_publish_readiness_not_ready_when_placeholders_present(tmp_path):
    site = _make_site(tmp_path, {
        "content/site.ts": 'export const PHONE = "[BUSINESS PHONE]";',
    })
    r = pc.publish_readiness(site)
    assert r["ready"] is False
    assert r["count"] >= 1
    assert isinstance(r["message"], str) and r["message"]
    assert r["items"]


def test_publish_readiness_ready_when_clean(tmp_path):
    site = _make_site(tmp_path, {
        "content/site.ts": 'export const HERO = "Pest control that respects your home.";',
        "app/page.tsx": "export default function Page(){ return null; }",
    })
    r = pc.publish_readiness(site)
    assert r["ready"] is True
    assert r["count"] == 0


def test_publish_readiness_handles_missing_dir(tmp_path):
    r = pc.publish_readiness(tmp_path / "does-not-exist")
    assert r["ready"] is True  # nothing to flag; fail-open, never block on our own error
    assert r["count"] == 0


def test_does_not_flag_js_array_literals():
    # A real service-area array is content, not a placeholder.
    txt = 'export const AREAS = ["Portland", "Portland Metro", "Beaverton"];'
    assert pc.find_placeholders(txt, loose=True) == []
