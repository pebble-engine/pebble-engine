"""WCAG AA contrast audit for the Pebble v3 palette.

Run via:
    python scripts/contrast_audit.py

Reads palette tokens from `ui/v3/app/globals.css` (the canonical source),
enumerates the text/bg pairs that actually appear in the v3 codebase, and
prints a contrast report. Surfaces any pair that fails WCAG AA (4.5:1
normal text, 3:1 large text) so they can be remediated.

Limitations:
- Tailwind opacity modifiers like `bg-earth/10` are approximated by alpha-
  compositing the named color over its parent surface (assumed sand or
  stone for light theme; #14110d for dark). Real browsers do the same
  composite at paint time, so the math matches what users actually see.
- Doesn't enumerate EVERY combination in source — only the canonical
  semantic pairs + the tinted-pill pattern. Spot-checks rather than
  exhaustive.
"""
from __future__ import annotations

import re
from pathlib import Path


# ------------------------------ Palette ------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
GLOBALS_CSS = REPO_ROOT / "ui" / "v3" / "app" / "globals.css"


def parse_palette() -> dict[str, str]:
    """Extract --color-* hex values from globals.css."""
    src = GLOBALS_CSS.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for match in re.finditer(r"--color-([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", src):
        out[match.group(1)] = match.group(2)
    return out


# ------------------------------ Contrast math ------------------------------


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def srgb_to_linear(channel: int) -> float:
    c = channel / 255.0
    if c <= 0.03928:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    r, g, b = hex_to_rgb(hex_color)
    return 0.2126 * srgb_to_linear(r) + 0.7152 * srgb_to_linear(g) + 0.0722 * srgb_to_linear(b)


def contrast(fg_hex: str, bg_hex: str) -> float:
    l1, l2 = luminance(fg_hex), luminance(bg_hex)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def composite(fg_hex: str, alpha: float, bg_hex: str) -> str:
    """Alpha-composite fg over bg, return hex of the result."""
    fr, fg, fb = hex_to_rgb(fg_hex)
    br, bgg, bb = hex_to_rgb(bg_hex)
    out_r = round(alpha * fr + (1 - alpha) * br)
    out_g = round(alpha * fg + (1 - alpha) * bgg)
    out_b = round(alpha * fb + (1 - alpha) * bb)
    return f"#{out_r:02x}{out_g:02x}{out_b:02x}"


# ------------------------------ Test pairs ------------------------------


def main() -> int:
    p = parse_palette()

    # Light theme surfaces
    BG       = p["sand"]              # background (#f7f3ec)
    CARD     = p["stone"]             # card surface (#ece6dc)
    ACCENT   = p["mist"]              # accent surface (#efeae1)
    TEXT_1   = p["charcoal"]          # primary text
    TEXT_2   = p["graphite"]          # secondary text
    BORDER   = p["pebble"]            # border (#d8d1c5)
    ACCENT_1 = p["river"]             # primary brand
    SECONDARY = p["sage"]             # secondary brand
    DESTRUCTIVE = "#ba1a1a"           # destructive (hardcoded)
    WHITE    = "#ffffff"

    # Dark theme surfaces
    DARK_BG   = "#14110d"
    DARK_CARD = "#1f1d1a"
    DARK_TEXT_1 = p["sand"]
    DARK_TEXT_2 = "#b8b1a4"
    DARK_ACCENT_1 = "#6ea8b6"

    AA_NORMAL = 4.5
    AA_LARGE  = 3.0

    pairs: list[tuple[str, str, str, float]] = []  # (label, fg, bg, threshold)

    # --- Light theme: foundational pairs ---
    pairs += [
        ("light: text-foreground on bg-background",    TEXT_1, BG,       AA_NORMAL),
        ("light: text-foreground on bg-card",          TEXT_1, CARD,     AA_NORMAL),
        ("light: text-muted-foreground on bg-background", TEXT_2, BG,    AA_NORMAL),
        ("light: text-muted-foreground on bg-card",    TEXT_2, CARD,     AA_NORMAL),
        ("light: text-muted-foreground on bg-accent",  TEXT_2, ACCENT,   AA_NORMAL),
        ("light: text-primary-foreground on bg-primary",         BG,    ACCENT_1,    AA_NORMAL),
        ("light: text-secondary-foreground on bg-secondary",     WHITE, SECONDARY,   AA_NORMAL),
        ("light: text-destructive-foreground on bg-destructive", WHITE, DESTRUCTIVE, AA_NORMAL),
    ]

    # --- Light theme: accent text on tinted bgs (the pill pattern) ---
    for tint in [10, 15, 20, 30]:
        alpha = tint / 100
        # bg-spark/X over bg-card
        bg = composite(p["spark"], alpha, CARD)
        pairs.append((f"light: text-spark on bg-spark/{tint}-over-card",  p["spark"],  bg, AA_NORMAL))
        bg = composite(p["earth"], alpha, CARD)
        pairs.append((f"light: text-earth on bg-earth/{tint}-over-card",  p["earth"],  bg, AA_NORMAL))
        bg = composite(ACCENT_1, alpha, CARD)
        pairs.append((f"light: text-primary on bg-primary/{tint}-over-card", ACCENT_1, bg, AA_NORMAL))
        bg = composite(SECONDARY, alpha, CARD)
        pairs.append((f"light: text-secondary on bg-secondary/{tint}-over-card", SECONDARY, bg, AA_NORMAL))
        bg = composite(DESTRUCTIVE, alpha, CARD)
        pairs.append((f"light: text-destructive on bg-destructive/{tint}-over-card", DESTRUCTIVE, bg, AA_NORMAL))

    # --- Light theme: standalone accent text on plain bg ---
    pairs += [
        ("light: text-spark on bg-background",  p["spark"],  BG,   AA_NORMAL),
        ("light: text-earth on bg-background",  p["earth"],  BG,   AA_NORMAL),
        ("light: text-primary on bg-background", ACCENT_1,   BG,   AA_NORMAL),
        ("light: text-secondary on bg-background", SECONDARY, BG,  AA_NORMAL),
    ]

    # --- Light theme: muted on tinted backgrounds (status pill subtext) ---
    pairs += [
        ("light: text-muted-foreground on bg-muted (=bg-card)", TEXT_2, CARD, AA_NORMAL),
    ]

    # --- Light theme: border contrast (3:1 for UI components) ---
    pairs += [
        ("light: border-border on bg-background (UI contrast)", BORDER, BG, AA_LARGE),
        ("light: border-border on bg-card (UI contrast)",       BORDER, CARD, AA_LARGE),
    ]

    # --- Dark theme: foundational pairs ---
    pairs += [
        ("dark: text-foreground on bg-background",    DARK_TEXT_1, DARK_BG,   AA_NORMAL),
        ("dark: text-foreground on bg-card",          DARK_TEXT_1, DARK_CARD, AA_NORMAL),
        ("dark: text-muted-foreground on bg-background", DARK_TEXT_2, DARK_BG, AA_NORMAL),
        ("dark: text-muted-foreground on bg-card",    DARK_TEXT_2, DARK_CARD, AA_NORMAL),
        ("dark: text-primary-foreground on bg-primary", DARK_BG, DARK_ACCENT_1, AA_NORMAL),
    ]

    # --- Dark theme: accent text on tinted bgs ---
    for tint in [10, 15, 20, 30]:
        alpha = tint / 100
        bg = composite(p["spark"], alpha, DARK_CARD)
        pairs.append((f"dark: text-spark on bg-spark/{tint}-over-card",   p["spark"], bg, AA_NORMAL))
        bg = composite(p["earth"], alpha, DARK_CARD)
        pairs.append((f"dark: text-earth on bg-earth/{tint}-over-card",   p["earth"], bg, AA_NORMAL))
        bg = composite(DARK_ACCENT_1, alpha, DARK_CARD)
        pairs.append((f"dark: text-primary on bg-primary/{tint}-over-card", DARK_ACCENT_1, bg, AA_NORMAL))

    # --- Report ---
    print("=" * 80)
    print("PEBBLE v3 WCAG AA CONTRAST AUDIT")
    print("=" * 80)
    print()
    fails = []
    warns = []
    passes = 0
    for label, fg, bg, threshold in pairs:
        ratio = contrast(fg, bg)
        status = "PASS"
        if ratio < threshold:
            status = "FAIL"
            fails.append((label, fg, bg, ratio, threshold))
        elif ratio < AA_NORMAL and threshold < AA_NORMAL:
            # large-text-only — still pass but worth flagging
            warns.append((label, fg, bg, ratio))
        else:
            passes += 1
        print(f"  {status}  {ratio:5.2f}:1  (threshold {threshold:.1f})  {label}")
        print(f"           fg={fg}  bg={bg}")
    print()
    print(f"Summary: {passes} passing | {len(warns)} large-only | {len(fails)} FAILS")
    print()
    if fails:
        print("FAILING PAIRS (WCAG AA requires >=4.5:1 for normal text, >=3:1 for large/UI):")
        for label, fg, bg, ratio, threshold in fails:
            print(f"  - {label}: {ratio:.2f}:1 (need {threshold:.1f})")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
