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
        "forbidden": ["Three.js", "rounded corners > 4px", "glow shadows", "card grids with shadows", "any use of Fraunces or Inter (use the DNA fonts only)"],
        "industry_affinity": ["editorial", "journal", "publish", "gallery", "museum", "art", "design", "architect", "consult", "advisor", "law", "legal", "attorney", "foundation", "nonprofit"],
        "industry_aversion": ["bar", "club", "gym", "daycare", "plumb", "electric", "hvac", "tow", "automotive"],
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
        "industry_affinity": ["software", "tech", "security", "defense", "engineer", "fintech", "crypto", "b2b", "manufactur", "agency", "data", "infrastructure"],
        "industry_aversion": ["wedding", "yoga", "spa", "daycare", "kids", "baby", "pediatric", "therapy", "florist", "baker", "salon", "beauty", "nursery"],
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
        "industry_affinity": ["software", "security", "devops", "cybersecurity", "infosec", "host", "gaming", "blockchain", "infrastructure", "network", "data", "saas", "dev tool"],
        "industry_aversion": ["wedding", "yoga", "spa", "photo", "daycare", "kids", "baby", "therapy", "florist", "baker", "salon", "beauty", "restaurant", "bar", "hotel", "real estate", "health", "dental", "medical", "retire", "funeral", "hospice", "law", "account", "advisor", "financ", "gallery", "museum", "art", "fashion", "jewel", "watch", "automotive", "plumb", "electric", "hvac", "tow", "construct", "roof", "landscape", "cafe", "deli", "brewery", "distillery", "music venue", "herb", "garden", "farm", "naturopath", "holistic", "coach", "fitness", "gym", "sport", "dance", "pilates", "family", "nursery", "coffee"],
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
        "industry_affinity": ["automotive", "real estate", "hotel", "resort", "travel", "luxury", "fitness", "gym", "sport", "music", "film", "video", "agency", "brand", "fashion", "performance"],
        "industry_aversion": ["daycare", "kids", "baby", "pediatric", "therapy", "hospice", "funeral"],
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
        "forbidden": ["Fraunces", "drop shadows", "gradient anything", "rounded corners > 0px", "color photography (monochrome only)"],
        "industry_affinity": ["architect", "interior", "design", "engineer", "furniture", "yoga", "pilates", "dance", "surveyor", "real estate", "studio"],
        "industry_aversion": ["daycare", "kids", "fast food", "hospice", "funeral"],
    },
    {
        "id": "tactile_y2k",
        "label": "Tactile Y2K",
        "feel": "Pinterest moodboard × early-2000s Apple × a really good neighborhood bakery. Soft, friendly, organic.",
        "display_font": "Bricolage Grotesque",
        "display_font_weight": "600 (variable width)",
        "body_font": "Inter Tight",
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
        "industry_affinity": ["baker", "cafe", "florist", "daycare", "kids", "baby", "family", "salon", "spa", "therapy", "coach", "wellness", "pet", "boutique", "yoga", "photo", "nursery", "beauty"],
        "industry_aversion": ["software", "security", "defense", "contractor", "automotive", "plumb", "electric", "hvac", "tow", "manufactur", "law", "attorney", "account", "fintech"],
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
        "forbidden": ["multiple accent colors", "gradients", "rounded corners > 2px", "drop shadows", "Fraunces", "any decorative element"],
        "industry_affinity": ["consult", "software", "agency", "design", "brand", "architect", "law", "account", "financ", "advisor", "professional", "saas"],
        "industry_aversion": ["daycare", "kids", "automotive", "plumb", "hvac", "tow", "wedding", "florist"],
    },
    {
        "id": "postmodern_max",
        "label": "Postmodern Maximalist",
        "feel": "David Carson × Wieden+Kennedy lookbook × club flyer. Loud, layered, intentionally chaotic.",
        "display_font": "Big Shoulders",
        "display_font_weight": "900",
        "body_font": "Space Grotesk",
        "body_font_weight": "400 / 500",
        "mono_font": "Space Mono",
        "palette_posture": "off-black #1A1A1A page, white #FAFAFA type, THREE accent colors clashing intentionally — hot pink #FF2D87, lime #DCFF00, electric blue #2B6BFF",
        "hero_structure": "Layered chaotic hero. Headline is Big Shoulders 900 at 9XL (industrial display variable font), rotated -3deg, set behind a smaller secondary headline in Space Mono at 2XL rotated +2deg. Photographic element collaged in the background with a halftone filter. Multiple text fragments scattered at different rotations.",
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
        "industry_affinity": ["coffee", "brewery", "music", "club", "gallery", "art", "streetwear", "fashion", "agency", "restaurant", "bar", "tattoo", "skate", "record label", "creative"],
        "industry_aversion": ["law", "attorney", "account", "health", "daycare", "therapy", "financ", "dental", "medical", "retire", "hospice", "funeral", "pediatric", "wedding", "real estate", "advisor"],
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
        "forbidden": ["sans-serif headlines", "Three.js", "card grids", "drop shadows", "neon or saturated accents", "centered headlines that aren't italic"],
        "industry_affinity": ["gallery", "museum", "art", "photo", "bookshop", "antique", "publish", "editorial", "writer", "jewel", "ceramic", "atelier", "wedding", "studio"],
        "industry_aversion": ["software", "contractor", "automotive", "plumb", "gym", "fitness", "fast food", "tow", "hvac", "electric"],
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
        "industry_affinity": ["contractor", "plumb", "electric", "hvac", "roof", "landscape", "automotive", "mechanic", "tow", "manufactur", "warehouse", "logistics", "construct", "demolition", "freight", "fleet", "hauling", "industrial"],
        "industry_aversion": ["wedding", "yoga", "spa", "baker", "florist", "jewel", "salon", "therapy", "pediatric", "gallery", "art", "photo", "cafe", "coffee", "restaurant", "food"],
    },
    {
        "id": "garden_press",
        "label": "Garden Press",
        "feel": "Kinfolk magazine × botanical letterpress almanac. Quiet, premium, considered. The site of someone who plants their own herbs and reads Wendell Berry.",
        "display_font": "Tenor Sans",
        "display_font_weight": "400 (only weight — light editorial, never bold)",
        "body_font": "Inter",
        "body_font_weight": "400",
        "mono_font": "JetBrains Mono",
        "palette_posture": "warm cream #FAF6EE page, charcoal #2C2C2A type, ONE single muted botanical accent (deep sage #4A5D4F or terracotta #C57E5A)",
        "hero_structure": "Decorative hand-drawn botanical line illustrations (single leaf, herb sprig, fern frond) as accents at section dividers and beside pull-quotes. The foundation hero h1 stands clean in Inter; the DNA adds a small botanical illustration in the right column instead of the standard liquid-glass tag — same FadeIn delay (1400ms), same restraint.",
        "motion_intensity": "subtle",
        "motion_rules": "Opacity fades only (0.6s). No parallax. No clip-path reveals. Drop caps animate in via simple opacity. Botanical illustrations appear with a gentle stroke-draw animation (1.2s) if SVG paths allow — otherwise plain fade.",
        "layout_grid": "12-column asymmetric with generous outer margins (12% on desktop). Sections separated by hairline rules (#E8E2D5), never by colored bands. Pull-quotes hang in the margin like a print magazine.",
        "image_treatment": "Warm-toned photography, natural light, no people in stock-photo poses. One dominant photograph per section, full-bleed or two-column. Captions in mono small caps.",
        "signature_moves": [
            "Hand-drawn botanical line illustration (leaf, fern, herb) at top of each section, small enough to feel like a margin doodle",
            "Drop cap on first body paragraph (4-line, Tenor Sans 400, accent color)",
            "Pull-quotes set in Tenor Sans italic, indented like a poem, hanging in the margin",
            "Issue-number footer: 'ISSUE 01 · SUMMER 2026' in mono small caps",
        ],
        "forbidden": ["bright neon", "harsh pure-white backgrounds", "sterile minimalism with no warmth", "sans-serif-only display typography", "stock photography of smiling people in offices"],
        "industry_affinity": ["florist", "herb", "nursery", "garden", "farm", "restaurant", "baker", "wellness", "yoga", "naturopath", "holistic", "photo", "wedding", "tea", "soap", "candle", "artisan", "ceramic", "jewel", "baby", "organic"],
        "industry_aversion": ["software", "automotive", "contractor", "plumb", "security", "hvac", "tow", "defense"],
    },
    {
        "id": "velvet_lounge",
        "label": "Velvet Lounge",
        "feel": "Late-night Manhattan jazz bar × private members club brochure × 1962 cocktail menu. Rich, intimate, candlelit, never garish.",
        "display_font": "Fraunces",
        "display_font_weight": "400 / 500",
        "body_font": "Inter Tight",
        "body_font_weight": "400",
        "mono_font": "IBM Plex Mono",
        "palette_posture": "deep oxblood #2E1A1D page, warm cream #F0E6D2 type, ONE warm gold accent #C8A96E used like brass inlay — never as a button background, always as a hairline or numeral",
        "hero_structure": "Foundation hero with a candlelit night-vision Pexels video (search 'jazz bar low light cocktail'). DNA's right-column accent: a gold-foil-style serif numeral '§ 01' in Fraunces italic (use the SOFT optical-size axis for editorial warmth) instead of the standard liquid-glass tag. Photo captions in IBM Plex Mono small caps mimic a vintage cocktail menu (e.g. 'OLD FASHIONED · 1947').",
        "motion_intensity": "subtle",
        "motion_rules": "Slow opacity fades (1s). Soft warm glow on accent gold elements (text-shadow: 0 0 12px rgba(200,169,110,0.3)). Hover transitions are slow and considered (0.5s ease). No bouncing, no aggressive scroll, no harsh cuts.",
        "layout_grid": "Asymmetric centered with margins. Photographic full-bleeds at section breaks. Body copy hangs in a single column max 60ch wide, never the full viewport width.",
        "image_treatment": "Very warm-toned, low-key lighting, intimate detail shots (one cocktail close-up, one band silhouette, one barback's hands). No bright daylight. No people facing camera. Captions in mono small caps.",
        "signature_moves": [
            "Gold-foil-style serif numerals ('§ 01', '§ 02') at section dividers, in Fraunces italic",
            "Pull-quotes set in Fraunces italic XL, indented like a poem, gold accent on the opening quotation mark",
            "Photo captions in IBM Plex Mono small caps mimicking a vintage cocktail menu ('OLD FASHIONED · 1947')",
            "Footer with a faint film-grain texture and small gold ornament between sections",
        ],
        "forbidden": ["pure white backgrounds", "bright primary colors", "sans-serif-only display headlines", "harsh daylight photography", "neon palette", "rounded corners > 4px", "modern startup tech aesthetic"],
        "industry_affinity": ["bar", "cocktail", "lounge", "jazz", "music", "restaurant", "hotel", "wine", "whiskey", "distillery", "tobacco", "tailor", "jewel", "watchmaker", "club"],
        "industry_aversion": ["daycare", "kids", "baby", "pediatric", "family", "software", "contractor", "gym", "fitness", "plumb", "automotive", "hvac"],
    },
    {
        "id": "marina",
        "label": "Marina",
        "feel": "Hinckley Yachts catalog × Hamptons summer journal × maritime chart. Clean, fresh, salt-air premium — coastal without a single cliched anchor or pirate.",
        "display_font": "Fraunces",
        "display_font_weight": "400 / 500",
        "body_font": "Inter Tight",
        "body_font_weight": "400 / 500",
        "mono_font": "JetBrains Mono",
        "palette_posture": "sailcloth white #FAFAF7 page, deep navy #0E2842 type, ONE warm rope-brown accent #C49E6C used for hairlines and metadata, weathered teak #5D4037 for occasional warm contrast",
        "hero_structure": "Foundation hero video shows coastal water (Pexels search 'sailing yacht coastal water sunset'). DNA's right-column accent: latitude/longitude microcopy in IBM Plex Mono ('40.7128°N · 74.0060°W') instead of the standard liquid-glass tag. A tiny compass-rose icon (4 cardinal points only) appears at section break dividers.",
        "motion_intensity": "subtle",
        "motion_rules": "Opacity fades (0.8s). Very gentle parallax on coastal imagery (yPercent -8% only). No aggressive scroll-jacking, no jarring transitions. Wave-like ease curves where motion exists.",
        "layout_grid": "Asymmetric editorial with generous outer margins. Photographic full-bleeds. Body content centered, max 65ch.",
        "image_treatment": "Cool blue tones offset by warm wood/sailcloth/rope. No surfer-bro aesthetics, no pirate cliches, no 'tropical vacation' brightness. Closer to a Hinckley Yachts catalog than a spring-break ad. Crops favor horizon lines and the meeting of water + wood.",
        "signature_moves": [
            "Latitude/longitude microcopy in IBM Plex Mono near the top of the page ('40.7128°N · 74.0060°W')",
            "Tiny compass-rose icon (4 cardinal marks only) at section dividers, never a full nautical-chart wheel",
            "Photo captions in IBM Plex Mono small caps mimicking a log entry ('AT THE HELM — 0900 HRS')",
            "Footer in 4-section compass layout: NORTH (mission) · EAST (services) · SOUTH (contact) · WEST (legal)",
        ],
        "forbidden": ["literal cartoon anchors", "ship's wheels", "pirate motifs", "bright tropical-vacation color palettes", "all-caps 'BOATING' or 'SAIL' word marks", "surfer aesthetics", "stock photos of people laughing on yachts"],
        "industry_affinity": ["yacht", "boat", "sail", "charter", "marine", "coastal", "beach", "hotel", "resort", "fish", "real estate", "wedding", "photo", "jewel", "watch"],
        "industry_aversion": ["software", "automotive", "plumb", "contractor", "daycare", "urban", "factory", "industrial"],
    },
]


def pick_random_dna(seed: Optional[int] = None) -> dict:
    """Return one random DNA card. Each call rerolls — pass `seed` for determinism in tests."""
    rng = random.Random(seed) if seed is not None else random
    return rng.choice(DNA_CARDS)


_AFFINITY_BOOST = 15


def pick_dna_for_brief(brief: dict, seed: Optional[int] = None) -> dict:
    """Pick a DNA card weighted by the brief's industry signals.

    Each card declares `industry_affinity` (10× weight boost) and
    `industry_aversion` (hard exclude) keyword lists. A card is excluded
    if ANY aversion keyword appears as a substring of the brief's
    `business_type`. Otherwise its weight is `_AFFINITY_BOOST` when any
    affinity keyword matches, else 1. Falls back to uniform random if
    every card was aversed (defensive — shouldn't happen with current
    taxonomy).
    """
    haystack = (brief.get("business_type") or "").lower()
    candidates: list[dict] = []
    weights: list[int] = []
    for card in DNA_CARDS:
        if any(kw in haystack for kw in card.get("industry_aversion", [])):
            continue
        weight = _AFFINITY_BOOST if any(
            kw in haystack for kw in card.get("industry_affinity", [])
        ) else 1
        candidates.append(card)
        weights.append(weight)

    if not candidates:
        return pick_random_dna(seed)

    rng = random.Random(seed) if seed is not None else random
    return rng.choices(candidates, weights=weights, k=1)[0]


def pick_dna_by_id(dna_id: str) -> Optional[dict]:
    """Look up a card by id (used when a brief.json already has a chosen DNA)."""
    for card in DNA_CARDS:
        if card["id"] == dna_id:
            return card
    return None


def build_dna_block(dna: dict) -> str:
    """Return the markdown block to prepend at the TOP of PROMPT.md.

    The DNA block describes ACCENT decorations layered over the engine's
    mandatory foundation (Inter typography, video hero, AnimatedHeading +
    FadeIn components, liquid-glass utility). The DNA does NOT redefine the
    hero, override the body font, or skip the foundation components.
    """
    signatures = "\n".join(f"- {m}" for m in dna["signature_moves"])
    forbidden = ", ".join(dna["forbidden"])
    return f"""# ============================================================
# DESIGN DNA — ACCENT LAYER OVER THE FOUNDATION
# ============================================================

**This build's accent identity is `{dna['label'].upper()}` ({dna['id']}).**

> **{dna['feel']}**

**Read this carefully — the hierarchy is non-obvious:**

The engine's MANDATORY FOUNDATION (defined later in Section 2: AnimatedHeading
hero, FadeIn cascade, liquid-glass navbar chip, Inter typography globally,
background-video hero with NO overlay) is the universal floor every build
matches. The DNA below adds personality ON TOP of that foundation. It does NOT
replace the hero. It does NOT override Inter as the global body/h1 typeface.

When this DNA's `Hero structure` description (below) names elements that
contradict the foundation (a "boot-sequence terminal hero," "no image in hero,"
"NO video"), treat those as accent decorations to layer where compatible — NOT
as a replacement for the foundation. The foundation video + AnimatedHeading +
FadeIn cascade stays in place.

When this DNA's accent display font is named (Cormorant Garamond, Tektur, EB
Garamond, etc.), use it for ACCENT/decorative elements ONLY: pull-quotes, drop
caps in body sections, stat numbers, the optional right-column hero tag, big
sectional numerals. The hero h1 and body copy ALWAYS use Inter. Load the
accent font via `next/font/google` as a second face, attach to a Tailwind
utility (e.g. `font-display`), and apply only on the decorative elements named
in Signature Moves.

The skill files (iOS, Stack, No-Slop, Business Intelligence) still apply for
code correctness. The Foundation governs the universal visual structure. The
DNA governs accent + voice + signature decorations layered on top.

## Accent fonts — DECORATIVE only (NOT the hero h1, NOT body text)

| Role | Face | Weight | Where to apply |
|---|---|---|---|
| Accent display | **{dna['display_font']}** | {dna['display_font_weight']} | Pull-quotes, drop caps, stat numbers, optional right-column hero tag, big sectional numerals |
| Accent body | **{dna['body_font']}** | {dna['body_font_weight']} | Section eyebrows, decorative captions (Inter handles the bulk of body copy) |
| Mono | **{dna['mono_font']}** | 400 | Code-style labels, technical numbering, signature corner marks |

## Palette posture

{dna['palette_posture']}

The Resolved Industry Intelligence palette is a starting point — adapt its hex
values to fit this posture. Apply the accent colors to: section backgrounds
(alternating dark/accent below the hero), CTA fills (the secondary glass CTA
stays glass), pull-quote rules, stat number color, signature decorations. The
HERO section background stays `bg-black` regardless of palette — the video
provides the visual.

## Decorative hero accents (layer on the foundation video hero)

{dna['hero_structure']}

If the description above says "no video" or "no image in hero," IGNORE that
clause — the foundation video hero is mandatory. Take the OTHER elements
(typographic treatment of the headline, optional right-column meta, custom CTA
shapes, signature corner marks) and layer them on the foundation. The
right-column tag in the hero is a perfect home for DNA-flavored accent
typography.

## Motion

**Intensity:** {dna['motion_intensity']}

{dna['motion_rules']}

The hero's AnimatedHeading + FadeIn cascade runs regardless of DNA motion
intensity. The DNA's motion rules apply to sections BELOW the hero.

## Layout grid

{dna['layout_grid']}

## Image treatment

{dna['image_treatment']}

## Signature moves — include AT LEAST 3 of the following in this build

{signatures}

These signature moves are what makes a `{dna['label']}` build feel like a
`{dna['label']}` build. Apply them in sections BELOW the hero — the hero
itself stays the foundation pattern.

## Forbidden in this build

{forbidden}

If any of the above appear elsewhere in this prompt as suggestions for sections
BELOW the hero, ignore those suggestions. The hero foundation is exempt — its
required elements (background video, AnimatedHeading, FadeIn, Inter h1, no
overlay) override the DNA's forbiddens for the hero only.

# ============================================================
# (end Design DNA block — continue to the standard brief below)
# ============================================================

"""
