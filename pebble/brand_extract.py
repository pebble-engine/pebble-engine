"""Brand / inspiration extraction with optional vision images.

Two modes — determined by the caller, not by this module:

- **brand**:   the images are the business's own assets (logo, photos of
               their space, product shots).  The LLM uses them to pull
               concrete identity signals: colour from the actual logo, texture
               from the real interior, etc.

- **inspire**: the images are external reference sites or mood boards the
               user wants to borrow from.  The LLM uses them for palette and
               layout cues — it won't infer the user's *own* brand from them.

``inspiration_images`` is a list of ``(mime_type, bytes)`` pairs already
validated and size-capped by the HTTP handler.  When provided, each image is
base64-encoded and forwarded to the LLM as a vision block ahead of the text
prompt.  The function works fine with no images; callers always get the same
return shape.

The extract is intentionally thin: a short JSON blob the v3 questionnaire
can pre-fill.  Heavy site analysis (colours from CSS, type families, SSRF-
safe fetching) lives in :mod:`pebble.inspire` and :mod:`pebble.migrate`.
"""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field, asdict
from typing import Optional

from pebble.llm import LLMError, get_llm_client


# ---- Result shape -----------------------------------------------------------

@dataclass
class BrandExtract:
    """Signals pulled from URL + optional images by the LLM.

    Every field defaults to something safe so callers never have to guard
    against None from a partial parse.
    """
    mode: str = "brand"                     # "brand" | "inspire"
    url: str = ""
    business_name_guess: str = ""
    business_type_guess: str = ""
    palette_hints: list[str] = field(default_factory=list)   # hex strings
    layout_notes: str = ""                  # free-form LLM observation
    copy_voice: str = ""                    # "warm / playful / minimal / …"
    dna_hint: str = ""                      # suggested DNA card id, if any
    extra_context: str = ""                 # ready-to-paste brief field
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_brief_partial(self) -> dict:
        """Map onto fields the v3 questionnaire can pre-fill."""
        bits: list[str] = []
        if self.layout_notes:
            bits.append(self.layout_notes)
        if self.copy_voice:
            bits.append(f"Voice / tone: {self.copy_voice}.")
        return {
            "extra_context":      " ".join(bits).strip() or self.extra_context,
            "business_name":      self.business_name_guess,
            "business_type":      self.business_type_guess,
            "_brand_dna_hint":    self.dna_hint,
        }


# ---- Prompt assembly --------------------------------------------------------

_SYSTEM_PROMPT = """\
You are a brand and design analyst assisting a website builder.

Given a URL (and optionally some images), extract the following as JSON:

{
  "business_name_guess": "...",   // best guess at the brand name
  "business_type_guess": "...",   // e.g. "restaurant", "law firm", "photographer"
  "palette_hints": ["#rrggbb", ...],  // 2-5 dominant hex colours
  "layout_notes": "...",          // one sentence on layout / visual style
  "copy_voice": "...",            // one or two adjectives, e.g. "warm, editorial"
  "dna_hint": "..."               // closest match from: swiss_magazine, brutalist_editorial,
                                  //   terminal_operator, cinematic_imax, industrial_freight,
                                  //   velvet_lounge, tactile_y2k, marina, neue_haas_minimal,
                                  //   postmodern_max, arthouse_folio, garden_press
                                  // Leave empty string if unsure.
}

Image guidance:
- In **inspire** mode the images are external references or mood boards —
  use them for palette and layout cues only.  Do not infer the user's own
  business identity from them.
- In **brand** mode the images are the business's own assets (logo, photos
  of their space, products).  Use them to pull concrete identity signals
  (colour from the actual logo, texture from the real interior, etc.).

Return ONLY the JSON object, no markdown fences, no extra commentary.
"""


def _build_user_message(url: str, mode: str) -> str:
    if url:
        return (
            f"Mode: {mode}\n"
            f"URL: {url}\n\n"
            "Analyse the URL and any attached images, then return the JSON."
        )
    return (
        f"Mode: {mode}\n"
        "No URL was provided — analyse only the attached images, then return the JSON."
    )


# ---- Public API -------------------------------------------------------------

def extract_brand(
    url: str,
    mode: str = "brand",
    *,
    inspiration_images: Optional[list[tuple[str, bytes]]] = None,
) -> BrandExtract:
    """Run a brand extraction against ``url`` with optional ``inspiration_images``.

    ``inspiration_images`` is a list of ``(mime_type, bytes)`` pairs.  Each
    image is base64-encoded and forwarded to the LLM as a vision block.

    Returns a :class:`BrandExtract`; the ``error`` field is set on failure —
    never raises to the HTTP layer.
    """
    client, reason = get_llm_client()
    if client is None:
        return BrandExtract(mode=mode, url=url, error=f"LLM unavailable: {reason}")

    images: list[dict] = []
    if inspiration_images:
        for mime_type, raw_bytes in inspiration_images:
            images.append({
                "media_type": mime_type,
                "data": base64.b64encode(raw_bytes).decode("ascii"),
            })

    user_text = _build_user_message(url, mode)
    try:
        raw = client.generate(
            system=_SYSTEM_PROMPT,
            user=user_text,
            max_tokens=512,
            images=images or None,
        )
    except LLMError as exc:
        return BrandExtract(mode=mode, url=url, error=str(exc))
    except Exception as exc:  # pragma: no cover
        return BrandExtract(mode=mode, url=url, error=f"unexpected LLM error: {exc}")

    # Best-effort JSON parse — if the model wraps in fences, strip them.
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(text)
    except Exception:
        return BrandExtract(mode=mode, url=url, error=f"could not parse LLM response: {text[:200]}")

    if not isinstance(parsed, dict):
        return BrandExtract(mode=mode, url=url, error="LLM returned non-object JSON")

    palette = parsed.get("palette_hints") or []
    if not isinstance(palette, list):
        palette = []

    return BrandExtract(
        mode=mode,
        url=url,
        business_name_guess=str(parsed.get("business_name_guess") or ""),
        business_type_guess=str(parsed.get("business_type_guess") or ""),
        palette_hints=[str(h) for h in palette if isinstance(h, str)][:5],
        layout_notes=str(parsed.get("layout_notes") or ""),
        copy_voice=str(parsed.get("copy_voice") or ""),
        dna_hint=str(parsed.get("dna_hint") or ""),
        extra_context="",
    )


__all__ = ["BrandExtract", "extract_brand"]
