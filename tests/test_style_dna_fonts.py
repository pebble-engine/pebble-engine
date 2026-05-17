"""Every DNA card's display/body/mono font MUST be a real `next/font/google`
identifier. If this test fails, `next dev` will throw 'Unknown font ...' at
runtime — the LLM dutifully imports whatever string the DNA tells it to.

Historical regression: Big Shoulders Display was renamed to "Big Shoulders"
in 2024 when Google merged the family. Other commercial fonts (General Sans,
ABC Diatype Mono, Tiempos Headline, Söhne, GT Sectra Display) had crept in
over time. This test prevents that class of bug from reaching builds.
"""
from __future__ import annotations

from style_dna import DNA_CARDS


# Allowlist of fonts known to be in next/font/google's catalog at v15.x.
# When adding a new font to a DNA card, verify it appears in
# node_modules/next/dist/compiled/@next/font/dist/google/font-data.json
# and add it here.
ALLOWED_GOOGLE_FONTS = frozenset({
    "Inter",
    "Inter Tight",
    "Anton",
    "Archivo",
    "Big Shoulders",
    "Bricolage Grotesque",
    "Cormorant Garamond",
    "EB Garamond",
    "Fraunces",
    "Geist",
    "Geist Mono",
    "IBM Plex Mono",
    "JetBrains Mono",
    "Space Grotesk",
    "Space Mono",
    "Tektur",
    "Tenor Sans",
    "Unbounded",
})

# Fonts that previously shipped in DNA cards but DO NOT load via
# `next/font/google`. Hard-banned — including the renamed-Google case
# (Big Shoulders Display) and several commercial-only names.
FORBIDDEN_FONTS = frozenset({
    "Big Shoulders Display",  # renamed to "Big Shoulders" in 2024
    "General Sans",  # commercial (ITF)
    "ABC Diatype Mono",  # commercial (Dinamo)
    "Tiempos Headline",  # commercial (Klim)
    "Söhne",  # commercial (Klim)
    "GT Sectra Display",  # commercial (Grilli Type)
})


def _font_fields(card: dict) -> list[tuple[str, str]]:
    return [
        ("display_font", card["display_font"]),
        ("body_font", card["body_font"]),
        ("mono_font", card["mono_font"]),
    ]


def test_every_dna_card_uses_allowed_google_fonts():
    errors = []
    for card in DNA_CARDS:
        for field, value in _font_fields(card):
            if value not in ALLOWED_GOOGLE_FONTS:
                errors.append(
                    f"DNA card {card['id']!r} {field}={value!r} is not in "
                    f"next/font/google catalog. Either add it to "
                    f"ALLOWED_GOOGLE_FONTS (after verifying in "
                    f"node_modules/.../google/font-data.json) or pick a "
                    f"different font."
                )
    assert not errors, "\n".join(errors)


def test_no_dna_card_uses_known_forbidden_fonts():
    """Belt-and-suspenders: even if someone adds a forbidden font back to
    the allowlist by mistake, this still trips."""
    errors = []
    for card in DNA_CARDS:
        for field, value in _font_fields(card):
            if value in FORBIDDEN_FONTS:
                errors.append(
                    f"DNA card {card['id']!r} {field}={value!r} is on the "
                    f"forbidden list — it will fail at `next dev` time."
                )
    assert not errors, "\n".join(errors)
