"""Seed-brief library — gold-standard reference briefs per industry.

NLM's adversarial review of the search-API proposal surfaced this as the
highest-leverage move for first-build accuracy: a hand-curated library
of idealized briefs per top industry that the LLM sees as context for
"here's how a great brief in this industry reads." NOT user-facing copy
— these are anchors for tone, specificity level, and industry-appropriate
language patterns.

Loaded from `pebble/seed_briefs.json` (kept as JSON so non-engineers can
edit copy without touching Python).

Usage:
    from pebble.seed_briefs import get_seed_brief, build_seed_brief_block
    seed = get_seed_brief("plumbing")
    if seed:
        block = build_seed_brief_block(seed, industry_key="plumbing")
        prompt = creative_block + layout_block + style_block + block + lang_prefix + template
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


_PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SEED_BRIEFS_PATH = _PROJECT_ROOT / "pebble" / "seed_briefs.json"

# Cache the parsed JSON — loaded once per process. Tests can clear it
# via `_clear_cache()` if they want to test the load path.
_CACHE: Optional[dict] = None


def _load() -> dict:
    """Load seed_briefs.json once and cache. Returns {} if missing/malformed
    so the caller always sees a usable dict and never crashes the build."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not SEED_BRIEFS_PATH.exists():
        _CACHE = {}
        return _CACHE
    try:
        data = json.loads(SEED_BRIEFS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        _CACHE = {}
        return _CACHE
    # Strip the _meta key so callers iterating .items() never see it
    # as a candidate industry.
    if isinstance(data, dict):
        _CACHE = {k: v for k, v in data.items() if not k.startswith("_")}
    else:
        _CACHE = {}
    return _CACHE


def _clear_cache() -> None:
    """Test-only — force the next _load() to re-read from disk."""
    global _CACHE
    _CACHE = None


def get_seed_brief(industry_key: Optional[str]) -> Optional[dict]:
    """Return the seed brief for an industry, or None.

    ``industry_key`` should be the same key produced by
    `pebble.industry.lookup_industry_intel()` — e.g. ``"plumbing"``,
    ``"wedding_photography"``. Match is exact; no fuzzy fallback (the
    industry layer already does the fuzzy resolution).
    """
    if not industry_key:
        return None
    return _load().get(industry_key)


def list_seeded_industries() -> list[str]:
    """Return the list of industry keys with a seed brief, for diagnostics."""
    return sorted(_load().keys())


def build_seed_brief_block(seed: dict, industry_key: str = "") -> str:
    """Render a seed brief as a context block for the build prompt.

    The block frames the seed as a REFERENCE, not a template to copy.
    The LLM is instructed to match the level of specificity + tone, but
    NOT to lift the actual business name / services / addresses.
    """
    if not seed:
        return ""

    industry_label = (industry_key or "this industry").replace("_", " ")

    parts = [
        f"# REFERENCE: how a great brief for a {industry_label} business reads",
        "",
        "Below is a hand-crafted reference brief for the user's industry. "
        "It captures the voice, specificity level, trust-signal vocabulary, "
        "and CTA hierarchy that converts in this niche. Use it as a tone "
        "and structure ANCHOR — match this level of specificity in the "
        "user's site. DO NOT copy the reference business name, addresses, "
        "or any literal text from it. The user's actual brief (below) "
        "is authoritative for facts; the reference is authoritative for STYLE.",
        "",
    ]

    field_order = [
        ("business_name", "Business name"),
        ("business_type", "Business type"),
        ("audience", "Audience"),
        ("services_offered", "Services offered"),
        ("brand_position", "Brand position"),
        ("brand_tone", "Brand tone"),
        ("trust_signals", "Trust signals"),
        ("copy_voice_notes", "Copy voice notes"),
        ("cta_hierarchy", "CTA hierarchy"),
    ]
    for key, label in field_order:
        val = seed.get(key)
        if val:
            parts.append(f"**{label}:** {val}")
            parts.append("")

    parts.append("# END REFERENCE — the user's actual brief follows.")
    parts.append("")

    return "\n".join(parts)


__all__ = [
    "get_seed_brief",
    "list_seeded_industries",
    "build_seed_brief_block",
    "SEED_BRIEFS_PATH",
]
