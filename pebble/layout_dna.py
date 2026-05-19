"""Layout DNA — structural architecture personalities for generated sites.

Each card defines HOW a site is built (hero type, nav pattern, section
flow, component usage) rather than WHAT it looks like (colors/fonts —
that is Style DNA's job in style_dna.py).

The separation is deliberate:
  - Layout DNA  →  structure  →  "what shape is the container?"
  - Style DNA   →  surface    →  "what color is the paint?"

Combining 10 layout cards × 11 style cards = 110 combinations before
industry or brief content enters the picture. A mechanic shop can be a
dense data-dashboard (weather_report) OR a manifesto of bold type OR a
gallery of workshop photography — all with the same Safety Yellow palette.

Usage:
    from pebble.layout_dna import pick_layout_for_brief, build_layout_block
    layout = pick_layout_for_brief(brief, creative_direction="")
    block  = build_layout_block(layout)
    prompt = block + style_block + lang_prefix + rendered_template
"""

from __future__ import annotations
import random
from typing import Optional


LAYOUT_CARDS: list[dict] = [

    # ------------------------------------------------------------------ #
    # 1. GRADIENT MESH — current engine default, kept as one option        #
    # ------------------------------------------------------------------ #
    {
        "id": "gradient_mesh",
        "label": "Gradient Mesh",
        "feel": "Contemporary product site. Full-viewport ambient-light hero. The engine's classic output — elevated.",
        "hero_type": "gradient_mesh",
        "hero_structure": """Full-viewport CSS gradient mesh hero. Two or three radial-gradient blobs
absolutely positioned (pointer-events-none, aria-hidden), filter: blur(60-80px),
using --color-accent-glow. The h1 sits at the BOTTOM of the viewport (flex flex-col
justify-end). AnimatedHeading for the h1. FadeIn cascade for subhead + CTAs.
Two-column grid on lg+ screens. Liquid-glass chip in the right column.""",
        "nav_pattern": "floating_chip",
        "nav_structure": "Liquid-glass rounded chip floating at top. absolute top-0 inset-x-0 z-50 with horizontal page padding.",
        "section_flow": ["hero", "trust_bar", "services_alternating", "social_proof", "about_story", "faq_callout", "final_cta", "footer"],
        "information_density": "medium",
        "reading_mode": "scroll",
        "use_animated_heading": True,
        "use_liquid_glass_nav": True,
        "use_fade_in_cascade": True,
        "use_grain_overlay": True,
        "industry_affinity": ["tech", "saas", "software", "agency", "startup", "brand", "marketing", "studio", "consult", "advisory", "finance", "invest"],
        "industry_aversion": ["mechanic", "plumb", "hvac", "electrician", "contractor", "bakery", "florist", "restaurant", "bar", "pub"],
        "keyword_triggers": ["modern", "sleek", "tech", "product", "startup", "clean gradient", "glow", "ambient"],
        "forbidden": ["flat single-color hero background", "video hero", "image-only hero", "no gradient blobs"],
        "signature_moves": [
            "Gradient mesh blobs with radial-gradient + blur create an ambient light source specific to the brand color",
            "Hero text anchored at bottom of viewport — reads up from the fold",
            "Liquid-glass chip navbar floats over the gradient",
        ],
    },

    # ------------------------------------------------------------------ #
    # 2. SPLIT SCREEN — editorial, photo-left or photo-right               #
    # ------------------------------------------------------------------ #
    {
        "id": "split_screen",
        "label": "Split Screen",
        "feel": "Editorial bi-panel. Half photograph, half typeset argument. The NYT real-estate section meets a design agency folio.",
        "hero_type": "split_screen",
        "hero_structure": """Hero is a perfect CSS Grid: grid-cols-2 with 50vw each column.
LEFT panel: full-bleed photograph (next/image fill + object-cover).
RIGHT panel: dark/light panel (background from --color-bg), centered content column.
  - Eyebrow in mono uppercase tracking-widest (12px)
  - h1 in Inter 700 (NOT AnimatedHeading — static, heavy, serif-like authority)
  - Subhead in regular weight, max 2 sentences
  - Two CTAs: one filled, one ghost
  - NO gradient mesh blobs on the right panel — use a solid --color-bg
Mobile: stack vertically (photo top, text below). The photo becomes 55vh,
text panel becomes auto.
There is NO full-viewport gradient blob behind the type — the split is
the visual statement.""",
        "nav_pattern": "fixed_top",
        "nav_structure": "Thin fixed header above the split. No liquid-glass — instead: transparent bg, white text, with a 1px bottom border that appears only on scroll (IntersectionObserver). Logo left, links right, one CTA button far right.",
        "section_flow": ["hero_split", "intro_paragraph", "services_alternating", "numbers_bar", "team_grid", "testimonials", "contact_inline", "footer"],
        "information_density": "medium",
        "reading_mode": "scroll",
        "use_animated_heading": False,
        "use_liquid_glass_nav": False,
        "use_fade_in_cascade": True,
        "use_grain_overlay": False,
        "industry_affinity": ["real estate", "architect", "interior", "property", "photo", "wedding", "atelier", "fashion", "boutique", "studio"],
        "industry_aversion": ["mechanic", "plumb", "hvac", "electrician", "contractor", "fast food"],
        "keyword_triggers": ["editorial", "split", "half", "photo left", "photo right", "newspaper", "magazine layout", "two column hero"],
        "forbidden": ["gradient mesh blobs in hero", "AnimatedHeading in hero h1", "liquid-glass chip nav"],
        "signature_moves": [
            "Hero is a hard 50/50 CSS grid split — not a hero image with an overlay",
            "Nav border appears only after scrolling past the hero (JS IntersectionObserver)",
            "Services section uses full-bleed alternating left/right photo panels (not cards)",
        ],
    },

    # ------------------------------------------------------------------ #
    # 3. MAGAZINE SCROLL — long-form editorial                             #
    # ------------------------------------------------------------------ #
    {
        "id": "magazine_scroll",
        "label": "Magazine Scroll",
        "feel": "Long-form editorial. Kinfolk meets The New Yorker. Text is the hero. Photography supports prose.",
        "hero_type": "type_only",
        "hero_structure": """NO full-viewport hero image or gradient. The page opens directly into the first
editorial section: a large typeset headline (5xl–7xl, Inter 300 light weight) that
bleeds into a standfirst paragraph. Below it: a single wide editorial photograph
(full-width, aspect-ratio 21/9, no rounded corners). The headline IS the page opening.
No gradient mesh. No blobs. No AnimatedHeading.
The date/issue/category appears above the headline in mono 11px uppercase
(like a magazine dateline): 'ISSUE 04 · {INDUSTRY} · {CITY}'""",
        "nav_pattern": "sticky_chapter",
        "nav_structure": "Sticky left sidebar (hidden on mobile, visible lg+). Contains the chapter list as short text links: '01 Services', '02 Process', '03 About', '04 Contact'. Each link highlights on scroll via IntersectionObserver. On mobile: a compact fixed top bar with just logo + hamburger. The chapter nav IS the navigation — no traditional menu.",
        "section_flow": ["dateline_hero", "editorial_intro", "chapter_01_services", "pull_quote_break", "chapter_02_process", "full_bleed_photo", "chapter_03_about", "chapter_04_contact", "footnotes_footer"],
        "information_density": "dense",
        "reading_mode": "scroll",
        "use_animated_heading": False,
        "use_liquid_glass_nav": False,
        "use_fade_in_cascade": False,
        "use_grain_overlay": False,
        "industry_affinity": ["editorial", "publish", "journal", "media", "writer", "law", "attorney", "consult", "advisory", "gallery", "art", "museum", "foundation"],
        "industry_aversion": ["mechanic", "plumb", "hvac", "electrician", "contractor", "fast food", "bar", "club"],
        "keyword_triggers": ["long form", "editorial", "essay", "magazine", "chapter", "reading experience", "text heavy", "journal", "newsletter"],
        "forbidden": ["AnimatedHeading", "gradient mesh hero", "liquid-glass chip", "card grids", "trust bar with icons"],
        "signature_moves": [
            "Sticky chapter sidebar replaces traditional navbar on desktop",
            "Pull-quotes rendered as full-width type blocks with a left border accent",
            "Sections labeled as chapters with dateline formatting",
        ],
    },

    # ------------------------------------------------------------------ #
    # 4. SINGLE SCREEN — compact, everything above the fold                #
    # ------------------------------------------------------------------ #
    {
        "id": "single_screen",
        "label": "Single Screen",
        "feel": "Everything on one scroll. No dedicated sub-pages needed. Dense but not crowded. Business card meets landing page.",
        "hero_type": "compact_hero",
        "hero_structure": """Compact hero — NOT full-viewport. max-height 60vh. Gradient mesh background
(--color-bg + --color-accent-glow blobs) but smaller: blobs at 50% opacity,
200-300px. Headline in AnimatedHeading at a smaller scale (text-3xl md:text-4xl lg:text-5xl).
Subhead one sentence max. Single CTA only — no secondary CTA clutter.
The reduction is intentional: the hero is a compact header that announces the
business, not a film-poster moment. The information-dense sections below are
the point.""",
        "nav_pattern": "anchor_scroll",
        "nav_structure": "Anchor-scroll nav: a single-row of text links at the very top (no background, no chip). Each link is an anchor to a same-page section ID. Logo left, anchor links center, phone number right (as tel: link). Becomes fixed after scrolling 100px. No sub-pages — the entire site is app/page.tsx.",
        "section_flow": ["compact_hero", "services_grid_3col", "hours_and_location", "testimonials_row", "contact_inline", "footer_minimal"],
        "information_density": "dense",
        "reading_mode": "anchor",
        "use_animated_heading": True,
        "use_liquid_glass_nav": False,
        "use_fade_in_cascade": True,
        "use_grain_overlay": True,
        "industry_affinity": ["local business", "plumb", "hvac", "electrician", "mechanic", "locksmith", "tow", "delivery", "repair"],
        "industry_aversion": ["luxury", "fashion", "hotel", "resort", "architect", "editorial"],
        "keyword_triggers": ["one page", "single page", "everything on one page", "simple", "compact", "quick", "fast"],
        "forbidden": ["separate page routes (app/services/, app/about/ etc.)", "full-viewport hero", "sticky chapter sidebar", "split-screen hero"],
        "signature_moves": [
            "Entire site is app/page.tsx — no sub-routes",
            "Anchor-scroll nav links jump to section IDs on the same page",
            "Services in a tight 3-column grid instead of full-bleed alternating",
        ],
    },

    # ------------------------------------------------------------------ #
    # 5. GALLERY FIRST — image-led, photography or portfolio               #
    # ------------------------------------------------------------------ #
    {
        "id": "gallery_first",
        "label": "Gallery First",
        "feel": "The work speaks. Hero is a tiled photograph grid, not a headline. For businesses whose portfolio IS the proof.",
        "hero_type": "masonry_grid",
        "hero_structure": """Hero is a responsive masonry-style image grid (CSS columns: 2 on mobile, 3 on md, 4 on lg).
Images fill the first viewport (min-height 100dvh). NO headline inside the grid.
The headline floats BELOW the grid:
  'Photography. Flowers. Food. Work.' — wide, Inter 300, tracking-wide
  (one category per line or separated by ·)
This is a GALLERY, not a hero section. Images must not have rounded corners.
Captions appear on hover (opacity 0 → 1, 0.2s ease). No CTA above the fold —
the images ARE the call to action.
Use the Pexels URLs from the brief. Wrap each in next/image. ALL images are
next/image with priority={false} except the first two (priority={true}).""",
        "nav_pattern": "minimal_overlay",
        "nav_structure": "Absolutely positioned nav (z-50) over the image grid. Logo left (white, light font-weight). Three links right (white). No background, no chip, no blur. Very thin: just text over the images. The images' content contrast provides legibility. On mobile: hamburger → fullscreen overlay with white links on dark bg.",
        "section_flow": ["masonry_hero", "tagline_fullwidth", "services_photo_cards", "process_numbered", "testimonials_quote_wall", "cta_minimal", "footer"],
        "information_density": "sparse",
        "reading_mode": "scroll",
        "use_animated_heading": False,
        "use_liquid_glass_nav": False,
        "use_fade_in_cascade": True,
        "use_grain_overlay": True,
        "industry_affinity": ["photo", "florist", "baker", "cafe", "wedding", "studio", "art", "gallery", "ceramic", "jewel", "fashion", "restaurant", "food", "hotel"],
        "industry_aversion": ["mechanic", "plumb", "hvac", "contractor", "software", "saas", "law", "account"],
        "keyword_triggers": ["gallery", "portfolio", "photos", "images", "work speaks", "visual", "photography", "masonry"],
        "forbidden": ["AnimatedHeading in hero", "gradient mesh blobs filling hero background", "text-heavy hero", "card grid services"],
        "signature_moves": [
            "Hero is an image grid — no text overlay, no gradient, just photographs",
            "Tagline appears BELOW the grid fold as a very wide, light-weight statement",
            "Hover on gallery images reveals the caption (opacity transition)",
        ],
    },

    # ------------------------------------------------------------------ #
    # 6. CHAT LOG — conversational, Q&A format                            #
    # ------------------------------------------------------------------ #
    {
        "id": "chat_log",
        "label": "Chat Log",
        "feel": "The site reads as a conversation. Every section is a question from a prospective customer answered by the business owner. Therapy, coaching, care businesses.",
        "hero_type": "conversation_open",
        "hero_structure": """Hero opens with a single customer question in a speech bubble:
  '"I've been struggling with [pain point]. Can you help?"'
Below it, the owner's answer as a second bubble — 3-4 sentences, warm and direct.
Below both bubbles, a name + role attribution: 'Marc Santos — Owner since 1987'.
Then a simple CTA row: 'Yes, let's talk →' (as tel: link).
NO gradient mesh. Background is --color-bg (solid, dark). The bubbles have
rounded-2xl corners, the customer bubble is --color-surface-1, the owner
bubble is --color-surface-2 with a left border in --color-accent.
AnimatedHeading is NOT used — the opening quote IS the h1 (a real <h1>
tag, sr-only fallback for the first visible heading).""",
        "nav_pattern": "minimal_fixed",
        "nav_structure": "Simple fixed top bar: logo left, three text links right, phone number as a pill button far right. No liquid-glass, no blur. Background: --color-bg with a 1px bottom border --color-border.",
        "section_flow": ["conversation_hero", "qa_services_1", "qa_services_2", "qa_process", "qa_about_us", "qa_pricing_faq", "contact_form_warm", "footer"],
        "information_density": "medium",
        "reading_mode": "scroll",
        "use_animated_heading": False,
        "use_liquid_glass_nav": False,
        "use_fade_in_cascade": True,
        "use_grain_overlay": False,
        "industry_affinity": ["therapy", "coach", "wellness", "counseling", "dental", "medical", "vet", "daycare", "family", "baby", "nutrition", "yoga", "spa", "massage"],
        "industry_aversion": ["mechanic", "contractor", "plumb", "software", "saas", "law", "invest", "finance"],
        "keyword_triggers": ["conversation", "chat", "friendly", "Q&A", "question and answer", "approachable", "human", "warm"],
        "forbidden": ["AnimatedHeading in hero", "gradient mesh blobs in hero", "liquid-glass chip nav", "stats trust bar", "card grids"],
        "signature_moves": [
            "Every section is a customer question followed by the business owner's answer — formatted as chat bubbles",
            "Owner attribution (name + role) appears once in the hero and carries through pull quotes",
            "CTA is always a conversational phrase, never a command: 'Let's talk' not 'Get Started'",
        ],
    },

    # ------------------------------------------------------------------ #
    # 7. INDEX CARD — services as a physical card stack                    #
    # ------------------------------------------------------------------ #
    {
        "id": "index_card",
        "label": "Index Card",
        "feel": "Services are physical cards in a drawer. Consultancies, studios, agencies that list their work like a menu board. No cinematic pretense.",
        "hero_type": "text_only_minimal",
        "hero_structure": """Minimal hero — NOT full viewport. Just a typeset section:
  - Business name in Inter 700, 4xl, no animation
  - One-sentence descriptor in Inter 300 light, 2xl
  - Two inline metadata items in mono: 'Est. {YEAR}' · '{CITY}, {STATE}'
  - No gradient, no blobs, no images — solid --color-bg background
  - Compact: padding-top 80px, padding-bottom 48px
The card stack begins immediately below — this is the main event.""",
        "nav_pattern": "top_text_minimal",
        "nav_structure": "Ultra-minimal top nav: logo left in Inter 500, links right as plain text (no hover backgrounds, just color transition). No background behind the nav — it sits directly on --color-bg. A thin 1px bottom border --color-border separates it from the hero text.",
        "section_flow": ["minimal_hero", "card_stack_services", "about_two_col", "testimonial_quotes", "contact_inline", "footer_simple"],
        "information_density": "dense",
        "reading_mode": "scroll",
        "use_animated_heading": False,
        "use_liquid_glass_nav": False,
        "use_fade_in_cascade": False,
        "use_grain_overlay": False,
        "industry_affinity": ["consult", "advisory", "agency", "design", "legal", "law", "attorney", "account", "tax", "financial", "engineer", "surveyor", "architect"],
        "industry_aversion": ["bar", "club", "gym", "bakery", "florist", "wedding", "salon", "spa"],
        "keyword_triggers": ["cards", "index", "menu", "list", "directory", "simple list", "no fuss", "no frills", "catalogue"],
        "forbidden": ["AnimatedHeading", "gradient mesh blobs", "liquid-glass", "full-viewport hero", "masonry grid", "split-screen"],
        "signature_moves": [
            "Services rendered as a column of bordered index cards — each card has a service name, one-line descriptor, and a right-aligned arrow link",
            "No images in the card stack — it is entirely typographic",
            "Hover on each card shifts background to --color-surface-1 (subtle, no shadow)",
        ],
    },

    # ------------------------------------------------------------------ #
    # 8. TERMINAL — monospace, command-line aesthetic                      #
    # ------------------------------------------------------------------ #
    {
        "id": "terminal",
        "label": "Terminal",
        "feel": "The site IS a terminal. Monospace everything. Green or amber on black. For software, security, and dev-tooling businesses that want to signal they are serious.",
        "hero_type": "terminal_prompt",
        "hero_structure": """Hero renders like a terminal session:
  $ whoami
  {business_name} — {tagline}
  $ ls services/
  {service_1}  {service_2}  {service_3}  ...
  $ cat about.txt
  {one-sentence about}
  > █  (blinking cursor via CSS animation)
The 'typing' is pre-rendered static HTML (NO JavaScript typing animations
that delay readability). The cursor blinks via a CSS keyframes animation.
Background is pure --color-bg (near-black). Text color is --color-accent
(use a green #00FF41 or amber #FFB800 as accent — let the style DNA set it).
The h1 is the `$ whoami` line — it IS the semantic heading even though it
looks like a command prompt. No AnimatedHeading. No gradient blobs.""",
        "nav_pattern": "terminal_prompt_nav",
        "nav_structure": "Navigation IS the terminal prompt. At the top: a mock terminal title bar (window chrome dots: red, yellow, green — CSS only). Below it: 'pebble-engine ~ $ ' followed by nav links as path-style commands: './services' · './about' · './contact' · './call'. All in JetBrains Mono 13px. No backgrounds, no chips.",
        "section_flow": ["terminal_hero", "terminal_services", "terminal_process", "terminal_trust", "terminal_contact", "footer_minimal"],
        "information_density": "dense",
        "reading_mode": "scroll",
        "use_animated_heading": False,
        "use_liquid_glass_nav": False,
        "use_fade_in_cascade": False,
        "use_grain_overlay": False,
        "industry_affinity": ["software", "saas", "security", "cyber", "dev", "engineer", "tech", "cloud", "infra", "network", "linux", "open source"],
        "industry_aversion": ["bakery", "florist", "wedding", "salon", "spa", "yoga", "baby", "daycare", "restaurant", "bar", "cafe"],
        "keyword_triggers": ["terminal", "command line", "monospace", "hacker", "cli", "developer", "technical", "green on black", "amber"],
        "forbidden": ["AnimatedHeading", "gradient mesh blobs", "liquid-glass", "any sans-serif font except JetBrains Mono as primary", "card grids with shadows"],
        "signature_moves": [
            "Every section heading is a terminal command: '$ cat services.txt', '$ ls team/', '$ ping contact'",
            "Services listed as directory entries with file-size-style metadata on the right",
            "Footer shows a fake shell uptime: 'pebble-engine uptime: {years} years, {days} days'",
        ],
    },

    # ------------------------------------------------------------------ #
    # 9. MANIFESTO — type-only, words are the hero                        #
    # ------------------------------------------------------------------ #
    {
        "id": "manifesto",
        "label": "Manifesto",
        "feel": "Typography IS the design. One very large statement fills the first viewport. No images above the fold. Copy is the craft.",
        "hero_type": "full_viewport_type",
        "hero_structure": """The entire first viewport is ONE large statement — 7xl to 9xl Inter, font-weight 300 or 700
(pick by style DNA). It wraps naturally across 2-4 lines. No image. No gradient blobs.
Background is --color-bg. The only decoration: a single thin line (1px, --color-accent)
either above or below the statement.
Below the statement (NOT in the first viewport — scroll required):
  - 3-4 sentence paragraph at regular text size
  - Two CTAs: one filled, one ghost
The statement IS the h1. Inter. No AnimatedHeading. Just raw, confident typography.
Examples:
  'We fix what others replace.'
  'Honest work. Honest price. No appointment needed.'
  'Photography that earns its wall space.'""",
        "nav_pattern": "transparent_minimal",
        "nav_structure": "Ultra-minimal transparent nav. Logo only on the left. Three text links on the right with no backgrounds. On mobile: hamburger → fullscreen overlay. The nav is so thin it almost disappears — the type is the design, not the chrome.",
        "section_flow": ["type_hero", "paragraph_and_cta", "services_simple_list", "one_big_quote", "about_two_sentences", "contact_minimal", "footer"],
        "information_density": "sparse",
        "reading_mode": "scroll",
        "use_animated_heading": False,
        "use_liquid_glass_nav": False,
        "use_fade_in_cascade": True,
        "use_grain_overlay": False,
        "industry_affinity": ["agency", "art", "studio", "design", "brand", "photography", "consultant", "advisor", "creative", "filmmaker", "writer", "independent"],
        "industry_aversion": ["fast food", "contractor", "hvac", "plumb", "tow", "mechanic", "daycare", "bakery"],
        "keyword_triggers": ["minimal", "type only", "words", "manifesto", "statement", "typography", "bold text", "clean", "no images"],
        "forbidden": ["AnimatedHeading", "gradient mesh blobs", "liquid-glass chip", "images above the fold", "card grids", "trust badge bars"],
        "signature_moves": [
            "First viewport is entirely typographic — no image, no gradient, just the statement",
            "Single 1px accent line is the only graphic element in the hero",
            "Services listed as a simple ordered list, not cards",
        ],
    },

    # ------------------------------------------------------------------ #
    # 10. WEATHER REPORT — dense service dashboard                         #
    # ------------------------------------------------------------------ #
    {
        "id": "weather_report",
        "label": "Weather Report",
        "feel": "Dense, honest, data-forward. A dashboard for businesses that run on real-time information: hours, availability, pricing, service status. Mechanics, plumbers, contractors — businesses that show up and do the work.",
        "hero_type": "dashboard_hero",
        "hero_structure": """Hero is a compact dashboard panel — NOT full viewport (max-height 55vh).
Layout: a two-column grid.
LEFT column (60% width):
  - Business name as a stencil-like header (Inter 700 uppercase, tracking-wide, 3xl)
  - One-line descriptor
  - CURRENT STATUS indicator: a colored dot + text. Green dot = 'OPEN · Closes at 6PM'.
    Red dot = 'CLOSED · Opens at 7:30AM'. (Static — set from the brief's hours.)
  - Phone number displayed large (2xl, Inter 700) as a tel: link — this is the #1 CTA
  - Address as a small mono line below the phone
RIGHT column (40% width, mono font throughout):
  - 'TODAY'S AVAILABILITY' header
  - Horizontal rule
  - List of services with a ✓ or — indicator:
    ✓ Brake jobs  ·  Same-day
    ✓ Oil change  ·  30 min
    — Transmission  ·  Call ahead
  - 'WAIT TIME: approx 45 min' at the bottom
No gradient blobs. No AnimatedHeading. Background is --color-bg. Accent used for
the status dot and section headers only.""",
        "nav_pattern": "utility_bar",
        "nav_structure": "A thin utility bar at the very top — even thinner than a normal nav. Two rows: top row is a mini-announcement bar ('Mon–Fri 7:30–6PM  ·  Sat 8–2PM  ·  (216) 555-0142') in mono 11px. Bottom row is the actual nav: logo left, links center, 'CALL NOW' button right (filled, --color-accent background). No liquid-glass. No blur.",
        "section_flow": ["dashboard_hero", "services_grid_with_prices", "trust_bar_simple", "process_numbered_compact", "testimonials_row_3col", "service_area_text", "contact_form", "footer_utility"],
        "information_density": "dense",
        "reading_mode": "scroll",
        "use_animated_heading": False,
        "use_liquid_glass_nav": False,
        "use_fade_in_cascade": False,
        "use_grain_overlay": False,
        "industry_affinity": ["mechanic", "automotive", "auto repair", "tow", "plumb", "hvac", "electrician", "contractor", "roof", "landscap", "locksmith", "emergency", "repair", "service"],
        "industry_aversion": ["luxury", "hotel", "resort", "fashion", "wedding", "editorial", "gallery", "museum", "art"],
        "keyword_triggers": ["dashboard", "status", "availability", "hours", "open now", "utility", "service menu", "price list", "no nonsense"],
        "forbidden": ["AnimatedHeading", "gradient mesh blobs", "liquid-glass chip", "full-viewport hero", "masonry gallery", "split-screen hero"],
        "signature_moves": [
            "Status indicator (colored dot + OPEN/CLOSED) is the first thing visible in the hero",
            "Phone number rendered large and prominent — it IS a primary design element",
            "Services listed with availability indicators (same-day, call ahead, wait time)",
        ],
    },
]


# ------------------------------------------------------------------ #
# CREATIVE DIRECTION KEYWORD CLASSIFIER                                #
# Maps user free-text hints to preferred layout IDs.                  #
# ------------------------------------------------------------------ #

_KEYWORD_TO_LAYOUT: list[tuple[list[str], str, int]] = [
    # (keywords, layout_id, weight)
    (["terminal", "command line", "monospace", "hacker", "cli", "developer", "tech aesthetic"], "terminal", 10),
    (["manifesto", "type only", "typography", "minimal", "words", "bold text", "clean", "no images", "just text"], "manifesto", 10),
    (["gallery", "portfolio", "photos", "images", "photography", "masonry", "work speaks"], "gallery_first", 10),
    (["split", "editorial", "half photo", "magazine layout", "two column"], "split_screen", 10),
    (["dashboard", "status", "open now", "availability", "utility", "service menu", "dense info"], "weather_report", 10),
    (["one page", "single page", "everything on one page", "simple", "compact", "quick"], "single_screen", 8),
    (["conversation", "chat", "friendly", "warm", "approachable", "Q&A", "human"], "chat_log", 8),
    (["cards", "index", "menu", "list", "catalogue", "no fuss", "no frills"], "index_card", 8),
    (["long form", "editorial", "essay", "magazine", "chapter", "reading", "journal"], "magazine_scroll", 8),
    (["gradient", "glow", "modern", "tech", "sleek", "product", "startup", "ambient"], "gradient_mesh", 6),
]


def _classify_creative_direction(text: str) -> Optional[str]:
    """Return the layout id most strongly implied by the user's free text.

    Simple keyword matching — no LLM call. Returns None if nothing matches.
    """
    if not text:
        return None
    lower = text.lower()
    best_id: Optional[str] = None
    best_weight = 0
    for keywords, layout_id, weight in _KEYWORD_TO_LAYOUT:
        for kw in keywords:
            if kw in lower:
                if weight > best_weight:
                    best_weight = weight
                    best_id = layout_id
                break
    return best_id


def pick_layout_for_brief(
    brief: dict,
    creative_direction: str = "",
    seed: Optional[int] = None,
) -> dict:
    """Return the best-fit layout DNA card for a brief.

    Priority order:
    1. Pinned ``_layout_dna_id`` in the brief — explicit override.
    2. creative_direction text → keyword classifier → hard-lock if confident match.
    3. Industry affinity strict mode (same algorithm as style_dna.pick_dna_for_brief).
    4. Safe-random fallback (aversion-free cards only).
    5. Pure random last resort.
    """
    # 1 — pinned
    pinned = (brief.get("_layout_dna_id") or "").strip()
    if pinned:
        card = pick_layout_by_id(pinned)
        if card:
            return card

    # 2 — creative direction keyword classifier
    cd_match = _classify_creative_direction(creative_direction or brief.get("creative_direction", ""))
    if cd_match:
        card = pick_layout_by_id(cd_match)
        if card:
            return card

    haystack = (brief.get("business_type") or brief.get("industry", "")).lower()

    # 3 — affinity strict mode
    affinity_matched = [
        c for c in LAYOUT_CARDS
        if any(kw in haystack for kw in c.get("industry_affinity", []))
    ]
    if affinity_matched:
        candidates = [
            c for c in affinity_matched
            if not any(kw in haystack for kw in c.get("industry_aversion", []))
        ]
        if candidates:
            rng = random.Random(seed) if seed is not None else random
            return rng.choice(candidates)

    # 4 — safe-random (no aversion)
    safe = [
        c for c in LAYOUT_CARDS
        if not any(kw in haystack for kw in c.get("industry_aversion", []))
    ]
    if safe:
        rng = random.Random(seed) if seed is not None else random
        return rng.choice(safe)

    # 5 — last resort
    rng = random.Random(seed) if seed is not None else random
    return rng.choice(LAYOUT_CARDS)


def pick_layout_by_id(layout_id: str) -> Optional[dict]:
    """Look up a layout card by id."""
    for card in LAYOUT_CARDS:
        if card["id"] == layout_id:
            return card
    return None


def build_layout_block(layout: dict) -> str:
    """Return the markdown block to inject at the TOP of the prompt.

    This block describes the site's structural architecture. It is injected
    BEFORE the style DNA block so the LLM knows the structural frame first,
    then applies the visual surface on top.
    """
    forbidden = ", ".join(layout.get("forbidden", []))
    signatures = "\n".join(f"- {m}" for m in layout.get("signature_moves", []))
    use_animated = layout.get("use_animated_heading", True)
    use_lg_nav = layout.get("use_liquid_glass_nav", True)
    use_fadein = layout.get("use_fade_in_cascade", True)
    use_grain = layout.get("use_grain_overlay", True)

    component_table = f"""| Component | Use in this layout |
|---|---|
| AnimatedHeading | {'✅ YES — use for hero h1' if use_animated else '❌ NO — use a plain <h1> tag'} |
| FadeIn cascade | {'✅ YES — 800ms / 1200ms / 1400ms delays' if use_fadein else '❌ NO — sections reveal via scroll or static'} |
| Liquid-glass chip nav | {'✅ YES' if use_lg_nav else '❌ NO — see nav_structure below'} |
| GrainOverlay | {'✅ YES — singleton in app/layout.tsx' if use_grain else '❌ NO — omit GrainOverlay'} |"""

    return f"""# ============================================================
# LAYOUT DNA — STRUCTURAL ARCHITECTURE (read before Style DNA)
# ============================================================

**This build's layout architecture is `{layout['label'].upper()}` ({layout['id']}).**

> **{layout['feel']}**

## What this means structurally

The layout DNA defines the skeleton — hero type, nav pattern, section flow,
and which foundation components apply. The Style DNA (below) paints the
surface. BOTH must be honored. If they conflict, the Layout DNA wins for
structure, Style DNA wins for color/font choices.

## Hero architecture — build THIS, not the default gradient mesh

{layout['hero_structure']}

## Navigation pattern: {layout['nav_pattern'].replace('_', ' ').upper()}

{layout['nav_structure']}

## Foundation components — this layout's usage

{component_table}

## Section flow

Build the homepage sections in this sequence:
{chr(10).join(f'{i+1}. {s.replace("_", " ").title()}' for i, s in enumerate(layout.get('section_flow', [])))}

## Signature moves — implement ALL of these

{signatures}

## Forbidden in this layout

{forbidden}

These forbidden items override any conflicting guidance elsewhere in this prompt.
The Style DNA block below may suggest components from this forbidden list (e.g. it
might assume AnimatedHeading exists). When it does, honor the Style DNA's
color/font/motion guidance but substitute the layout-appropriate structure here.

# ============================================================
# (end Layout DNA block — Style DNA follows)
# ============================================================

"""


__all__ = [
    "LAYOUT_CARDS",
    "pick_layout_for_brief",
    "pick_layout_by_id",
    "build_layout_block",
]
