"""Hidden brief composition — merges raw prompt + confirmed fields for build LLM."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

from pebble.brief_display import display_name

_AUDIENCE_LABELS = {
    "locals": "local customers", "travelers": "travelers", "professionals": "professionals",
    "families": "families", "enthusiasts": "enthusiasts", "patients": "patients",
    "students": "students", "members": "members", "pet_owners": "pet owners", "other": "customers",
}
_FUNCTION_LABELS = {
    "presence": "learn about the business", "leads": "get in touch or request a quote",
    "booking": "book an appointment", "ecommerce": "browse and buy products",
    "portfolio": "view past work", "payment": "pay or donate online",
}
_TONE_LABELS = {
    "warm": "warm and welcoming", "professional": "professional and trustworthy",
    "bold": "bold and confident", "calm": "calm and considered",
    "playful": "playful and friendly", "premium": "premium and refined",
}

_COMPOSE_MAX_TOKENS = 350


def _template_compose(data: dict[str, Any]) -> str:
    raw = (data.get("_raw_prompt") or "").strip()
    name = display_name(
        str(data.get("business_name") or ""),
        str(data.get("business_type") or ""),
        raw,
    ) or "the business"
    btype = (data.get("business_type") or "small business").replace("_", " ")
    loc = (data.get("location") or "").strip()
    audience = data.get("audience") or ["locals"]
    funcs = data.get("site_functions") or ["presence", "leads"]
    tone = data.get("brand_tone") or "professional"

    aud = ", ".join(_AUDIENCE_LABELS.get(a, a) for a in audience[:2])
    goals = ", ".join(_FUNCTION_LABELS.get(f, f) for f in funcs[:3])
    tone_phrase = _TONE_LABELS.get(tone, tone)

    parts = [f"Build a marketing website for {name}, a {btype}."]
    if loc:
        parts.append(f"They serve {loc} and nearby areas.")
    parts.append(f"Primary visitors are {aud}; the site should help them {goals}.")
    parts.append(f"Voice and feel: {tone_phrase}.")
    if raw:
        parts.append(f"Owner's words: {raw}")
    return " ".join(parts)


def _try_llm_compose(data: dict[str, Any]) -> Optional[str]:
    try:
        from pebble.llm import get_llm_client
        client, reason = get_llm_client()
        if not client or reason != "ok":
            return None
    except Exception:
        return None

    prompt = (
        "Write 2-3 sentences describing a small-business website to build. "
        "Use ONLY the facts given. No markdown.\n\n"
        f"Facts JSON:\n{json.dumps(data, ensure_ascii=False)}\n"
    )
    try:
        text = client.generate(
            system="You expand brief facts into clear build instructions. Output prose only.",
            user=prompt,
            max_tokens=_COMPOSE_MAX_TOKENS,
        )
        text = (text or "").strip()
        return text if len(text) > 40 else None
    except Exception:
        return None


def compose_brief(fields: dict[str, Any]) -> dict[str, Any]:
    raw = (fields.get("_raw_prompt") or fields.get("raw_prompt") or "").strip()
    if not raw and not fields.get("business_name"):
        return {"ok": False, "error": "insufficient input"}

    data = {
        "_raw_prompt": raw,
        "business_name": fields.get("business_name") or "",
        "business_type": fields.get("business_type") or fields.get("industry") or "",
        "location": fields.get("location") or "",
        "phone": fields.get("phone") or "",
        "audience": fields.get("audience") if isinstance(fields.get("audience"), list) else [],
        "site_functions": fields.get("site_functions") if isinstance(fields.get("site_functions"), list) else [],
        "brand_tone": fields.get("brand_tone") or "",
        "intent": fields.get("intent") or "business",
    }

    narrative = _template_compose(data)
    source = "template"
    if len(raw) < 40 and len(narrative) < 120:
        llm_text = _try_llm_compose(data)
        if llm_text:
            narrative = llm_text
            source = "llm"

    patch: dict[str, Any] = {
        "business_name": data["business_name"],
        "business_type": data["business_type"],
        "extra_context": narrative,
        "_raw_prompt": raw,
        "_composed": True,
        "_composed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if data["location"]:
        patch["location"] = data["location"]
    if data["phone"]:
        patch["phone"] = data["phone"]
    if data["audience"]:
        patch["audience"] = data["audience"]
    if data["site_functions"]:
        patch["site_functions"] = data["site_functions"]
    if data["brand_tone"]:
        patch["brand_tone"] = data["brand_tone"]
    if data["intent"]:
        patch["intent"] = data["intent"]

    return {"ok": True, "brief_patch": patch, "compose_source": source}
