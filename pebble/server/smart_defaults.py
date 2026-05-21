"""Smart-defaults endpoint — Phase 39a (2026-05-21).

POST /api/smart-defaults
Body: { industry?: str, business_type?: str, business_name?: str }
Returns: {
  audience:       list[str],            # subset of: locals, travelers, professionals, families, enthusiasts, other
  site_functions: list[str],            # subset of: presence, leads, booking, ecommerce, portfolio, payment
  brand_tone:     str,                  # one of: warm, professional, bold, calm, playful, premium
  source:         "industries_json" | "llm" | "fallback",
  fallback:       bool,                 # true when LLM call failed; UI may de-emphasize
}

The endpoint exists to collapse the 3-step v3 questionnaire (audience →
site_functions → brand_tone) when the user already provided an industry
via URL extraction or by typing it directly. Instead of asking the user
3 chip questions, we infer their answers and let them confirm.

Two-tier strategy:
  Tier 1 — industries.json hints
    For the 50+ curated industries, industries.json already has tone +
    section ordering. We translate those hints into chip IDs that match
    the v3 idea-phase taxonomy.
  Tier 2 — gpt-4o-mini fallback
    For arbitrary industries (anything not in industries.json), call the
    cheap chat model with the chip taxonomy and ask it to pick.

Cost: ~$0.0001 per call via gpt-4o-mini on OpenRouter when Tier 2 fires.
Tier 1 is free. Public endpoint, rate-limited via plan_limiter.

Failure mode: if both tiers fail, return a safe "presence/leads/professional"
default with fallback=true so the UI can degrade gracefully — the user
still has the option to fill in the questionnaire by hand.
"""
from __future__ import annotations

import json
import re
from typing import Any, Optional

from pebble.log import log
from pebble.security import client_ip, plan_limiter


# ---------------------------------------------------------------------------
# Allowed chip ids — must match ui/v3/components/phases/idea-phase.tsx
# ---------------------------------------------------------------------------

VALID_AUDIENCE       = {
    "locals", "travelers", "professionals", "families", "enthusiasts",
    # Phase 39c (2026-05-21) — Marc's feedback after the Bon Appétit
    # build defaulted to "other": every industry HAS an audience. These
    # four new chips knock out the most common "other" cases:
    "patients",   # healthcare, dental, pediatric, therapy, hospice, vet
    "students",   # tutors, coaches, online educators, schools
    "members",    # gyms, clubs, churches, nonprofits, fraternal orgs
    "pet_owners", # vets, groomers, pet daycare, pet supply stores
    "other",
}
VALID_SITE_FUNCTIONS = {"presence", "leads", "booking", "ecommerce", "portfolio", "payment"}
VALID_BRAND_TONE     = {"warm", "professional", "bold", "calm", "playful", "premium"}

# Last-resort defaults if every layer fails — neutral choices that work
# for the broadest range of small businesses without misleading anyone.
SAFE_FALLBACK = {
    "audience":       ["locals"],
    "site_functions": ["presence", "leads"],
    "brand_tone":     "professional",
    "source":         "fallback",
    "fallback":       True,
}


# Cheap chat model, identical to pebble.server.bot_message.
SMART_DEFAULTS_MODEL = "openai/gpt-4o-mini"
SMART_DEFAULTS_MAX_TOKENS = 200


# ---------------------------------------------------------------------------
# Tier 1: industries.json hints → chip ids
# ---------------------------------------------------------------------------
#
# industries.json doesn't store these chip ids directly, but the tone +
# trust_signals + section keywords are good enough to derive an audience
# pick and tone with high confidence for the curated entries. Site functions
# are inferred from sections (book/booking → booking; gallery/portfolio →
# portfolio; pricing/services → leads + presence; cart/shop → ecommerce).


# Tone phrases → brand_tone chip id. industries.json tones are 2-4 adjectives
# like "warm, professional, local"; we pick the most distinctive single tag.
_TONE_PRIORITY = [
    ("playful",      ["playful", "fun", "whimsical", "quirky", "energetic"]),
    ("bold",         ["bold", "confident", "dramatic", "cinematic", "loud"]),
    ("premium",      ["premium", "luxury", "high-end", "elevated", "refined"]),
    ("warm",         ["warm", "welcoming", "intimate", "cozy", "homey", "local"]),
    ("calm",         ["calm", "quiet", "minimal", "serene", "considered", "editorial"]),
    ("professional", ["professional", "authoritative", "credible", "polished", "formal"]),
]


def _tone_from_industry_intel(tone_str: str) -> Optional[str]:
    if not tone_str:
        return None
    lowered = tone_str.lower()
    for chip_id, hints in _TONE_PRIORITY:
        for hint in hints:
            if hint in lowered:
                return chip_id
    return None


# Section keyword → site_function chip id.
_SECTION_TO_FUNCTION = [
    ("ecommerce",  ["cart", "shop", "store", "product", "checkout", "ecommerce", "e-commerce", "merch"]),
    ("booking",    ["book", "booking", "appointment", "reserve", "schedule", "calendar"]),
    ("portfolio",  ["gallery", "portfolio", "work", "case study", "case-study", "projects"]),
    ("payment",    ["donate", "donation", "pay", "tip", "subscribe", "membership"]),
    ("leads",      ["contact", "lead", "inquiry", "quote", "estimate", "consultation"]),
    ("presence",   ["about", "story", "service", "services", "menu", "team", "hero"]),
]


def _site_functions_from_industry_intel(sections: list) -> list[str]:
    """Map industries.json `key_sections` keywords to chip ids. Deduped,
    preserves order of first appearance, never exceeds 4 picks."""
    if not isinstance(sections, list):
        return []
    sections_lower = [str(s).lower() for s in sections]
    picked: list[str] = []
    for chip_id, hints in _SECTION_TO_FUNCTION:
        for section in sections_lower:
            if any(h in section for h in hints):
                if chip_id not in picked:
                    picked.append(chip_id)
                break
        if len(picked) >= 4:
            break
    # Always include "presence" + "leads" if nothing matched, since
    # almost every business website has these.
    if not picked:
        picked = ["presence", "leads"]
    return picked


# Audience picks per common industry category keyword. Order matters —
# more specific categories first so e.g. "pediatric dental" routes to
# "patients" (medical specificity) over "families" (general).
# Defaults to "locals" (the most generic small-biz audience).
_AUDIENCE_BY_KEYWORD = [
    # Phase 39c — new specific audience chips ordered before more general ones
    ("pet_owners",    ["vet", "veterinarian", "veterinary", "groomer", "groom", "pet daycare", "pet_daycare", "pet supply", "pet_supply", "kennel", "boarding", "dog walk"]),
    ("patients",      ["medical", "doctor", "physician", "dentist", "dental", "orthodontic", "pediatric", "therapy", "therapist", "chiropract", "physio", "psychology", "psychiatr", "hospice", "clinic", "hospital", "urgent care", "dermatol"]),
    ("students",      ["tutor", "tutoring", "coach", "coaching", "online educator", "online course", "school", "academy", "instructor", "instruction", "lesson", "training", "bootcamp", "music teacher", "language teach"]),
    ("members",       ["church", "synagogue", "mosque", "temple", "congregation", "nonprofit", "non-profit", "charity", "foundation", "fraternal", "club", "membership", "co-op", "cooperative", "guild", "association"]),
    # Existing chips
    ("families",      ["daycare", "kid", "child", "family", "school", "tutor"]),
    ("professionals", ["law", "legal", "attorney", "account", "consult", "advisor", "agency", "b2b", "saas"]),
    ("travelers",     ["hotel", "resort", "travel", "tourism", "tour", "airbnb", "vacation", "rental"]),
    ("enthusiasts",   ["enthusiast", "gym", "fitness", "yoga", "climbing", "music", "guitar", "art", "craft", "tattoo", "photo"]),
    ("locals",        ["bakery", "café", "cafe", "coffee", "restaurant", "salon", "barber", "plumb", "electric", "hvac", "garage", "landscap"]),
]


def _audience_from_industry(industry_key: str, intel: dict) -> list[str]:
    """Map industry key + intel to audience chip ids. Returns 1-2 picks
    by default."""
    haystack = " ".join([
        str(industry_key or "").lower(),
        str(intel.get("emotion", "")).lower(),
        " ".join(str(s) for s in (intel.get("key_sections") or [])).lower(),
    ])
    for chip_id, hints in _AUDIENCE_BY_KEYWORD:
        if any(h in haystack for h in hints):
            return [chip_id]
    # Default — most small-business sites talk to locals first.
    return ["locals"]


def _try_industries_json(industry: str, business_type: str) -> Optional[dict]:
    """Look up the industry in industries.json and translate hints into
    chip ids. Returns None if no match (caller falls back to LLM)."""
    try:
        from pebble.industry import resolve_industry_intel
    except Exception:
        return None

    candidates = [s.strip().lower() for s in (industry, business_type) if isinstance(s, str) and s.strip()]
    if not candidates:
        return None

    intel: Optional[dict] = None
    matched_key: str = ""
    for cand in candidates:
        try:
            key, found = resolve_industry_intel(cand)
        except Exception:
            continue
        if found and isinstance(found, dict):
            intel = found
            matched_key = key or cand
            break

    if intel is None:
        return None

    tone = _tone_from_industry_intel(intel.get("tone", "")) or "professional"
    sections = intel.get("key_sections") or []
    site_funcs = _site_functions_from_industry_intel(sections)
    audience = _audience_from_industry(matched_key, intel)

    return {
        "audience":       audience,
        "site_functions": site_funcs,
        "brand_tone":     tone,
        "source":         "industries_json",
        "fallback":       False,
    }


# ---------------------------------------------------------------------------
# Tier 2: gpt-4o-mini fallback
# ---------------------------------------------------------------------------


_LLM_PROMPT = """You map a business industry to the audience it serves, the things
its website needs to let visitors do, and the brand tone it should have.
Output ONLY a JSON object — first character must be `{{`, no commentary,
no markdown fences.

Industry: {industry}
Business type: {business_type}
Business name: {business_name}

Output schema (you MUST pick from these enumerations — never invent new ids):

{{
  "audience": ["locals" | "travelers" | "professionals" | "families" | "enthusiasts" | "patients" | "students" | "members" | "pet_owners" | "other"],
  "site_functions": ["presence" | "leads" | "booking" | "ecommerce" | "portfolio" | "payment"],
  "brand_tone": "warm" | "professional" | "bold" | "calm" | "playful" | "premium"
}}

Rules:
- audience: 1-2 picks. Pick what FITS — be specific.
    • patients   for medical / dental / therapy / hospice / pediatric / clinics
    • students   for tutors / coaches / online educators / schools / instructors
    • members    for gyms / clubs / churches / nonprofits / fraternal orgs
    • pet_owners for vets / pet groomers / pet daycare / pet supply
    • locals     for neighborhood businesses (bakery / cafe / salon / contractor)
    • travelers  for hotels / resorts / tourism / vacation rentals
    • professionals for B2B / legal / accounting / advisors / agencies
    • families   for daycare / kid-focused services (not medical — that's patients)
    • enthusiasts for fitness / photography / art / music / hobby specialists
    • other      ONLY as a last resort when no specific chip fits
- site_functions: 2-4 picks. Always include "presence" (every site has
  a story) and "leads" (every site needs contact) unless the industry
  genuinely doesn't (e.g. donation-only nonprofits skip "leads").
  Add "booking" for service industries that take appointments. Add
  "ecommerce" only when the business sells products online. Add
  "portfolio" for creative services (photography, design, agency).
  Add "payment" for donation / tip / subscription flows.
- brand_tone: pick exactly one that fits the industry's emotional
  positioning. Funeral homes are calm. Bakeries are warm. Law firms are
  professional. Custom tattoo studios are bold. Daycares are playful.
  Luxury hotels are premium."""


def _call_llm(industry: str, business_type: str, business_name: str) -> Optional[dict]:
    """Call gpt-4o-mini and parse the response into a chip-ids dict.

    Returns None on any failure — caller falls back to SAFE_FALLBACK.
    """
    import os

    try:
        from pebble.llm import OpenRouterClient
    except Exception:
        return None

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        client = OpenRouterClient(api_key=api_key, model=SMART_DEFAULTS_MODEL)
        raw = client.generate(
            system="You output strict JSON mapping business industries to chip-id taxonomies.",
            user=_LLM_PROMPT.format(
                industry=industry or "(unknown)",
                business_type=business_type or "(unknown)",
                business_name=business_name or "(unknown)",
            ),
            max_tokens=SMART_DEFAULTS_MAX_TOKENS,
        )
        text = raw if isinstance(raw, str) else getattr(raw, "text", "")
    except Exception as e:
        log.warning("[smart-defaults] LLM call failed: %s", e)
        return None

    return _parse_llm_json(text)


def _parse_llm_json(raw: str) -> Optional[dict]:
    """Tolerate code fences + leading prose. Validate ids against the
    enumerations — refuse anything invented."""
    if not raw:
        return None
    text = raw.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    start = text.find("{")
    end   = text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None

    audience       = _whitelist_list(data.get("audience"), VALID_AUDIENCE, default=["locals"])[:2]
    site_functions = _whitelist_list(data.get("site_functions"), VALID_SITE_FUNCTIONS, default=["presence", "leads"])[:4]

    brand_tone_raw = data.get("brand_tone")
    if isinstance(brand_tone_raw, str) and brand_tone_raw.strip().lower() in VALID_BRAND_TONE:
        brand_tone = brand_tone_raw.strip().lower()
    else:
        brand_tone = "professional"

    return {
        "audience":       audience,
        "site_functions": site_functions,
        "brand_tone":     brand_tone,
        "source":         "llm",
        "fallback":       False,
    }


def _whitelist_list(value: Any, allowed: set[str], default: list[str]) -> list[str]:
    if not isinstance(value, list):
        return list(default)
    out: list[str] = []
    for v in value:
        if isinstance(v, str):
            v_clean = v.strip().lower()
            if v_clean in allowed and v_clean not in out:
                out.append(v_clean)
    return out or list(default)


# ---------------------------------------------------------------------------
# HTTP endpoint
# ---------------------------------------------------------------------------


_MAX_BODY_BYTES = 4096


def run_smart_defaults(handler) -> None:
    """POST /api/smart-defaults

    Body: { industry?: str, business_type?: str, business_name?: str }
    """
    ip = client_ip(handler)
    if not plan_limiter.allow(ip or ""):
        handler._json(429, {"error": "too many requests — try again in a moment"})
        return

    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"})
        return
    if length <= 0 or length > _MAX_BODY_BYTES:
        handler._json(400, {"error": "missing or oversized body"})
        return

    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"})
        return

    if not isinstance(body, dict):
        handler._json(400, {"error": "body must be a json object"})
        return

    industry      = (body.get("industry") or "").strip() if isinstance(body.get("industry"), str) else ""
    business_type = (body.get("business_type") or "").strip() if isinstance(body.get("business_type"), str) else ""
    business_name = (body.get("business_name") or "").strip() if isinstance(body.get("business_name"), str) else ""

    if not industry and not business_type:
        handler._json(400, {"error": "industry or business_type is required"})
        return

    # Tier 1: industries.json — free, fast, high confidence
    tier1 = _try_industries_json(industry, business_type)
    if tier1 is not None:
        handler._json(200, tier1)
        return

    # Tier 2: gpt-4o-mini
    tier2 = _call_llm(industry, business_type, business_name)
    if tier2 is not None:
        handler._json(200, tier2)
        return

    # Safe fallback — never 500 on a malformed LLM response or missing key
    handler._json(200, dict(SAFE_FALLBACK))
