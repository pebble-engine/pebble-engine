"""
Style DNA — per-build aesthetic personalities.

Each card is a complete visual identity: display/body/mono fonts, hero structure,
motion intensity, layout grid, image treatment, and a list of signature moves the
LLM must include. The engine picks one at random per build so two builds for the
same industry come out feeling like they were made by different studios.

The DNA card is injected at the TOP of the prompt with override-priority framing —
it explicitly contradicts and overrides the Fraunces/Inter defaults baked deeper
in the template. The skill files (iOS, Stack, No-Slop, BI) still apply for code
correctness and conversion patterns; the DNA only governs *visual surface*.

Usage:
    from style_dna import pick_random_dna, build_dna_block
    dna = pick_random_dna()        # random per build
    block = build_dna_block(dna)   # markdown to prepend to PROMPT.md
"""

from __future__ import annotations
import random
from typing import Optional


# Each DNA card is intentionally over-specified. The LLM follows the most concrete
# instruction it sees; vague directions converge, specific ones diverge.
DNA_CARDS: list[dict] = [
    {
        "id": "swiss_magazine",
        "label": "Swiss Magazine",
        "feel": "Editorial print magazine. Vignelli-meets-Pentagram. Quiet authority.",
        "display_font": "Cormorant Garamond",
        "display_font_weight": "600 (italic optional for emphasis)",
        "body_font": "Inter Tight",
        "body_font_weight": "400 / 500",
        "mono_font": "IBM Plex Mono",
        "palette_posture": "warm off-white #FAF8F3 page, ink #0E0E10 type, ONE single muted accent (sage #5E7A6E or burgundy #6B2B2B)",
        "hero_structure": "Asymmetric two-column. Left: oversized italic Cormorant headline (8XL, hangs into negative space). Right: thin meta column with year established, license number, jurisdiction set in IBM Plex Mono 10px uppercase. NO video, NO image overlay — a single dominant editorial photograph sits below the fold, not behind the text.",
        "motion_intensity": "subtle",
        "motion_rules": "Scroll-tied opacity fades only (0.6s). NO SplitText, NO parallax, NO clip-path reveals, NO Three.js. Drop caps animate in via simple opacity. Lenis smooth scroll is on, but ScrollTrigger usage is minimal.",
        "layout_grid": "12-column asymmetric with generous outer margins (10% on desktop). Sections separated by hairline rules (#E8E2D5), never by colored bands.",
        "image_treatment": "ONE dominant photograph per section, full-bleed or two-column, never card grids. Black and white or desaturated. Captions in IBM Plex Mono.",
        "signature_moves": [
            "Drop cap on first body paragraph (4-line, Cormorant 600, color #6B2B2B)",
            "Running header at top of each section: '§ 02 · SERVICES' in IBM Plex Mono",
            "Pull-quotes set in Cormorant italic 4XL, no quote marks, hairline rules above and below",
            "Page numbers in the footer like a magazine: '03 / 07'",
        ],
        "forbidden": ["Three.js", "video hero", "rounded corners > 4px", "glow shadows", "card grids with shadows", "any use of Fraunces or Inter (use the DNA fonts only)"],
    },
    {
        "id": "brutalist_editorial",
        "label": "Brutalist Editorial",
        "feel": "Stripe Press × Are.na × defense-contractor investor deck. Confident, unornamented, large.",
        "display_font": "Tektur",
        "display_font_weight": "900 (wide stance, hard edges)",
        "body_font": "Geist",
        "body_font_weight": "400 / 500",
        "mono_font": "Geist Mono",
        "palette_posture": "pure black #050505 page, off-white #F5F5F5 type, ONE saturated accent (electric orange #FF5A1F or acid green #C4FF00)",
        "hero_structure": "Full-bleed typographic hero. Headline is Tektur 900 set to wrap into 2-3 lines that fill the viewport — uppercase, tight tracking, raw. No image behind it. Single thin horizontal rule across the bottom of the viewport with mono kicker text. CTA is a flat rectangular button, no shadow, hover inverts colors.",
        "motion_intensity": "aggressive",
        "motion_rules": "Hero text splits character-by-character on scroll using vanilla splitWords. ScrollTrigger pins one statement section mid-page. Hover states snap (no 300ms ease). One looping video clip muted in the background of section 2, not the hero.",
        "layout_grid": "Hard 12-column with zero outer margin (page goes edge to edge). Sections separated by thick (4px) horizontal rules in the accent color.",
        "image_treatment": "Raw photo grids, no rounded corners, no captions overlaid — captions sit below in mono. Photos in full saturation or pure black-and-white, never desaturated middle ground.",
        "signature_moves": [
            "Big numbers section with one statistic per line, mono kicker labels (e.g. '5,000+ JOBS' / '12-YR WARRANTY')",
            "Sticky horizontal rule at the bottom of viewport on scroll with current section name in mono",
            "Image captions formatted as: 'FIG. 03 — TECHNICIAN ON SITE, BAY SHORE NY'",
            "Footer is a single typographic block, no columns, set in Tektur",
        ],
        "forbidden": ["Fraunces", "Inter as display", "serif headlines", "rounded corners > 2px", "drop shadows", "gradient backgrounds", "Three.js particles"],
    },
    {
        "id": "terminal_operator",
        "label": "Terminal Operator",
        "feel": "Vintage CRT terminal. Mission control. Hacker News × NASA Apollo Guidance Computer.",
        "display_font": "IBM Plex Mono",
        "display_font_weight": "700 (uppercase, wide tracking)",
        "body_font": "IBM Plex Mono",
        "body_font_weight": "400",
        "mono_font": "IBM Plex Mono",
        "palette_posture": "pure black #000000 page, phosphor green #00FF7F primary or amber #FFB000 type, no other colors except white #FFFFFF for emphasis",
        "hero_structure": "Boot-sequence hero. Top of viewport shows mono text typing in line by line: '> initializing...', '> module: [BUSINESS_NAME].sys loaded', '> location: [CITY]', then the headline appears in big mono 6XL after a 0.4s delay. Cursor blinks at the end. NO images in hero. ASCII art logo optional in the corner.",
        "motion_intensity": "smooth",
        "motion_rules": "Every reveal is a typewriter effect (vanilla JS, ~30ms per char). Scanline overlay across the whole page (1px horizontal lines at 1% opacity). Subtle CRT bloom on text (text-shadow 0 0 8px accent color). No GSAP timelines beyond the typewriter — Lenis still on.",
        "layout_grid": "Fixed-width monospace columns (80 chars max body, like a terminal). ASCII box-drawing characters as section dividers: ┌─────┐ etc.",
        "image_treatment": "Images dithered to 2-tone (black + accent) using CSS filter. Captions formatted as '[ IMG_03.JPG — TECHNICIAN ]'. No full-color photography.",
        "signature_moves": [
            "ASCII section dividers between every block (e.g. '════════════════')",
            "Cursor block (█) that blinks next to interactive elements",
            "Status bar at the bottom of viewport showing 'CONN: SECURE · TIME: 14:32:08 · MODE: OPERATIONAL' updating live",
            "All buttons render as: [ CALL NOW ] with bracket characters as the border",
        ],
        "forbidden": ["any sans-serif other than mono", "any serif font", "color photography", "gradients", "rounded corners > 0px", "glow effects beyond CRT bloom", "Three.js"],
    },
    {
        "id": "cinematic_imax",
        "label": "Cinematic IMAX",
        "feel": "Movie poster meets Tesla product page. Widescreen, dramatic, score-driven.",
        "display_font": "Unbounded",
        "display_font_weight": "700-900 (wide, geometric)",
        "body_font": "Geist",
        "body_font_weight": "400 / 500",
        "mono_font": "Geist Mono",
        "palette_posture": "deep black #0A0A0A page, white #FFFFFF type, ONE single bold accent (vermilion #FF3A1F or cyan #00DAF3 — pick by industry mood)",
        "hero_structure": "Full-viewport video hero (Pexels mp4) at 100vh, dark gradient overlay from black at bottom to transparent at top. Unbounded 900 headline anchored bottom-left, 8XL, set to wrap to fill the bottom third. Eyebrow in mono uppercase above it. CTAs at the very bottom: one filled rectangle, one ghost.",
        "motion_intensity": "cinematic",
        "motion_rules": "Hero text reveals via clip-path inset wipe (0.8s cubic-bezier). ScrollTrigger pins each 100vh section, scroll-zooms the hero video out as you leave it. Three.js particle field optional in section 3. GSAP timelines with offset delays. Lenis lerp 0.08 (a touch slower than default).",
        "layout_grid": "100vh-section based, full-bleed everything, no outer margins on desktop, content max-width 1400px centered.",
        "image_treatment": "Widescreen crops (16:9 or wider) only. High contrast, cinematic color grade. Each image is full-bleed or 2/3 width with massive caption.",
        "signature_moves": [
            "Scroll progress indicator pinned to the right edge of viewport, dot per section",
            "Section numbers as oversized ghost numerals behind headlines ('02' in Unbounded 12XL at 4% opacity)",
            "Stat counters that animate from 0 on scroll into view",
            "End-of-section transitions: a 0.6s fade-to-black between major chapters",
        ],
        "forbidden": ["Fraunces", "serif headlines", "card grids", "horizontal scroll", "static heroes", "any flat background color hero"],
    },
    {
        "id": "architectural_spec",
        "label": "Architectural Spec",
        "feel": "OMA / Bjarke Ingels project page. Drafting-table precision. Dimensions visible.",
        "display_font": "Archivo",
        "display_font_weight": "700 (or Archivo Narrow for emphasis)",
        "body_font": "Inter",
        "body_font_weight": "400 / 500",
        "mono_font": "JetBrains Mono",
        "palette_posture": "drafting-paper #F4F1EA page, ink #1A1A1A type, ONE blueprint blue #2B4DCB accent",
        "hero_structure": "Technical-drawing hero. Headline set in Archivo 700 left-aligned. To its right: a technical line-drawing diagram (SVG, no fills, just strokes) showing the business in plan view. Dimension lines with mono labels mark the headline like architectural plans: '← 480px →'.",
        "motion_intensity": "minimal",
        "motion_rules": "SVG line-drawings stroke-animate on scroll into view (stroke-dasharray trick). Dimension labels fade in 0.2s after their lines complete. Everything else is static. No video, no Three.js.",
        "layout_grid": "Grid lines visible on hover (toggle via small button in footer). Strict 12-column with 8px gutters. Sections labeled '01.00 — IDENTITY' '02.00 — SERVICES' in mono.",
        "image_treatment": "Photos rendered as monochrome with dimension annotations overlaid (e.g. arrows pointing to specific elements with mono labels). Or replaced entirely with SVG technical drawings.",
        "signature_moves": [
            "Drafting-style dimension lines that bracket the headline and key images",
            "North arrow icon in the top-right corner of the page (vestigial but charming)",
            "Section labels formatted like blueprint sheets: '01.00 — IDENTITY · SHT 1 OF 4'",
            "Toggle button labeled 'GRID' in the footer that shows/hides the underlying 12-column grid",
        ],
        "forbidden": ["Fraunces", "video hero", "drop shadows", "gradient anything", "rounded corners > 0px", "color photography (monochrome only)"],
    },
    {
        "id": "tactile_y2k",
        "label": "Tactile Y2K",
        "feel": "Pinterest moodboard × early-2000s Apple × a really good neighborhood bakery. Soft, friendly, organic.",
        "display_font": "Bricolage Grotesque",
        "display_font_weight": "600 (variable width)",
        "body_font": "General Sans",
        "body_font_weight": "400 / 500",
        "mono_font": "IBM Plex Mono",
        "palette_posture": "warm peach-cream #FBF1E3 page, cocoa #2A1F1A type, dusty rose #D4899A primary accent, soft sage #B8C5A6 secondary accent",
        "hero_structure": "Centered hero with a single soft-shadowed photograph at the top, organic blob-shaped frame (border-radius: 60% 40% 70% 30%). Headline below in Bricolage italic 5XL with the variable-width axis animated subtly. CTA is a pill button with a soft inner shadow.",
        "motion_intensity": "smooth",
        "motion_rules": "Subtle wobble animations on interactive elements (rotate -1deg to 1deg on hover). Bricolage variable axis morphs on scroll. Soft fade-ups on section reveal. No aggressive scroll pinning.",
        "layout_grid": "Loose centered single-column with offset image floats. Generous padding (96px section gaps). All corners rounded 24px-32px.",
        "image_treatment": "Single dominant photos with organic blob masks. Soft drop shadows (0 24px 48px rgba(0,0,0,0.08)). Slight grain overlay.",
        "signature_moves": [
            "One subtle SVG wave or blob shape that slowly morphs in the hero background (4s ease-in-out)",
            "Hand-drawn-style icons (rough/sketch stroke) for service categories",
            "Pull quotes set in Bricolage italic with quote marks rendered as oversized opening-quote glyph behind the text",
            "Soft-glow focus states on inputs (box-shadow with peach tint)",
        ],
        "forbidden": ["pure black backgrounds", "Tektur", "any aggressive motion", "ASCII characters", "monochrome photography only — color is required"],
    },
    {
        "id": "neue_haas_minimal",
        "label": "Neue Haas Minimal",
        "feel": "Massimo Vignelli × Apple Marcom 2014. Brutally simple, monochrome, one accent.",
        "display_font": "Inter Tight",
        "display_font_weight": "700 (uppercase tracking-wide)",
        "body_font": "Inter",
        "body_font_weight": "400",
        "mono_font": "JetBrains Mono",
        "palette_posture": "pure white #FFFFFF page, near-black #111111 type, ONE single accent — Vignelli red #C8102E — used sparingly (CTA only, one underline, one quote dash)",
        "hero_structure": "Centered hero. Headline in Inter Tight 700 uppercase, letter-spacing 0.02em, max 4 words, fills 60% of viewport. Below it a single horizontal red bar (4px × 80px). Below that a one-sentence sub. No image in hero. Negative space dominates.",
        "motion_intensity": "minimal",
        "motion_rules": "Single opacity fade-in on each section as it enters viewport (0.5s). Hover states use 0.2s linear color shift only. No GSAP timelines, no SplitText, no parallax. Lenis on but barely noticeable.",
        "layout_grid": "Strict 12-column, perfectly aligned. All text left-aligned. Every section starts with a number label '01.' '02.' '03.' in red.",
        "image_treatment": "Single image per section, perfect 16:10 ratio, monochrome with subtle red duotone tint. Aligned to grid, no breaking out.",
        "signature_moves": [
            "Numbered section starts: '01.' in red at the top-left of each major block",
            "Single 4px red horizontal bar that recurs as visual signature (after headline, after key stats)",
            "All buttons are simple text links with red underline — no boxed CTAs anywhere",
            "Massive negative space — sections often only 30% filled vertically",
        ],
        "forbidden": ["multiple accent colors", "video hero", "gradients", "rounded corners > 2px", "drop shadows", "Fraunces", "any decorative element"],
    },
    {
        "id": "postmodern_max",
        "label": "Postmodern Maximalist",
        "feel": "David Carson × Wieden+Kennedy lookbook × club flyer. Loud, layered, intentionally chaotic.",
        "display_font": "Big Shoulders Display",
        "display_font_weight": "900",
        "body_font": "Space Grotesk",
        "body_font_weight": "400 / 500",
        "mono_font": "Space Mono",
        "palette_posture": "off-black #1A1A1A page, white #FAFAFA type, THREE accent colors clashing intentionally — hot pink #FF2D87, lime #DCFF00, electric blue #2B6BFF",
        "hero_structure": "Layered chaotic hero. Headline is Big Shoulders 900 at 9XL, rotated -3deg, set behind a smaller secondary headline in Space Mono at 2XL rotated +2deg. Photographic element collaged in the background with a halftone filter. Multiple text fragments scattered at different rotations.",
        "motion_intensity": "aggressive",
        "motion_rules": "Marquee scrollers running horizontally in multiple sections (different speeds, different directions). Hover states flash to a clashing color and shake (subtle). Sections slide in from different directions on scroll (left, right, up). Three.js NOT used — keep it 2D and graphic.",
        "layout_grid": "Broken grid. Elements bleed off edges. Some images at 110% width (clipped by overflow:hidden on body). Diagonal section dividers (SVG triangles, not rules).",
        "image_treatment": "Halftone filter on photography. Color-blocked overlays partially obscuring images. Captions in Space Mono ALL CAPS, sometimes overlapping the image.",
        "signature_moves": [
            "Horizontal marquee with the business name repeating: 'IRON CESSPOOL — IRON CESSPOOL — IRON CESSPOOL —' running across at section breaks",
            "Diagonal SVG cuts as section dividers (not horizontal rules)",
            "Multiple type sizes within a single headline — 'WE' huge, 'fix' tiny, 'PIPES' medium",
            "Sticker-style trust signals — circular badges with rotated text 'LICENSED!' 'INSURED!' overlapping each other",
        ],
        "forbidden": ["Fraunces", "Inter as display", "minimalism", "single accent color", "perfect grid alignment", "rounded subtle anything"],
    },
    {
        "id": "arthouse_folio",
        "label": "Arthouse Folio",
        "feel": "Museum exhibition catalog × small-press art book. Quiet, considered, italics for emphasis.",
        "display_font": "EB Garamond",
        "display_font_weight": "500 (italic for headlines)",
        "body_font": "Inter",
        "body_font_weight": "400",
        "mono_font": "Geist Mono",
        "palette_posture": "soft cream #F7F3EC page, warm ink #2A2520 type, ONE muted accent — dusty terracotta #C5614B — appearing only on links and small marks",
        "hero_structure": "Centered editorial hero. Single italic EB Garamond 6XL headline (max one sentence, often italic-only), centered on the page. Below it: a thin horizontal rule (1px terracotta, 120px wide). Below that: subhead in Inter 18px italic. NO image in the hero — the typography is the hero.",
        "motion_intensity": "minimal",
        "motion_rules": "Subtle parallax on hero text only — slight Y-translate on scroll (10px max). Section reveals are gentle fade-ups (0.7s ease-out). No SplitText, no clip-path. Lenis on, very smooth.",
        "layout_grid": "Centered single-column for prose (max-width 680px), full-bleed for images. Generous vertical padding between sections (160px desktop).",
        "image_treatment": "Single large image per section, treated like museum-catalog photography. Light grain, warm tone. Always captioned with title + medium + year in italic Garamond ('Untitled, oil on canvas, 2024').",
        "signature_moves": [
            "Italic-set pull quotes with the author/role attribution beneath in Inter 14px",
            "Section openers framed like a book chapter: 'I.', 'II.', 'III.' as oversized italic Garamond Roman numerals",
            "Footnotes — actual superscript footnote markers in body text that scroll to a footnotes section at the bottom",
            "Page numbers in the footer as roman numerals (iii / x)",
        ],
        "forbidden": ["sans-serif headlines", "video hero", "Three.js", "card grids", "drop shadows", "neon or saturated accents", "centered headlines that aren't italic"],
    },
    {
        "id": "industrial_freight",
        "label": "Industrial Freight",
        "feel": "Shipping manifest × heavy-equipment catalog × warehouse signage. Utilitarian, blocky, no nonsense.",
        "display_font": "Anton",
        "display_font_weight": "400 (only weight — narrow industrial sans)",
        "body_font": "Inter",
        "body_font_weight": "400 / 500",
        "mono_font": "JetBrains Mono",
        "palette_posture": "concrete grey #2D2D2D page, off-white #E8E5E0 type, ONE high-vis accent — safety yellow #FFD200 — used like industrial signage",
        "hero_structure": "Hero feels like a freight container side. Anton headline at 9XL set in all-caps fills the width. Mono stencil-style ID number ('REF-2026-IRN') in the top corner. Yellow diagonal hazard stripes (CSS gradient) at the very top of the page as a 4px-tall band.",
        "motion_intensity": "smooth",
        "motion_rules": "Section reveals: slide in from the right like loading containers (transform: translateX, 0.6s ease-out). Buttons have a depressed-stamp animation on click (briefly translateY 2px). No flashy stuff — feels mechanical.",
        "layout_grid": "Strict modular grid like a cargo manifest. Equal-height rows. Every section labeled at top-left with stencil-style mono code: 'SVC-001 / EMERGENCY' 'CRD-014 / TESTIMONIAL'.",
        "image_treatment": "Photos with slight desaturation and yellow corner overlay. Captions look like shipping labels (mono on yellow rectangles).",
        "signature_moves": [
            "Yellow diagonal hazard-stripe pattern as a hairline accent (top of page, between sections)",
            "Mono REF codes on every block (e.g. 'SVC-001', 'TM-003') in the top-left corner of each",
            "Stencil-letter section headers (Anton with white outline, no fill)",
            "A 'CERTIFIED' stamp graphic (rotated -8deg, terracotta on cream) over a trust-signal element",
        ],
        "forbidden": ["Fraunces", "serif headlines", "rounded corners > 2px", "soft drop shadows", "pastel palettes", "delicate motion"],
    },
]


def pick_random_dna(seed: Optional[int] = None) -> dict:
    """Return one random DNA card. Each call rerolls — pass `seed` for determinism in tests."""
    rng = random.Random(seed) if seed is not None else random
    return rng.choice(DNA_CARDS)


def pick_dna_by_id(dna_id: str) -> Optional[dict]:
    """Look up a card by id (used when a brief.json already has a chosen DNA)."""
    for card in DNA_CARDS:
        if card["id"] == dna_id:
            return card
    return None


def build_dna_block(dna: dict) -> str:
    """Return the markdown block to prepend at the TOP of PROMPT.md.

    The block uses uppercase OVERRIDE framing because the rest of the prompt
    (skill files, resolved contract) contains older Fraunces/Inter defaults
    that we need the LLM to ignore in favor of the DNA's chosen fonts.
    """
    signatures = "\n".join(f"- {m}" for m in dna["signature_moves"])
    forbidden = ", ".join(dna["forbidden"])
    return f"""# ============================================================
# DESIGN DNA — TOP-PRIORITY DIRECTIVE
# ============================================================

**This build's aesthetic identity is `{dna['label'].upper()}` ({dna['id']}).**

> **{dna['feel']}**

The choices in this block OVERRIDE any conflicting recommendations elsewhere in
this prompt — including the Resolved Design Contract's font suggestions, the
Code Patterns section's hero structure, and any "always cinematic" language
deeper in the spec. The skill files (iOS, Stack, No-Slop, Business Intelligence)
still apply for code correctness; this block governs the *visual surface*.

## Fonts — use these EXACT faces, loaded via `next/font/google` in `layout.tsx`

| Role | Face | Weight |
|---|---|---|
| Display (headings, hero) | **{dna['display_font']}** | {dna['display_font_weight']} |
| Body (paragraphs, UI) | **{dna['body_font']}** | {dna['body_font_weight']} |
| Mono (labels, captions, code) | **{dna['mono_font']}** | 400 |

Set them as CSS variables (`--font-display`, `--font-body`, `--font-mono`) on
`<html>` and reference them via Tailwind's `font-display` / `font-body` /
`font-mono` utilities or direct CSS variables.

## Palette posture

{dna['palette_posture']}

The Resolved Industry Intelligence palette (below) is a *starting point* — adapt
its hex values to fit this posture. If the industry says `#1B3A6B primary` but
this DNA calls for "pure black + one neon accent," push the industry primary
toward `#0A0A0A` and lift the accent to the DNA-recommended saturation.

## Hero structure (THIS build's hero, overriding the generic spec)

{dna['hero_structure']}

## Motion

**Intensity:** {dna['motion_intensity']}

{dna['motion_rules']}

## Layout grid

{dna['layout_grid']}

## Image treatment

{dna['image_treatment']}

## Signature moves — include AT LEAST 3 of the following in this build

{signatures}

These signature moves are what makes a `{dna['label']}` build feel like a
`{dna['label']}` build. Without them, you have a generic site with new fonts —
that's not enough.

## Forbidden in this build

{forbidden}

If any of the above appear elsewhere in this prompt as suggestions, **ignore
those suggestions for this build**. The DNA is the highest visual authority.

# ============================================================
# (end Design DNA block — continue to the standard brief below)
# ============================================================

"""
