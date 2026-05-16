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
from pebble.plan import build_pebble_plan


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

    fixture_brief = {
        "business_name": "Good Co",
        "business_type": "plumbing",
        "phone": "(212) 234-9876",
        "_design_dna": "swiss_magazine",
        "_industry_intel_key": "plumbing",
    }
    (d / "brief.json").write_text(json.dumps(fixture_brief))
    # Pebble Plan emitted by every real build. Hand-constructed here to
    # include the plumbing industry's two extra pages (service-area,
    # guarantee) on top of the universal extras (faq, privacy, terms) —
    # build_pebble_plan() only adds industry pages when industry_intel
    # is passed, and the fixture stays decoupled from industries.json.
    plan = build_pebble_plan(fixture_brief)
    plan["pages"].extend([
        {"id": "service_area", "title": "Service Area", "route": "/service-area",
         "purpose": "Where we serve.", "foundation": False},
        {"id": "guarantee",    "title": "Guarantee",    "route": "/guarantee",
         "purpose": "Our promise.",   "foundation": False},
    ])
    (d / "plan.json").write_text(json.dumps(plan, indent=2))

    (site / "package.json").write_text(json.dumps({
        "name": "good",
        "dependencies": {"next": "^15.0.0", "react": "^19.0.0", "resend": "^4.0.0"},
    }))
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
        'const ld = { "@context": "https://schema.org", "@type": "LocalBusiness", "name": "Good Co" };\n'
        'export default function L({children}: any) {\n'
        '  return <html lang="en" className={inter.variable}><body className={inter.className}><script type="application/ld+json" dangerouslySetInnerHTML={{__html: JSON.stringify(ld)}} />{children}</body></html>;\n'
        '}'
    )
    # Next.js 14 convention files — emit sitemap.xml + robots.txt.
    (site / "app" / "sitemap.ts").write_text(
        'export default function sitemap() { return [{ url: "https://example.com/", lastModified: new Date() }]; }'
    )
    (site / "app" / "robots.ts").write_text(
        'export default function robots() { return { rules: [{ userAgent: "*", allow: "/" }], sitemap: "https://example.com/sitemap.xml" }; }'
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
    # Foundation contact form scaffold (Server Action + Resend).
    (site / "app" / "actions").mkdir(parents=True, exist_ok=True)
    (site / "app" / "actions" / "contact.ts").write_text(
        '"use server";\n'
        'export async function submitContactForm(_p:any, f:FormData) {\n'
        '  return { ok: true, message: "Thanks." };\n'
        '}'
    )
    (site / "components" / "forms").mkdir(parents=True, exist_ok=True)
    (site / "components" / "forms" / "ContactForm.tsx").write_text(
        '"use client";\n'
        'import { useActionState } from "react";\n'
        'import { submitContactForm } from "@/app/actions/contact";\n'
        'export function ContactForm() {\n'
        '  const [state, action] = useActionState(submitContactForm, null);\n'
        '  return <form action={action} />;\n'
        '}'
    )
    # Deploy-to-Vercel scaffold.
    (site / "vercel.json").write_text('{"$schema":"https://openapi.vercel.sh/vercel.json","framework":"nextjs"}')
    (site / "README.md").write_text(
        "# Good Co\n\nGenerated by Pebble Engine.\n\n"
        "## Deploy\n\n"
        "1. Push this directory to a new GitHub repo.\n"
        "2. Import the repo at https://vercel.com/new.\n"
        "3. Add `RESEND_API_KEY`, `CONTACT_FROM_EMAIL`, `CONTACT_TO_EMAIL` in the Vercel dashboard.\n\n"
        "## What This Site Does NOT Include\n\n"
        "- Real-time technician dispatch (recommended: Jobber or Housecall Pro).\n"
        "- Payment processing beyond contact-form lead capture (recommended: Stripe Payment Links).\n"
        "- Customer accounts or saved estimates (recommended: out of scope for v1).\n"
    )
    # Industry-aware pages (May 2026 expansion). For brief["_industry_intel_key"]
    # = "plumbing", industries.json declares pages = ["service_area", "guarantee"].
    # Plus the universal extras: faq, privacy, terms. Five stub pages total.
    for route in ("faq", "privacy", "terms", "service-area", "guarantee"):
        page_dir = site / "app" / route
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "page.tsx").write_text(
            f'export default function P() {{ return <main><h1>{route}</h1></main>; }}'
        )
    # Footer with sitemap links to every non-foundation page (May 2026
    # multi-page discoverability — eval `footer_lists_all_pages` enforces).
    (site / "components" / "layout").mkdir(parents=True, exist_ok=True)
    (site / "components" / "layout" / "Footer.tsx").write_text(
        'import Link from "next/link";\n'
        'export function Footer() {\n'
        '  return (\n'
        '    <footer className="border-t border-white/10 bg-black text-white/80">\n'
        '      <Link href="/">Home</Link>\n'
        '      <Link href="/services">Services</Link>\n'
        '      <Link href="/about">About</Link>\n'
        '      <Link href="/contact">Contact</Link>\n'
        '      <Link href="/service-area">Service Area</Link>\n'
        '      <Link href="/guarantee">Guarantee</Link>\n'
        '      <Link href="/faq">FAQ</Link>\n'
        '      <Link href="/privacy">Privacy</Link>\n'
        '      <Link href="/terms">Terms</Link>\n'
        '    </footer>\n'
        '  );\n'
        '}'
    )
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


def test_no_invented_phone_passes_when_fake_brief_phone_downgraded(good_build):
    """When the brief contains a fake 555-marker phone (e.g. a tester pasted
    "(718) 555-0143"), the LLM is RIGHT to downgrade to [BUSINESS PHONE].
    The check should pass in that case, not fail.

    This was the false-positive that bit Bridgewater + Heron builds in May 2026:
    Gemini 3.1 Pro correctly recognized 555-XXXX as a test marker and emitted
    the placeholder, but the check counted that as a failure because the
    brief's literal phone wasn't in the output."""
    brief = json.loads((good_build / "brief.json").read_text())
    brief["phone"] = "(718) 555-0143"  # real area code, 555 exchange → fake
    (good_build / "brief.json").write_text(json.dumps(brief))
    (good_build / "site" / "app" / "page.tsx").write_text(
        'export default function P() { return <h1>Call [BUSINESS PHONE]</h1>; }'
    )
    # Also wipe the Hero.tsx that has the real (212) phone so it doesn't
    # confuse the test
    (good_build / "site" / "components" / "sections" / "Hero.tsx").write_text(
        'export function Hero() { return <section><h1>Hero</h1></section>; }'
    )
    ctx = BuildContext.load(good_build)
    r = checks.no_invented_phone(ctx)
    assert r.status == "pass", r.message
    assert "fake" in r.message.lower() or "placeholder" in r.message.lower()


def test_no_invented_phone_fails_when_fake_brief_phone_NOT_downgraded(good_build):
    """If the brief's fake phone passes through to the site verbatim
    (LLM didn't recognize the 555 marker), that's NOT invented (it's
    the brief's phone), so the check passes — but it's worth being
    explicit about this case for future reference."""
    brief = json.loads((good_build / "brief.json").read_text())
    brief["phone"] = "(718) 555-0143"
    (good_build / "brief.json").write_text(json.dumps(brief))
    (good_build / "site" / "app" / "page.tsx").write_text(
        'export default function P() { return <h1>Call (718) 555-0143</h1>; }'
    )
    (good_build / "site" / "components" / "sections" / "Hero.tsx").write_text(
        'export function Hero() { return <section><h1>Hero</h1></section>; }'
    )
    ctx = BuildContext.load(good_build)
    # The brief's literal phone IS in the site → found_brief_phone=true → pass.
    # Even though the brief phone is fake, the check's job is to flag
    # INVENTED numbers (LLM-fabricated), not to second-guess the brief.
    assert checks.no_invented_phone(ctx).status == "pass"


def test_no_invented_phone_detects_exchange_555_in_site(good_build):
    """Catch the LLM if it invents a phone with the 555 EXCHANGE pattern
    (real area code, fake middle 3 digits), not just the 555 AREA CODE
    pattern. Previously _INVENTED_555 only caught area-code-555."""
    (good_build / "site" / "app" / "page.tsx").write_text(
        'export default function P() { return <h1>Call (212) 555-0123</h1>; }'
    )
    ctx = BuildContext.load(good_build)
    r = checks.no_invented_phone(ctx)
    assert r.status == "fail"
    assert "invented" in r.message.lower() or "555" in r.message


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
# 2b. footer_lists_all_pages — multi-page discoverability
# ---------------------------------------------------------------------------

def test_footer_lists_all_pages_passes_when_every_route_linked(good_build):
    ctx = BuildContext.load(good_build)
    result = checks.footer_lists_all_pages(ctx)
    assert result.status == "pass", result.message
    # Plumbing fixture: 2 industry pages (service-area, guarantee) plus
    # 3 universal extras (faq, privacy, terms) = 5 non-foundation pages.
    assert "5 non-foundation page(s)" in result.message


def test_footer_lists_all_pages_fails_when_industry_route_missing(good_build):
    """Drop the /guarantee link — the check must call it out specifically."""
    footer = good_build / "site" / "components" / "layout" / "Footer.tsx"
    footer.write_text(
        footer.read_text(encoding="utf-8").replace(
            '<Link href="/guarantee">Guarantee</Link>\n', ""
        ),
        encoding="utf-8",
    )
    ctx = BuildContext.load(good_build)
    result = checks.footer_lists_all_pages(ctx)
    assert result.status == "fail"
    assert "/guarantee" in result.message
    assert result.details["missing_routes"] == ["/guarantee"]


def test_footer_lists_all_pages_fails_when_universal_route_missing(good_build):
    """Privacy / Terms / FAQ are universal — also enforced."""
    footer = good_build / "site" / "components" / "layout" / "Footer.tsx"
    footer.write_text(
        footer.read_text(encoding="utf-8").replace(
            '<Link href="/privacy">Privacy</Link>\n', ""
        ),
        encoding="utf-8",
    )
    ctx = BuildContext.load(good_build)
    result = checks.footer_lists_all_pages(ctx)
    assert result.status == "fail"
    assert "/privacy" in result.details["missing_routes"]


def test_footer_lists_all_pages_fails_when_footer_file_absent_and_layout_silent(good_build):
    """Footer.tsx is gone AND app/layout.tsx doesn't carry the links — the
    check falls back to layout.tsx and reports the missing routes."""
    (good_build / "site" / "components" / "layout" / "Footer.tsx").unlink()
    ctx = BuildContext.load(good_build)
    result = checks.footer_lists_all_pages(ctx)
    assert result.status == "fail"
    assert "missing from footer sitemap" in result.message
    # The fallback file the check looked at, surfaced in details.
    assert result.details["footer_file"] == "app/layout.tsx"


def test_footer_lists_all_pages_accepts_layout_tsx_fallback(good_build):
    """If a build inlines the footer in app/layout.tsx instead of a
    component file, that's still discoverable — check should pass."""
    (good_build / "site" / "components" / "layout" / "Footer.tsx").unlink()
    layout = good_build / "site" / "app" / "layout.tsx"
    layout.write_text(
        layout.read_text(encoding="utf-8").replace(
            "</body>",
            '<footer>'
            '<a href="/service-area">Service Area</a>'
            '<a href="/guarantee">Guarantee</a>'
            '<a href="/faq">FAQ</a>'
            '<a href="/privacy">Privacy</a>'
            '<a href="/terms">Terms</a>'
            '</footer></body>',
        ),
        encoding="utf-8",
    )
    ctx = BuildContext.load(good_build)
    assert checks.footer_lists_all_pages(ctx).status == "pass"


def test_footer_lists_all_pages_accepts_single_quoted_hrefs(good_build):
    """LLMs sometimes emit `Link href={'/faq'}` — single quotes should match."""
    footer = good_build / "site" / "components" / "layout" / "Footer.tsx"
    footer.write_text(
        'import Link from "next/link";\n'
        'const ROUTES = {\n'
        "  faq: '/faq',\n"
        "  privacy: '/privacy',\n"
        "  terms: '/terms',\n"
        "  serviceArea: '/service-area',\n"
        "  guarantee: '/guarantee',\n"
        '};\n'
        'export function Footer() {\n'
        '  return <footer>{Object.values(ROUTES).map(r => <Link key={r} href={r}>{r}</Link>)}</footer>;\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    assert checks.footer_lists_all_pages(ctx).status == "pass"


def test_footer_lists_all_pages_skips_when_no_plan(good_build):
    (good_build / "plan.json").unlink()
    ctx = BuildContext.load(good_build)
    result = checks.footer_lists_all_pages(ctx)
    assert result.status == "skip"
    assert "no plan.json" in result.message


def test_footer_lists_all_pages_skips_when_no_site(tmp_path):
    d = tmp_path / "prompt-only"
    d.mkdir()
    (d / "brief.json").write_text("{}")
    (d / "plan.json").write_text('{"pages": [{"route": "/faq"}]}')
    ctx = BuildContext.load(d)
    assert checks.footer_lists_all_pages(ctx).status == "skip"


def test_footer_lists_all_pages_passes_when_only_foundation_pages(good_build):
    """A plan with only the 4 foundation pages has nothing to surface in
    the footer beyond what the navbar already shows. Check should pass."""
    plan = json.loads((good_build / "plan.json").read_text(encoding="utf-8"))
    plan["pages"] = [
        {"id": "homepage", "route": "/", "foundation": True},
        {"id": "services", "route": "/services", "foundation": True},
        {"id": "about", "route": "/about", "foundation": True},
        {"id": "contact", "route": "/contact", "foundation": True},
    ]
    (good_build / "plan.json").write_text(json.dumps(plan))
    # Even with no footer file, a foundation-only plan passes.
    (good_build / "site" / "components" / "layout" / "Footer.tsx").unlink()
    ctx = BuildContext.load(good_build)
    result = checks.footer_lists_all_pages(ctx)
    assert result.status == "pass"
    assert "nothing to link" in result.message


# ---------------------------------------------------------------------------
# 2c. a11y_static_audit — top axe-core categories statically
# ---------------------------------------------------------------------------

def _write_tsx(good_build, rel_path: str, content: str) -> Path:
    p = good_build / "site" / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def test_a11y_passes_on_good_build(good_build):
    result = checks.a11y_static_audit(good_build_ctx := BuildContext.load(good_build))
    assert result.status == "pass", result.message


def test_a11y_flags_icon_only_button_without_label(good_build):
    _write_tsx(good_build, "components/ui/IconBtn.tsx",
        '"use client";\n'
        'import { X } from "lucide-react";\n'
        'export function IconBtn() {\n'
        '  return <button onClick={() => {}}><X /></button>;\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    result = checks.a11y_static_audit(ctx)
    assert result.status == "fail"
    assert "icon-only button" in result.message
    assert "components/ui/IconBtn.tsx" in result.details["files"]


def test_a11y_passes_icon_button_with_aria_label(good_build):
    _write_tsx(good_build, "components/ui/IconBtn.tsx",
        '"use client";\n'
        'import { X } from "lucide-react";\n'
        'export function IconBtn() {\n'
        '  return <button aria-label="Close"><X /></button>;\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    assert checks.a11y_static_audit(ctx).status == "pass"


def test_a11y_passes_icon_button_with_title(good_build):
    """`title` is a softer affordance than aria-label but still readable
    by every major screen reader. Accept either."""
    _write_tsx(good_build, "components/ui/IconBtn.tsx",
        '"use client";\n'
        'import { X } from "lucide-react";\n'
        'export function IconBtn() {\n'
        '  return <button title="Close"><X /></button>;\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    assert checks.a11y_static_audit(ctx).status == "pass"


def test_a11y_flags_icon_only_link_without_label(good_build):
    _write_tsx(good_build, "components/ui/SocialLink.tsx",
        'import Link from "next/link";\n'
        'import { Twitter } from "lucide-react";\n'
        'export function SocialLink() {\n'
        '  return <Link href="https://x.com/x"><Twitter /></Link>;\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    result = checks.a11y_static_audit(ctx)
    assert result.status == "fail"
    assert "icon-only link" in result.message


def test_a11y_passes_link_with_text_inside(good_build):
    _write_tsx(good_build, "components/ui/SocialLink.tsx",
        'import Link from "next/link";\n'
        'import { Twitter } from "lucide-react";\n'
        'export function SocialLink() {\n'
        '  return <Link href="https://x.com/x"><Twitter />Follow us</Link>;\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    assert checks.a11y_static_audit(ctx).status == "pass"


def test_a11y_flags_input_without_label(good_build):
    _write_tsx(good_build, "components/forms/Search.tsx",
        '"use client";\n'
        'export function Search() {\n'
        '  return (\n'
        '    <form>\n'
        '      <input type="text" placeholder="Search" name="q" />\n'
        '    </form>\n'
        '  );\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    result = checks.a11y_static_audit(ctx)
    assert result.status == "fail"
    assert "input" in result.message.lower()


def test_a11y_passes_input_with_associated_label(good_build):
    _write_tsx(good_build, "components/forms/Search.tsx",
        '"use client";\n'
        'export function Search() {\n'
        '  return (\n'
        '    <form>\n'
        '      <label htmlFor="search-q">Search</label>\n'
        '      <input id="search-q" type="text" name="q" />\n'
        '    </form>\n'
        '  );\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    assert checks.a11y_static_audit(ctx).status == "pass"


def test_a11y_passes_input_with_aria_label(good_build):
    _write_tsx(good_build, "components/forms/Search.tsx",
        '"use client";\n'
        'export function Search() {\n'
        '  return <input type="text" aria-label="Search" name="q" />;\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    assert checks.a11y_static_audit(ctx).status == "pass"


def test_a11y_ignores_hidden_and_submit_inputs(good_build):
    _write_tsx(good_build, "components/forms/Tokens.tsx",
        'export function Tokens() {\n'
        '  return (\n'
        '    <form>\n'
        '      <input type="hidden" name="csrf" value="abc" />\n'
        '      <input type="submit" value="Send" />\n'
        '      <input type="button" value="Cancel" />\n'
        '    </form>\n'
        '  );\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    assert checks.a11y_static_audit(ctx).status == "pass"


def test_a11y_flags_heading_skip_h1_to_h3(good_build):
    _write_tsx(good_build, "app/about/page.tsx",
        'export default function P() {\n'
        '  return <main><h1>Title</h1><h3>Sub</h3></main>;\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    result = checks.a11y_static_audit(ctx)
    assert result.status == "fail"
    assert "heading-order" in result.message or "h1 → h3" in result.message


def test_a11y_passes_proper_heading_hierarchy(good_build):
    _write_tsx(good_build, "app/about/page.tsx",
        'export default function P() {\n'
        '  return <main><h1>Title</h1><h2>Sub</h2><h3>Detail</h3></main>;\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    assert checks.a11y_static_audit(ctx).status == "pass"


def test_a11y_skip_when_no_site(tmp_path):
    d = tmp_path / "prompt-only"
    d.mkdir()
    (d / "brief.json").write_text("{}")
    ctx = BuildContext.load(d)
    assert checks.a11y_static_audit(ctx).status == "skip"


def test_a11y_brace_scanner_handles_template_literals(good_build):
    """NLM 2026-05-15 flagged that the brace scanner naively counted
    `{`/`}` and would miscount when an attribute used a template
    literal like `onClick={`prefix-${id}`}`. The scanner now tracks
    template-literal mode + interpolation depth separately."""
    _write_tsx(good_build, "components/ui/A.tsx",
        'import { X } from "lucide-react";\n'
        'export function A({ id }: { id: string }) {\n'
        '  return (\n'
        '    <button onClick={() => console.log(`prefix-${id}-suffix`)}>\n'
        '      <X />\n'
        '    </button>\n'
        '  );\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    result = checks.a11y_static_audit(ctx)
    # The button is icon-only and has no aria-label — should fail. If
    # the scanner mishandled the template literal it would either skip
    # the button entirely (false negative) or flag a different file.
    assert result.status == "fail"
    assert "components/ui/A.tsx" in result.details["files"]


def test_a11y_brace_scanner_ignores_braces_inside_strings(good_build):
    """An attribute like `data-x="{}"` (literal braces in a string)
    must not confuse the brace-balanced scanner."""
    _write_tsx(good_build, "components/ui/B.tsx",
        'import { X } from "lucide-react";\n'
        'export function B() {\n'
        '  return (\n'
        '    <button data-meta="{a:1, b:2}" aria-label="Close">\n'
        '      <X />\n'
        '    </button>\n'
        '  );\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    # aria-label is present, so this button is fine. If the scanner
    # mishandled the quoted braces it would either fail to find the
    # close > (treating button as never closed) or count the braces
    # toward depth and miss the aria-label.
    assert checks.a11y_static_audit(ctx).status == "pass"


def test_a11y_violations_payload_carries_file_paths_for_repair(good_build):
    _write_tsx(good_build, "components/ui/A.tsx",
        'import { X } from "lucide-react";\n'
        'export function A(){ return <button><X /></button>; }'
    )
    _write_tsx(good_build, "components/ui/B.tsx",
        'import { Y } from "lucide-react";\n'
        'export function B(){ return <button><Y /></button>; }'
    )
    ctx = BuildContext.load(good_build)
    result = checks.a11y_static_audit(ctx)
    assert result.status == "fail"
    assert "components/ui/A.tsx" in result.details["files"]
    assert "components/ui/B.tsx" in result.details["files"]


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


# ---------------------------------------------------------------------------
# schema_org_jsonld_present (#34) — Schema.org JSON-LD in app/layout.tsx
# ---------------------------------------------------------------------------

def test_schema_org_passes_with_jsonld_in_layout(good_build):
    """The good_build fixture already includes a Schema.org JSON-LD
    script tag — the check should pass on it."""
    ctx = BuildContext.load(good_build)
    assert checks.schema_org_jsonld_present(ctx).status == "pass"


def test_schema_org_fails_when_layout_has_no_script_tag(good_build):
    """Strip the JSON-LD script from the layout — the check should
    fail with a clear "no script tag" message."""
    (good_build / "site" / "app" / "layout.tsx").write_text(
        'import { Inter } from "next/font/google";\n'
        'const inter = Inter({ subsets: ["latin"], weight: ["300","400","500","600"], variable: "--font-inter" });\n'
        'export default function L({children}: any) {\n'
        '  return <html lang="en" className={inter.variable}><body className={inter.className}>{children}</body></html>;\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    result = checks.schema_org_jsonld_present(ctx)
    assert result.status == "fail"
    assert "ld+json" in result.message


def test_schema_org_fails_when_jsonld_lacks_schema_org_context(good_build):
    """A script tag with the right MIME but no @context: https://schema.org
    declaration is malformed structured data — the search engine won't
    interpret it. Check should catch this."""
    (good_build / "site" / "app" / "layout.tsx").write_text(
        'import { Inter } from "next/font/google";\n'
        'const inter = Inter({ subsets: ["latin"], weight: ["300","400","500","600"], variable: "--font-inter" });\n'
        'const broken = { "@type": "LocalBusiness", "name": "X" };\n'  # no @context
        'export default function L({children}: any) {\n'
        '  return <html lang="en" className={inter.variable}><body className={inter.className}><script type="application/ld+json" dangerouslySetInnerHTML={{__html: JSON.stringify(broken)}} />{children}</body></html>;\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    result = checks.schema_org_jsonld_present(ctx)
    assert result.status == "fail"
    assert "@context" in result.message


def test_schema_org_skips_when_no_site_dir(tmp_path):
    """No site dir → skip (consistent with every other check)."""
    empty = tmp_path / "no-site"
    empty.mkdir()
    ctx = BuildContext.load(empty)
    result = checks.schema_org_jsonld_present(ctx)
    assert result.status == "skip"


def test_schema_org_fails_when_layout_missing(good_build):
    """Layout file missing → fail with a clear message."""
    (good_build / "site" / "app" / "layout.tsx").unlink()
    ctx = BuildContext.load(good_build)
    result = checks.schema_org_jsonld_present(ctx)
    assert result.status == "fail"
    assert "layout.tsx" in result.message


def test_schema_org_accepts_organization_type(good_build):
    """Both LocalBusiness and Organization are valid foundation types.
    The check is type-agnostic (doesn't pin @type) so an online-only
    SaaS that picks Organization still passes."""
    (good_build / "site" / "app" / "layout.tsx").write_text(
        'import { Inter } from "next/font/google";\n'
        'const inter = Inter({ subsets: ["latin"], weight: ["300","400","500","600"], variable: "--font-inter" });\n'
        'const ld = { "@context": "https://schema.org", "@type": "Organization", "name": "SaaSCo" };\n'
        'export default function L({children}: any) {\n'
        '  return <html lang="en" className={inter.variable}><body className={inter.className}><script type="application/ld+json" dangerouslySetInnerHTML={{__html: JSON.stringify(ld)}} />{children}</body></html>;\n'
        '}'
    )
    ctx = BuildContext.load(good_build)
    assert checks.schema_org_jsonld_present(ctx).status == "pass"


# ---------------------------------------------------------------------------
# sitemap_and_robots_present (#35) — crawler discoverability
# ---------------------------------------------------------------------------

def test_sitemap_robots_passes_on_good_build(good_build):
    """The good_build fixture writes both Next.js 14 convention files."""
    ctx = BuildContext.load(good_build)
    assert checks.sitemap_and_robots_present(ctx).status == "pass"


def test_sitemap_robots_fails_when_sitemap_missing(good_build):
    (good_build / "site" / "app" / "sitemap.ts").unlink()
    ctx = BuildContext.load(good_build)
    result = checks.sitemap_and_robots_present(ctx)
    assert result.status == "fail"
    assert "sitemap.ts" in result.message


def test_sitemap_robots_fails_when_robots_missing(good_build):
    (good_build / "site" / "app" / "robots.ts").unlink()
    ctx = BuildContext.load(good_build)
    result = checks.sitemap_and_robots_present(ctx)
    assert result.status == "fail"
    assert "robots.ts" in result.message


def test_sitemap_robots_fails_when_sitemap_has_no_default_export(good_build):
    """A sitemap.ts that defines but doesn't export a default function
    is broken under Next.js convention."""
    (good_build / "site" / "app" / "sitemap.ts").write_text(
        'function sitemap() { return []; }'  # no export
    )
    ctx = BuildContext.load(good_build)
    result = checks.sitemap_and_robots_present(ctx)
    assert result.status == "fail"
    assert "sitemap.ts" in result.message
    assert "export" in result.message.lower()


def test_sitemap_robots_fails_when_robots_has_no_default_export(good_build):
    (good_build / "site" / "app" / "robots.ts").write_text(
        'function robots() { return {}; }'  # no export
    )
    ctx = BuildContext.load(good_build)
    result = checks.sitemap_and_robots_present(ctx)
    assert result.status == "fail"
    assert "robots.ts" in result.message


def test_sitemap_robots_accepts_arrow_function_export(good_build):
    """`export default () => [...]` is legal Next.js convention."""
    (good_build / "site" / "app" / "sitemap.ts").write_text(
        'export default () => [{ url: "https://example.com/" }];'
    )
    ctx = BuildContext.load(good_build)
    assert checks.sitemap_and_robots_present(ctx).status == "pass"


def test_sitemap_robots_skips_when_no_site_dir(tmp_path):
    empty = tmp_path / "no-site"
    empty.mkdir()
    ctx = BuildContext.load(empty)
    assert checks.sitemap_and_robots_present(ctx).status == "skip"
