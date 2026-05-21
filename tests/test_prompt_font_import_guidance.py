"""Pins the next/font/google import guidance in the prompt template
(Phase 38f, 2026-05-21).

Background: the Bon Appétit build hit a TypeScript compile error because
the LLM hallucinated `Big_Shoulders_Display` (Google consolidated the
Big Shoulders family — only `Big_Shoulders`, `Big_Shoulders_Inline`,
and `Big_Shoulders_Stencil` exist now). The prompt template now
includes explicit guidance against adding subfamily suffixes the DNA
didn't specify. This test pins that guidance so a future edit can't
silently delete it.
"""
from __future__ import annotations

from pathlib import Path

import pytest


PROMPT_PATH = Path(__file__).resolve().parents[1] / "skills" / "prompt_template.md"


@pytest.fixture(scope="module")
def prompt_body() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def test_template_has_font_import_rule_section(prompt_body):
    assert "Font import name rule" in prompt_body


def test_template_warns_about_subfamily_suffixes(prompt_body):
    # The rule must enumerate the suffixes the LLM tends to hallucinate
    for suffix in ("_Display", "_Text", "_Inline", "_Stencil"):
        assert suffix in prompt_body, f"missing warning for {suffix!r} suffix"


def test_template_calls_out_big_shoulders_specifically(prompt_body):
    """Regression — the Bon Appétit build that triggered this rule used
    Postmodern Maximalist DNA which specifies 'Big Shoulders'. The fix
    must include this specific example or the LLM will keep making the
    same mistake."""
    assert "Big Shoulders" in prompt_body
    assert "Big_Shoulders" in prompt_body
    assert "Big_Shoulders_Display" in prompt_body  # the WRONG form, shown as a counter-example


def test_template_mentions_consolidation_reason(prompt_body):
    """The rule should explain WHY — Google consolidated some families.
    Without the reason, the LLM is more likely to revert under pressure
    from its training data."""
    assert "consolidated" in prompt_body.lower() or "no longer exists" in prompt_body.lower() or "doesn't exist" in prompt_body.lower()


def test_template_mentions_ts_compile_error(prompt_body):
    """Naming the specific TypeScript error gives the LLM a tangible
    consequence to avoid (TS2305)."""
    assert "TS2305" in prompt_body or "has no exported member" in prompt_body
