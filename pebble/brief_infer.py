"""Fast heuristic infer from a short user prompt — pre-fills confirm UI only.

No LLM, no expanded narrative. See brief_compose for hidden merge after confirm.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from pebble.text import sanitize_business_name

_INDUSTRY_HINTS: list[tuple[str, str]] = [
    ("bakery", "bakery"), ("restaurant", "restaurant"), ("coffee", "cafe"), ("cafe", "cafe"),
    ("dentist", "dentist"), ("yoga", "yoga_studio"), ("plumb", "plumbing"), ("hvac", "hvac"),
    ("lawyer", "law_firm"), ("attorney", "law_firm"), ("real estate", "real_estate"),
    ("photo", "photography"), ("therapist", "therapist"), ("salon", "hair_salon"),
    ("barber", "barbershop"), ("spa", "spa"), ("fitness", "gym"), ("gym", "gym"),
    ("pet", "pet_grooming"), ("clean", "cleaning_service"), ("landscap", "landscaping"),
    ("construct", "construction"), ("consult", "consultant"), ("agency", "agency"),
    ("jewel", "jeweler"), ("car", "auto_repair"), ("auto", "auto_repair"),
    ("pest", "pest_control"),
]

_LOCATION_RE = re.compile(
    r"\b(?:in|near|around|based in|located in)\s+"
    r"([A-Z][a-zA-Z\s.'-]{1,48}(?:,\s*[A-Z]{2})?)",
    re.I,
)
_PHONE_RE = re.compile(
    r"(\+?\d{1,2}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
)


def _guess_industry(text: str) -> str:
    lower = text.lower()
    for needle, key in _INDUSTRY_HINTS:
        if needle in lower:
            return key
    return "small_business"


def _derive_name(raw: str) -> str:
    if not raw or not raw.strip():
        return "New project"
    first = re.split(r"[.!?]", raw.strip(), maxsplit=1)[0].strip()
    capped = first[:60].strip() if len(first) > 60 else first
    name = sanitize_business_name(capped) or "New project"
    name = re.sub(r"^(I\s+(?:own|run|have|started)\s+(?:a|an|the)\s+)", "", name, flags=re.I).strip()
    return name or "New project"


def _extract_location(text: str) -> Optional[str]:
    m = _LOCATION_RE.search(text)
    if m:
        return m.group(1).strip().rstrip(".")
    return None


def _extract_phone(text: str) -> Optional[str]:
    m = _PHONE_RE.search(text)
    return m.group(0).strip() if m else None


def infer_brief(raw_prompt: str, *, intent: str = "business") -> dict[str, Any]:
    """Return structured pre-fill fields for the confirm screen."""
    raw = (raw_prompt or "").strip()
    if not raw:
        return {"ok": False, "error": "raw_prompt required"}

    industry_guess = _guess_industry(raw)
    business_type = industry_guess
    industry_key = industry_guess

    try:
        from pebble.industry import resolve_industry_intel
        key, intel = resolve_industry_intel(industry_guess)
        if intel and key:
            industry_key = key
            business_type = key
    except Exception:
        pass

    chips: Optional[dict] = None
    try:
        from pebble.server.smart_defaults import _try_industries_json
        chips = _try_industries_json(industry_key, business_type)
    except Exception:
        chips = None

    if not chips:
        chips = {
            "audience": ["locals"],
            "site_functions": ["presence", "leads"],
            "brand_tone": "professional",
            "source": "fallback",
            "fallback": True,
        }

    return {
        "ok": True,
        "business_name": _derive_name(raw),
        "business_type": business_type,
        "industry_key": industry_key,
        "location": _extract_location(raw) or "",
        "phone": _extract_phone(raw) or "",
        "audience": chips.get("audience") or ["locals"],
        "site_functions": chips.get("site_functions") or ["presence", "leads"],
        "brand_tone": chips.get("brand_tone") or "professional",
        "intent": intent if intent in ("business", "project") else "business",
        "source": chips.get("source", "heuristic"),
    }
