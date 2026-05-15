"""GET /api/dna/preview — return one DNA card without doing a full build.

The Live DNA Preview is the questionnaire's biggest visual differentiator:
template-gallery competitors can only show pre-baked options, but Pebble
generates fresh against a Style DNA, so we can show the user "your style
direction is forming" in real time.

This endpoint never spends LLM tokens; it's a deterministic pick from
:data:`style_dna.DNA_CARDS`.

Usage from the v3 questionnaire:

    GET /api/dna/preview                  → random card (whatever the RNG picks)
    GET /api/dna/preview?id=swiss_magazine → that exact card (for hydration)
    GET /api/dna/preview?exclude=a,b,c    → random card, but never one of those
                                           (the "Try another" button passes the
                                           current id so the user always sees
                                           something different)
    GET /api/dna/preview?seed=42          → deterministic pick (for tests)
"""
from __future__ import annotations

import random
from typing import Optional
from urllib.parse import parse_qs, urlparse


# Fields the v3 UI uses today. Surfacing extras (signature_moves,
# forbidden) so the chip strip can render a tooltip / "what does this
# style do?" disclosure without another round-trip.
_PUBLIC_FIELDS = (
    "id", "label", "feel",
    "display_font", "body_font", "mono_font",
    "palette_posture", "hero_structure",
    "motion_intensity", "signature_moves", "forbidden",
)


def _slim_card(card: dict) -> dict:
    """Return only the fields the UI consumes — keeps the response small
    and avoids leaking internal-only knobs if any get added later."""
    return {k: card.get(k) for k in _PUBLIC_FIELDS if k in card}


def _parse_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_csv_list(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [s.strip() for s in value.split(",") if s.strip()]


def run_dna_preview(handler) -> None:
    """GET /api/dna/preview. Returns one DNA card.

    Response 200:
        { "ok": true, "card": { id, label, feel, ... }, "total": <int> }
    Response 404:
        { "error": "no DNA card with id 'foo'" }   (when ?id=... unknown)
        { "error": "every DNA card excluded; relax the exclusion list" }
    """
    try:
        from style_dna import DNA_CARDS, pick_dna_by_id
    except Exception as e:
        handler._json(500, {"error": f"DNA module unavailable: {e}"})
        return

    # do_GET strips the query string from handler.path for route matching
    # but stashes the raw form on handler._raw_path. Fall back to .path for
    # handlers (or tests) that didn't go through the do_GET strip.
    raw_path = getattr(handler, "_raw_path", None) or handler.path
    parsed = urlparse(raw_path)
    qs = parse_qs(parsed.query, keep_blank_values=False)

    chosen_id = (qs.get("id") or [None])[0]
    if chosen_id:
        card = pick_dna_by_id(chosen_id)
        if not card:
            handler._json(404, {"error": f"no DNA card with id '{chosen_id}'"})
            return
        handler._json(200, {
            "ok":    True,
            "card":  _slim_card(card),
            "total": len(DNA_CARDS),
        })
        return

    exclude = set(_parse_csv_list((qs.get("exclude") or [None])[0]))
    candidates = [c for c in DNA_CARDS if c.get("id") not in exclude]
    if not candidates:
        handler._json(404, {
            "error": "every DNA card excluded; relax the exclusion list",
            "total": len(DNA_CARDS),
        })
        return

    seed = _parse_int((qs.get("seed") or [None])[0])
    rng = random.Random(seed) if seed is not None else random
    card = rng.choice(candidates)
    handler._json(200, {
        "ok":    True,
        "card":  _slim_card(card),
        "total": len(DNA_CARDS),
    })
