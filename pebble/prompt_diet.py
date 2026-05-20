"""Compact replacements for the 5 giant skill blocks (Phase 14a, 2026-05-20).

Per agent research + audit:
- Current paid build prompt: ~54K tokens
- Target (Qwen documented sweet spot): ~10-15K tokens
- Biggest bloat: full SKILL.md injection for no-slop / iOS / stack / BI / ds_text
- Total bloat from those 5 blocks: ~27K tokens

The compact replacements below distill each skill to the LOAD-BEARING rules
(things the eval suite enforces or that genuinely improve quality) and drop
the prose, examples, and rules that the Layout DNA / Style DNA / industry
intel blocks already cover.

Specifically guided by:
- Qwen wants positive directives, NOT "NEVER" lists (qwen3lm.com prompt guide)
- Qwen places critical info at the BEGINNING or END of long prompts; middle
  is at retrieval risk (digitalapplied.com Qwen 3.6 Plus guide)
- The HF Sample-Qwen analysis showed Qwen does WELL on CSS tokens, Tailwind
  config, real Unsplash URLs, GSAP wiring — STOP dictating those.
- Qwen does POORLY on a11y, schema, working forms with name attrs, mobile
  menu JS — KEEP those as explicit guardrails.

Gated by `PEBBLE_PROMPT_DIET` env var (default: "true"). Set to "false" to
revert to the full skill injection if quality regresses.
"""
from __future__ import annotations

import os


def diet_enabled() -> bool:
    """True if prompt diet is active (default). Set PEBBLE_PROMPT_DIET=false
    to revert to the full skill injection for A/B comparison."""
    val = os.environ.get("PEBBLE_PROMPT_DIET", "true").strip().lower()
    return val in {"1", "true", "yes", "on"}


# ─────────────────────────────────────────────────────────────────────
# Replacement for `no_slop_block` (was ~2.5K tokens → now ~150 tokens)
# Keep only rules NOT covered by Style DNA's authoritative font choice.
# ─────────────────────────────────────────────────────────────────────
NO_SLOP_DIET = """
## No-slop rules (positive form)

- **Headlines say something specific.** If the brief gave you a value prop, use it. If it didn't, write a concrete promise about what the visitor will get.
- **Testimonials are real or absent.** When the brief includes real testimonials, render them with the real attribution. When it does not, omit the testimonials section entirely. Never invent a quote, a name, a title, or a star count.
- **Phone numbers are real or labeled.** When the brief includes a real phone number, use it everywhere. When it does not, use the literal string `[BUSINESS PHONE]` so the owner sees what to fill in. Never invent `(555)`-style numbers.
- **Body copy is industry-specific.** If you're writing for a plumber, mention `same-day service` or `up-front pricing`. If you're writing for a coach, mention the specific outcome ("clarity in 3 sessions"). Generic SaaS copy ("transform your business") is forbidden.
- **Voice matches the Style DNA card.** Its `signature_moves` and `feel` describe how the copy should sound. Honor them.
"""


# ─────────────────────────────────────────────────────────────────────
# Replacement for `ios_skill_block` (was ~6.4K tokens → now ~200 tokens)
# All these are eval-enforced. Keep them, drop the long examples.
# ─────────────────────────────────────────────────────────────────────
IOS_RULES_DIET = """
## iOS / mobile non-negotiables

- **Use `100dvh` (or `min-h-dvh`) on all full-height elements**, never `100vh` or `h-screen`. Mobile Safari's URL bar collapses, and `vh` would create a visual jump.
- **Every autoplay video MUST have all four attributes**: `autoPlay muted loop playsInline`. Missing `playsInline` blocks autoplay on iOS.
- **Form inputs MUST be `font-size: 16px` minimum**. Anything smaller triggers Safari's punitive auto-zoom on focus.
- **GSAP `ScrollTrigger.normalizeScroll(true)` and `ScrollTrigger.config({ ignoreMobileResize: true })` MUST be inside `useEffect`**, never at module level — they touch `window` and crash Next.js SSR.
- **No `scroll-behavior: smooth` in CSS anywhere** — it fights GSAP's smooth-scroll and creates a visible double-scroll effect.
- **Respect `@media (prefers-reduced-motion: reduce)`** — wrap each motion component with the project's `withReducedMotion()` helper or guard the animation behind the media query.
"""


# ─────────────────────────────────────────────────────────────────────
# Replacement for `stack_block` (was ~9K tokens → now ~200 tokens)
# File tree + package.json deps. Drop the long prose explanations.
# ─────────────────────────────────────────────────────────────────────
STACK_RULES_DIET = """
## Stack non-negotiables

- **Framework:** Next.js 14 App Router, React 18, TypeScript, Tailwind v3
- **package.json deps (minimum):** `next@^14`, `react@^18`, `react-dom@^18`, `gsap`, `lenis`, `resend`, `@react-three/fiber`, `@react-three/drei` (only if a Three.js scene is used)
- **next.config MUST be `.mjs`** — not `.ts`, not `.js`. Use a JSDoc type hint at top, not `import type`.
- **tsconfig.json paths MUST be `{"@/*": ["./*"]}`** — no `./src/*`. Pebble forbids the `site/src/` directory.
- **File tree:** `app/` (page routes + layout.tsx + globals.css + actions/) · `components/` (Hero, Nav, Footer, ContactForm, ui/) · `lib/` (email.ts, utils, etc.) · `public/` (.gitkeep in images/hero, images/about, images/services, images/gallery, images/logos, images/og, videos, fonts).
- **Server vs Client boundary:** `app/layout.tsx` is a Server Component (must NOT start with `"use client"`). ContactForm + any component using `useState`/`useEffect` MUST start with `"use client"`.
- **Forms USE Server Actions** (`app/actions/contact.ts` calling Resend), not API routes.
- **`next/font/google` config: weight and axes are mutually exclusive.** Either pick specific weights (`weight: ["400", "500", "600"]` — no axes property) OR opt into a variable font with axes (`weight: "variable", axes: [...]`). NEVER pass both. The Next.js font loader throws "Axes can only be defined for variable fonts when the weight property is nonexistent or set to `variable`" at build time if you do.
"""


# ─────────────────────────────────────────────────────────────────────
# Replacement for `bi_block` (was ~6.2K tokens → now ~150 tokens)
# Universal conversion principles. Industry-specific stuff is already
# in industries.json (`{industry_intel_block}` in the prompt).
# ─────────────────────────────────────────────────────────────────────
BUSINESS_INTEL_DIET = """
## Conversion rules

- **One clear primary CTA per page.** If the industry intel says "Call Now", that's the primary. Secondary CTAs (Book, Learn More) are visually subordinate.
- **The phone number is visible above the fold** on home + contact pages when the industry uses phone as a primary CTA (trades, restaurants, salons).
- **Trust signals appear in the first viewport** — years in business, license number, BBB rating, real testimonial count, etc. — whatever the industry intel says converts.
- **Services/menu uses the structure the Layout DNA prescribes** — alternating panels, dense grid, single list, etc. Don't impose a single pattern across layouts.
- **Mobile is the default browser, not an afterthought.** Test the hero, the CTA, the form, and the menu at 375px before considering the page done.
"""


# ─────────────────────────────────────────────────────────────────────
# Replacement for `ds_block` (ui-ux-pro-max output, was ~2.7K tokens
# → now: a single one-liner that defers to the DNA)
# The ds_text engine returned the same Satoshi/General Sans/blue+orange
# template for every build. Style DNA + Industry Intel are authoritative.
# ─────────────────────────────────────────────────────────────────────
DESIGN_SYSTEM_DIET = """
## Design system

The **Style DNA block** at the top of this prompt is the single source of truth for fonts, colors, motion intensity, and layout posture. The **Industry Intel block** in Section 0 is the source for hero type, color psychology, copy tone, and trust signals. Use them. Do not substitute Satoshi, General Sans, glassmorphism, or any other "safe default" that contradicts the DNA.
"""


# ─────────────────────────────────────────────────────────────────────
# Permit + encourage real image URLs (the agent analysis of playground
# HTMLs showed Qwen reliably uses real Unsplash/Pexels URLs when not
# explicitly forbidden — Pebble's current prompt accidentally forbids
# "external image URLs"). This block re-permits them.
# ─────────────────────────────────────────────────────────────────────
IMAGE_RULES_DIET = """
## Image sourcing

- **Use real image URLs from Unsplash or Pexels.** The pattern that works: `https://images.unsplash.com/photo-{id}?auto=format&fit=crop&w={width}&q=80` or `https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=format&fit=crop&w={width}&q=80`. Pick photos that match the industry, palette, and Layout DNA's posture.
- **For local-business images (owner portraits, shop interiors, team photos)** that you cannot know the real photo for, use `/images/about/owner.jpg`, `/images/about/shop.jpg`, etc. with a `next/image` placeholder. The owner replaces these later.
- **`next/image` does NOT forward refs.** To animate an image's container, wrap in a `<div ref={...}>` and animate the wrapper, never `<Image ref={...}>` — that crashes at runtime.
- **Hero image gets `priority` prop.** All other images lazy-load by default.
- **Every `<Image>` has explicit `width` and `height`** (or `fill` + parent `position: relative`).
"""


# ─────────────────────────────────────────────────────────────────────
# Code Pattern verbatim-block stripper (Phase 15d, 2026-05-20)
# ─────────────────────────────────────────────────────────────────────
#
# Per the audit, 8 of the 14 "Code Pattern" sections in
# skills/prompt_template.md contain verbatim TSX/CSS code that Qwen treats
# as copy-paste templates instead of design inspiration. The Layout DNA
# block already specifies which components apply per layout; the verbatim
# code blocks contradict that for ~9/10 layouts.
#
# Patterns to STRIP (verbatim → one-line description):
#   1.  Hero Entrance (AnimatedHeading + FadeIn + Hero usage)  — Layout DNA dictates
#   2.  Liquid-Glass Navbar                                    — Layout DNA dictates
#   9.  GrainOverlay                                           — 6/10 layouts forbid
#   10. GlassCard                                              — most layouts don't use
#   11. BentoGrid                                              — never referenced in any DNA
#   12. MagneticButton                                         — gradient_mesh-specific
#   13. SectionHeader                                          — most DNAs don't use
#   14. CinematicHero                                          — third(!) competing hero spec
#
# Patterns to KEEP (load-bearing, eval-enforced, or genuinely useful):
#   2b. Liquid-Glass CSS utility                               — short, conditional
#   3.  ScrollReveal                                            — small Framer Motion wrapper
#   5.  Parallax Background + Image-ref rule                   — known footgun
#   7.  Three.js Hero (gated by industry intel)                — niche, gated
#   8.  Contact Form (Server Action + Resend)                  — eval-enforced
#
# Net savings: ~5K tokens cut from the template at runtime.

import re

# Headings that mark the START of a stripped section. The matcher finds
# from this heading up to the next `^#### ` heading (the next Code Pattern)
# OR the next `^---$` (section break), whichever comes first.
_STRIP_PATTERNS = [
    "#### 1. Hero Entrance",
    "#### 2. Liquid-Glass Navbar",
    "#### 9. GrainOverlay",
    "#### 10. GlassCard",
    "#### 11. BentoGrid",
    "#### 12. MagneticButton",
    "#### 13. SectionHeader",
    "#### 14. CinematicHero",
]

# One-line replacement summaries (Qwen reads these instead of the verbatim
# TSX blocks). Each tells the LLM to defer to Layout DNA / Style DNA /
# foundation requirements without dictating exact code.
_REPLACEMENT = {
    "#### 1. Hero Entrance": (
        "#### 1. Hero h1 + entrance animation\n\n"
        "**Build per Layout DNA's component table.** If the Layout DNA card "
        "says `use_animated_heading: True`, build a per-character entrance "
        "animation component (named `AnimatedHeading`) using framer-motion. "
        "If `False`, use a plain `<h1>` with Inter font and CSS text-shadow "
        "for legibility. EITHER WAY the component file `components/ui/"
        "AnimatedHeading.tsx` must exist (eval-enforced) — even if your "
        "hero doesn't mount it. Same rule for FadeIn / FadeIn cascade per "
        "the Layout DNA's `use_fade_in_cascade` flag.\n"
    ),
    "#### 2. Liquid-Glass Navbar": (
        "#### 2. Navbar\n\n"
        "**Build per Layout DNA's `nav_pattern` + `nav_structure` description.** "
        "If the DNA says `use_liquid_glass_nav: True`, render a liquid-glass "
        "rounded chip using the `.liquid-glass` CSS utility (see Code Pattern 2b). "
        "If False, build the nav pattern the DNA prescribes (utility bar, "
        "transparent fixed, terminal prompt, etc.). EVERY anchor and `<Link>` "
        "in the nav MUST have explicit Tailwind className for color + hover "
        "+ font weight. Never emit a className-less link.\n"
    ),
    "#### 9. GrainOverlay": (
        "#### 9. GrainOverlay (conditional)\n\n"
        "**Only when Layout DNA says `use_grain_overlay: True`** — render a "
        "fixed `<div>` in app/layout.tsx with an SVG feTurbulence pattern at "
        "opacity ~0.04, mix-blend-mode: overlay, pointer-events: none, "
        "z-index above content but below the nav. Singleton, not per-page. "
        "When False, omit entirely.\n"
    ),
    "#### 10. GlassCard": (
        "#### 10. GlassCard (conditional)\n\n"
        "When the build needs a glassmorphism card, use `backdrop-filter: "
        "blur(var(--glass-blur))`, semi-transparent surface, hairline ring "
        "in `var(--color-border)`. Skip entirely when the Layout DNA doesn't "
        "call for glass treatment.\n"
    ),
    "#### 11. BentoGrid": (
        "#### 11. BentoGrid (only if Layout DNA calls for it)\n\n"
        "Most Layout DNAs don't use bento grids. Build one inline with CSS "
        "Grid only when the DNA explicitly requests it; otherwise omit.\n"
    ),
    "#### 12. MagneticButton": (
        "#### 12. MagneticButton (conditional)\n\n"
        "When you build a magnetic-hover CTA, use Framer Motion's `useSpring` "
        "on x/y translation, dampening ~25, stiffness ~150, rest at 0. Only "
        "use magnetic hover for layouts where the DNA's signature_moves call "
        "for it (typically gradient_mesh, cinematic). Plain hover states are "
        "fine for the rest.\n"
    ),
    "#### 13. SectionHeader": (
        "#### 13. Section headers\n\n"
        "Style section openings per Layout DNA's voice — magazine_scroll uses "
        "chapter labels (`Chapter 02 · Services`), terminal uses command-line "
        "framing (`$ cat services.txt`), weather_report uses status rows, etc. "
        "Don't impose a single eyebrow+h2+subhead pattern across all DNAs.\n"
    ),
    "#### 14. CinematicHero": (
        "#### 14. Gradient-mesh hero (only when Layout DNA is gradient_mesh)\n\n"
        "If and only if Layout DNA is `gradient_mesh`, build the full-viewport "
        "ambient-blob hero with radial-gradient + filter:blur, AnimatedHeading "
        "anchored to the bottom of the viewport, liquid-glass chip in the "
        "right column. For all 9 other Layout DNAs, build the hero per that "
        "DNA's `hero_structure` description instead.\n"
    ),
}


def strip_verbatim_code_patterns(rendered_prompt: str) -> str:
    """Replace verbatim Code Pattern code blocks with one-line summaries.

    Runs ONLY when diet is enabled (caller-checked). For each pattern in
    _STRIP_PATTERNS, find the heading and replace the section content
    through the next `^#### ` or `^---` boundary with the compact
    replacement from _REPLACEMENT.

    Safe to call on a prompt that doesn't contain these patterns — the
    regex just doesn't match and the prompt is returned unchanged.

    The substitution preserves the original `---` section separators so
    the document structure isn't disrupted.
    """
    result = rendered_prompt
    for heading in _STRIP_PATTERNS:
        # Match from the heading to (next #### heading) OR (--- on own line)
        # OR end-of-string, whichever comes first.
        pattern = re.compile(
            r"(?ms)^" + re.escape(heading) + r".*?(?=^####\s|^---\s*$|\Z)"
        )
        replacement = _REPLACEMENT.get(heading, "")
        # Add trailing blank line so the document stays well-spaced
        if not replacement.endswith("\n\n"):
            replacement = replacement.rstrip() + "\n\n"
        result = pattern.sub(replacement, result, count=1)
    return result


__all__ = [
    "diet_enabled",
    "NO_SLOP_DIET",
    "IOS_RULES_DIET",
    "STACK_RULES_DIET",
    "BUSINESS_INTEL_DIET",
    "DESIGN_SYSTEM_DIET",
    "IMAGE_RULES_DIET",
    "strip_verbatim_code_patterns",
]
