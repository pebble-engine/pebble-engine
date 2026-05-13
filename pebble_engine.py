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
import urllib.parse
import urllib.request
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
# IMAGE SOURCING SYSTEM
# Primary:  Pexels API (keyword-relevant, requires PEXELS_API_KEY in .env)
# Fallback: Picsum Photos (seed-based, no key needed, generic photos)
# --------------------------------------------------------------------------

# Maps industry keywords → (main scene query, people/team query)
_PEXELS_QUERIES: dict[str, tuple[str, str]] = {
    # Home services
    "plumbing":          ("plumber pipe repair bathroom",        "plumber technician worker"),
    "electrician":       ("electrical wiring installation",      "electrician worker professional"),
    "electrical":        ("electrical wiring installation",      "electrician worker professional"),
    "hvac":              ("air conditioning heating system",     "hvac technician professional"),
    "roofing":           ("roof shingles construction",          "roofer contractor worker"),
    "landscaping":       ("garden landscape lawn design",        "landscaper gardener worker"),
    "cleaning":          ("clean modern interior spotless",      "cleaning service professional"),
    "painting":          ("interior painting home",              "painter contractor worker"),
    "general contractor":("home renovation construction",        "contractor builder worker"),
    "construction":      ("construction building site",          "construction worker builder"),
    "moving":            ("moving boxes relocation truck",       "movers professional team"),
    "pest control":      ("clean pest free home interior",       "pest control technician"),
    "pool":              ("swimming pool luxury backyard",       "pool technician professional"),
    "fence":             ("fence installation backyard",         "fence contractor worker"),
    "flooring":          ("hardwood floor installation",         "flooring contractor worker"),
    # Health & wellness
    "yoga":              ("yoga studio peaceful zen",            "yoga instructor class"),
    "fitness":           ("gym equipment modern workout",        "personal trainer coaching"),
    "personal trainer":  ("fitness training gym",               "personal trainer athlete"),
    "wellness":          ("spa wellness relaxing retreat",       "wellness therapist professional"),
    "spa":               ("luxury spa interior serene",          "spa therapist massage"),
    "massage":           ("massage therapy room calm",           "massage therapist professional"),
    "chiropractic":      ("chiropractic clinic office",          "chiropractor patient treatment"),
    "physical therapy":  ("physical therapy rehabilitation",     "physical therapist patient"),
    # Medical & dental
    "dentist":           ("dental office clinic modern",         "dentist patient professional"),
    "dental":            ("dental office clinic modern",         "dentist professional"),
    "doctor":            ("medical clinic office modern",        "doctor patient professional"),
    "optometry":         ("eye care clinic optical",             "optometrist professional"),
    "veterinary":        ("veterinary clinic pet care",          "veterinarian pet owner"),
    "vet":               ("veterinary animal clinic",            "veterinarian professional"),
    # Mental health
    "therapist":         ("therapy office calm peaceful",        "therapist counselor professional"),
    "counseling":        ("counseling therapy office serene",    "counselor therapist"),
    "psychology":        ("psychology office calm neutral",      "psychologist professional"),
    # Beauty
    "hair salon":        ("hair salon interior modern",          "hairstylist client beauty"),
    "salon":             ("beauty salon interior modern",        "hairstylist beautician professional"),
    "barbershop":        ("barbershop interior classic",         "barber client professional"),
    "nail":              ("nail salon manicure art",             "nail technician client"),
    "makeup":            ("makeup artist studio beauty",         "makeup artist professional"),
    # Food & beverage
    "restaurant":        ("restaurant interior fine dining",     "chef server professional"),
    "cafe":              ("coffee shop cafe interior cozy",      "barista coffee professional"),
    "coffee":            ("coffee shop cafe cozy interior",      "barista professional"),
    "bakery":            ("bakery fresh bread pastry",           "baker pastry chef"),
    "bar":               ("cocktail bar lounge interior",        "bartender mixologist"),
    "catering":          ("catering food event elegant",         "catering chef professional"),
    # Professional services
    "law":               ("law office modern professional",      "lawyer attorney professional"),
    "attorney":          ("law firm office professional",        "attorney professional"),
    "accounting":        ("accounting office finance modern",    "accountant professional"),
    "financial":         ("financial planning office",           "financial advisor professional"),
    "insurance":         ("professional office business",        "insurance agent professional"),
    "real estate":       ("luxury modern home interior",         "real estate agent professional"),
    # Tech & creative
    "tech":              ("technology startup office modern",    "software developer team"),
    "software":          ("software development modern office",  "developer programmer team"),
    "saas":              ("modern tech office startup",          "software team professional"),
    "agency":            ("creative agency studio modern",       "design team professional"),
    "marketing":         ("marketing creative office",           "marketing team professional"),
    "web design":        ("design studio creative workspace",    "designer professional"),
    "photography":       ("photography studio camera equipment", "photographer professional"),
    # Events & lifestyle
    "wedding":           ("wedding ceremony elegant venue",      "wedding couple celebration"),
    "event":             ("event venue elegant setup",           "event planner professional"),
    # Education & childcare
    "childcare":         ("daycare children bright classroom",   "childcare teacher professional"),
    "education":         ("classroom school learning bright",    "teacher student professional"),
    "tutoring":          ("tutoring study desk learning",        "tutor student"),
    # Pet services
    "pet grooming":      ("pet grooming salon dog",              "pet groomer professional"),
    "dog training":      ("dog training obedience outdoor",      "dog trainer professional"),
    # Auto
    "auto repair":       ("auto repair shop garage clean",       "mechanic car professional"),
    "car wash":          ("car wash clean shiny auto",           "car wash professional"),
}


def _pexels_queries_for_industry(industry: str) -> tuple[str, str]:
    ind = industry.lower()
    for key, queries in _PEXELS_QUERIES.items():
        if key in ind:
            return queries
    safe = re.sub(r"[^a-z0-9 ]", " ", ind).strip()
    return (f"{safe} professional business", f"{safe} professional team")


def get_placeholder_images(industry: str, image_count: int = 8) -> dict[str, str]:
    """Picsum Photos fallback — seed-based, no API key, generic photos."""
    slug = _slugify(industry)
    return {
        "hero":      f"https://picsum.photos/seed/{slug}-hero/1600/900",
        "service_1": f"https://picsum.photos/seed/{slug}-svc1/800/600",
        "service_2": f"https://picsum.photos/seed/{slug}-svc2/800/600",
        "service_3": f"https://picsum.photos/seed/{slug}-svc3/800/600",
        "team_1":    f"https://picsum.photos/seed/{slug}-team1/600/600",
        "team_2":    f"https://picsum.photos/seed/{slug}-team2/600/600",
        "gallery_1": f"https://picsum.photos/seed/{slug}-gal1/800/600",
        "gallery_2": f"https://picsum.photos/seed/{slug}-gal2/800/600",
    }


def get_pexels_images(industry: str, api_key: str) -> dict[str, str]:
    """
    Fetch industry-relevant images from Pexels API.
    Makes 2 requests: one landscape query for scenes, one portrait for team.
    Falls back to Picsum per-slot on any individual failure.
    """
    fallback = get_placeholder_images(industry)
    main_q, people_q = _pexels_queries_for_industry(industry)

    def _fetch(query: str, orientation: str, count: int) -> list[str]:
        params = urllib.parse.urlencode({
            "query": query,
            "per_page": max(count + 5, 15),
            "orientation": orientation,
        })
        req = urllib.request.Request(
            f"https://api.pexels.com/v1/search?{params}",
            headers={"Authorization": api_key, "User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
        urls, seen = [], set()
        for photo in data.get("photos", []):
            pid = photo["id"]
            if pid in seen:
                continue
            seen.add(pid)
            src = photo["src"]
            urls.append(src.get("large2x") or src.get("large") or src["original"])
            if len(urls) >= count:
                break
        return urls

    images: dict[str, str] = {}

    try:
        scene = _fetch(main_q, "landscape", 6)
        keys = ["hero", "service_1", "service_2", "service_3", "gallery_1", "gallery_2"]
        for i, key in enumerate(keys):
            images[key] = scene[i] if i < len(scene) else fallback[key]
    except Exception as e:
        print(f"  Pexels scene query failed ({e!r}) — using Picsum fallback for scene slots")
        for key in ["hero", "service_1", "service_2", "service_3", "gallery_1", "gallery_2"]:
            images[key] = fallback[key]

    try:
        people = _fetch(people_q, "portrait", 2)
        images["team_1"] = people[0] if len(people) > 0 else fallback["team_1"]
        images["team_2"] = people[1] if len(people) > 1 else fallback["team_2"]
    except Exception as e:
        print(f"  Pexels people query failed ({e!r}) — using Picsum fallback for team slots")
        images["team_1"] = fallback["team_1"]
        images["team_2"] = fallback["team_2"]

    return images


# Keep old name as alias so any external callers don't break
get_unsplash_images = get_placeholder_images


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
# RESOLVED DESIGN CONTRACT
# Maps quiz answers → concrete, non-negotiable values before any skill fires.
# Visual experience is ALWAYS cinematic — it is no longer a user choice.
# --------------------------------------------------------------------------

_FONT_BY_POSITION = {
    "premium":      ("Fraunces",         "light/thin weight (300–400) — luxury lives in restraint; wide tracking"),
    "professional": ("Fraunces",         "semibold (600) — editorial authority; pairs with Inter body"),
    "accessible":   ("Lora",             "regular/medium — warm humanist serif, approachable and credible"),
    "budget":       ("Manrope",          "extrabold (800) — direct, confident, no subtlety needed"),
}

_PALETTE_BY_POSITION = {
    # (bg, surface, text, dark_default)
    "premium":      ("#0A0A0A", "#1A1A1A", "#F9FAFB", "Yes"),
    "professional": ("#FFFFFF", "#F9FAFB", "#111827", "No"),
    "accessible":   ("#F5EFE6", "#FFFFFF", "#1A1A1A", "No"),
    "budget":       ("#FFFFFF", "#F9FAFB", "#111827", "No"),
}

_TONE_BY_BRAND = {
    "professional_formal":   "Authoritative and specific. Credentials, years, certifications. Declarative sentences. No filler.",
    "friendly_approachable": "Warm and conversational. Empathy before selling. 'We' language. CTAs are invitations: 'Let\\'s talk' not 'GET STARTED'.",
    "technical_expert":      "Data-driven and precise. Numbers, specs, methodology. Prove the claim — don't state it.",
    "creative_confident":    "Bold, opinionated, memorable. Strong verbs. Distinctive voice that sounds like a person, not a template.",
}

_CTA_BY_POSITION = {
    "premium":      "'Inquire' / 'Schedule a consultation' / 'Request access'",
    "professional": "'Book a free consultation' / 'Get a free quote' / 'Call us today'",
    "accessible":   "'Let\\'s talk' / 'Reach out' / 'Get started'",
    "budget":       "'Call now' / 'Get a quote' / 'Save today'",
}

# Visual is always cinematic — easing values hardcoded
_CINEMATIC = ("expo.out", "0.9s", "0.12s", "scroll-pinned sections allowed (`anticipatePin: 1`, `scrub: 1`)")

# Industries that default to dark background regardless of brand_position
_DARK_INDUSTRIES = {
    "luxury", "premium", "yacht", "jewelry", "bar", "nightclub",
    "photography", "auto detail", "car detail", "detailing", "club",
    "lounge", "studio", "agency", "tattoo", "cigar",
}
# Industries that default to warm-light background
_WARM_INDUSTRIES = {
    "yoga", "wellness", "dentist", "therapist", "bakery", "cafe",
    "spa", "massage", "florist", "counseling", "meditation",
}


def build_resolved_contract(answers: dict) -> str:
    brand_position = answers.get("brand_position", "professional").strip()
    brand_tone     = answers.get("brand_tone", "professional_formal").strip()
    industry       = answers.get("industry", answers.get("business_type", "")).lower()

    heading_font, font_note = _FONT_BY_POSITION.get(brand_position, _FONT_BY_POSITION["professional"])
    bg, surface, text_col, dark_default = _PALETTE_BY_POSITION.get(brand_position, _PALETTE_BY_POSITION["professional"])
    copy_tone    = _TONE_BY_BRAND.get(brand_tone, _TONE_BY_BRAND["professional_formal"])
    cta_examples = _CTA_BY_POSITION.get(brand_position, _CTA_BY_POSITION["professional"])
    easing, duration, stagger, scroll_pin = _CINEMATIC

    # Industry overrides
    if any(w in industry for w in _DARK_INDUSTRIES) and dark_default == "No":
        bg, surface, text_col, dark_default = "#0A0A0A", "#1A1A1A", "#F9FAFB", "Yes"
    elif any(w in industry for w in _WARM_INDUSTRIES) and dark_default == "No":
        bg, surface, text_col = "#F5EFE6", "#FFFFFF", "#1A1A1A"

    # Video hero industries
    video_industries = {
        "auto detail", "detailing", "restaurant", "cafe", "fitness", "gym",
        "photography", "events", "wedding", "real estate", "construction",
        "beauty", "salon", "barbershop",
    }
    recommend_video = any(w in industry for w in video_industries)
    video_note = "Yes — use `<video autoPlay muted loop playsInline>` with Pexels image poster" if recommend_video else "Optional — use if client has footage; otherwise full-bleed image with parallax"

    return f"""| Decision | Resolved Value |
|---|---|
| **Heading font** | {heading_font} — {font_note} |
| **Body font** | Inter (body, UI, data only — never headings) |
| **Font loading** | Both via `next/font/google` in `layout.tsx`; both CSS variables on `<html>` |
| **Background** | `{bg}` |
| **Surface / card** | `{surface}` |
| **Text color** | `{text_col}` |
| **Dark mode** | {dark_default} |
| **Motion** | **Always cinematic** — SplitText headlines, clip-path reveals, scroll-pinned sections, parallax, counting stats |
| **GSAP easing** | `{easing}` |
| **Duration** | `{duration}` per element · Stagger: `{stagger}` |
| **Scroll pinning** | {scroll_pin} |
| **Video hero** | {video_note} |
| **Copy tone** | {copy_tone} |
| **CTA language** | {cta_examples} |

*Brand: `{brand_position}` · Tone: `{brand_tone}` · Visual: always cinematic*"""


# --------------------------------------------------------------------------
# PROMPT TEMPLATE  -- 11-section structure
# --------------------------------------------------------------------------

PROMPT_TEMPLATE = """\
# Website Build Brief -- {business_name}

You are building a complete, production-quality website. Read every section of this brief before writing a single line of code. The skills embedded in this brief contain thousands of words of specific, researched direction. Apply all of it.

---

## RESOLVED DESIGN CONTRACT — Read This First

These values were computed from your quiz answers before any skill content was loaded. Skills in sections 3–10 are implementation guides — they do not override these values. When any skill content seems to suggest a different choice, the contract wins. Concrete beats ambiguous.

{resolved_contract}

---

## 1. Project Overview

- **Business name:** {business_name}
- **Type of business:** {business_type}
- **Location / service area:** {location}
- **Primary visitor action:** {visitor_action}
- **Booking or payment system:** {booking_system}

---

## 2. MANDATORY OUTPUT STRUCTURE — CINEMATIC BY DEFAULT

Every site built by this engine is cinematic. This is not a setting — it is the standard. No flat card grids. No static heroes. No dead links. No approximations of the code patterns below.

### Required Pages

1. **Homepage** (`app/page.tsx`) — cinematic landing page, all sections below
2. **Services** (`app/services/page.tsx`) — full-bleed alternating layout, NOT a card grid
3. **About** (`app/about/page.tsx`) — editorial story with parallax imagery
4. **Contact** (`app/contact/page.tsx`) — working form with success state, map embed

### Homepage — Cinematic Section Structure (Build in Order)

**Section 1: Hero — Full Viewport**
- `min-h-[100dvh]` always — never `min-h-screen`
- Full-bleed background: dark overlay on image or video
- **Video hero** (check Resolved Contract above): `<video autoPlay muted loop playsInline>` — use the hero Pexels URL from Section 8b as `poster` attribute
- If no video: full-bleed `next/image` with `priority` and a `className="parallax-bg"` wrapper
- Layout (all elements required, in order):
  1. `<p className="hero-eyebrow">` — location · industry tagline (small caps, accent color)
  2. `<h1 className="hero-heading font-display text-7xl md:text-9xl leading-none text-white">` — the main headline. **THIS MUST BE PRESENT AND VISIBLE. No hero without a large headline.**
  3. `<p className="hero-sub">` — supporting sentence naming the outcome
  4. `<div className="hero-cta flex gap-4">` — primary + secondary CTA
  5. `<div className="hero-badge">` — floating trust signal (years · certified · insured)
- DO NOT: plain color background, centered white-background hero, static text block, hero with only CTA buttons and no headline

**Section 2: Trust Bar — Counting Stats**
- Dark or brand-accent background strip — NOT white
- 3–4 numbers that count up on scroll: years in business, jobs completed, rating, insured/certified
- Each number uses `data-target` attribute + GSAP textContent counter (see Code Patterns)
- Single horizontal row — NOT cards, NOT icons in a grid

**Section 3: Services — Horizontal Scroll or Full-Bleed Alternating**
CHOOSE ONE — a 3-column card grid is forbidden:

*Horizontal Scroll (4+ services):*
Pin the section. Scrub service panels horizontally via ScrollTrigger. Each panel: full-height, image fills left 55%, content right 45%.

*Full-Bleed Alternating (2–3 services):*
Each service is a full-width section. Image fills one half, text the other. Alternate: image-left/text-right, text-left/image-right. Every image uses clip-path reveal (see Code Patterns).

**Section 4: Social Proof — Dark Editorial**
- Dark background
- ONE large quote, 3–4rem font size, centered — not a carousel of small cards
- Stars above the quote, attribution below (name + specific result: "saved $3,200" / "back in 2 days")
- If no testimonials: bold credibility statement with a striking number ("Over 1,200 vehicles restored")

**Section 5: About / Story — Parallax Editorial**
- Full-bleed parallax background image (see Code Patterns)
- Owner story: specific, first-person, human — NOT "we are committed to excellence"
- Credentials woven into narrative — not a badge row
- Link to full About page

**Section 6: FAQ or Feature Callout**
- FAQ: 4–6 accordion questions, industry-specific, genuinely useful answers
- Alternative if few questions: a "Why us" section with 2–3 bold differentiating claims

**Section 7: Final CTA — Full Bleed, One Action**
- Full-width section, brand dark or strong accent color
- ONE headline + ONE large centered CTA button
- Phone number as secondary option beneath it
- NO competing buttons

**Section 8: Footer**
- tel: links, mailto: links, address, hours, social icons, copyright

### Navigation — Animated Header

- Fixed position, `className="navbar"` on `<header>` (required for animation below)
- Logo left · nav links center · phone CTA right
- Mobile: hamburger → fullscreen overlay with staggered link reveals
- CTA button: `<a href="tel:[BUSINESS PHONE]">` — never a dead link

---

### REQUIRED TECH STACK

```json
{{
  "dependencies": {{
    "next": "^15.0.0",
    "react": "^19.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "gsap": "^3.12.0",
    "@gsap/react": "^2.1.0",
    "lenis": "^1.1.0",
    "framer-motion": "^11.0.0"
  }}
}}
```

**Performance non-negotiables:**
- `next/image` for ALL images — never raw `<img>` tags. Use `fill` + `object-cover` for full-bleed, explicit `width`/`height` for fixed-size. `priority` on hero image only.
- `next/font/google` for both fonts — zero layout shift
- `gsap.registerPlugin(ScrollTrigger, SplitText)` at module level — never inside useEffect
- `dynamic()` with `{{ ssr: false }}` for any component using `window` or `document`
- `will-change: transform` only during active animation — remove after with `gsap.set(el, {{ clearProps: "willChange" }})`
- `@media (prefers-reduced-motion: reduce) {{ * {{ animation-duration: 0.01ms !important }} }}` in globals.css

---

### CINEMATIC CODE PATTERNS — Implement Verbatim

#### 1. Hero Entrance with SplitText

```tsx
"use client"
import {{ useGSAP }} from "@gsap/react"
import gsap from "gsap"
import {{ SplitText }} from "gsap/SplitText"

gsap.registerPlugin(SplitText)

useGSAP(() => {{
  const heading = document.querySelector<HTMLElement>(".hero-heading")
  const split = heading ? new SplitText(heading, {{ type: "words" }}) : null

  const tl = gsap.timeline({{ delay: 0.1, defaults: {{ ease: "expo.out" }} }})
  tl.from(".hero-eyebrow", {{ opacity: 0, y: 16, duration: 0.6 }})

  if (split) {{
    tl.from(split.words, {{ opacity: 0, y: 52, stagger: 0.06, duration: 0.85 }}, "-=0.3")
  }} else {{
    tl.from(".hero-heading", {{ opacity: 0, y: 48, duration: 0.9 }}, "-=0.3")
  }}

  tl.from(".hero-sub",   {{ opacity: 0, y: 20, duration: 0.7 }}, "-=0.5")
    .from(".hero-cta",   {{ opacity: 0, y: 20, stagger: 0.1, duration: 0.6 }}, "-=0.4")
    .from(".hero-badge", {{ opacity: 0, scale: 0.9, duration: 0.5 }}, "-=0.3")

  return () => split?.revert()
}})
```

Apply: `className="hero-eyebrow"`, `"hero-heading"`, `"hero-sub"`, `"hero-cta"` (on each CTA), `"hero-badge"`.

#### 2. Navbar — Hide/Show + Background Fill

```tsx
useGSAP(() => {{
  let lastY = 0
  const darkSite = document.body.dataset.theme === "dark"

  ScrollTrigger.create({{
    onUpdate: () => {{
      const y = ScrollTrigger.positionInViewport(document.body, "top") * -1 || window.scrollY
      const scrollingDown = y > lastY && y > 80

      gsap.to(".navbar", {{
        yPercent: scrollingDown ? -100 : 0,
        duration: 0.35,
        ease: "power2.out",
        overwrite: "auto",
      }})

      const bg = darkSite ? "rgba(10,10,10,0.92)" : "rgba(255,255,255,0.92)"
      gsap.to(".navbar", {{
        backgroundColor: y > 60 ? bg : "transparent",
        backdropFilter: y > 60 ? "blur(14px)" : "blur(0px)",
        boxShadow: y > 60 ? "0 1px 0 rgba(0,0,0,0.08)" : "none",
        duration: 0.3,
        overwrite: "auto",
      }})

      lastY = y
    }},
  }})
}})
```

#### 3. Clip-Path Image Reveal

```tsx
useGSAP(() => {{
  gsap.utils.toArray<HTMLElement>(".reveal-image").forEach((img) => {{
    gsap.fromTo(img,
      {{ clipPath: "inset(0 100% 0 0)" }},
      {{
        clipPath: "inset(0 0% 0 0)",
        duration: 1.1,
        ease: "expo.out",
        scrollTrigger: {{ trigger: img, start: "top 78%" }},
      }}
    )
  }})
}})
```

Add `className="reveal-image"` to every `<Image>` that should reveal on scroll.

#### 4. Counting Stats

```tsx
useGSAP(() => {{
  gsap.utils.toArray<HTMLElement>(".stat-number").forEach((el) => {{
    const target = parseInt(el.dataset.target ?? "0", 10)
    gsap.fromTo(el,
      {{ textContent: 0 }},
      {{
        textContent: target,
        duration: 2,
        ease: "power2.out",
        snap: {{ textContent: 1 }},
        scrollTrigger: {{ trigger: el, start: "top 85%" }},
      }}
    )
  }})
}})
```

JSX: `<span className="stat-number" data-target={{500}}>0</span>`

#### 5. Parallax Background

```tsx
useGSAP(() => {{
  gsap.utils.toArray<HTMLElement>(".parallax-bg").forEach((bg) => {{
    gsap.to(bg, {{
      yPercent: -25,
      ease: "none",
      scrollTrigger: {{
        trigger: bg.closest("section"),
        start: "top top",
        end: "bottom top",
        scrub: 1,
      }},
    }})
  }})
}})
```

Wrap in `overflow-hidden` container. Apply `className="parallax-bg"` to image/video element.

#### 6. Horizontal Scroll Services

```tsx
useGSAP(() => {{
  const cards = gsap.utils.toArray<HTMLElement>(".service-card")
  if (cards.length < 2) return

  gsap.to(".services-track", {{
    xPercent: -100 * (cards.length - 1),
    ease: "none",
    scrollTrigger: {{
      trigger: ".services-scroll",
      start: "top top",
      end: `+=${{cards.length * 100}}%`,
      scrub: 1,
      pin: true,
      anticipatePin: 1,
    }},
  }})
}})
```

Structure: `<section className="services-scroll h-screen overflow-hidden"><div className="services-track flex h-full">{{cards}}</div></section>`

---

### Working CTAs — Zero Dead Links

| CTA | Implementation |
|---|---|
| Phone | `<a href="tel:[BUSINESS PHONE]">` |
| Email | `<a href="mailto:[EMAIL]">` |
| Book | External booking URL or `onClick` scroll to `#contact` |
| Form submit | `onSubmit` with `e.preventDefault()` + success state — never just `href="#"` |
| Page nav | `<Link href="/services">` — real Next.js routes only |

---

### Image Usage

Section 8b provides Pexels photo URLs. Use `next/image` — never raw `<img>`:

```tsx
import Image from "next/image"

<div className="relative overflow-hidden">
  <Image
    src="https://images.pexels.com/photos/..."
    alt="descriptive alt text"
    fill
    className="object-cover reveal-image"
    priority={{false}}
  />
</div>
```

Hero image only: add `priority` prop. All others: lazy load (default).

### Delivery Checklist

- [ ] Hero: video OR full-bleed image with overlay — no flat backgrounds
- [ ] Hero headline: `<h1 className="hero-heading">` present, visible, and large (min text-6xl) — a hero with only CTA buttons is incomplete
- [ ] Hero entrance: SplitText word-by-word headline on mount
- [ ] Navbar: hides scroll-down, returns scroll-up, fills blur at 60px
- [ ] Trust bar: counting stats with `data-target` + GSAP textContent
- [ ] Services: horizontal scroll OR full-bleed alternating — NEVER 3-column card grid
- [ ] Social proof: dark section, one large quote
- [ ] All section images: `next/image` + clip-path reveal on scroll
- [ ] All phone CTAs: `href="tel:..."` — zero `href="#"` links
- [ ] Contact form: `onSubmit` + success state
- [ ] `prefers-reduced-motion` in globals.css
- [ ] 4 pages: Homepage, Services, About, Contact
- [ ] All docs: README, HANDOFF, TODO_ASSETS, STYLE_GUIDE

---

## 3. Visual Reference & Inspiration

{reference_block}

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

## 8b. Placeholder Images (Pexels / Picsum)

{images_block}

---

## 9. Stack, Motion System, and Build Instructions
{stack_block}

### Self-audit before delivering

| Check | Required |
|---|---|
| Phone number | `[BUSINESS PHONE]` — NEVER a 555 number or invented number |
| Heading font | NOT Inter / Geist / Poppins / DM Sans / Space Grotesk — named distinctive face from Contract |
| Subtext | No "Where X meets Y" — specific claim, number, or location |
| Headline | No "Unrivaled / World-class / Unleash" — specific and arguable |
| Hero | Full-bleed image or video with overlay — NEVER flat color behind text |
| Hero headline | `<h1 className="hero-heading">` PRESENT and LARGE (min text-6xl) — CTAs alone are not a hero |
| Hero height | `min-h-[100dvh]` — never `min-h-screen` |
| Hero animation | SplitText word-by-word + 5-element staggered timeline on mount |
| Navbar | Hides scroll-down, returns scroll-up, blur fill at 60px |
| Images | `next/image` everywhere — never raw `<img>` |
| Services layout | Horizontal scroll OR full-bleed alternating — NEVER 3-column card grid |
| Stats | GSAP counting numbers — never static text |
| Social proof | Dark section, large single quote — never a carousel of small cards |
| Section images | Clip-path reveal on scroll |
| Video | `autoPlay muted loop playsInline` — always all four attributes |
| CTAs | `href="tel:..."` for phone — zero dead `href="#"` links |
| Form | `onSubmit` handler with success state |
| Input font | Minimum `font-size: 16px` — prevents iOS zoom |
| Safe area | `env(safe-area-inset-*)` in globals.css |
| reduced-motion | `prefers-reduced-motion` media query in globals.css |
| Booking tool | Matches industry — Booksy ONLY for beauty/wellness |
| Testimonials | Real only or omitted — never fabricated |

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
    extra_block = extra if extra else "*(No extra context provided — use the Business Intelligence skill to fill in industry best practices.)*"

    # Reference URLs / inspiration sites (up to 3)
    _skip = {"", "none", "n/a", "no", "skip"}
    ref_urls = [
        answers.get("reference_url",   "").strip(),
        answers.get("reference_url_2", "").strip(),
        answers.get("reference_url_3", "").strip(),
    ]
    ref_urls = [u for u in ref_urls if u.lower() not in _skip]

    if len(ref_urls) == 1:
        reference_block = f"""A reference site has been provided: **{ref_urls[0]}**

Browse this URL before writing any code. Extract and apply:
- Dominant colors and color temperature (warm vs cool, light vs dark)
- Typography weight, rhythm, and personality
- Spacing philosophy — how tight or generous the layout feels
- Animation style and intensity
- Layout approach — grid, asymmetric, editorial, etc.
- Overall brand feeling

**Important:** Abstract the FEELING, not the layout. Do not copy structure or content from this site. Use it to calibrate the aesthetic direction only. If this is a Dribbble link, extract the visual composition and color mood."""
    elif len(ref_urls) >= 2:
        url_list = "\n".join(f"- **{u}**" for u in ref_urls)
        reference_block = f"""Multiple reference sites have been provided:

{url_list}

Browse all of them before writing any code. Your job is synthesis, not imitation:
1. Identify what they share — color temperature, spacing density, typography weight, animation pace
2. Note where they differ — these are stylistic choices, not requirements
3. Extract the overlap as the aesthetic baseline; apply it to this business's specific context

Extract and synthesize across all references:
- Dominant color temperature (warm vs cool, saturated vs muted)
- Typography personality (formal vs casual, heavy vs refined)
- Spacing rhythm — how generous or dense
- Animation energy — subtle or expressive
- Layout philosophy — structured grid vs editorial vs asymmetric

**Important:** Abstract the FEELING, not any single layout. Do not copy structure or content from these sites. The goal is a site that feels consistent with this aesthetic family — not a clone of any one reference."""
    else:
        reference_block = "*(No reference sites provided — infer aesthetic direction from the Resolved Design Contract and the Business Intelligence skill.)*"

    # Resolved design contract (pre-computed before any skill fires)
    resolved_contract = build_resolved_contract(answers)

    # No-slop skill
    if _NS_SKILL:
        no_slop_block = f"\n\n{_NS_SKILL.strip()}\n"
    else:
        no_slop_block = "\n*(No-slop skill not loaded — apply general quality rules: no 555 phone numbers, no 'Where X meets Y' subtext, no vague superlatives, hero must have visual element.)*\n"

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
            "Use it as supporting detail — it enriches the Resolved Design Contract above. "
            "If any value here contradicts the Contract, the Contract wins.\n\n"
            f"```\n{ds_text.strip()}\n```\n"
        )
    else:
        # Derive a concrete direction from the quiz answers so the LLM has real guidance
        industry_lower = industry.lower()
        is_dark = any(w in industry_lower for w in [
            "luxury", "premium", "yacht", "jewelry", "tech", "saas", "software",
            "agency", "studio", "bar", "nightclub", "photography",
        ])
        is_warm_light = any(w in industry_lower for w in [
            "yoga", "wellness", "dentist", "therapist", "bakery", "cafe", "spa",
        ])
        if is_dark:
            color_dir = (
                "dominant #0A0A0A, secondary #1A1A1A, accent a precise single color "
                "(gold #C8A96E, electric blue #3B82F6, or brand-specific), text #F9FAFB"
            )
            bg_dir = "dark background"
        elif is_warm_light:
            color_dir = (
                "dominant warm white #F5EFE6 or pale sage, secondary #FFFFFF, "
                "accent soft earth tone (dusty rose #D4899A, warm amber #D97706, muted teal #5EAAA8), "
                "text dark charcoal #1A1A1A"
            )
            bg_dir = "warm light background"
        else:
            # Home services, professional services, real estate, food, retail — default light
            color_dir = (
                "dominant #FFFFFF, secondary #F9FAFB, "
                "accent one clean color (trust blue #2563EB, reliability green #059669, or urgency amber #D97706), "
                "text #111827"
            )
            bg_dir = "clean light background"

        ds_block = (
            f"\n**Design system engine unavailable. Apply this direction derived from the brief:**\n\n"
            f"- **Background:** {bg_dir} — confirmed by the Business Intelligence skill for this industry\n"
            f"- **Colors:** {color_dir}\n"
            f"- **Heading font:** choose a DISTINCTIVE face from the No-Slop acceptable list "
            f"(Oswald, Syne, Fraunces, Playfair Display, Instrument Serif, Manrope, Bebas Neue) "
            f"— match to emotional direction. NOT Inter, Roboto, Poppins, or any convergence font.\n"
            f"- **Body font:** Inter (body only, never headings)\n"
            f"- **Load both fonts in layout.tsx** via next/font/google and pass both variables to <html>\n"
            f"- **Override anything generic** — the goal is a site that looks hand-designed, not generated\n"
        )

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
        uses_pexels = any("pexels.com" in url for url in images.values())
        source_label = "Pexels industry-relevant photos" if uses_pexels else "Picsum Photos"
        image_lines = [f"**Use these {source_label} as placeholder images in your build:**\n"]
        for label, url in images.items():
            clean_label = label.replace("_", " ").title()
            image_lines.append(f"- **{clean_label}:** `{url}`")
        image_lines.append("\n**Important:**")
        image_lines.append("- Use these exact URLs in `next/image` `src` props — never raw `<img>` tags")
        image_lines.append("- Do NOT use local paths like `/images/hero.jpg`")
        image_lines.append("- Add `priority` only to the hero image; all others lazy-load by default")
        image_lines.append("- Document all images in TODO_ASSETS.md so client knows to replace with real photos")
        image_lines.append("- Add descriptive alt text for each image")
        if uses_pexels:
            image_lines.append("- **next.config.ts**: `images.pexels.com` MUST be in `remotePatterns` or `next/image` will throw — see Stack skill for the complete config")
        images_block = "\n".join(image_lines)
    else:
        images_block = "\n*(No placeholder images available -- use descriptive alt text with empty src, or use Unsplash source URLs.)*\n"

    return PROMPT_TEMPLATE.format(
        business_name=answers.get("business_name", ""),
        business_type=industry,
        location=answers.get("location", ""),
        visitor_action=visitor_action,
        booking_system=booking_str,
        resolved_contract=resolved_contract,
        reference_block=reference_block,
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

_GEMINI_DEFAULT_MODEL    = "gemini-2.0-flash"
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
                        "aesthetic_direction": b.get("visual_aesthetic", b.get("emotional_direction", "")),
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
                ds_text = generate_design_system(query, answers["business_name"], output_format="markdown")
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

        # Fetch placeholder images (Pexels if key present, else Picsum)
        images = {}
        if business_type:
            try:
                _pexels_key = os.environ.get("PEXELS_API_KEY", "").strip()
                if _pexels_key:
                    print("  Fetching industry photos from Pexels...")
                    images = get_pexels_images(business_type, _pexels_key)
                else:
                    images = get_placeholder_images(business_type)
            except Exception as e:
                print(f"Image fetching failed: {e}")
                images = get_placeholder_images(business_type)

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
