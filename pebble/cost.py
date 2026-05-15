"""Token + cost estimation for build telemetry.

Goal: every generated build records ``tokens_used`` and
``estimated_cost_usd`` in ``build_meta.json`` so we have an honest audit
trail when billing eventually exists. The numbers don't need to match
provider billing exactly — they need to be in the right ballpark and
consistent across builds so we can show users a "this generation used
about $0.X" indicator without lying.

Rates are intentionally pessimistic (lean toward over-estimating) so the
user is never surprised by a higher bill than what we showed.

Future: when the official Anthropic / Google APIs return usage objects
on responses, replace ``estimate_tokens`` with the actual reported
usage. Until then, the chars/4 heuristic is the right call — it matches
what OpenAI's tokenizer cookbook says for English text within ~10%.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostEstimate:
    input_tokens:        int
    output_tokens:       int
    estimated_cost_usd:  float
    rate_card_used:      str   # human-readable provider/model id we matched

    def to_dict(self) -> dict:
        return {
            "input_tokens":      self.input_tokens,
            "output_tokens":     self.output_tokens,
            "estimated_cost_usd": round(self.estimated_cost_usd, 6),
            "rate_card_used":     self.rate_card_used,
        }


# (input_per_million, output_per_million) — USD.
# Loosely calibrated from public list prices, May 2026. Source-of-truth is
# whatever the provider charges on the invoice; this is for UX-time display
# only.
_RATE_CARD: dict[str, tuple[float, float]] = {
    # Gemini family
    "gemini-3.1-pro-preview": (1.25, 5.00),
    "gemini-3.1-pro":         (1.25, 5.00),
    "gemini-3.0-pro":         (1.25, 5.00),
    "gemini-1.5-pro":         (1.25, 5.00),
    "gemini-1.5-flash":       (0.075, 0.30),
    # Anthropic family
    "claude-opus-4-7":     (15.0, 75.0),
    "claude-opus-4-6":     (15.0, 75.0),
    "claude-sonnet-4-6":   (3.0,  15.0),
    "claude-haiku-4-5":    (0.80, 4.00),
    # Default fallback
    "_unknown":            (5.0, 15.0),
}


def _rate_for_model(model: str | None) -> tuple[tuple[float, float], str]:
    """Resolve a (input_rate, output_rate) tuple for a model string.

    Tries exact match first, then prefix match (so ``gemini-1.5-pro-001``
    falls back to ``gemini-1.5-pro``). Returns the ``_unknown`` fallback
    if nothing matches — never crashes.
    """
    if not model:
        return _RATE_CARD["_unknown"], "_unknown"
    if model in _RATE_CARD:
        return _RATE_CARD[model], model
    # Prefix match — e.g. claude-opus-4-7-20260101 → claude-opus-4-7
    for key in _RATE_CARD:
        if key != "_unknown" and model.startswith(key):
            return _RATE_CARD[key], key
    return _RATE_CARD["_unknown"], "_unknown"


def estimate_tokens(text: str | None) -> int:
    """Rough English token count: ~4 chars per token. Good to ±10%.

    Returns 0 for empty/None input. Never crashes.
    """
    if not text:
        return 0
    return max(1, len(text) // 4)


def estimate_cost(
    prompt: str | None,
    response: str | None,
    model: str | None,
) -> CostEstimate:
    """Compute a CostEstimate for one LLM round-trip.

    The arithmetic is straightforward: tokens × rate. The point is to
    record the result on EVERY build so we have a longitudinal series we
    can inspect later — "how much does the average bakery site cost to
    build?" becomes answerable from a directory of build_meta.json files.
    """
    in_tok = estimate_tokens(prompt)
    out_tok = estimate_tokens(response)
    (in_rate, out_rate), card_id = _rate_for_model(model)
    cost = (in_tok / 1_000_000) * in_rate + (out_tok / 1_000_000) * out_rate
    return CostEstimate(
        input_tokens=in_tok,
        output_tokens=out_tok,
        estimated_cost_usd=cost,
        rate_card_used=card_id,
    )


__all__ = ["CostEstimate", "estimate_tokens", "estimate_cost"]
