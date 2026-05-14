"""Raw-string validation for every check that does pattern matching.

Each check is exercised against a curated table of ``(case, files, expected)``
tuples. The goal is to catch false positives/negatives at write time, NOT
when a new build trips them in production. Specifically prompted by the
2026-05-14 ``no_css_smooth_scroll`` incident — a regex check shipped without
a comment-vs-declaration negative case and produced a self-defeating false
positive on every existing build.

Each parameterized case builds a minimal site directory with just the
named files, runs the check, asserts the status. No DNA / brief setup
beyond what each specific check needs.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pebble.evals import BuildContext, checks


def _make_minisite(root: Path, files: dict[str, str], brief: dict | None = None) -> Path:
    """Create a tmp site dir with just ``files`` (relative paths under site/).

    ``brief`` defaults to the minimum dna_display_font_honored needs.
    """
    site = root / "site"
    for rel, content in files.items():
        full = site / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
    (root / "brief.json").write_text(json.dumps(brief or {
        "_design_dna": "swiss_magazine",
    }))
    return root


# ---------------------------------------------------------------------------
# no_css_smooth_scroll — the canonical false-positive bait
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case,files,expected", [
    ("clean_auto", {"app/globals.css": "html { scroll-behavior: auto; }"}, "pass"),
    ("real_violation", {"app/globals.css": "html { scroll-behavior: smooth; }"}, "fail"),
    ("only_in_block_comment",
     {"app/globals.css": "/* Never set scroll-behavior: smooth — Lenis handles */"}, "pass"),
    ("block_comment_plus_auto",
     {"app/globals.css": "/* no scroll-behavior: smooth */\nhtml { scroll-behavior: auto !important; }"}, "pass"),
    ("only_in_line_comment",
     {"app/foo.tsx": "// reminder: don't write scroll-behavior: smooth here"}, "pass"),
    ("multiline_block_comment_with_violation_outside",
     {"app/globals.css": "/* a long\nmultiline comment */\nhtml { scroll-behavior: smooth; }"}, "fail"),
    ("next_artifact_ignored",
     {".next/static/css/app/layout.css": "html { scroll-behavior: smooth; }"}, "pass"),
    ("uppercase_match",
     {"app/globals.css": "html { Scroll-Behavior: SMOOTH; }"}, "fail"),
    ("whitespace_variations",
     {"app/globals.css": "html { scroll-behavior :   smooth ; }"}, "fail"),
])
def test_no_css_smooth_scroll_raw(tmp_path, case, files, expected):
    d = _make_minisite(tmp_path, files)
    ctx = BuildContext.load(d)
    assert checks.no_css_smooth_scroll(ctx).status == expected, case


# ---------------------------------------------------------------------------
# images_have_alt — Image regex sensitivity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case,files,expected", [
    ("no_images",
     {"app/page.tsx": "export default () => <main />;"}, "pass"),
    ("single_line_with_alt",
     {"app/page.tsx": 'import I from "next/image"; export default () => <Image src="/x.jpg" alt="hi" width={1} height={1} />;'}, "pass"),
    ("single_line_without_alt",
     {"app/page.tsx": 'import I from "next/image"; export default () => <Image src="/x.jpg" width={1} height={1} />;'}, "fail"),
    ("empty_alt_accepted",
     {"app/page.tsx": 'export default () => <Image src="/x.jpg" alt="" />;'}, "pass"),
    ("multi_line_image_with_alt",
     {"app/page.tsx": 'export default () => (\n  <Image\n    src="/x.jpg"\n    alt="hi"\n    width={100}\n    height={100}\n  />\n);'}, "pass"),
    ("multi_line_image_without_alt",
     {"app/page.tsx": 'export default () => (\n  <Image\n    src="/x.jpg"\n    width={100}\n    height={100}\n  />\n);'}, "fail"),
])
def test_images_have_alt_raw(tmp_path, case, files, expected):
    d = _make_minisite(tmp_path, files)
    ctx = BuildContext.load(d)
    assert checks.images_have_alt(ctx).status == expected, case


# ---------------------------------------------------------------------------
# scroll_trigger_ssr_safe — brace-depth scope tracker
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case,content,expected", [
    ("inside_useeffect", '"use client";\n'
        'import { useEffect } from "react";\n'
        'export const X = () => {\n'
        '  useEffect(() => {\n'
        '    ScrollTrigger.normalizeScroll(true);\n'
        '  }, []);\n'
        '  return null;\n'
        '};', "pass"),
    ("module_level", 'import { ScrollTrigger } from "gsap/ScrollTrigger";\n'
        'ScrollTrigger.normalizeScroll(true);\n'
        'export const X = () => null;', "fail"),
    ("module_level_config", 'ScrollTrigger.config({ ignoreMobileResize: true });\n'
        'export const X = () => null;', "fail"),
    ("inside_useeffect_then_module_level_other_file",
        # only this file matters; passes within the file's scope
        '"use client";\nimport { useEffect } from "react";\n'
        'export const Y = () => {\n'
        '  useEffect(() => { ScrollTrigger.config({}); }, []);\n'
        '};', "pass"),
    ("no_scrolltrigger_at_all",
        'export const Z = () => <div />;', "pass"),
])
def test_scroll_trigger_ssr_safe_raw(tmp_path, case, content, expected):
    d = _make_minisite(tmp_path, {"components/Motion.tsx": content})
    ctx = BuildContext.load(d)
    assert checks.scroll_trigger_ssr_safe(ctx).status == expected, case


# ---------------------------------------------------------------------------
# html_lang_attr — exact lang= pattern
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case,content,expected", [
    ("lang_en", '<html lang="en"><body /></html>', "pass"),
    ("lang_with_extra_attrs", '<html lang="es" className="dark"><body /></html>', "pass"),
    ("no_lang", '<html><body /></html>', "fail"),
    ("lang_in_body_only", '<html><body lang="en" /></html>', "fail"),
    ("lang_with_whitespace", '<html  lang = "en" ><body /></html>', "pass"),
])
def test_html_lang_attr_raw(tmp_path, case, content, expected):
    d = _make_minisite(tmp_path, {"app/layout.tsx": f'export default () => ({content});'})
    ctx = BuildContext.load(d)
    assert checks.html_lang_attr(ctx).status == expected, case


# ---------------------------------------------------------------------------
# dna_display_font_honored — space + underscore form matching
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case,layout_content,expected", [
    ("space_form_in_css",
        # font is in globals.css instead, layout is bare
        None, "pass"),  # special-cased below
    ("underscore_form_via_next_font",
        'import { Cormorant_Garamond } from "next/font/google";\n'
        'const cg = Cormorant_Garamond({ subsets: ["latin"] });\n'
        'export default () => <html lang="en"><body /></html>;', "pass"),
    ("camelcase_only_no_match",
        # camelCase variable but no Cormorant_Garamond / Cormorant Garamond literal
        'const cormorantGaramond = "foo";\n'
        'export default () => <html lang="en"><body /></html>;', "fail"),
    ("wrong_font_only",
        'export default () => <html lang="en"><body /></html>;', "fail"),
])
def test_dna_display_font_honored_raw(tmp_path, case, layout_content, expected):
    if case == "space_form_in_css":
        # Verify the space form match path via globals.css
        d = _make_minisite(tmp_path, {
            "app/globals.css": "body { font-family: 'Cormorant Garamond', serif; }",
            "app/layout.tsx": "export default () => <html lang='en' />;",
        })
    else:
        d = _make_minisite(tmp_path, {
            "app/layout.tsx": layout_content,
            "app/globals.css": "body { font-family: 'Inter', sans-serif; }",
        })
    ctx = BuildContext.load(d)
    assert checks.dna_display_font_honored(ctx).status == expected, case


# ---------------------------------------------------------------------------
# Metadata sanity — every check in ALL_CHECKS has either static_files,
# details_file_key, or both set to defaults. Catches missing @check_metadata.
# ---------------------------------------------------------------------------

def test_every_check_has_metadata():
    """A check missing @check_metadata wouldn't crash, but would silently
    have no file hints — exactly the bug that motivated the metadata
    refactor in the first place. Assert the decorator was applied."""
    for fn in checks.ALL_CHECKS:
        assert hasattr(fn, "static_files"), f"{fn.__name__} missing @check_metadata"
        assert hasattr(fn, "details_file_key"), f"{fn.__name__} missing @check_metadata"


# ---------------------------------------------------------------------------
# FOUNDATION CHECKS (May 2026 overhaul — VEX-spec hero pattern)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case,files,expected", [
    ("video_in_hero_component",
     {"components/sections/Hero.tsx": '<video autoPlay muted loop playsInline src="/x.mp4" />'}, "pass"),
    ("video_in_page",
     {"app/page.tsx": 'export default () => <video autoPlay muted loop src="/x.mp4" />'}, "pass"),
    ("video_with_react_style_autoPlay",
     {"components/sections/Hero.tsx": '<video autoPlay={true} src="/x.mp4" />'}, "pass"),
    ("no_video_anywhere",
     {"app/page.tsx": 'export default () => <div>just text</div>'}, "fail"),
    ("video_without_autoplay",
     {"app/page.tsx": '<video controls src="/x.mp4" />'}, "fail"),
])
def test_hero_uses_background_video_raw(tmp_path, case, files, expected):
    d = _make_minisite(tmp_path, files)
    ctx = BuildContext.load(d)
    assert checks.hero_uses_background_video(ctx).status == expected, case


@pytest.mark.parametrize("case,hero_content,expected", [
    ("no_overlay_clean",
     '<section><video autoPlay src="/x.mp4" /><h1>Hi</h1></section>', "pass"),
    ("bg_black_40_overlay",
     '<section><video autoPlay src="/x.mp4" /><div className="absolute inset-0 bg-black/40" /></section>', "fail"),
    ("gradient_from_black_overlay",
     '<section><video autoPlay src="/x.mp4" /><div className="bg-gradient-to-b from-black/60 to-transparent" /></section>', "fail"),
    ("rgba_overlay",
     '<section><video autoPlay src="/x.mp4" /><div className="bg-[rgba(0,0,0,0.5)]" /></section>', "fail"),
    ("mix_blend_multiply",
     '<section><video autoPlay src="/x.mp4" /><div className="mix-blend-multiply" /></section>', "fail"),
    ("overlay_only_in_comment",
     '<section><video autoPlay src="/x.mp4" />{/* never bg-black/40 */}<h1>Hi</h1></section>', "pass"),
])
def test_no_dark_overlay_on_hero_video_raw(tmp_path, case, hero_content, expected):
    d = _make_minisite(tmp_path, {"components/sections/Hero.tsx": hero_content})
    ctx = BuildContext.load(d)
    assert checks.no_dark_overlay_on_hero_video(ctx).status == expected, case


@pytest.mark.parametrize("case,layout_content,expected", [
    ("clean_inter_import_with_classname",
     'import { Inter } from "next/font/google"; const inter = Inter({}); export default (p:any) => <html className={inter.variable} />;', "pass"),
    ("no_inter_import",
     'export default (p:any) => <html />;', "fail"),
    ("inter_imported_but_not_applied",
     'import { Inter } from "next/font/google"; export default (p:any) => <html />;', "fail"),
    ("wrong_font_imported",
     'import { Roboto } from "next/font/google"; const roboto = Roboto({}); export default (p:any) => <html className={roboto.variable} />;', "fail"),
])
def test_inter_font_global_raw(tmp_path, case, layout_content, expected):
    d = _make_minisite(tmp_path, {"app/layout.tsx": layout_content})
    ctx = BuildContext.load(d)
    assert checks.inter_font_global(ctx).status == expected, case


@pytest.mark.parametrize("case,css,expected", [
    ("with_backdrop_filter",
     ".liquid-glass { background: rgba(0,0,0,0.4); backdrop-filter: blur(4px); }", "pass"),
    ("without_backdrop_filter",
     ".liquid-glass { background: rgba(0,0,0,0.4); }", "fail"),
    ("missing_class_entirely",
     ".something-else { color: red; }", "fail"),
])
def test_liquid_glass_class_present_raw(tmp_path, case, css, expected):
    d = _make_minisite(tmp_path, {"app/globals.css": css})
    ctx = BuildContext.load(d)
    assert checks.liquid_glass_class_present(ctx).status == expected, case


def test_animation_components_present_pass(tmp_path):
    d = _make_minisite(tmp_path, {
        "components/ui/AnimatedHeading.tsx": "export function AnimatedHeading(){return null;}",
        "components/ui/FadeIn.tsx": "export function FadeIn(){return null;}",
    })
    ctx = BuildContext.load(d)
    assert checks.animation_components_present(ctx).status == "pass"


def test_animation_components_present_fail_missing_one(tmp_path):
    d = _make_minisite(tmp_path, {
        "components/ui/AnimatedHeading.tsx": "export function AnimatedHeading(){return null;}",
    })
    ctx = BuildContext.load(d)
    r = checks.animation_components_present(ctx)
    assert r.status == "fail"
    assert "FadeIn.tsx" in str(r.details["missing"])


@pytest.mark.parametrize("case,css,expected", [
    ("clean_rule",
     "@media (prefers-reduced-motion: reduce) { * { transition-duration: 0.01ms; } }", "pass"),
    ("no_rule",
     "body { margin: 0; }", "fail"),
])
def test_prefers_reduced_motion_respected_raw(tmp_path, case, css, expected):
    d = _make_minisite(tmp_path, {"app/globals.css": css})
    ctx = BuildContext.load(d)
    assert checks.prefers_reduced_motion_respected(ctx).status == expected, case
