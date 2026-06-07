"""P3 — per-account "brand kit" (design-system lite).

A returning owner pins brand colors, a font, and a voice once; every new
build inherits them via a directive block in the build prompt. Style
directives, not facts — anti-slop is unaffected.

Storage: ``output/.users/<uid>/brand_kit.json``.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

MAX_FONT = 60
MAX_VOICE = 600
_KEYS = ("primary_color", "accent_color", "font", "voice")
_HEX = re.compile(r"^#[0-9a-fA-F]{3,8}$")


def _neutralize(s: str) -> str:
    return (s or "").replace("{", "(").replace("}", ")")


def sanitize_kit(d: dict[str, Any]) -> dict[str, str]:
    d = d or {}
    out: dict[str, str] = {}
    for color_key in ("primary_color", "accent_color"):
        v = str(d.get(color_key, "")).strip()
        out[color_key] = v if _HEX.match(v) else ""
    out["font"] = str(d.get("font", "")).strip()[:MAX_FONT]
    out["voice"] = str(d.get("voice", "")).strip()[:MAX_VOICE]
    return out


def _path(output_dir: Path, uid: str) -> Path:
    return Path(output_dir) / ".users" / uid / "brand_kit.json"


def load_account_brand_kit(output_dir: Path, uid: str) -> dict[str, str]:
    if not uid:
        return {}
    p = _path(output_dir, uid)
    try:
        if p.exists():
            return sanitize_kit(json.loads(p.read_text(encoding="utf-8")))
    except Exception:
        pass
    return {}


def save_account_brand_kit(output_dir: Path, uid: str, kit: dict[str, Any]) -> dict[str, str]:
    if not uid:
        return {}
    clean = sanitize_kit(kit)
    p = _path(output_dir, uid)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(clean, indent=2), encoding="utf-8")
    return clean


def render_brand_kit_block(kit: dict[str, Any]) -> str:
    k = sanitize_kit(kit)
    lines: list[str] = []
    if k["primary_color"]:
        lines.append(f"- Primary brand color: {k['primary_color']} — use it for primary CTAs/accents in the :root design tokens.")
    if k["accent_color"]:
        lines.append(f"- Secondary/accent color: {k['accent_color']}.")
    if k["font"]:
        lines.append(f"- Preferred display/accent font: {_neutralize(k['font'])} (load via next/font/google; keep Inter for body if this isn't a Google font).")
    if k["voice"]:
        lines.append(f"- Brand voice: {_neutralize(k['voice'])}.")
    if not lines:
        return ""
    return "## BRAND KIT (apply consistently across the whole site)\n" + "\n".join(lines)


__all__ = [
    "MAX_FONT", "MAX_VOICE",
    "sanitize_kit", "load_account_brand_kit", "save_account_brand_kit",
    "render_brand_kit_block",
]
