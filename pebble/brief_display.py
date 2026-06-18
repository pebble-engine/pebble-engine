"""Short display names for confirm/plan UI and brief composition.

Pure helpers — no I/O. Keeps meta-prompts like "build a website for…"
from becoming the visible business name.
"""
from __future__ import annotations

import re

from pebble.text import sanitize_business_name

_MAX_WORDS = 4
_MAX_CHARS = 40

_META_PREFIXES = (
    r"build\s+(?:a|me|us)?\s*(?:website|site|web\s*site|page)\s+(?:for\s+)?",
    r"(?:i\s+)?need\s+(?:a|an)\s+(?:website|site)\s+(?:for\s+)?",
    r"create\s+(?:a|me)\s+(?:website|site)\s+(?:for\s+)?",
    r"make\s+(?:a|me)\s+(?:website|site)\s+(?:for\s+)?",
)

_META_NAME_MARKERS = (
    "build a website",
    "build a site",
    "need a website",
    "need a site",
    "called alpine",  # truncated meta tails
    "it's called",
    "its called",
    "website for my",
    "site for my",
)

_GENERIC_BUSINESS = re.compile(r"^my\s+(\w+)\s+business$", re.I)
_INDUSTRY_ONLY = re.compile(r"^(?:(?:a|an|the)\s+)?(\w+)\s+business$", re.I)

_CALLED_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?:called|named)\s+[\"']([^\"']{2,60})[\"']", re.I),
    re.compile(
        r"(?:it'?s|its|is)\s+called\s+([A-Za-z0-9][\w\s&'.-]{1,58}?)"
        r"(?:\s*[,.\-–—]|$)",
        re.I,
    ),
    re.compile(r"(?:called|named)\s+([A-Za-z0-9][\w\s&'.-]{1,58}?)(?:\s*[,.\-–—]|$)", re.I),
    re.compile(r"my\s+(?:business|shop|store|company)\s+is\s+([A-Za-z0-9][\w\s&'.-]{1,58})", re.I),
)
_OWN_PREFIX = re.compile(
    r"^I\s+(?:own|run|have|started)\s+(?:a|an|the)\s+",
    re.I,
)

_LOCATION_KIND = re.compile(
    r"^(?:(?:a|an|the)\s+)?(\w+)\s+in\s+([A-Z][a-zA-Z\s.'-]{1,40})$",
    re.I,
)


def industry_label(industry_key: str) -> str:
    """Human-readable industry label from a key like ``hair_salon``."""
    key = (industry_key or "").strip().replace("-", "_")
    if not key or key == "small_business":
        return "Business"
    return " ".join(w.capitalize() for w in key.split("_"))


def _cap_words(text: str) -> str:
    cleaned = sanitize_business_name(text.strip())
    if not cleaned:
        return ""
    words = cleaned.split()
    if len(words) > _MAX_WORDS:
        words = words[:_MAX_WORDS]
    out = " ".join(words)
    if len(out) > _MAX_CHARS:
        out = out[:_MAX_CHARS].rsplit(" ", 1)[0].strip()
    return out or ""


def looks_like_meta_name(name: str) -> bool:
    """True when ``name`` reads like a prompt fragment, not a business name."""
    if not name or not name.strip():
        return True
    lower = name.lower().strip()
    if len(lower) > _MAX_CHARS:
        return True
    if any(marker in lower for marker in _META_NAME_MARKERS):
        return True
    if _GENERIC_BUSINESS.match(lower) or _INDUSTRY_ONLY.match(lower):
        return True
    if lower.endswith(" business") and len(lower.split()) <= 4:
        return True
    for prefix in _META_PREFIXES:
        if re.match(prefix, lower, re.I):
            return True
    return False


def extract_business_name(raw_prompt: str) -> str:
    """Pull a short business name from a free-text prompt."""
    raw = (raw_prompt or "").strip()
    if not raw:
        return ""

    for pat in _CALLED_PATTERNS:
        m = pat.search(raw)
        if m:
            candidate = _cap_words(m.group(1))
            if candidate and not looks_like_meta_name(candidate):
                return candidate

    first = re.split(r"[.!?]", raw, maxsplit=1)[0].strip()
    stripped = first
    for prefix in _META_PREFIXES:
        stripped = re.sub(rf"^{prefix}", "", stripped, flags=re.I).strip()
    stripped = _OWN_PREFIX.sub("", stripped).strip()

    if _GENERIC_BUSINESS.match(stripped) or _INDUSTRY_ONLY.match(stripped):
        return ""

    m = _LOCATION_KIND.match(stripped)
    if m:
        kind, loc = m.group(1), m.group(2).strip().rstrip(".")
        candidate = _cap_words(f"{loc} {kind}")
        if candidate:
            return candidate

    candidate = _cap_words(stripped)
    if candidate and not looks_like_meta_name(candidate):
        return candidate
    return ""


def display_name(
    business_name: str,
    business_type: str,
    raw_prompt: str = "",
) -> str:
    """Best short label for UI — never the full raw prompt."""
    name = (business_name or "").strip()
    raw = (raw_prompt or "").strip()
    btype = (business_type or "").strip()

    if name and not looks_like_meta_name(name):
        return _cap_words(name) or industry_label(btype)

    extracted = extract_business_name(raw) if raw else ""
    if extracted:
        return extracted

    if name:
        short = _cap_words(name)
        if short and not looks_like_meta_name(short):
            return short

    return industry_label(btype)
