#!/usr/bin/env python3
"""
Pebble Engine -- local briefing engine for websites that don't look generated.

USAGE
    python3 pebble_engine.py                # default port 8000
    python3 pebble_engine.py --port 8765    # custom port

OPTIONAL DEPS (for auto-build mode only)
    pip install -r requirements.txt

CONFIG (for auto-build mode only)
    Copy .env.example to .env and fill in your provider + API key.
    Default provider is Gemini (use your Google AI Ultra key).
    Switch to Claude Opus for premium runs: PEBBLE_PROVIDER=anthropic

The quiz, brief generator, anti-slop audit, and prompt download all work
without any of these. The auto-build feature is the only thing that
requires the provider packages and API keys.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional

# --------------------------------------------------------------------------
# PATHS
# --------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.resolve()
UIUX_SCRIPTS = PROJECT_ROOT / "skills" / "ui-ux-pro-max" / "scripts"
INDEX_HTML = PROJECT_ROOT / "ui" / "index.html"
OUTPUT_DIR = PROJECT_ROOT / "output"
RESEARCH_CACHE_DIR = OUTPUT_DIR / "research_cache"
sys.path.insert(0, str(UIUX_SCRIPTS))


# --------------------------------------------------------------------------
# .env LOADER (stdlib-only, no python-dotenv dep)
# --------------------------------------------------------------------------

def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val

load_env_file(PROJECT_ROOT / ".env")


# --------------------------------------------------------------------------
# OPTIONAL IMPORTS
# --------------------------------------------------------------------------

try:
    from design_system import generate_design_system  # type: ignore
    _ENGINE_OK = True
except Exception:
    generate_design_system = None
    _ENGINE_OK = False

try:
    from anthropic import Anthropic  # type: ignore
    _ANTHROPIC_OK = True
except Exception:
    Anthropic = None  # type: ignore
    _ANTHROPIC_OK = False

try:
    from google import genai as _genai                     # type: ignore
    from google.genai import types as _genai_types         # type: ignore
    _GOOGLE_OK = True
except Exception:
    _genai = None                                          # type: ignore
    _genai_types = None                                    # type: ignore
    _GOOGLE_OK = False


# --------------------------------------------------------------------------
# ANTI-SLOP AUDIT
# --------------------------------------------------------------------------

CONVERGENCE_FONTS = {
    "inter", "roboto", "poppins", "geist", "plus jakarta sans",
    "space grotesk", "dm sans",
}
ACCEPTABLE_DISPLAY_PAIRS = {
    "fraunces", "playfair", "instrument serif", "tobias", "migra",
    "pp editorial", "söhne", "sohne", "national 2", "tiempos",
    "gt alpina", "boogy brut", "dm serif", "serif",
}
WATCH_STYLES = {"neumorphism", "claymorphism", "default cyberpunk"}


def audit_design_system(ds_text: str) -> list[tuple[str, str]]:
    notes: list[tuple[str, str]] = []
    text = ds_text.lower()
    heading = _extract_field(ds_text, r"heading[^:\n]*?:\s*([^\n]+)")
    body = _extract_field(ds_text, r"body[^:\n]*?:\s*([^\n]+)")
    has_distinctive = any(d in heading.lower() for d in ACCEPTABLE_DISPLAY_PAIRS)

    for font in CONVERGENCE_FONTS:
        if font in heading.lower():
            notes.append(("TYPOGRAPHY",
                f"Heading uses '{heading.strip()}' (contains '{font}'). "
                f"Swap heading face for Fraunces, Instrument Serif, "
                f"PP Editorial, Migra, or Tobias."))
        if font in body.lower() and not has_distinctive:
            notes.append(("TYPOGRAPHY",
                f"Body is '{body.strip()}' and heading lacks a distinctive "
                f"display face. Pair with serif or swap body to Söhne/Mona Sans."))

    if "purple" in text and ("gradient" in text or "to-blue" in text):
        notes.append(("COLOR",
            "Purple-to-blue gradient detected -- the most recognizable AI tell. "
            "Replace with a flat dominant color + sharp accent."))

    for style in WATCH_STYLES:
        if style in text:
            notes.append(("STYLE",
                f"'{style.title()}' in recommendation -- trends slop-adjacent. "
                "Override unless the direction explicitly calls for it."))

    if "hero + 3 features + cta" in text.replace("-", " "):
        notes.append(("LAYOUT",
            "Default 'Hero -> 3 cards -> CTA' pattern. Break it with asymmetric "
            "grids, full-bleed sections, or numbered lists."))

    return notes


def _extract_field(text: str, pattern: str) -> str:
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else ""


# --------------------------------------------------------------------------
# QUERY SYNTHESIS
# --------------------------------------------------------------------------

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "of", "in", "on", "at",
    "to", "for", "with", "by", "from", "as", "is", "it", "this",
    "that", "be", "are", "was", "were", "feel", "feels", "should",
    "like", "look", "looks", "if", "than", "more", "less",
}


def build_ui_query(answers: dict) -> str:
    parts = [
        answers.get("business_type", "") or answers.get("industry", ""),
        _distill(answers.get("visitor_action", "")),
        _distill(answers.get("extra_context", "")),
    ]
    return " ".join(p for p in parts if p)[:200]


def _distill(sentence: str) -> str:
    words = re.findall(r"[A-Za-z]+", sentence.lower())
    return " ".join(w for w in words if w not in STOP_WORDS and len(w) > 2)


def _slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-") or "untitled"


# --------------------------------------------------------------------------
# IMAGE SOURCING SYSTEM (Unsplash)
# --------------------------------------------------------------------------

# Unsplash image search queries by industry and section type
IMAGE_QUERIES = {
    "hero": {
        "plumbing": ["professional plumber working", "plumbing repair service", "plumber tools professional"],
        "hvac": ["hvac technician professional", "air conditioning repair", "heating system service"],
        "electrical": ["electrician working professional", "electrical repair service", "electrician tools"],
        "restaurant": ["restaurant interior modern", "restaurant dining elegant", "chef cooking kitchen"],
        "cafe": ["coffee shop interior modern", "cafe atmosphere cozy", "barista coffee"],
        "yoga": ["yoga studio peaceful", "yoga class group", "wellness space modern"],
        "lawyer": ["law office professional", "lawyer meeting client", "legal office modern"],
        "real estate": ["modern home exterior", "real estate professional", "luxury home interior"],
        "dentist": ["dental office modern", "dentist professional smiling", "dental clinic clean"],
        "default": ["professional business office", "modern workspace", "professional service"],
    },
    "service": {
        "plumbing": ["plumbing tools close-up", "pipe repair work", "water fixture installation"],
        "hvac": ["hvac equipment modern", "air conditioning unit", "heating system"],
        "electrical": ["electrical panel professional", "wiring work closeup", "electrical tools"],
        "restaurant": ["food plating elegant", "restaurant dish gourmet", "culinary presentation"],
        "cafe": ["coffee latte art", "pastry display bakery", "espresso machine"],
        "default": ["professional tools workspace", "service quality detail", "professional equipment"],
    },
    "team": {
        "default": ["professional portrait business", "business professional smiling", "team member professional"],
    },
    "about": {
        "default": ["business team meeting", "professionals collaborating", "office team working"],
    },
}


def get_unsplash_images(industry: str, image_count: int = 8) -> dict[str, str]:
    """
    Fetch relevant images from Unsplash for a given industry.
    Returns a dict of {label: url} for different image types.

    Uses Unsplash Source API (no API key needed) for simplicity.
    Format: https://source.unsplash.com/{WIDTH}x{HEIGHT}/?{KEYWORDS}

    Args:
        industry: Business industry (plumbing, restaurant, etc.)
        image_count: Number of images to fetch (default 8)

    Returns:
        Dictionary with image labels and Unsplash URLs
    """
    industry_slug = _slugify(industry)
    images = {}

    # Map industry to query categories
    hero_queries = IMAGE_QUERIES["hero"].get(industry_slug, IMAGE_QUERIES["hero"]["default"])
    service_queries = IMAGE_QUERIES["service"].get(industry_slug, IMAGE_QUERIES["service"]["default"])
    team_queries = IMAGE_QUERIES["team"]["default"]

    # Generate Unsplash URLs (using source.unsplash.com for simplicity)
    # Note: These are random but themed. For production, could use official API for specific images.

    # Hero image (large, 1600x900)
    hero_keywords = hero_queries[0].replace(" ", ",")
    images["hero"] = f"https://source.unsplash.com/1600x900/?{hero_keywords}"

    # Service images (medium, 800x600)
    for i, query in enumerate(service_queries[:3], 1):
        keywords = query.replace(" ", ",")
        images[f"service_{i}"] = f"https://source.unsplash.com/800x600/?{keywords}"

    # Team/About images (square, 600x600)
    team_keywords = team_queries[0].replace(" ", ",")
    images["team_1"] = f"https://source.unsplash.com/600x600/?{team_keywords}"
    images["team_2"] = f"https://source.unsplash.com/600x600/?{team_keywords},portrait"

    # Gallery images (if needed, 800x600)
    if industry_slug in ["restaurant", "cafe", "yoga", "dentist", "real-estate"]:
        images["gallery_1"] = f"https://source.unsplash.com/800x600/?{hero_keywords},interior"
        images["gallery_2"] = f"https://source.unsplash.com/800x600/?{hero_keywords},detail"

    return images


# --------------------------------------------------------------------------
# INDUSTRY RESEARCH SYSTEM
# --------------------------------------------------------------------------

RESEARCH_PROMPT_TEMPLATE = """You are a web design researcher conducting industry analysis.

**Your task:** Research the {industry} industry to provide data-driven design recommendations.

**What to research:**
1. Analyze 3-5 top-performing websites in the {industry} industry
2. Identify visual patterns:
   - Light vs dark backgrounds (which converts better for this industry?)
   - Common color palettes and accent colors
   - Typography choices (serif vs sans, formal vs friendly)
   - Motion/animation intensity (minimal, smooth, cinematic?)
3. Customer psychology:
   - What drives purchasing decisions in this industry?
   - What builds trust? (Reviews, credentials, photos, certifications?)
   - What are the typical pain points or anxieties?
4. Conversion elements:
   - Primary CTA patterns (call, book, buy, browse?)
   - Trust signals that work (licenses, awards, testimonials?)
   - Page structure patterns
5. Industry-specific warnings:
   - What looks cheap or unprofessional in this industry?
   - Common mistakes to avoid

**Output format (markdown):**
## Industry Research: {industry}

### Visual Aesthetic Patterns
[What you observed about colors, backgrounds, typography from top sites]

### Motion & Interaction
[Animation intensity, scroll effects, interactivity patterns]

### Customer Psychology
[What drives decisions, what builds trust, what creates anxiety]

### Trust Signals
[Specific elements that build credibility in this industry]

### Industry-Specific Warnings
[What NOT to do - mistakes that hurt conversion in this industry]

### Recommended Approach
[Your data-driven recommendation for: aesthetic, motion, tone, structure]

**Rules:**
- Be specific. Cite patterns from actual top sites.
- Focus on CONVERSION, not just aesthetics.
- If dark backgrounds work for this industry, say so. If they hurt conversion, say so.
- Call out industry-specific quirks (e.g., "luxury real estate can use dark mode; residential real estate cannot")
- Keep it under 800 words. Concise and actionable.

Begin your research now for: {industry}"""


def research_industry(business_type: str, industry_category: str = "") -> str:
    """
    Research an industry using Gemini to provide data-driven design recommendations.
    Results are cached per industry to avoid redundant research.

    Args:
        business_type: The specific business type (e.g., "plumbing", "boat sales")
        industry_category: Optional broader category (e.g., "home services", "luxury")

    Returns:
        Research markdown text or empty string if research fails
    """
    # Normalize industry slug for caching
    industry_slug = _slugify(business_type)
    cache_file = RESEARCH_CACHE_DIR / f"{industry_slug}.md"

    # Check cache first
    if cache_file.exists():
        try:
            cached = cache_file.read_text(encoding="utf-8")
            if cached and len(cached) > 100:  # Basic validation
                return cached
        except Exception:
            pass  # Cache read failed, proceed to research

    # Get LLM client for research
    client, reason = get_llm_client()
    if not client or reason != "ok":
        return ""  # No LLM available, skip research

    # Build research prompt
    research_prompt = RESEARCH_PROMPT_TEMPLATE.format(
        industry=business_type,
    )

    # Call Gemini to research
    try:
        system_instruction = (
            "You are an expert web design researcher. You analyze successful websites "
            "and extract data-driven design patterns. You provide specific, actionable "
            "recommendations based on what actually converts in each industry."
        )

        research_result = client.generate(
            system=system_instruction,
            user=research_prompt,
            max_tokens=2000  # Research should be concise
        )

        # Validate result
        if not research_result or len(research_result) < 100:
            return ""

        # Cache the result
        RESEARCH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(research_result, encoding="utf-8")

        return research_result

    except Exception as e:
        # Research failed, return empty (prompt will work without it)
        print(f"Industry research failed: {e}")
        return ""


# --------------------------------------------------------------------------
# BUSINESS INTELLIGENCE SKILL LOADER
# --------------------------------------------------------------------------

BI_SKILL_PATH    = PROJECT_ROOT / "skills" / "business-intelligence" / "SKILL.md"
STACK_SKILL_PATH = PROJECT_ROOT / "skills" / "stack" / "SKILL.md"
IOS_SKILL_PATH   = PROJECT_ROOT / "skills" / "ios" / "SKILL.md"
VX_SKILL_PATH    = PROJECT_ROOT / "skills" / "visitor-experience" / "SKILL.md"
NS_SKILL_PATH    = PROJECT_ROOT / "skills" / "no-slop-web" / "SKILL.md"

def load_business_intelligence() -> str:
    if BI_SKILL_PATH.exists(): return BI_SKILL_PATH.read_text(encoding="utf-8")
    return ""

def load_stack_skill() -> str:
    if STACK_SKILL_PATH.exists(): return STACK_SKILL_PATH.read_text(encoding="utf-8")
    return ""

def load_ios_skill() -> str:
    if IOS_SKILL_PATH.exists(): return IOS_SKILL_PATH.read_text(encoding="utf-8")
    return ""

def load_visitor_experience_skill() -> str:
    if VX_SKILL_PATH.exists(): return VX_SKILL_PATH.read_text(encoding="utf-8")
    return ""

def load_no_slop_skill() -> str:
    if NS_SKILL_PATH.exists(): return NS_SKILL_PATH.read_text(encoding="utf-8")
    return ""

_BI_SKILL    = load_business_intelligence()
_STACK_SKILL = load_stack_skill()
_IOS_SKILL   = load_ios_skill()
_VX_SKILL    = load_visitor_experience_skill()
_NS_SKILL    = load_no_slop_skill()


# --------------------------------------------------------------------------
# PROMPT TEMPLATE  -- 11-section structure
# --------------------------------------------------------------------------

PROMPT_TEMPLATE = """\
# Website Build Brief -- {business_name}

You are building a complete, production-quality website. Read every section of this brief before writing a single line of code. The skills embedded in this brief contain thousands of words of specific, researched direction. Apply all of it.

---

## 1. Project Overview

- **Business name:** {business_name}
- **Type of business:** {business_type}
- **Location / service area:** {location}
- **Primary visitor action:** {visitor_action}
- **Booking or payment system:** {booking_system}

---

## 2. Visual Reference & Inspiration

{reference_block}

---

## 3. Visitor Experience Direction

**How visitors should feel:** {emotional_direction}
**Visual experience level:** {visual_experience}

{visitor_experience_block}

Apply the matching interpretations from the Visitor Experience Skill above to EVERY decision:
- Typography weight, rhythm, and size
- Motion speed, easing, and intensity
- Copy tone and vocabulary
- Color saturation and warmth -- light vs dark background
- Layout density and whitespace
- Which animation libraries are appropriate
- Whether Three.js is warranted

These two settings override all generic defaults.

---

## 4. Additional Context

{extra_context}

---

## 5. No-Slop Rules
{no_slop_block}

---

## 6. Business Intelligence
{business_intelligence_block}

---

## 6b. Industry Research — Data-Driven Insights

{industry_research_block}

---

## 7. iOS / iPhone Compatibility
{ios_skill_block}

---

## 8. Recommended Design System
{design_system_block}

---

## 8b. Placeholder Images (Unsplash)

{images_block}

---

## 9. Stack, Motion System, and Build Instructions
{stack_block}

### Self-audit before delivering

| Check | Required |
|---|---|
| Phone number | `[BUSINESS PHONE]` placeholder -- NEVER a 555 number or invented number |
| Primary heading font | NOT Inter/Geist/Poppins/Space Grotesk/DM Sans -- named distinct face |
| Subtext | No "Where X meets Y" -- contains specific claim, number, or place name |
| Headline | No "Unrivaled/World-class/Unleash your inner" -- specific and arguable |
| Hero visual | Has photo, video, 3D, or animated CSS element -- NOT flat background behind text |
| Background | Dark for premium/tech -- Light for local service/wellness/food |
| Booking tool | Matches business category -- Booksy is ONLY for beauty/wellness |
| Page structure | NOT Hero + 3 cards + testimonials + pricing + footer |
| Testimonials | Real only, or omitted -- never fabricated |
| SplitText headings | `word-break: keep-all` on heading wrapper |
| Hero height | `min-h-[100dvh]` not `min-h-screen` |
| Scroll animations | Match visual experience level |
| Navbar | Scroll-aware hide/show + mobile hamburger |
| Input font size | Minimum `font-size: 16px` |
| Safe area | `env(safe-area-inset-*)` in globals.css |
| Video | `autoPlay muted loop playsInline` |

---

## 10. Anti-Slop Audit
{anti_slop_block}

---

## 11. Output -- NO QUESTIONS, BUILD IMMEDIATELY

**Do not write a plan. Do not ask questions. Build now.**

Output every file the project needs. Follow the Stack Skill project structure.

Required files:
- `README.md`, `HANDOFF.md`, `TODO_ASSETS.md`, `STYLE_GUIDE.md`, `CLIENT_ANSWERS.md`
- `src/content/site.ts`, `src/content/sections.ts`, `src/content/services.ts`, `src/content/faqs.ts`, `src/content/testimonials.ts`
- `src/lib/motion.ts`, `src/components/motion/Reveal.tsx`, `src/components/motion/Parallax.tsx`, `src/components/motion/SplitText.tsx`, `src/components/motion/SmoothScroll.tsx`
- `src/config/brand.config.ts`, `src/config/motion.config.ts`

Where contact info is missing: use `[BUSINESS PHONE]`, `[EMAIL]`, `[ADDRESS]`. Never invent.
"""




def build_prompt(answers: dict, ds_text: str, notes: list[tuple[str, str]], research_text: str = "", images: dict[str, str] = None) -> str:
    # Map quiz fields -> template variables
    industry = answers.get("industry", answers.get("business_type", ""))
    fns = answers.get("site_functions") or []
    fn_labels = {
        "booking":   "online booking / appointments",
        "payment":   "online payment collection",
        "portfolio": "portfolio / gallery of past work",
        "leads":     "lead capture / contact form",
        "ecommerce": "e-commerce / online store",
        "presence":  "business presence (hours, location, contact)",
    }
    visitor_action = "; ".join(fn_labels.get(f, f) for f in fns) if fns else "general presence"

    booking = answers.get("booking_system", "").strip()
    payment = answers.get("payment_system", "").strip()
    systems_parts = []
    if booking and booking.lower() not in {"", "none", "n/a", "none specified"}:
        systems_parts.append(f"Booking: {booking}")
    if payment and payment.lower() not in {"", "none", "n/a", "none specified"}:
        systems_parts.append(f"Payment: {payment}")
    booking_str = " . ".join(systems_parts) if systems_parts else "None yet -- recommend the best option for this business type."

    extra = answers.get("extra_context", "").strip()
    extra_block = extra if extra else "*(No extra context -- use the business intelligence skill to fill in industry best practices.)*"

    # Emotional direction and visual experience
    emotional = answers.get("emotional_direction", "").strip()
    visual = answers.get("visual_experience", "").strip()
    emotional_direction = emotional if emotional else "Trusting and confident (default -- apply calm, credibility-focused direction)"
    visual_experience = visual if visual else "Smooth and professional -- subtle animations (default)"

    # Reference URL / inspiration site
    ref_url = answers.get("reference_url", "").strip()
    if ref_url and ref_url.lower() not in {"", "none", "n/a", "no", "skip"}:
        reference_block = f"""A reference site has been provided: **{ref_url}**

Browse this URL before writing any code. Extract and apply:
- Dominant colors and color temperature (warm vs cool, light vs dark)
- Typography weight, rhythm, and personality
- Spacing philosophy -- how tight or generous the layout feels
- Animation style and intensity
- Layout approach -- grid, asymmetric, editorial, etc.
- Overall brand feeling

**Important:** Abstract the FEELING, not the layout. Do not copy structure or content from this site. Use it to calibrate the aesthetic direction only. If this is a Dribbble link, extract the visual composition and color mood."""
    else:
        reference_block = "*(No reference site provided. Infer aesthetic direction from the emotional direction and visual experience settings above, and from the business category in the Business Intelligence skill.)*"

    # No-slop skill
    if _NS_SKILL:
        no_slop_block = f"\n\n{_NS_SKILL.strip()}\n"
    else:
        no_slop_block = "\n*(No-slop skill not loaded -- apply general quality rules: no 555 phone numbers, no 'Where X meets Y' subtext, no vague superlatives, hero must have visual element.)*\n"

    # Visitor experience skill
    if _VX_SKILL:
        vx_block = f"\n\n{_VX_SKILL.strip()}\n"
    else:
        vx_block = "\n*(Visitor experience skill not loaded -- infer motion and tone from the emotional direction and visual experience answers above.)*\n"

    # iOS skill
    if _IOS_SKILL:
        ios_skill_block = f"\n\n{_IOS_SKILL.strip()}\n"
    else:
        ios_skill_block = "\n*(iOS skill not loaded -- apply standard iOS Safari fixes: 100dvh, normalizeScroll, muted playsInline video, 16px inputs, safe-area-inset.)*\n"

    # Stack skill
    if _STACK_SKILL:
        stack_block = f"\n\nRead and follow the Stack Skill below for project structure, dependencies, motion components, and handoff files.\n\n{_STACK_SKILL.strip()}\n"
    else:
        stack_block = "\nNext.js 14 + React 18 + TypeScript + Tailwind CSS v3 + GSAP + Lenis. Follow the project structure in the Stack Skill.\n"

    # Business intelligence skill
    if _BI_SKILL:
        bi_block = f"\n\n{_BI_SKILL.strip()}\n"
    else:
        bi_block = "\n*(Business intelligence skill not loaded -- apply general conversion best practices.)*\n"

    if ds_text:
        ds_block = (
            "\nThe ui-ux-pro-max engine generated this recommendation. "
            "Use it as a starting point; override anything that conflicts with the emotional direction or business type.\n\n"
            f"```\n{ds_text.strip()}\n```\n"
        )
    else:
        ds_block = "\n*(ui-ux-pro-max engine unavailable -- derive design system from the visitor experience direction and business category.)*\n"

    if notes:
        lines = ["\nAnti-slop warnings fired. Resolve in favor of the audit:\n"]
        for severity, note in notes:
            lines.append(f"- **[{severity}]** {note}")
        anti_slop_block = "\n".join(lines)
    else:
        anti_slop_block = "\n*(No conflicts detected. Design rules below still apply.)*"

    # Industry research block
    if research_text:
        research_block = (
            f"\n**Gemini researched the {industry} industry and found:**\n\n"
            f"{research_text.strip()}\n\n"
            "Apply these data-driven insights to every design decision. "
            "This research is based on analysis of top-performing websites in this industry. "
            "When research conflicts with user choices, explain the conflict and recommend the research-backed approach."
        )
    else:
        research_block = "\n*(Industry research unavailable -- rely on Business Intelligence skill defaults above.)*\n"

    # Images block
    if images:
        image_lines = ["**Use these Unsplash placeholder images in your build:**\n"]
        for label, url in images.items():
            clean_label = label.replace("_", " ").title()
            image_lines.append(f"- **{clean_label}:** `{url}`")
        image_lines.append("\n**Important:**")
        image_lines.append("- Use these exact URLs in your `<img src=\"...\">` tags")
        image_lines.append("- Do NOT use local paths like `/images/hero.jpg`")
        image_lines.append("- These are high-quality placeholders that make the site look real")
        image_lines.append("- Document all images in TODO_ASSETS.md so client knows to replace with real photos")
        image_lines.append("- Add descriptive alt text for each image")
        images_block = "\n".join(image_lines)
    else:
        images_block = "\n*(No placeholder images available -- use descriptive alt text with empty src, or use Unsplash source URLs.)*\n"

    return PROMPT_TEMPLATE.format(
        business_name=answers.get("business_name", ""),
        business_type=industry,
        location=answers.get("location", ""),
        visitor_action=visitor_action,
        booking_system=booking_str,
        reference_block=reference_block,
        emotional_direction=emotional_direction,
        visual_experience=visual_experience,
        visitor_experience_block=vx_block,
        extra_context=extra_block,
        no_slop_block=no_slop_block,
        ios_skill_block=ios_skill_block,
        stack_block=stack_block,
        business_intelligence_block=bi_block,
        industry_research_block=research_block,
        design_system_block=ds_block,
        images_block=images_block,
        anti_slop_block=anti_slop_block,
    )


# --------------------------------------------------------------------------
# LLM CLIENT (Anthropic; abstracted so Gemini drops in later)
# --------------------------------------------------------------------------

class LLMError(Exception):
    pass


# ---------- Gemini 3.1 Pro client (default) --------------------------------

class GeminiClient:
    """Wraps google-genai for Gemini 3.1 Pro (and any future Gemini model).
    Interface: generate(system, user, max_tokens) -> str -- same as AnthropicClient."""

    def __init__(self, api_key: str, model: str):
        if not _GOOGLE_OK:
            raise LLMError("google-genai package not installed. Run: pip install google-genai")
        self.client = _genai.Client(api_key=api_key)
        self.model = model
        self.provider = "gemini"

    def generate(self, system: str, user: str, max_tokens: int = 16000) -> str:
        try:
            config = _genai_types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=max_tokens,
                temperature=0.7,
            )
            response = self.client.models.generate_content(
                model=self.model,
                contents=user,
                config=config,
            )
            return response.text
        except Exception as e:
            raise LLMError(f"Gemini API call failed: {e}")


# ---------- Anthropic Claude client (premium / second-opinion option) -------

class AnthropicClient:
    """Wraps anthropic for Claude Sonnet/Opus.
    Interface: generate(system, user, max_tokens) -> str -- same as GeminiClient."""

    def __init__(self, api_key: str, model: str):
        if not _ANTHROPIC_OK:
            raise LLMError("anthropic package not installed. Run: pip install anthropic")
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.provider = "anthropic"

    def generate(self, system: str, user: str, max_tokens: int = 16000) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return response.content[0].text
        except Exception as e:
            raise LLMError(f"Anthropic API call failed: {e}")


# ---------- Provider selector -----------------------------------------------

_GEMINI_DEFAULT_MODEL    = "gemini-3.1-pro-preview"
_ANTHROPIC_DEFAULT_MODEL = "claude-opus-4-6"


def get_llm_client() -> tuple[Optional[object], str]:
    """Return (client, reason). Client is None if unavailable; reason explains why.

    Provider priority:
        PEBBLE_PROVIDER=gemini     -> GeminiClient (default if key present)
        PEBBLE_PROVIDER=anthropic  -> AnthropicClient
        (unset)                    -> try Gemini first, fall back to Anthropic
    """
    provider = os.environ.get("PEBBLE_PROVIDER", "").strip().lower()

    # -- Explicit Anthropic request --
    if provider == "anthropic":
        if not _ANTHROPIC_OK:
            return None, "anthropic package not installed (run: pip install anthropic)"
        key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not key:
            return None, "ANTHROPIC_API_KEY not set (PEBBLE_PROVIDER=anthropic)"
        model = os.environ.get("PEBBLE_MODEL", _ANTHROPIC_DEFAULT_MODEL).strip() or _ANTHROPIC_DEFAULT_MODEL
        try:
            return AnthropicClient(api_key=key, model=model), "ok"
        except LLMError as e:
            return None, str(e)

    # -- Gemini (explicit or default) --
    gemini_key = os.environ.get("GOOGLE_API_KEY", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()
    if gemini_key and _GOOGLE_OK:
        model = os.environ.get("PEBBLE_MODEL", _GEMINI_DEFAULT_MODEL).strip() or _GEMINI_DEFAULT_MODEL
        try:
            return GeminiClient(api_key=gemini_key, model=model), "ok"
        except LLMError as e:
            return None, str(e)

    # -- Fall back to Anthropic if Gemini key isn't set --
    if provider != "gemini":
        if _ANTHROPIC_OK:
            key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
            if key:
                model = os.environ.get("PEBBLE_MODEL", _ANTHROPIC_DEFAULT_MODEL).strip() or _ANTHROPIC_DEFAULT_MODEL
                try:
                    return AnthropicClient(api_key=key, model=model), "ok"
                except LLMError as e:
                    return None, str(e)

    # -- Nothing configured --
    if not _GOOGLE_OK and not _ANTHROPIC_OK:
        return None, "no LLM package installed (run: pip install -r requirements.txt)"
    if not gemini_key:
        return None, "GOOGLE_API_KEY not set -- add it to .env (or set PEBBLE_PROVIDER=anthropic)"
    return None, "auto-build not configured"


# --------------------------------------------------------------------------
# FILE OUTPUT PARSER
# --------------------------------------------------------------------------

FILE_BLOCK_RE = re.compile(
    r'<pebble-file\s+path="([^"]+)">\s*\n(.*?)\n?\s*</pebble-file>',
    re.DOTALL,
)


def parse_files(llm_output: str) -> list[tuple[str, str]]:
    return FILE_BLOCK_RE.findall(llm_output)


FILE_FORMAT_INSTRUCTION = """

---

## OUTPUT FORMAT -- START BUILDING NOW

Do not write a plan. Do not ask questions. Your entire response must be working project files starting immediately with the first `<pebble-file>` tag.

Return every file the project needs using this exact format:

<pebble-file path="package.json">
[complete file contents]
</pebble-file>

<pebble-file path="app/layout.tsx">
[complete file contents]
</pebble-file>

Strict rules:
- One <pebble-file> block per file. The `path` is the relative path from the project root.
- Nothing outside the <pebble-file> blocks. No commentary. No plan. The first character of your response MUST be `<`.
- Output EVERY file the project needs: package.json, all config files, app/globals.css, app/layout.tsx, app/page.tsx, all additional pages, all components referenced in code.
- Include README.md with the media drop-in guide from the Stack Skill.
- Create placeholder `.gitkeep` files in every media folder so the directory structure exists on disk when the client clones the project:
  - `public/images/hero/.gitkeep`
  - `public/images/about/.gitkeep`
  - `public/images/services/.gitkeep`
  - `public/images/gallery/.gitkeep`
  - `public/images/logos/.gitkeep`
  - `public/images/og/.gitkeep`
  - `public/videos/.gitkeep`
  - `public/fonts/.gitkeep`
- All files must be complete. No TODOs. No stubs.
- Follow the Stack Skill's media path conventions exactly -- `/images/hero/hero.jpg`, `/images/about/owner.jpg`, etc.
- Testimonials: only include real ones. If none provided, omit the section. Never write fake reviews.
- Missing contact info: use `[BUSINESS PHONE]`, `[EMAIL]`, `[ADDRESS]` -- do not invent.
"""


# --------------------------------------------------------------------------
# HTTP SERVER
# --------------------------------------------------------------------------

class PebbleHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    # ---- GET ----
    def do_GET(self):
        try:
            if self.path in ("/", "/index.html"):
                self._serve_file(INDEX_HTML, "text/html; charset=utf-8")
            elif self.path == "/api/health":
                self._handle_health()
            elif self.path == "/api/briefs":
                self._handle_list_briefs()
            elif self.path.startswith("/api/briefs/"):
                slug = self.path.split("/api/briefs/", 1)[1]
                self._handle_get_brief(slug)
            elif self.path.startswith("/preview/"):
                self._handle_preview()
            else:
                self.send_response(404); self.end_headers()
                self.wfile.write(b"Not found")
        except Exception as exc:
            try:
                self._json(500, {"error": f"Server error: {exc}"})
            except Exception:
                pass

    # ---- POST ----
    def do_POST(self):
        try:
            if self.path == "/api/build":
                self._handle_build(generate=False)
            elif self.path == "/api/generate":
                self._handle_build(generate=True)
            elif self.path == "/api/setup":
                self._handle_setup()
            else:
                self.send_response(404); self.end_headers()
        except Exception as exc:
            try:
                self._json(500, {"error": f"Server error: {exc}"})
            except Exception:
                pass

    def _handle_health(self):
        client, reason = get_llm_client()
        provider = getattr(client, "provider", None) if client else None
        model = getattr(client, "model", None) if client else None
        self._json(200, {
            "engine_ok": _ENGINE_OK,
            "google_installed": _GOOGLE_OK,
            "anthropic_installed": _ANTHROPIC_OK,
            "google_key_set": bool(
                os.environ.get("GOOGLE_API_KEY", "").strip() or
                os.environ.get("GEMINI_API_KEY", "").strip()
            ),
            "anthropic_key_set": bool(os.environ.get("ANTHROPIC_API_KEY", "").strip()),
            "llm_ready": reason == "ok",
            "llm_reason": reason,
            "provider": provider,
            "model": model,
        })

    def _handle_list_briefs(self):
        briefs = []
        if OUTPUT_DIR.exists():
            for d in sorted(OUTPUT_DIR.iterdir()):
                bp = d / "brief.json"
                if not bp.exists():
                    continue
                try:
                    b = json.loads(bp.read_text(encoding="utf-8"))
                    briefs.append({
                        "slug": d.name,
                        "business_name": b.get("business_name", "?"),
                        "industry": b.get("industry", ""),
                        "aesthetic_direction": b.get("aesthetic_direction", ""),
                        "created_at": b.get("_created_at", ""),
                        "has_site": (d / "site").exists(),
                    })
                except Exception:
                    pass
        briefs.sort(key=lambda b: b["created_at"], reverse=True)
        self._json(200, {"briefs": briefs})

    def _handle_get_brief(self, slug: str):
        slug = _slugify(slug)
        d = OUTPUT_DIR / slug
        if not d.exists() or not (d / "brief.json").exists():
            self._json(404, {"error": "brief not found"}); return
        brief = json.loads((d / "brief.json").read_text(encoding="utf-8"))
        prompt = (d / "PROMPT.md").read_text(encoding="utf-8") if (d / "PROMPT.md").exists() else ""
        files = []
        site_dir = d / "site"
        if site_dir.exists():
            for f in sorted(site_dir.rglob("*")):
                if f.is_file():
                    files.append(str(f.relative_to(site_dir)))
        self._json(200, {
            "brief": brief, "prompt": prompt,
            "files": files, "has_site": site_dir.exists(),
            "slug": slug,
        })

    def _handle_setup(self):
        """Save API key + provider to .env, reload env, return new health state."""
        length = int(self.headers.get("Content-Length", "0"))
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            self._json(400, {"error": "invalid json"}); return

        provider = data.get("provider", "gemini").strip().lower()
        api_key  = data.get("api_key", "").strip()

        if not api_key:
            self._json(400, {"error": "API key cannot be empty"}); return

        if provider == "gemini":
            key_name = "GOOGLE_API_KEY"
        elif provider == "anthropic":
            key_name = "ANTHROPIC_API_KEY"
        else:
            self._json(400, {"error": f"unknown provider: {provider}"}); return

        # Read existing .env, remove old entries for this key + provider
        env_path = PROJECT_ROOT / ".env"
        lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
        lines = [l for l in lines
                 if not l.startswith(f"{key_name}=") and not l.startswith("PEBBLE_PROVIDER=")]
        lines.append(f"PEBBLE_PROVIDER={provider}")
        lines.append(f"{key_name}={api_key}")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        # Reload into current process
        os.environ[key_name]       = api_key
        os.environ["PEBBLE_PROVIDER"] = provider

        # Return new health state
        client, reason = get_llm_client()
        self._json(200, {
            "ok": reason == "ok",
            "reason": reason,
            "provider": getattr(client, "provider", None),
            "model": getattr(client, "model", None),
        })

    def _handle_preview(self):
        rest = self.path[len("/preview/"):]
        if not rest:
            self.send_response(404); self.end_headers(); return
        parts = rest.split("/", 1)
        slug = _slugify(parts[0])
        rel = parts[1] if len(parts) > 1 and parts[1] else "index.html"
        if ".." in rel.split("/"):
            self.send_response(403); self.end_headers(); return
        site_file = OUTPUT_DIR / slug / "site" / rel
        if not site_file.exists() or not site_file.is_file():
            self.send_response(404); self.end_headers()
            self.wfile.write(f"Preview file not found: {rel}".encode()); return
        ext = site_file.suffix.lstrip(".").lower()
        ct_map = {
            "html": "text/html", "htm": "text/html",
            "css": "text/css", "js": "application/javascript",
            "json": "application/json", "svg": "image/svg+xml",
            "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif", "ico": "image/x-icon",
            "woff": "font/woff", "woff2": "font/woff2",
        }
        ct = ct_map.get(ext, "text/plain")
        if ct.startswith("text/") or ct in ("application/javascript", "application/json", "image/svg+xml"):
            ct += "; charset=utf-8"
        self._serve_file(site_file, ct)

    def _handle_build(self, generate: bool):
        length = int(self.headers.get("Content-Length", "0"))
        try:
            answers = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            self._json(400, {"error": "invalid json"}); return

        slug = _slugify(answers.get("business_name", "untitled"))
        answers["_slug"] = slug
        if "_created_at" not in answers:
            answers["_created_at"] = datetime.now().isoformat()

        ds_text = ""
        if generate_design_system:
            try:
                query = build_ui_query(answers)
                ds_text = generate_design_system(query, answers["business_name"], format="markdown")
            except Exception as e:
                ds_text = f"*(Design system generation failed: {e})*"

        # Research industry for data-driven recommendations
        business_type = answers.get("business_type", answers.get("industry", ""))
        research_text = ""
        if business_type:
            try:
                research_text = research_industry(business_type)
            except Exception as e:
                print(f"Industry research failed: {e}")
                research_text = ""  # Continue without research

        # Fetch placeholder images from Unsplash
        images = {}
        if business_type:
            try:
                images = get_unsplash_images(business_type)
            except Exception as e:
                print(f"Image fetching failed: {e}")
                images = {}  # Continue without images

        notes = audit_design_system(ds_text) if ds_text else []
        prompt = build_prompt(answers, ds_text, notes, research_text, images)

        out_dir = OUTPUT_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "brief.json").write_text(json.dumps(answers, indent=2), encoding="utf-8")
        (out_dir / "PROMPT.md").write_text(prompt, encoding="utf-8")

        if not generate:
            self._json(200, {
                "prompt": prompt,
                "warning_count": len(notes),
                "slug": slug,
                "saved_to": f"output/{slug}/",
            }); return

        client, reason = get_llm_client()
        if not client:
            self._json(503, {
                "error": f"LLM not configured: {reason}",
                "prompt": prompt, "warning_count": len(notes),
                "slug": slug, "saved_to": f"output/{slug}/",
            }); return

        try:
            full_user = prompt + FILE_FORMAT_INSTRUCTION
            system = (
                "You are a senior web engineer executing a precise build specification. "
                "You do not have opinions. You do not ask questions. You do not present alternatives. "
                "You read the brief, you read every skill file, and you build exactly what is specified.\n\n"

                "NON-NEGOTIABLE RULES -- violating any of these is a build failure:\n"
                "1. Output ONLY <pebble-file> blocks. No preamble. No plan. No commentary. First character is `<`.\n"
                "2. Every file must be complete. Zero TODOs. Zero stubs. Zero placeholder functions.\n"
                "3. Apply the iOS Skill rules to every animation, scroll effect, and layout. Not optional.\n"
                "4. `100dvh` not `100vh` or `h-screen` on any full-height element.\n"
                "5. `ScrollTrigger.normalizeScroll(true)` and `ScrollTrigger.config({ ignoreMobileResize: true })` -- always present.\n"
                "6. All autoplay video: `autoPlay muted loop playsInline` -- all four attributes, always.\n"
                "7. All form inputs: minimum `font-size: 16px` -- without exception.\n"
                "8. No fake testimonials. No invented phone numbers or addresses. Use `[BUSINESS PHONE]` etc.\n"
                "9. No `scroll-behavior: smooth` in CSS anywhere.\n"
                "10. Three.js: dynamic import with `ssr: false`, `dpr={[1, 2]}`, context-lost handler, dispose on unmount.\n\n"

                "If you are uncertain about any detail not in the brief, make the best decision and build. "
                "The owner reviews the output. You are not the reviewer."
            )
            t0 = time.time()
            response = client.generate(system=system, user=full_user, max_tokens=16000)
            elapsed = time.time() - t0
        except LLMError as e:
            self._json(500, {
                "error": str(e),
                "prompt": prompt, "warning_count": len(notes),
                "slug": slug, "saved_to": f"output/{slug}/",
            }); return

        files = parse_files(response)
        (out_dir / "llm_response_raw.txt").write_text(response, encoding="utf-8")

        if not files:
            self._json(500, {
                "error": "LLM response had no <pebble-file> blocks. Raw response saved to llm_response_raw.txt.",
                "prompt": prompt, "warning_count": len(notes),
                "slug": slug, "saved_to": f"output/{slug}/",
                "raw_preview": response[:1500],
            }); return

        site_dir = out_dir / "site"
        site_dir.mkdir(exist_ok=True)
        written: list[str] = []
        for path, content in files:
            safe = path.lstrip("/\\")
            if ".." in Path(safe).parts or safe.startswith("/"):
                continue
            full = site_dir / safe
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
            written.append(safe)

        (out_dir / "build_meta.json").write_text(json.dumps({
            "model": client.model,
            "elapsed_seconds": round(elapsed, 1),
            "file_count": len(written),
            "built_at": datetime.now().isoformat(),
        }, indent=2))

        self._json(200, {
            "prompt": prompt, "warning_count": len(notes),
            "slug": slug, "saved_to": f"output/{slug}/",
            "files_written": written, "file_count": len(written),
            "site_path": f"output/{slug}/site/",
            "preview_url": f"/preview/{slug}/",
            "elapsed_seconds": round(elapsed, 1),
            "model": client.model,
        })

    def _serve_file(self, path: Path, content_type: str):
        if not path.exists():
            self.send_response(404); self.end_headers()
            self.wfile.write(f"{path} not found".encode()); return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _banner():
    client, reason = get_llm_client()
    engine_status = "loaded" if _ENGINE_OK else "degraded (no design_system.py)"
    print()
    print("  " + "-" * 56)
    print(f"   Pebble Engine")
    print(f"   ui-ux-pro-max engine: {engine_status}")
    if reason == "ok":
        provider = getattr(client, "provider", "?")
        model    = getattr(client, "model", "?")
        print(f"   auto-build mode:      ready")
        print(f"   provider:             {provider}")
        print(f"   model:                {model}")
    else:
        print(f"   auto-build mode:      unavailable")
        print(f"     reason: {reason}")
    print("  " + "-" * 56)


def serve(port: int = 8000, open_browser: bool = True) -> None:
    _banner()
    url = f"http://localhost:{port}"
    print(f"   running at {url}\n")
    server = HTTPServer(("127.0.0.1", port), PebbleHandler)
    if open_browser:
        try: webbrowser.open(url)
        except Exception: pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pebble Engine -- visual website briefing.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    serve(port=args.port, open_browser=not args.no_browser)
