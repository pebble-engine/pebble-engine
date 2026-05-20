"""Comparison-harness tests (Phase 14b, 2026-05-20).

The harness lets us measure prompt diet effectiveness by sending the same
brief through Pebble's full prompt + a playground-style mini prompt and
diffing the outputs. Tests cover prompt construction, response analysis,
and the dry-run path (no LLM cost).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pebble.compare_prompts import (
    PromptRun,
    analyze_response,
    build_pebble_prompt,
    build_playground_prompt,
    cli,
    render_report,
)


# ------------------------------------------------------------------ #
# build_playground_prompt — the lean prompt                            #
# ------------------------------------------------------------------ #

def _brief():
    return {
        "business_name": "Onyx Properties",
        "business_type": "Luxury real estate brokerage",
        "location": "Manhattan, NY",
        "audience": "high net worth individuals",
        "brand_tone": "confident, premium",
    }


def _dna():
    return {
        "label": "Cinematic IMAX",
        "feel": "Movie poster meets product page — bold, sharp, dramatic.",
        "display_font": "Unbounded",
        "body_font": "Inter",
        "palette_posture": "Dark surfaces #0A0A0A / vermilion accent #FF3A1F / pure white text",
    }


def _layout():
    return {
        "label": "Gradient Mesh",
        "feel": "Contemporary product site with ambient gradient hero",
    }


def test_playground_prompt_includes_brief_facts():
    system, user = build_playground_prompt(_brief(), _dna(), _layout())
    for needle in ["Onyx Properties", "Luxury real estate", "Manhattan", "high net worth"]:
        assert needle in user, f"missing brief fact: {needle!r}"


def test_playground_prompt_includes_dna_details():
    _, user = build_playground_prompt(_brief(), _dna(), _layout())
    assert "Cinematic IMAX" in user
    assert "Unbounded" in user
    assert "#FF3A1F" in user  # vermilion accent hex extracted from palette_posture


def test_playground_prompt_is_short():
    """The whole point of this prompt is being short. Must stay under ~3K
    chars (~750 tokens) so it can be honestly compared to playground use."""
    system, user = build_playground_prompt(_brief(), _dna(), _layout())
    assert len(system) + len(user) < 3500, (
        f"playground prompt too long ({len(system) + len(user)} chars); "
        f"defeats the lean-prompt thesis"
    )


def test_playground_prompt_handles_missing_dna():
    """If DNA isn't resolved, the prompt should still build with a
    designer's-choice fallback rather than crashing."""
    _, user = build_playground_prompt(_brief(), None, None)
    assert "Onyx Properties" in user  # brief facts still there


# ------------------------------------------------------------------ #
# build_pebble_prompt — wraps the engine                               #
# ------------------------------------------------------------------ #

def test_pebble_prompt_invokes_engine():
    """Pebble's full path should produce a substantially LONGER prompt
    than the playground path (that's what the diet measures against)."""
    system_p, user_p = build_playground_prompt(_brief(), _dna(), _layout())
    system_e, user_e = build_pebble_prompt(_brief())
    assert len(user_e) > len(user_p) * 3, (
        f"Pebble full prompt should be >>3x playground; "
        f"got pebble={len(user_e)}, playground={len(user_p)}"
    )


# ------------------------------------------------------------------ #
# analyze_response — pattern detection                                 #
# ------------------------------------------------------------------ #

def test_analyze_counts_files_emitted():
    fake_response = (
        '<pebble-file path="app/page.tsx">\nbody\n</pebble-file>\n'
        '<pebble-file path="app/layout.tsx">\nbody\n</pebble-file>\n'
        '<pebble-file path="components/Hero.tsx">\nbody\n</pebble-file>'
    )
    run = analyze_response("test", fake_response, system_chars=100, user_chars=200, elapsed=1.5)
    assert run.files_emitted == 3
    assert "app/page.tsx" in run.file_list


def test_analyze_detects_real_image_urls():
    with_unsplash = '<img src="https://images.unsplash.com/photo-1234567?auto=format" />'
    with_pexels = '<img src="https://images.pexels.com/photos/1234/pexels-photo-1234.jpeg?w=800" />'
    without = '<img src="/images/about/owner.jpg" />'

    assert analyze_response("a", with_unsplash, 0, 0, 0).has_real_image_urls is True
    assert analyze_response("b", with_pexels,    0, 0, 0).has_real_image_urls is True
    assert analyze_response("c", without,         0, 0, 0).has_real_image_urls is False


def test_analyze_detects_custom_css_tokens():
    with_tokens = ":root { --color-bg: #0A0A0A; --color-text: #fff; }"
    without = "body { background: black; }"
    assert analyze_response("a", with_tokens, 0, 0, 0).has_custom_css_tokens is True
    assert analyze_response("b", without,     0, 0, 0).has_custom_css_tokens is False


def test_analyze_detects_tailwind_config_extension():
    with_ext = "tailwind.config = { theme: { extend: { colors: { bg: '#000' } } } }"
    without = "tailwind.config = { content: ['./**/*.tsx'] }"
    assert analyze_response("a", with_ext, 0, 0, 0).has_tailwind_config_extension is True
    assert analyze_response("b", without,  0, 0, 0).has_tailwind_config_extension is False


def test_analyze_detects_gsap_wired():
    with_gsap = 'import { gsap } from "gsap"; gsap.registerPlugin(ScrollTrigger);'
    without = "useEffect(() => { ... });"
    assert analyze_response("a", with_gsap, 0, 0, 0).has_gsap_wired is True
    assert analyze_response("b", without,   0, 0, 0).has_gsap_wired is False


def test_analyze_detects_resend_server_action():
    with_resend = 'const resend = new Resend(process.env.RESEND_API_KEY); resend.emails.send({...})'
    without = "console.log('not an email')"
    assert analyze_response("a", with_resend, 0, 0, 0).has_resend_server_action is True
    assert analyze_response("b", without,     0, 0, 0).has_resend_server_action is False


def test_analyze_detects_schema_jsonld():
    with_schema = '<script type="application/ld+json">{"@context":"https://schema.org",...}</script>'
    without = "<head><title>X</title></head>"
    assert analyze_response("a", with_schema, 0, 0, 0).has_schema_jsonld is True
    assert analyze_response("b", without,     0, 0, 0).has_schema_jsonld is False


# ------------------------------------------------------------------ #
# render_report — markdown shape                                       #
# ------------------------------------------------------------------ #

def test_render_report_includes_both_runs():
    runs = [
        PromptRun(label="Playground", files_emitted=8, has_real_image_urls=True),
        PromptRun(label="Pebble",     files_emitted=12, has_real_image_urls=False),
    ]
    report = render_report(_brief(), runs)
    assert "Playground" in report
    assert "Pebble" in report
    assert "Onyx Properties" in report  # brief facts in the report


def test_render_report_is_markdown():
    runs = [PromptRun(label="X", files_emitted=1)]
    report = render_report(_brief(), runs)
    # Has a markdown table
    assert "| Path |" in report
    assert "|---|" in report


# ------------------------------------------------------------------ #
# CLI — dry-run path (no LLM cost)                                     #
# ------------------------------------------------------------------ #

def test_cli_dry_run_writes_report(tmp_path, monkeypatch, capsys):
    """End-to-end smoke: write a brief, invoke CLI with --dry-run, verify
    the report file exists and contains both runs."""
    brief_file = tmp_path / "brief.json"
    brief_data = {**_brief(), "_slug": "test-dry-run"}
    brief_file.write_text(json.dumps(brief_data), encoding="utf-8")

    # Redirect output/ to tmp
    monkeypatch.chdir(tmp_path)

    rc = cli([str(brief_file), "--dry-run"])
    assert rc == 0

    report_path = tmp_path / "output" / "test-dry-run" / "compare_prompts_report.md"
    assert report_path.exists()
    report = report_path.read_text(encoding="utf-8")
    assert "Playground" in report
    assert "Pebble" in report
    # Stdout should also have the report
    captured = capsys.readouterr()
    assert "compare" in captured.out.lower() or "playground" in captured.out.lower()
