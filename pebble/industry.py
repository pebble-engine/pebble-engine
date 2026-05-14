"""Industry intelligence layer.

Two-tier system:
- Layer 1: `industries.json` — curated 52-entry database with palette, hero type,
  Three.js variant, copy tone, section order, trust signals, avoid list.
- Layer 2: LLM fallback — if a business type isn't in the JSON, the engine asks
  Claude/Gemini for a structured entry, validates the shape, and caches it
  back to `industries.json` so the next build hits Layer 1.

Also exposes the markdown-research helper (`research_industry`) that writes a
short data-driven analysis of an industry into the prompt. Cached per industry
under `output/research_cache/<slug>.md`.

Both functions use `get_llm_client()` lazily — never at import time — so the
package imports cleanly even when no API key is configured.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Optional

from pebble.llm import get_llm_client
from pebble.log import log


# ---- Paths --------------------------------------------------------------

# Resolved against the project root (the directory containing pebble_engine.py).
_PROJECT_ROOT = Path(__file__).parent.parent.resolve()
INDUSTRIES_JSON    = _PROJECT_ROOT / "industries.json"
RESEARCH_CACHE_DIR = _PROJECT_ROOT / "output" / "research_cache"


# ---- LLM prompt templates -----------------------------------------------

# Used by research_new_industry() — produces a JSON entry for industries.json.
INDUSTRY_RESEARCH_JSON_PROMPT = """You are a web design researcher. Output a single JSON object for the "{industry}" industry that matches this exact schema (no commentary, no markdown fences, no preamble):

{{
  "emotion": "2-4 emotional drivers customers feel (e.g. 'safety, relief, trust')",
  "visual_style": "one short phrase describing the visual aesthetic (e.g. 'dark cinematic, photo-forward')",
  "hero_type": "one of: video | image",
  "video_keyword": "2-6 word Pexels search query for a relevant looping hero video",
  "threejs_type": "one of: none | particles | aurora_mesh | wireframe_geometry | ripple_plane",
  "colors": {{
    "primary": "#RRGGBB hex (brand-ownable, not a generic blue)",
    "accent": "#RRGGBB hex (CTA color)",
    "background": "#RRGGBB hex (page background)"
  }},
  "tone": "2-4 adjective tone (e.g. 'urgent, reassuring, local')",
  "key_sections": ["array of 4-6 section keys in homepage order"],
  "trust_signals": ["array of 3-6 trust signals that work in this industry"],
  "avoid": ["array of 3-5 patterns to never use (must include 'horizontal_scroll')"]
}}

Rules:
- Choose colors that fit the industry psychology — not random tasteful values.
- hero_type is "video" if real-world footage drives the emotion; "image" if minimal editorial is the move.
- threejs_type is "none" unless the industry is abstract/tech/wellness/clean — never decorative.
- "avoid" MUST include "horizontal_scroll" as the first entry.
- Output JSON only. First character must be `{{`. No trailing commentary."""


# Used by research_industry() — produces a markdown analysis block for the PROMPT.
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


# ---- JSON load + normalization -----------------------------------------

def _load_industries_intel() -> dict:
    if not INDUSTRIES_JSON.exists():
        return {}
    try:
        return json.loads(INDUSTRIES_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        log.warning("industries.json load failed: %s", e)
        return {}


def _industry_key(text: str) -> str:
    """Normalize 'Pest Control' / 'pest-control' / 'pest_control' to 'pest_control'."""
    text = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return text or "untitled"


# Local copy of _slugify (also defined in pebble_engine for back-compat).
# Could be shared via a utils module later — for now duplicate keeps deps minimal.
def _slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-") or "untitled"


# ---- Lookup + LLM fallback ---------------------------------------------

def lookup_industry_intel(business_type: str) -> tuple[Optional[str], Optional[dict]]:
    """Find a matching industry entry. Returns (matched_key, entry) or (None, None).

    Match priority: exact key → fuzzy substring → partial word overlap.
    """
    intel = _load_industries_intel()
    if not intel:
        return None, None

    key = _industry_key(business_type)
    if key in intel:
        return key, intel[key]

    # Fuzzy substring — either direction
    bt_lower = business_type.lower()
    for industry_key, entry in intel.items():
        ik_words = industry_key.replace("_", " ")
        if ik_words in bt_lower or any(w in bt_lower for w in ik_words.split() if len(w) > 3):
            return industry_key, entry
        if any(w in ik_words for w in bt_lower.split() if len(w) > 3):
            return industry_key, entry

    return None, None


def research_new_industry(business_type: str) -> Optional[dict]:
    """LLM fallback for industries not in industries.json. Returns a structured
    entry and writes it back into industries.json so the next build is instant."""
    client, reason = get_llm_client()
    if not client or reason != "ok":
        return None

    prompt = INDUSTRY_RESEARCH_JSON_PROMPT.format(industry=business_type)
    system = (
        "You are an industry research engine. You output ONLY a single JSON object "
        "matching the schema in the user message. No prose. No fences. No preamble."
    )
    try:
        raw = client.generate(system=system, user=prompt, max_tokens=1200)
    except Exception as e:
        log.warning("industry intel research failed: %s", e)
        return None

    # Strip possible markdown fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```\s*$", "", raw)
    # Take from first { to last } to handle trailing whitespace / commentary
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        log.warning("industry intel: LLM did not return JSON")
        return None
    try:
        entry = json.loads(raw[start : end + 1])
    except Exception as e:
        log.warning("industry intel: JSON parse failed: %s", e)
        return None

    # Validate minimum shape
    required = {"emotion", "visual_style", "hero_type", "video_keyword",
                "threejs_type", "colors", "tone", "key_sections",
                "trust_signals", "avoid"}
    if not required.issubset(entry.keys()):
        log.warning("industry intel: missing required keys")
        return None

    # Cache back to industries.json
    try:
        intel = _load_industries_intel()
        intel[_industry_key(business_type)] = entry
        INDUSTRIES_JSON.write_text(
            json.dumps(intel, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        log.info("industry intel: cached new entry for '%s'", business_type)
    except Exception as e:
        log.warning("industry intel: cache write failed: %s", e)

    return entry


def resolve_industry_intel(business_type: str) -> tuple[Optional[str], Optional[dict]]:
    """One-call API: look up, fall back to LLM, return (key, entry) or (None, None)."""
    if not business_type:
        return None, None
    matched_key, entry = lookup_industry_intel(business_type)
    if entry:
        return matched_key, entry
    # Fallback: research and cache
    log.info("industry intel: '%s' not in JSON, researching...", business_type)
    entry = research_new_industry(business_type)
    if entry:
        return _industry_key(business_type), entry
    return None, None


# ---- Markdown research (for the prompt's "Industry Research" block) ----

def research_industry(business_type: str, industry_category: str = "") -> str:
    """Research an industry via LLM and return a markdown analysis block.

    Cached per business_type slug under output/research_cache/<slug>.md so
    subsequent builds for the same industry are instant.

    Returns the markdown string, or "" if research is unavailable (no LLM,
    no key, or the call failed).
    """
    industry_slug = _slugify(business_type)
    cache_file = RESEARCH_CACHE_DIR / f"{industry_slug}.md"

    # Cache hit?
    if cache_file.exists():
        try:
            cached = cache_file.read_text(encoding="utf-8")
            if cached and len(cached) > 100:
                return cached
        except Exception:
            pass

    client, reason = get_llm_client()
    if not client or reason != "ok":
        return ""

    research_prompt = RESEARCH_PROMPT_TEMPLATE.format(industry=business_type)
    try:
        result = client.generate(
            system=(
                "You are an expert web design researcher. You analyze successful websites "
                "and extract data-driven design patterns. You provide specific, actionable "
                "recommendations based on what actually converts in each industry."
            ),
            user=research_prompt,
            max_tokens=2000,
        )
        if not result or len(result) < 100:
            return ""
        RESEARCH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(result, encoding="utf-8")
        return result
    except Exception as e:
        log.warning("Industry research failed: %s", e)
        return ""


# ---- Prompt block formatter --------------------------------------------

def build_industry_intel_block(business_type: str, entry: Optional[dict]) -> str:
    """Format an industry intelligence entry as a markdown prompt block."""
    if not entry:
        return "*(No industry intelligence available — Business Intelligence skill governs.)*"

    colors = entry.get("colors", {}) or {}
    key_sections = entry.get("key_sections", []) or []
    trust_signals = entry.get("trust_signals", []) or []
    avoid = entry.get("avoid", []) or []

    return f"""**Industry:** `{business_type}`

This entry was sourced from `industries.json` (or researched + cached on first use). Apply every value below verbatim — they are the design DNA of this industry. The Resolved Design Contract derives from these values, not the other way around.

| Decision | Value |
|---|---|
| **Emotional drivers** | {entry.get("emotion", "")} |
| **Visual style** | {entry.get("visual_style", "")} |
| **Hero type** | `{entry.get("hero_type", "")}` |
| **Pexels video keyword** | `{entry.get("video_keyword", "")}` |
| **Three.js hero variant** | `{entry.get("threejs_type", "none")}` |
| **Primary color** | `{colors.get("primary", "")}` |
| **Accent color** | `{colors.get("accent", "")}` |
| **Background color** | `{colors.get("background", "")}` |
| **Copy tone** | {entry.get("tone", "")} |

**Required homepage sections (in this exact order):**
{chr(10).join(f"- {s}" for s in key_sections)}

**Industry trust signals to surface:**
{chr(10).join(f"- {s}" for s in trust_signals)}

**Never do — automatic build failures:**
{chr(10).join(f"- {a}" for a in avoid)}"""


__all__ = [
    "INDUSTRIES_JSON",
    "RESEARCH_CACHE_DIR",
    "INDUSTRY_RESEARCH_JSON_PROMPT",
    "RESEARCH_PROMPT_TEMPLATE",
    "lookup_industry_intel",
    "research_new_industry",
    "resolve_industry_intel",
    "research_industry",
    "build_industry_intel_block",
    "_industry_key",
    "_load_industries_intel",
]
