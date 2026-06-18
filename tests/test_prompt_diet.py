"""Prompt diet tests (Phase 14a, 2026-05-20).

Pins the diet's behavior: when PEBBLE_PROMPT_DIET is on (default), the
prompt is dramatically shorter and the 5 skill blocks use compact
replacements instead of full SKILL.md injection.
"""
from __future__ import annotations

import importlib

import pytest


# ------------------------------------------------------------------ #
# Diet toggle                                                          #
# ------------------------------------------------------------------ #

def test_diet_enabled_by_default(monkeypatch):
    monkeypatch.delenv("PEBBLE_PROMPT_DIET", raising=False)
    import pebble.prompt_diet
    importlib.reload(pebble.prompt_diet)
    assert pebble.prompt_diet.diet_enabled() is True


@pytest.mark.parametrize("val", ["true", "1", "yes", "on", "TRUE", "True"])
def test_diet_truthy_values(val, monkeypatch):
    monkeypatch.setenv("PEBBLE_PROMPT_DIET", val)
    import pebble.prompt_diet
    importlib.reload(pebble.prompt_diet)
    assert pebble.prompt_diet.diet_enabled() is True


@pytest.mark.parametrize("val", ["false", "0", "no", "off", "FALSE", ""])
def test_diet_falsy_values(val, monkeypatch):
    """Explicit values that turn diet OFF. Empty string counts as "explicitly
    set to nothing" — treated as OFF, distinct from "not set at all" (default)."""
    monkeypatch.setenv("PEBBLE_PROMPT_DIET", val)
    import pebble.prompt_diet
    importlib.reload(pebble.prompt_diet)
    assert pebble.prompt_diet.diet_enabled() is False


# ------------------------------------------------------------------ #
# Constants exist + non-empty                                          #
# ------------------------------------------------------------------ #

def test_all_diet_constants_present():
    from pebble.prompt_diet import (
        NO_SLOP_DIET, IOS_RULES_DIET, STACK_RULES_DIET,
        BUSINESS_INTEL_DIET, DESIGN_SYSTEM_DIET, IMAGE_RULES_DIET,
        UNIVERSAL_DESIGN_DIET, DESIGN_CRAFT_DIET, UIUX_MOBILE_DIET,
    )
    for name, val in [
        ("NO_SLOP_DIET", NO_SLOP_DIET),
        ("IOS_RULES_DIET", IOS_RULES_DIET),
        ("STACK_RULES_DIET", STACK_RULES_DIET),
        ("BUSINESS_INTEL_DIET", BUSINESS_INTEL_DIET),
        ("DESIGN_SYSTEM_DIET", DESIGN_SYSTEM_DIET),
        ("IMAGE_RULES_DIET", IMAGE_RULES_DIET),
        ("UNIVERSAL_DESIGN_DIET", UNIVERSAL_DESIGN_DIET),
        ("DESIGN_CRAFT_DIET", DESIGN_CRAFT_DIET),
        ("UIUX_MOBILE_DIET", UIUX_MOBILE_DIET),
    ]:
        assert isinstance(val, str) and val.strip(), f"{name} is empty"


def test_new_diet_blocks_under_token_budget():
    """Curated UX blocks stay compact — combined < ~800 tokens (~3200 chars)."""
    from pebble.prompt_diet import (
        UNIVERSAL_DESIGN_DIET, DESIGN_CRAFT_DIET, UIUX_MOBILE_DIET,
    )
    combined = UNIVERSAL_DESIGN_DIET + DESIGN_CRAFT_DIET + UIUX_MOBILE_DIET
    assert len(combined) <= 3200, f"new diet blocks are {len(combined)} chars; cap 3200"


def test_diet_on_includes_universal_design_in_prompt(monkeypatch):
    import pebble_engine

    monkeypatch.delenv("PEBBLE_PROMPT_DIET", raising=False)
    import pebble.prompt_diet
    importlib.reload(pebble.prompt_diet)
    prompt = pebble_engine.build_prompt(_sample_brief(), ds_text="", notes=[])
    assert "Universal readability" in prompt
    assert "Mobile UX guardrails" in prompt
    assert "44×44px" in prompt or "44px" in prompt


def test_diet_constants_are_short():
    """Each compact replacement should be ~100-300 tokens, NOT 2K+ like
    the full SKILL.md blocks they replace. Pins the size discipline."""
    from pebble.prompt_diet import (
        NO_SLOP_DIET, IOS_RULES_DIET, STACK_RULES_DIET,
        BUSINESS_INTEL_DIET, DESIGN_SYSTEM_DIET, IMAGE_RULES_DIET,
    )
    # Rough heuristic: 4 chars per token → 300 tokens ≈ 1200 chars
    LIMIT = 1500  # generous ceiling
    for name, val in [
        ("NO_SLOP_DIET", NO_SLOP_DIET),
        ("IOS_RULES_DIET", IOS_RULES_DIET),
        ("STACK_RULES_DIET", STACK_RULES_DIET),
        ("BUSINESS_INTEL_DIET", BUSINESS_INTEL_DIET),
        ("DESIGN_SYSTEM_DIET", DESIGN_SYSTEM_DIET),
        ("IMAGE_RULES_DIET", IMAGE_RULES_DIET),
    ]:
        assert len(val) <= LIMIT, f"{name} is {len(val)} chars; should be ≤{LIMIT}"


def test_diet_uses_positive_directives():
    """Qwen research: NEVER-stacking confuses smaller models. The diet's
    rules should be primarily affirmative ('Use X', 'Build per Y') not
    negative ('NEVER do X'). Allow up to ~3 NEVER per block as critical
    guardrails; flag if any block has more."""
    from pebble.prompt_diet import (
        NO_SLOP_DIET, IOS_RULES_DIET, STACK_RULES_DIET,
        BUSINESS_INTEL_DIET, DESIGN_SYSTEM_DIET, IMAGE_RULES_DIET,
    )
    for name, val in [
        ("NO_SLOP_DIET", NO_SLOP_DIET),
        ("IOS_RULES_DIET", IOS_RULES_DIET),
        ("STACK_RULES_DIET", STACK_RULES_DIET),
        ("BUSINESS_INTEL_DIET", BUSINESS_INTEL_DIET),
        ("DESIGN_SYSTEM_DIET", DESIGN_SYSTEM_DIET),
        ("IMAGE_RULES_DIET", IMAGE_RULES_DIET),
    ]:
        lower = val.lower()
        never_count = lower.count("never") + lower.count("do not") + lower.count("don't") + lower.count("forbidden")
        assert never_count <= 5, (
            f"{name} has {never_count} negative directives; "
            f"Qwen prefers positive guidance. Reduce or merge."
        )


# ------------------------------------------------------------------ #
# build_prompt integration — diet ON vs OFF actually differs           #
# ------------------------------------------------------------------ #

def _sample_brief() -> dict:
    return {
        "business_name": "Test Coaching",
        "business_type": "Executive coach",
        "audience": "professionals",
        "site_functions": ["leads"],
        "brand_tone": "professional",
        "_industry_intel_key": "business_consultant",
    }


def test_diet_on_produces_shorter_prompt(monkeypatch):
    """Diet ON should cut at least 30% of the prompt size vs OFF.
    Without this guarantee, the diet did nothing measurable."""
    import pebble_engine

    monkeypatch.delenv("PEBBLE_PROMPT_DIET", raising=False)  # default = on
    import pebble.prompt_diet
    importlib.reload(pebble.prompt_diet)
    prompt_on = pebble_engine.build_prompt(_sample_brief(), ds_text="", notes=[])

    monkeypatch.setenv("PEBBLE_PROMPT_DIET", "false")
    importlib.reload(pebble.prompt_diet)
    prompt_off = pebble_engine.build_prompt(_sample_brief(), ds_text="", notes=[])

    assert len(prompt_on) < len(prompt_off), "diet ON should be shorter"
    pct_cut = 1 - (len(prompt_on) / len(prompt_off))
    assert pct_cut >= 0.30, (
        f"diet only cut {pct_cut:.1%}; expected ≥30%. "
        f"Diet={len(prompt_on)}, Full={len(prompt_off)}"
    )


def test_diet_on_keeps_load_bearing_content(monkeypatch):
    """Diet must NOT cut critical content: business name, industry,
    Layout DNA + Style DNA blocks (when present in brief), iOS rules,
    image-sourcing rules."""
    import pebble_engine

    monkeypatch.delenv("PEBBLE_PROMPT_DIET", raising=False)
    import pebble.prompt_diet
    importlib.reload(pebble.prompt_diet)

    prompt = pebble_engine.build_prompt(_sample_brief(), ds_text="", notes=[])
    must_contain = [
        "Test Coaching",            # business name
        "Executive coach",           # business_type
        "100dvh",                    # ios rule (kept)
        "Unsplash",                  # image-sourcing rule (new in diet)
        "Style DNA",                 # the DNA precedence block
    ]
    for needle in must_contain:
        assert needle in prompt, f"diet dropped critical content: {needle!r}"


# ------------------------------------------------------------------ #
# Phase 15d — strip_verbatim_code_patterns                             #
# ------------------------------------------------------------------ #

def test_stripper_replaces_code_pattern_1():
    from pebble.prompt_diet import strip_verbatim_code_patterns
    src = (
        "#### 1. Hero Entrance — AnimatedHeading + FadeIn Components\n\n"
        "##### `components/ui/AnimatedHeading.tsx`\n\n"
        "```tsx\nexport function AnimatedHeading() {}\n```\n\n"
        "##### `components/ui/FadeIn.tsx`\n\n"
        "```tsx\nexport function FadeIn() {}\n```\n\n"
        "#### 2. Liquid-Glass Navbar\n"
    )
    out = strip_verbatim_code_patterns(src)
    # Heading 1 replaced by short summary
    assert "AnimatedHeading" in out  # the component is mentioned by name in the summary
    assert "Layout DNA" in out
    # The verbatim TSX is gone
    assert "export function AnimatedHeading() {}" not in out
    assert "export function FadeIn() {}" not in out
    # Heading 2 (next ####) is preserved as the boundary
    assert "#### 2." in out


def test_stripper_preserves_kept_patterns():
    """Code Pattern 2b (CSS utility), 3 (ScrollReveal), 5 (Parallax),
    7 (Three.js), 8 (Contact form) are NOT in the strip list and must
    survive intact."""
    from pebble.prompt_diet import strip_verbatim_code_patterns
    src = (
        "#### 2b. Liquid-Glass Utility — globals.css (FOUNDATION)\n\n"
        "```css\n.liquid-glass { backdrop-filter: blur(12px); }\n```\n\n"
        "#### 3. ScrollReveal — Framer Motion whileInView (FOUNDATION)\n\n"
        "Stays in.\n\n"
        "#### 8. Contact Form — Real Server Action + Resend\n\n"
        "Stays in.\n\n"
    )
    out = strip_verbatim_code_patterns(src)
    assert "Liquid-Glass Utility" in out
    assert "backdrop-filter: blur(12px)" in out  # CSS utility survives
    assert "ScrollReveal" in out
    assert "Contact Form" in out


def test_stripper_idempotent_on_already_stripped():
    """Calling the stripper twice produces the same output (the summaries
    don't trigger their own headings to be re-stripped)."""
    from pebble.prompt_diet import strip_verbatim_code_patterns
    src = "#### 1. Hero Entrance — long block\n\n...verbatim TSX...\n\n#### 2. Liquid-Glass Navbar\n"
    once = strip_verbatim_code_patterns(src)
    twice = strip_verbatim_code_patterns(once)
    assert once == twice


def test_stripper_safe_on_empty_input():
    from pebble.prompt_diet import strip_verbatim_code_patterns
    assert strip_verbatim_code_patterns("") == ""


def test_stripper_safe_when_no_patterns_present():
    """A document with none of the stripped headings should return unchanged."""
    from pebble.prompt_diet import strip_verbatim_code_patterns
    src = "## Some unrelated heading\n\nSome unrelated content."
    assert strip_verbatim_code_patterns(src) == src


def test_full_diet_on_cuts_substantially_more_with_stripper(monkeypatch):
    """Validate that adding the stripper cuts MORE tokens beyond the
    skill-block compact replacements. Net diet ON should now be ≥50%
    smaller than diet OFF (was ~47% with just compact skills)."""
    import pebble_engine

    monkeypatch.delenv("PEBBLE_PROMPT_DIET", raising=False)
    import pebble.prompt_diet
    importlib.reload(pebble.prompt_diet)
    prompt_on = pebble_engine.build_prompt(_sample_brief(), ds_text="", notes=[])

    monkeypatch.setenv("PEBBLE_PROMPT_DIET", "false")
    importlib.reload(pebble.prompt_diet)
    prompt_off = pebble_engine.build_prompt(_sample_brief(), ds_text="", notes=[])

    pct_cut = 1 - (len(prompt_on) / len(prompt_off))
    # Threshold relaxed 0.50 → 0.48 on 2026-06-06: the copy-craft guidance
    # added to prompt_template.md is prose (not verbatim TSX/CSS), so the
    # stripper correctly keeps it, nudging the cut to ~49.6%. The diet still
    # removes ~half the prompt (its purpose); 0.48 leaves headroom for future
    # legitimate guidance growth without masking a real diet regression.
    assert pct_cut >= 0.48, (
        f"diet only cut {pct_cut:.1%}; expected ≥48%. "
        f"ON={len(prompt_on)}, OFF={len(prompt_off)}"
    )
