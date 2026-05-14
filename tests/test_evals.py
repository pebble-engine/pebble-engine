"""Tests for the pebble.evals harness.

The strategy: build a synthetic site directory in tmp_path that satisfies
every check, then for each check write a "passes when correct" test and a
"fails when broken" test by mutating exactly one thing. This way each
test isolates a single assertion of the check's logic.

The heavy ``site_compiles`` check shells out to ``npx tsc`` and is not
exercised here — it's covered indirectly by the run against the real
sentinel builds.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pebble.evals import BuildContext, run_checks
from pebble.evals import checks
from pebble.evals.report import format_summary, format_text, to_json


# ---------------------------------------------------------------------------
# Fixture — a minimal "good" build that should pass every static check
# ---------------------------------------------------------------------------

@pytest.fixture
def good_build(tmp_path: Path) -> Path:
    """Synthetic build matching the May 2026 foundation (VEX-style hero).

    Passes every static check including the new FOUNDATION checks:
    Inter via next/font/google, AnimatedHeading + FadeIn components,
    liquid-glass class, video hero with no overlay, prefers-reduced-motion.
    """
    d = tmp_path / "good-build"
    site = d / "site"
    (site / "app").mkdir(parents=True)
    (site / "components" / "sections").mkdir(parents=True)
    (site / "components" / "ui").mkdir(parents=True)
    (site / "config").mkdir()

    (d / "brief.json").write_text(json.dumps({
        "business_name": "Good Co",
        "business_type": "plumbing",
        "phone": "(212) 234-9876",
        "_design_dna": "swiss_magazine",
        "_industry_intel_key": "plumbing",
    }))

    (site / "package.json").write_text('{"name":"good"}')
    (site / "tsconfig.json").write_text(json.dumps({
        "compilerOptions": {"paths": {"@/*": ["./*"]}}
    }))
    (site / "tailwind.config.ts").write_text(
        "export default { theme: { extend: { fontFamily: { "
        "sans: ['var(--font-inter)', 'Inter', 'sans-serif'], "
        "display: ['Cormorant Garamond', 'serif'] } } } }"
    )
    (site / "postcss.config.js").write_text("module.exports = {}")
    (site / "next.config.mjs").write_text("/** @type {import('next').NextConfig} */\nexport default {};\n")
    (site / "app" / "layout.tsx").write_text(
        'import { Inter } from "next/font/google";\n'
        'import "./globals.css";\n'
        'const inter = Inter({ subsets: ["latin"], weight: ["300","400","500","600"], variable: "--font-inter" });\n'
        'export default function L({children}: any) {\n'
        '  return <html lang="en" className={inter.variable}><body className={inter.className}>{children}</body></html>;\n'
        '}'
    )
    (site / "app" / "page.tsx").write_text(
        'import { Hero } from "@/components/sections/Hero";\n'
        'export default function P() {\n'
        '  return <main><Hero /><p>Call (212) 234-9876</p></main>;\n'
        '}'
    )
    (site / "app" / "globals.css").write_text(
        "body { font-family: var(--font-inter), Inter, sans-serif; "
        "-webkit-font-smoothing: antialiased; height: 100dvh; }\n"
        ".liquid-glass { background: rgba(0,0,0,0.4); backdrop-filter: blur(4px); }\n"
        "@media (prefers-reduced-motion: reduce) { * { transition-duration: 0.01ms !important; } }\n"
    )
    (site / "components" / "sections" / "Hero.tsx").write_text(
        'import { AnimatedHeading } from "@/components/ui/AnimatedHeading";\n'
        'import { FadeIn } from "@/components/ui/FadeIn";\n'
        'export function Hero() {\n'
        '  return (\n'
        '    <section className="relative min-h-[100dvh] overflow-hidden bg-black">\n'
        '      <video autoPlay muted loop playsInline className="absolute inset-0 w-full h-full object-cover" src="/videos/hero.mp4" poster="/images/hero-poster.jpg" />\n'
        '      <AnimatedHeading text={"Hello\\nworld."} className="text-7xl text-white" />\n'
        '      <FadeIn delay={800}><p>(212) 234-9876</p></FadeIn>\n'
        '    </section>\n'
        '  );\n'
        '}'
    )
    (site / "components" / "ui" / "AnimatedHeading.tsx").write_text(
        '"use client";\n'
        'export function AnimatedHeading({ text, className }: { text: string; className?: string }) {\n'
        '  return (\n'
        '    <h1 className={className} style={{ letterSpacing: "-0.04em", textShadow: "0 2px 24px rgba(0,0,0,0.5)" }}>\n'
        '      <span className="sr-only">{text}</span>\n'
        '      <span aria-hidden="true">{text}</span>\n'
        '    </h1>\n'
        '  );\n'
        '}'
    )
    (site / "components" / "ui" / "FadeIn.tsx").write_text(
        '"use client";\n'
        'export function FadeIn({ children, delay = 0 }: { children: any; delay?: number }) {\n'
        '  return <div style={{ opacity: 1, transitionDelay: `${delay}ms` }}>{children}</div>;\n'
        '}'
    )
    (site / ".gitignore").write_text("node_modules/\n.next/\n")
    return d


# ---------------------------------------------------------------------------
# 1. Runner
# ---------------------------------------------------------------------------

def test_runner_loads_brief_and_meta(good_build):
    ctx = BuildContext.load(good_build)
    assert ctx.slug == "good-build"
    assert ctx.brief["business_name"] == "Good Co"
    assert ctx.meta == {}  # no build_meta.json in the fixture


def test_runner_handles_missing_brief_gracefully(tmp_path):
    d = tmp_path / "no-brief"
    d.mkdir()
    ctx = BuildContext.load(d)
    assert ctx.brief == {}
    assert ctx.meta == {}


def test_runner_catches_crashing_check(good_build):
    """A check that raises is reported as 'error', not propagated."""
    def crashing(ctx):
        raise RuntimeError("boom")
    results = run_checks(good_build, checks=[crashing])
    assert len(results) == 1
    assert results[0].status == "error"
    assert "boom" in results[0].message


# ---------------------------------------------------------------------------
# 2. Individual checks — pass/fail pairs (excluding site_compiles)
# ---------------------------------------------------------------------------

def test_no_src_directory_passes_when_absent(good_build):
    ctx = BuildContext.load(good_build)
    assert checks.no_src_directory(ctx).status == "pass"


def test_no_src_directory_fails_when_present(good_build):
    (good_build / "site" / "src").mkdir()
    ctx = BuildContext.load(good_build)
    assert checks.no_src_directory(ctx).status == "fail"


def test_no_src_directory_skips_when_no_site(tmp_path):
    d = tmp_path / "prompt-only"
    d.mkdir()
    (d / "brief.json").write_text("{}")
    ctx = BuildContext.load(d)
    assert checks.no_src_directory(ctx).status == "skip"


def test_required_files_present_passes_for_minimal_site(good_build):
    ctx = BuildContext.load(good_build)
    assert checks.required_files_present(ctx).status == "pass"


def test_required_files_present_fails_when_page_missing(good_build):
    (good_build / "site" / "app" / "page.tsx").unlink()
    ctx = BuildContext.load(good_build)
    r = checks.required_files_present(ctx)
    assert r.status == "fail"
    assert "app/page.tsx" in r.details["missing"]


def test_tsconfig_paths_alias_passes_for_canonical(good_build):
    ctx = BuildContext.load(good_build)
    assert checks.tsconfig_paths_alias(ctx).status == "pass"


def test_tsconfig_paths_alias_fails_for_src_prefix(good_build):
    (good_build / "site" / "tsconfig.json").write_text(json.dumps({
        "compilerOptions": {"paths": {"@/*": ["./src/*"]}}
    }))
    ctx = BuildContext.load(good_build)
    r = checks.tsconfig_paths_alias(ctx)
    assert r.status == "fail"
    assert r.details["got"] == ["./src/*"]


def test_tsconfig_paths_alias_tolerates_jsonc_comments(good_build):
    """Some Next.js scaffolding produces JSONC. The check must strip
    // comments before parsing."""
    (good_build / "site" / "tsconfig.json").write_text(
        '// comment\n{ "compilerOptions": { "paths": { "@/*": ["./*"] } } }'
    )
    ctx = BuildContext.load(good_build)
    assert checks.tsconfig_paths_alias(ctx).status == "pass"


def test_next_config_is_mjs_passes(good_build):
    ctx = BuildContext.load(good_build)
    assert checks.next_config_is_mjs(ctx).status == "pass"


def test_next_config_is_mjs_fails_for_ts(good_build):
    (good_build / "site" / "next.config.ts").write_text("export default {}")
    ctx = BuildContext.load(good_build)
    assert checks.next_config_is_mjs(ctx).status == "fail"


def test_hero_has_h1_passes_when_in_page(good_build):
    ctx = BuildContext.load(good_build)
    assert checks.hero_has_h1(ctx).status == "pass"


def test_hero_has_h1_passes_when_in_hero_component(good_build):
    """Hero h1 in a Hero component, not in page.tsx — should still pass
    and report the actual file, not a stray h1 in a motion utility."""
    (good_build / "site" / "app" / "page.tsx").write_text(
        'import { Hero } from "@/components/sections/Hero";\n'
        'export default function P() { return <Hero />; }'
    )
    (good_build / "site" / "components" / "sections" / "Hero.tsx").write_text(
        'export const Hero = () => <h1>Big Headline</h1>;'
    )
    # Add a motion utility that ALSO has h1, to make sure the check prefers Hero
    (good_build / "site" / "components" / "motion").mkdir()
    (good_build / "site" / "components" / "motion" / "SplitText.tsx").write_text(
        'export const SplitText = () => <h1>tokens</h1>;'
    )
    ctx = BuildContext.load(good_build)
    r = checks.hero_has_h1(ctx)
    assert r.status == "pass"
    # The hero file should be the one reported, not the motion utility.
    assert "Hero.tsx" in r.message


def test_hero_has_h1_fails_when_missing_everywhere(good_build):
    """A build with NO h1 anywhere should fail. Since the foundation's
    AnimatedHeading component itself renders an `<h1>`, we must strip its
    body AND the Hero.tsx to make a build that genuinely has no h1."""
    (good_build / "site" / "app" / "page.tsx").write_text(
        'export default function P() { return <div>no heading</div>; }'
    )
    (good_build / "site" / "components" / "sections" / "Hero.tsx").write_text(
        'export function Hero() { return <section>no heading</section>; }'
    )
    # AnimatedHeading.tsx renders an h1 in the foundation; strip it so the
    # check walks all components and finds none.
    (good_build / "site" / "components" / "ui" / "AnimatedHeading.tsx").write_text(
        '"use client";\nexport function AnimatedHeading({text}:{text:string}){return <span>{text}</span>;}'
    )
    ctx = BuildContext.load(good_build)
    assert checks.hero_has_h1(ctx).status == "fail"


def test_images_use_next_image_passes_when_no_raw_img(good_build):
    ctx = BuildContext.load(good_build)
    assert checks.images_use_next_image(ctx).status == "pass"


def test_images_use_next_image_fails_on_raw_img(good_build):
    (good_build / "site" / "components" / "sections" / "Logo.tsx").write_text(
        'export const Logo = () => <img src="/logo.png" />;'
    )
    ctx = BuildContext.load(good_build)
    r = checks.images_use_next_image(ctx)
    assert r.status == "fail"
    assert any("Logo.tsx" in f for f in r.details["files"])


def test_no_invented_phone_passes_when_brief_phone_present(good_build):
    ctx = BuildContext.load(good_build)
    assert checks.no_invented_phone(ctx).status == "pass"


def test_no_invented_phone_fails_on_555(good_build):
    (good_build / "site" / "app" / "page.tsx").write_text(
        'export default function P() { return <h1>Call 555-123-4567</h1>; }'
    )
    ctx = BuildContext.load(good_build)
    assert checks.no_invented_phone(ctx).status == "fail"


def test_no_invented_phone_passes_with_placeholder_when_no_brief_phone(good_build):
    """When the brief lacks a phone, the [BUSINESS PHONE] placeholder
    is the correct artifact — not an invented number."""
    brief = json.loads((good_build / "brief.json").read_text())
    del brief["phone"]
    (good_build / "brief.json").write_text(json.dumps(brief))
    (good_build / "site" / "app" / "page.tsx").write_text(
        'export default function P() { return <h1>Call [BUSINESS PHONE]</h1>; }'
    )
    ctx = BuildContext.load(good_build)
    assert checks.no_invented_phone(ctx).status == "pass"


def test_dna_display_font_honored_passes_when_present(good_build):
    ctx = BuildContext.load(good_build)
    # The good_build fixture sets DNA to swiss_magazine; the real card's
    # display_font is 'Cormorant Garamond' which IS in globals.css.
    assert checks.dna_display_font_honored(ctx).status == "pass"


def test_dna_display_font_honored_passes_for_next_font_google_underscore_form(good_build):
    """next/font/google exposes fonts as underscore-separated identifiers
    (Cormorant_Garamond), but the DNA card stores the human-readable form
    (Cormorant Garamond). The check must accept either."""
    (good_build / "site" / "app" / "globals.css").write_text(
        "body { font-family: 'Inter', sans-serif; height: 100dvh; }"
    )
    (good_build / "site" / "tailwind.config.ts").write_text(
        "export default { theme: { fontFamily: { display: ['Inter'] } } }"
    )
    (good_build / "site" / "app" / "layout.tsx").write_text(
        'import { Cormorant_Garamond } from "next/font/google";\n'
        'const cg = Cormorant_Garamond({ subsets: ["latin"], variable: "--font-display" });\n'
        'export default function L({children}: any) {\n'
        '  return <html lang="en" className={cg.variable}><body>{children}</body></html>;\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    r = checks.dna_display_font_honored(ctx)
    assert r.status == "pass"
    assert "layout.tsx" in r.message


def test_dna_display_font_honored_fails_when_missing(good_build):
    """LLM dropped the DNA font and fell back to defaults — the silent
    regression the check is built to catch."""
    (good_build / "site" / "app" / "globals.css").write_text(
        "body { font-family: 'Inter', sans-serif; height: 100dvh; }"
    )
    (good_build / "site" / "tailwind.config.ts").write_text(
        "export default { theme: { fontFamily: { display: ['Inter', 'sans-serif'] } } }"
    )
    ctx = BuildContext.load(good_build)
    r = checks.dna_display_font_honored(ctx)
    assert r.status == "fail"
    assert "Cormorant Garamond" in r.details["expected_font"]


def test_uses_100dvh_passes_when_no_100vh(good_build):
    ctx = BuildContext.load(good_build)
    assert checks.uses_100dvh_not_100vh(ctx).status == "pass"


def test_uses_100dvh_fails_on_100vh_in_css(good_build):
    (good_build / "site" / "app" / "globals.css").write_text(
        ".hero { min-height: 100vh; }"
    )
    ctx = BuildContext.load(good_build)
    assert checks.uses_100dvh_not_100vh(ctx).status == "fail"


def test_html_lang_attr_passes_when_present(good_build):
    ctx = BuildContext.load(good_build)
    assert checks.html_lang_attr(ctx).status == "pass"


def test_html_lang_attr_fails_when_missing(good_build):
    (good_build / "site" / "app" / "layout.tsx").write_text(
        'export default function L({children}: any) { return <html><body>{children}</body></html>; }'
    )
    ctx = BuildContext.load(good_build)
    r = checks.html_lang_attr(ctx)
    assert r.status == "fail"
    assert "lang" in r.message


def test_images_have_alt_passes_with_alt_present(good_build):
    (good_build / "site" / "components" / "sections" / "Photo.tsx").write_text(
        'import Image from "next/image";\n'
        'export const Photo = () => <Image src="/x.jpg" alt="x" width={100} height={100} />;'
    )
    ctx = BuildContext.load(good_build)
    assert checks.images_have_alt(ctx).status == "pass"


def test_images_have_alt_fails_when_alt_missing(good_build):
    (good_build / "site" / "components" / "sections" / "Photo.tsx").write_text(
        'import Image from "next/image";\n'
        'export const Photo = () => <Image src="/x.jpg" width={100} height={100} />;'
    )
    ctx = BuildContext.load(good_build)
    r = checks.images_have_alt(ctx)
    assert r.status == "fail"
    assert any("Photo.tsx" in f for f in r.details["files"])


def test_images_have_alt_passes_with_no_images(good_build):
    """A build with no <Image> blocks should pass — there's nothing to fail on."""
    ctx = BuildContext.load(good_build)
    assert checks.images_have_alt(ctx).status == "pass"


def test_scroll_trigger_ssr_safe_passes_when_inside_useeffect(good_build):
    (good_build / "site" / "components" / "sections" / "Motion.tsx").write_text(
        '"use client";\nimport { useEffect } from "react";\n'
        'import { ScrollTrigger } from "gsap/ScrollTrigger";\n'
        'export const Motion = () => {\n'
        '  useEffect(() => {\n'
        '    ScrollTrigger.normalizeScroll(true);\n'
        '    ScrollTrigger.config({ ignoreMobileResize: true });\n'
        '  }, []);\n'
        '  return null;\n'
        '};\n'
    )
    ctx = BuildContext.load(good_build)
    assert checks.scroll_trigger_ssr_safe(ctx).status == "pass"


def test_scroll_trigger_ssr_safe_fails_at_module_level(good_build):
    (good_build / "site" / "components" / "sections" / "BadMotion.tsx").write_text(
        'import { ScrollTrigger } from "gsap/ScrollTrigger";\n'
        'ScrollTrigger.normalizeScroll(true);\n'
        'export const BadMotion = () => null;\n'
    )
    ctx = BuildContext.load(good_build)
    r = checks.scroll_trigger_ssr_safe(ctx)
    assert r.status == "fail"
    assert any("BadMotion.tsx" in f for f in r.details["files"])


def test_no_css_smooth_scroll_passes_when_clean(good_build):
    ctx = BuildContext.load(good_build)
    assert checks.no_css_smooth_scroll(ctx).status == "pass"


def test_no_css_smooth_scroll_fails_when_present(good_build):
    (good_build / "site" / "app" / "globals.css").write_text(
        "html { scroll-behavior: smooth; }"
    )
    ctx = BuildContext.load(good_build)
    r = checks.no_css_smooth_scroll(ctx)
    assert r.status == "fail"
    assert any("globals.css" in f for f in r.details["files"])


def test_no_css_smooth_scroll_ignores_block_comment(good_build):
    """The LLM commonly leaves a /* */ comment explaining the rule; matching
    that text would defeat the check on builds that are doing it RIGHT."""
    (good_build / "site" / "app" / "globals.css").write_text(
        "/* Never set scroll-behavior: smooth - Lenis handles scroll */\n"
        "html { scroll-behavior: auto !important; }\n"
    )
    ctx = BuildContext.load(good_build)
    assert checks.no_css_smooth_scroll(ctx).status == "pass"


def test_no_css_smooth_scroll_ignores_line_comment(good_build):
    """// comments shouldn't be matched either (uncommon in CSS but possible
    in JS files we also scan)."""
    (good_build / "site" / "components" / "sections" / "Note.tsx").write_text(
        "// reminder: do not use scroll-behavior: smooth here\n"
        "export const Note = () => null;\n"
    )
    ctx = BuildContext.load(good_build)
    assert checks.no_css_smooth_scroll(ctx).status == "pass"


def test_no_css_smooth_scroll_skips_next_build_artifacts(good_build):
    """``.next/`` is next.js's build output; if the source is clean, scanning
    the compiled artifact only ever produces noise."""
    next_css = good_build / "site" / ".next" / "static" / "css" / "app"
    next_css.mkdir(parents=True)
    (next_css / "layout.css").write_text("html { scroll-behavior: smooth; }")
    ctx = BuildContext.load(good_build)
    assert checks.no_css_smooth_scroll(ctx).status == "pass"


# ---------------------------------------------------------------------------
# 3. Report formatters
# ---------------------------------------------------------------------------

def test_format_text_includes_dna_and_industry(good_build):
    ctx = BuildContext.load(good_build)
    results = run_checks(good_build, checks=[c for c in checks.ALL_CHECKS if c is not checks.site_compiles])
    text = format_text(ctx.slug, ctx.brief, results)
    assert "good-build" in text
    assert "swiss_magazine" in text
    assert "plumbing" in text
    assert "Score:" in text


def test_format_summary_table_has_header_and_row(good_build):
    ctx = BuildContext.load(good_build)
    rows = [{
        "slug": ctx.slug,
        "dna": ctx.brief.get("_design_dna"),
        "pass": 8, "fail": 1, "skip": 0, "error": 0,
    }]
    table = format_summary(rows)
    assert "Build" in table
    assert "DNA" in table
    assert "good-build" in table
    assert "swiss_magazine" in table


def test_to_json_has_stable_shape(good_build):
    ctx = BuildContext.load(good_build)
    results = run_checks(good_build, checks=[checks.no_src_directory])
    blob = to_json(results, ctx.slug, ctx.brief)
    assert blob["slug"] == "good-build"
    assert blob["dna"] == "swiss_magazine"
    assert isinstance(blob["results"], list)
    assert blob["summary"]["pass"] >= 1


# ---------------------------------------------------------------------------
# 4. End-to-end run_checks
# ---------------------------------------------------------------------------

def test_run_checks_default_set_runs_all_static_checks(good_build):
    """All static (non-tsc) checks pass on the synthetic good build."""
    non_compile = [c for c in checks.ALL_CHECKS if c is not checks.site_compiles]
    results = run_checks(good_build, checks=non_compile)
    by_name = {r.name: r for r in results}
    for c in non_compile:
        name = c.__name__
        assert name in by_name, f"missing result for {name}"
        assert by_name[name].status in {"pass", "skip"}, \
            f"{name} should pass on good_build, got {by_name[name].status}: {by_name[name].message}"
