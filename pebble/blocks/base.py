"""Block-library types + DNA → theme-tokens derivation.

``BlockSpec`` is the registry entry shape. ``ThemeTokens`` is the
distilled palette+typography+posture the block renderers consume. The
two stay separate so a block renderer never reaches into a raw DNA
card — it works only against the curated tokens.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Optional


# ---- Palette extraction --------------------------------------------------

_HEX_RE = re.compile(r"#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b")


def _normalize_hex(raw: str) -> str:
    """``#abc`` → ``#aabbcc``; ``#AABBCC`` → ``#aabbcc``. Always 7 chars."""
    raw = raw.lstrip("#")
    if len(raw) == 3:
        raw = "".join(c * 2 for c in raw)
    return "#" + raw.lower()


def extract_palette_hexes(palette_posture: str) -> list[str]:
    """Pull every hex value out of a DNA card's ``palette_posture`` string,
    in document order. Deduped while preserving order — DNA cards usually
    list the background first, then ink, then accent(s)."""
    seen: set[str] = set()
    out: list[str] = []
    for m in _HEX_RE.findall(palette_posture or ""):
        norm = _normalize_hex(m)
        if norm in seen:
            continue
        seen.add(norm)
        out.append(norm)
    return out


def _hex_brightness(hex_color: str) -> float:
    """Perceived brightness 0..1 (ITU-R BT.601). Identical to the inspire
    module's helper — duplicated here to keep blocks/ self-contained."""
    raw = hex_color.lstrip("#")
    if len(raw) != 6:
        return 0.5
    try:
        r = int(raw[0:2], 16)
        g = int(raw[2:4], 16)
        b = int(raw[4:6], 16)
    except ValueError:
        return 0.5
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0


# ---- Theme tokens ---------------------------------------------------------

@dataclass
class ThemeTokens:
    """Theming inputs a block renderer is allowed to read.

    Each renderer should consume tokens via attribute access — *not*
    derive from the raw DNA card. That separation keeps blocks from
    quietly coupling to internal DNA fields (e.g. ``signature_moves``)
    that might evolve.
    """

    dna_id: str           # "swiss_magazine", "brutalist_editorial", ...
    dna_label: str        # human-readable
    display_font: str     # exact font family name ("Cormorant Garamond")
    body_font: str
    mono_font: str
    bg_hex: str           # canvas / section background
    ink_hex: str          # primary type color
    accent_hex: str       # single accent (CTA, hairline rules)
    secondary_hex: str    # optional second accent — empty string if N/A
    is_dark: bool
    motion_intensity: str # one of: minimal | subtle | smooth | aggressive | cinematic
    radius_class: str     # Tailwind utility name e.g. "rounded-none", "rounded-2xl"
    kicker_label_style: str  # "mono-uppercase" | "italic-section" | "stencil" | etc.

    def display_stack(self) -> str:
        """CSS font-family chain for the display font, with a safe fallback.

        The generated site loads Inter via ``next/font/google`` (foundation
        rule). The DNA's display_font *should* be loaded too, but the
        block can't assume so — fallback to Inter / serif / mono based on
        the DNA family."""
        return _font_stack(self.display_font, prefer_serif=_looks_serif(self.display_font),
                           prefer_mono=_looks_mono(self.display_font))

    def body_stack(self) -> str:
        return _font_stack(self.body_font, prefer_serif=_looks_serif(self.body_font),
                           prefer_mono=_looks_mono(self.body_font))

    def mono_stack(self) -> str:
        return _font_stack(self.mono_font or "IBM Plex Mono", prefer_mono=True)


_SERIF_HINTS = (
    "garamond", "cormorant", "times", "fraunces", "playfair", "merriweather",
    "lora", "tiempos", "newsreader", "spectral", "tenor", "eb garamond",
    "gt sectra",
)
_MONO_HINTS = (
    "mono", "ibm plex mono", "geist mono", "jetbrains", "iosevka", "courier",
    "space mono", "diatype mono", "fira code",
)


def _looks_serif(font_name: str) -> bool:
    name = (font_name or "").lower()
    return any(h in name for h in _SERIF_HINTS)


def _looks_mono(font_name: str) -> bool:
    name = (font_name or "").lower()
    return any(h in name for h in _MONO_HINTS)


def _font_stack(primary: str, *, prefer_serif: bool = False, prefer_mono: bool = False) -> str:
    """Build a CSS font-family chain. The primary is quoted; fallbacks
    chain through the family class to Inter (foundation) or a generic."""
    primary_q = f"'{primary}'" if primary else "'Inter'"
    if prefer_mono:
        return f"{primary_q}, 'IBM Plex Mono', ui-monospace, Menlo, Consolas, monospace"
    if prefer_serif:
        return f"{primary_q}, Georgia, 'Times New Roman', serif"
    return f"{primary_q}, 'Inter', ui-sans-serif, system-ui, sans-serif"


# ---- DNA → tokens --------------------------------------------------------

# Per-DNA overrides for the things you can't derive cleanly from the raw
# card (radius, kicker label style). Keep this small and explicit — the
# DNA card itself is the source of truth for fonts and palette.
_DNA_RADIUS_OVERRIDES: dict[str, str] = {
    "swiss_magazine":       "rounded-none",
    "brutalist_editorial":  "rounded-none",
    "terminal_operator":    "rounded-none",
    "architectural_spec":   "rounded-none",
    "neue_haas_minimal":    "rounded-none",
    "postmodern_max":       "rounded-sm",
    "industrial_freight":   "rounded-none",
    "arthouse_folio":       "rounded-sm",
    "cinematic_imax":       "rounded-md",
    "tactile_y2k":          "rounded-3xl",
    "garden_press":         "rounded-md",
    "velvet_lounge":        "rounded-md",
    "marina":               "rounded-md",
}

_DNA_KICKER_STYLE: dict[str, str] = {
    "swiss_magazine":       "section-numeral",   # § 02 ·
    "brutalist_editorial":  "mono-uppercase",    # FIG. 03 —
    "terminal_operator":    "terminal",          # > BOOT: 01
    "cinematic_imax":       "mono-uppercase",
    "architectural_spec":   "blueprint",         # 02.00 — TESTIMONIALS
    "tactile_y2k":          "soft-eyebrow",      # ◐ Kind words
    "neue_haas_minimal":    "numbered",          # 02.
    "postmodern_max":       "marquee",
    "arthouse_folio":       "roman",             # II.
    "industrial_freight":   "stencil",           # SVC-002 / TESTIMONIAL
    "garden_press":         "small-caps",        # ISSUE 02 — TESTIMONIALS
    "velvet_lounge":        "section-numeral",
    "marina":               "small-caps",
}


def derive_theme_from_dna(dna_card: Optional[dict]) -> ThemeTokens:
    """Distill a :class:`ThemeTokens` from a raw DNA card dict.

    Tolerates a missing ``dna_card`` (e.g. very old builds that pre-date
    the DNA system) by falling back to a calm neutral default that won't
    look broken on any site.
    """
    if not dna_card:
        return ThemeTokens(
            dna_id="", dna_label="Neutral",
            display_font="Inter Tight", body_font="Inter", mono_font="IBM Plex Mono",
            bg_hex="#fafaf7", ink_hex="#1a1a1a", accent_hex="#205661",
            secondary_hex="", is_dark=False,
            motion_intensity="subtle",
            radius_class="rounded-md",
            kicker_label_style="mono-uppercase",
        )

    palette_str = dna_card.get("palette_posture", "")
    hexes = extract_palette_hexes(palette_str)

    # Order in palette_posture is intentionally background → ink → accent(s).
    # Be defensive: empty palette_str shouldn't crash the renderer.
    bg = hexes[0] if hexes else "#fafaf7"
    ink = hexes[1] if len(hexes) > 1 else "#1a1a1a"
    accent = hexes[2] if len(hexes) > 2 else "#205661"
    secondary = hexes[3] if len(hexes) > 3 else ""

    is_dark = _hex_brightness(bg) < 0.4

    dna_id = dna_card.get("id", "")
    return ThemeTokens(
        dna_id=dna_id,
        dna_label=dna_card.get("label", dna_id or "Custom"),
        display_font=dna_card.get("display_font", "Inter Tight"),
        body_font=dna_card.get("body_font", "Inter"),
        mono_font=dna_card.get("mono_font", "IBM Plex Mono"),
        bg_hex=bg,
        ink_hex=ink,
        accent_hex=accent,
        secondary_hex=secondary,
        is_dark=is_dark,
        motion_intensity=dna_card.get("motion_intensity", "subtle"),
        radius_class=_DNA_RADIUS_OVERRIDES.get(dna_id, "rounded-md"),
        kicker_label_style=_DNA_KICKER_STYLE.get(dna_id, "mono-uppercase"),
    )


# ---- BlockSpec dataclass --------------------------------------------------

@dataclass
class BlockSpec:
    """Registry entry for one drop-in block type.

    ``render`` is a pure function so the registry stays declarative and
    testable; the spec doesn't know how the block is inserted, only how
    to render its JSX file content given (tokens, brief).
    """

    id: str             # snake_case identifier
    label: str          # human-readable label
    category: str       # "social-proof" | "conversion" | "explainer" | "monetization" | "growth"
    description: str    # one-sentence description for the gallery
    component_name: str # PascalCase component name
    icon: str           # lucide-react icon name (for the gallery thumbnail)
    render: Callable[[ThemeTokens, dict], str]  # (tokens, brief) → JSX file content

    def to_listing(self) -> dict:
        """Public payload shape used by ``GET /api/blocks``. Excludes the
        render callable (not JSON-serializable) and component_name
        (internal — the UI shouldn't depend on a specific filename)."""
        return {
            "id":          self.id,
            "label":       self.label,
            "category":    self.category,
            "description": self.description,
            "icon":        self.icon,
        }
