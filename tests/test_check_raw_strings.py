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


# ---------------------------------------------------------------------------
# FOUNDATION A11Y / LEGIBILITY ADDENDUM (May 2026 NLM cross-check follow-up)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case,content,expected", [
    ("both_markers_present",
     '<h1><span className="sr-only">{text}</span><span aria-hidden="true">animated</span></h1>', "pass"),
    ("missing_sr_only",
     '<h1><span aria-hidden="true">{text}</span></h1>', "fail"),
    ("missing_aria_hidden",
     '<h1><span className="sr-only">{text}</span>{text}</h1>', "fail"),
    ("missing_both",
     '<h1>{text}</h1>', "fail"),
    ("comment_mentioning_markers_doesnt_satisfy",
     '/* sr-only + aria-hidden are needed here */\n<h1>{text}</h1>', "fail"),
    ("aria_hidden_as_curly_true",
     '<h1><span className="sr-only">{text}</span><span aria-hidden={true}>x</span></h1>', "pass"),
])
def test_animated_heading_screen_reader_safe_raw(tmp_path, case, content, expected):
    d = _make_minisite(tmp_path, {"components/ui/AnimatedHeading.tsx": content})
    ctx = BuildContext.load(d)
    assert checks.animated_heading_screen_reader_safe(ctx).status == expected, case


def test_animated_heading_screen_reader_safe_skips_when_file_absent(tmp_path):
    """When the AnimatedHeading file doesn't exist at all, the check fails
    explicitly (not skip) — the file is a foundation contract artifact."""
    d = _make_minisite(tmp_path, {"app/page.tsx": "export default () => null;"})
    ctx = BuildContext.load(d)
    r = checks.animated_heading_screen_reader_safe(ctx)
    assert r.status == "fail"
    assert "missing" in r.message.lower()


@pytest.mark.parametrize("case,files,expected", [
    ("hero_link_with_focus_visible",
     {"components/sections/Hero.tsx": '<a href="/x" className="bg-white focus-visible:ring-2 focus-visible:ring-white/70">Go</a>'}, "pass"),
    ("hero_link_without_focus_visible",
     {"components/sections/Hero.tsx": '<a href="/x" className="bg-white text-black px-8 py-3 rounded-lg">Go</a>'}, "fail"),
    ("button_without_focus_visible",
     {"components/sections/Hero.tsx": '<button className="bg-blue">Click</button>'}, "fail"),
    ("link_without_className_is_skipped",
     {"components/sections/Hero.tsx": '<a href="/x">Go</a>'}, "pass"),
    ("focus_without_visible_modifier_also_accepted",
     {"components/sections/Hero.tsx": '<a href="/x" className="bg-white focus:ring-2 focus:ring-white">Go</a>'}, "pass"),
    ("multiline_link_with_focus_visible",
     {"components/sections/Hero.tsx": '<a\n  href="/x"\n  className="bg-white\n    focus-visible:ring-2"\n>Go</a>'}, "pass"),
    ("navbar_link_in_layout_dir",
     {"components/layout/Navbar.tsx": '<a href="/x" className="text-white focus-visible:ring-2 focus-visible:ring-white">Nav</a>'}, "pass"),
    ("navbar_link_missing_focus",
     {"components/layout/Navbar.tsx": '<a href="/x" className="text-white">Nav</a>'}, "fail"),
    ("offending_element_in_page_tsx_caught",
     {"app/page.tsx": '<button className="bg-red">Boom</button>'}, "fail"),
    ("closing_tags_dont_match",
     {"components/sections/Hero.tsx": 'Some text </a> more </button> end.'}, "pass"),
])
def test_interactive_elements_have_focus_visible_raw(tmp_path, case, files, expected):
    d = _make_minisite(tmp_path, files)
    ctx = BuildContext.load(d)
    assert checks.interactive_elements_have_focus_visible(ctx).status == expected, case


def test_interactive_elements_have_focus_visible_skips_when_no_targets(tmp_path):
    """No hero/navbar files at all → skip, not fail."""
    d = _make_minisite(tmp_path, {"app/layout.tsx": "export default () => null;"})
    ctx = BuildContext.load(d)
    assert checks.interactive_elements_have_focus_visible(ctx).status == "skip"


@pytest.mark.parametrize("case,files,expected", [
    ("textshadow_inline_in_animated_heading",
     {"components/ui/AnimatedHeading.tsx": '<h1 style={{ textShadow: "0 2px 24px rgba(0,0,0,0.5)" }}>{text}</h1>'}, "pass"),
    ("textshadow_in_hero",
     {"components/sections/Hero.tsx": '<p style={{ textShadow: "0 2px 16px rgba(0,0,0,0.5)" }}>sub</p>'}, "pass"),
    ("drop_shadow_tailwind_utility",
     {"components/sections/Hero.tsx": '<h1 className="drop-shadow-2xl">Title</h1>'}, "pass"),
    ("drop_shadow_arbitrary_value",
     {"components/sections/Hero.tsx": '<h1 className="drop-shadow-[0_2px_24px_rgba(0,0,0,0.5)]">Title</h1>'}, "pass"),
    ("none_anywhere",
     {"components/sections/Hero.tsx": '<h1>plain title</h1>'}, "fail"),
    ("only_in_comment",
     {"components/sections/Hero.tsx": '/* would normally need textShadow here */\n<h1>plain</h1>'}, "fail"),
    ("found_in_page_tsx",
     {"app/page.tsx": 'export default () => <h1 style={{ textShadow: "0 1px 2px black" }}>X</h1>'}, "pass"),
])
def test_hero_text_has_legibility_safeguard_raw(tmp_path, case, files, expected):
    d = _make_minisite(tmp_path, files)
    ctx = BuildContext.load(d)
    assert checks.hero_text_has_legibility_safeguard(ctx).status == expected, case


@pytest.mark.parametrize("case,content,expected", [
    ("video_with_poster",
     '<video autoPlay muted loop playsInline src="/x.mp4" poster="/p.jpg" />', "pass"),
    ("video_without_poster",
     '<video autoPlay muted loop playsInline src="/x.mp4" />', "fail"),
    ("multiline_video_with_poster",
     '<video\n  autoPlay\n  muted\n  loop\n  src="/x.mp4"\n  poster="/p.jpg"\n/>', "pass"),
    ("multiline_video_no_poster",
     '<video\n  autoPlay\n  muted\n  loop\n  src="/x.mp4"\n/>', "fail"),
    ("non_autoplay_video_skipped",
     '<video controls src="/x.mp4" />', "skip"),
])
def test_hero_video_has_poster_raw(tmp_path, case, content, expected):
    d = _make_minisite(tmp_path, {"components/sections/Hero.tsx": content})
    ctx = BuildContext.load(d)
    assert checks.hero_video_has_poster(ctx).status == expected, case


# ---------------------------------------------------------------------------
# FOUNDATION FUNCTIONALITY: contact form Server Action + Resend dep
# (May 2026 Base44/Lovable competitive addendum)
# ---------------------------------------------------------------------------

def _contact_form_files(action_body: str | None, form_body: str | None) -> dict[str, str]:
    """Helper: produce the minimal {action, form} pair given two bodies.
    Pass None for either to OMIT the file entirely."""
    out: dict[str, str] = {}
    if action_body is not None:
        out["app/actions/contact.ts"] = action_body
    if form_body is not None:
        out["components/forms/ContactForm.tsx"] = form_body
    return out


def test_contact_form_uses_server_action_passes_when_both_present(tmp_path):
    d = _make_minisite(tmp_path, _contact_form_files(
        '"use server";\nexport async function submitContactForm() { return { ok: true }; }',
        '"use client";\nimport { submitContactForm } from "@/app/actions/contact";\nexport function ContactForm(){ return <form />; }',
    ))
    ctx = BuildContext.load(d)
    assert checks.contact_form_uses_server_action(ctx).status == "pass"


def test_contact_form_uses_server_action_passes_with_useActionState_only(tmp_path):
    """A form that only mentions useActionState (no explicit import path) is
    still considered wired — useActionState requires a server-side action."""
    d = _make_minisite(tmp_path, _contact_form_files(
        '"use server";\nexport async function submitContactForm() { return { ok: true }; }',
        '"use client";\nimport { useActionState } from "react";\nexport function ContactForm(){ return null; }',
    ))
    ctx = BuildContext.load(d)
    assert checks.contact_form_uses_server_action(ctx).status == "pass"


def test_contact_form_uses_server_action_fails_when_action_file_missing(tmp_path):
    d = _make_minisite(tmp_path, _contact_form_files(
        None,
        '"use client";\nimport { useActionState } from "react";\nexport function ContactForm(){}',
    ))
    ctx = BuildContext.load(d)
    r = checks.contact_form_uses_server_action(ctx)
    assert r.status == "fail"
    assert "app/actions/contact.ts" in r.details["missing"]


def test_contact_form_uses_server_action_fails_when_form_file_missing(tmp_path):
    d = _make_minisite(tmp_path, _contact_form_files(
        '"use server";\nexport async function submitContactForm() { return { ok: true }; }',
        None,
    ))
    ctx = BuildContext.load(d)
    r = checks.contact_form_uses_server_action(ctx)
    assert r.status == "fail"
    assert "components/forms/ContactForm.tsx" in r.details["missing"]


def test_contact_form_uses_server_action_fails_without_use_server_directive(tmp_path):
    d = _make_minisite(tmp_path, _contact_form_files(
        'export async function submitContactForm() { return { ok: true }; }',
        '"use client";\nimport { submitContactForm } from "@/app/actions/contact";\nexport function ContactForm(){}',
    ))
    ctx = BuildContext.load(d)
    r = checks.contact_form_uses_server_action(ctx)
    assert r.status == "fail"
    assert "use server" in r.message


def test_contact_form_uses_server_action_fails_when_form_doesnt_reference_action(tmp_path):
    """Action file exists with "use server", but the form component is a fake
    onSubmit handler that never touches the Server Action — the regression
    this check is built to catch."""
    d = _make_minisite(tmp_path, _contact_form_files(
        '"use server";\nexport async function submitContactForm() { return { ok: true }; }',
        '"use client";\nexport function ContactForm() {\n'
        '  return <form onSubmit={(e) => { e.preventDefault(); }} />;\n'
        '}',
    ))
    ctx = BuildContext.load(d)
    r = checks.contact_form_uses_server_action(ctx)
    assert r.status == "fail"
    assert "Server Action" in r.message


@pytest.mark.parametrize("case,pkg,expected", [
    ("resend_present",
     '{"name":"x","dependencies":{"resend":"^4.0.0"}}', "pass"),
    ("resend_absent",
     '{"name":"x","dependencies":{"react":"^19.0.0"}}', "fail"),
    ("no_dependencies_section",
     '{"name":"x"}', "fail"),
    ("resend_pinned_version",
     '{"dependencies":{"resend":"4.5.1"}}', "pass"),
    ("invalid_json",
     '{this is not json', "fail"),
])
def test_resend_in_dependencies_raw(tmp_path, case, pkg, expected):
    d = _make_minisite(tmp_path, {"package.json": pkg})
    ctx = BuildContext.load(d)
    assert checks.resend_in_dependencies(ctx).status == expected, case


def test_resend_in_dependencies_fails_when_package_json_missing(tmp_path):
    d = _make_minisite(tmp_path, {"app/page.tsx": "export default () => null;"})
    ctx = BuildContext.load(d)
    r = checks.resend_in_dependencies(ctx)
    assert r.status == "fail"
    assert "package.json missing" in r.message


# ---------------------------------------------------------------------------
# deploy_to_vercel_scaffold — vercel.json + README Deploy section
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case,files,expected", [
    ("both_present_h2",
     {"vercel.json": '{"framework":"nextjs"}',
      "README.md": "# Site\n\n## Deploy\n\npush to GitHub\n"}, "pass"),
    ("both_present_h1",
     {"vercel.json": '{"framework":"nextjs"}',
      "README.md": "# Site\n\n# Deploy\n\n..."}, "pass"),
    ("both_present_h3",
     {"vercel.json": '{}',
      "README.md": "### Deploy\n"}, "pass"),
    ("vercel_missing",
     {"README.md": "## Deploy\n"}, "fail"),
    ("readme_missing",
     {"vercel.json": '{"framework":"nextjs"}'}, "fail"),
    ("readme_present_but_no_deploy_heading",
     {"vercel.json": '{}',
      "README.md": "# Site\n\nSome other content.\n"}, "fail"),
    ("deploy_only_in_body_not_heading",
     {"vercel.json": '{}',
      "README.md": "# Site\n\nYou can deploy to Vercel.\n"}, "fail"),
    ("case_insensitive_match",
     {"vercel.json": '{}',
      "README.md": "## DEPLOY\n"}, "pass"),
])
def test_deploy_to_vercel_scaffold_raw(tmp_path, case, files, expected):
    d = _make_minisite(tmp_path, files)
    ctx = BuildContext.load(d)
    assert checks.deploy_to_vercel_scaffold(ctx).status == expected, case


def test_deploy_to_vercel_scaffold_reports_specific_missing(tmp_path):
    # Site dir must exist for the check to run (it skips when site/ is absent).
    d = _make_minisite(tmp_path, {"app/page.tsx": "export default () => null;"})
    ctx = BuildContext.load(d)
    r = checks.deploy_to_vercel_scaffold(ctx)
    assert r.status == "fail"
    assert "vercel.json" in str(r.details["missing"])
    assert "README.md" in str(r.details["missing"])
