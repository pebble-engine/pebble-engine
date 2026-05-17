"""Anti-slop audit for design-system text.

The audit pass runs against the design-system Markdown the design_system
generator emits before we feed it to the LLM. It flags the visual patterns
that screech "AI-generated landing page" — the universal Inter+Poppins
duo, purple-to-blue gradients, the hero->3-cards->cta default layout —
and returns a list of human-readable notes the prompt template stitches
in as guard-rails for the LLM.

Extracted from pebble_engine.py as part of the engine-module slimming
pass. Same exports + same semantics; the function and its three
configuration sets are unchanged.
"""
from __future__ import annotations

import re


# Display faces that show up in roughly every AI-generated landing page.
# Their presence on the HEADING slot is the strongest single signal that
# a design-system suggestion is generic. We don't reject them — we tell
# the LLM to swap to something with personality (the ACCEPTABLE_DISPLAY
# set below).
CONVERGENCE_FONTS: frozenset[str] = frozenset({
    "inter", "roboto", "poppins", "geist", "plus jakarta sans",
    "space grotesk", "dm sans",
})

# Display-font picks that read as deliberate. If the heading uses one of
# these, the body can stay neutral (Inter, etc) without triggering the
# convergence-pair flag.
ACCEPTABLE_DISPLAY_PAIRS: frozenset[str] = frozenset({
    "fraunces", "playfair", "instrument serif", "tobias", "migra",
    "pp editorial", "söhne", "sohne", "national 2", "tiempos",
    "gt alpina", "boogy brut", "dm serif", "serif",
})

# Style references that consistently produce bad output when the LLM
# takes them at face value.
WATCH_STYLES: frozenset[str] = frozenset({
    "neumorphism", "claymorphism", "default cyberpunk",
})


def _extract_field(text: str, pattern: str) -> str:
    """Pull the first capture group of ``pattern`` from ``text`` or ``""``.

    Used by :func:`audit_design_system` to read named lines out of the
    design-system Markdown (e.g. ``Heading font: Inter`` -> ``Inter``).
    Caller relies on the empty-string fallback for "field missing".
    """
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def audit_design_system(ds_text: str) -> list[tuple[str, str]]:
    """Return human-readable notes flagging slop-adjacent patterns in
    a generated design-system block. Each note is ``(CATEGORY, message)``
    where CATEGORY is one of TYPOGRAPHY / COLOR / STYLE / LAYOUT.
    Empty list when nothing trips.
    """
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


__all__ = [
    "audit_design_system",
    "CONVERGENCE_FONTS",
    "ACCEPTABLE_DISPLAY_PAIRS",
    "WATCH_STYLES",
]
