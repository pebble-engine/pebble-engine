"""Smart template matcher — Phase F1 (2026-05-24).

Given a free-text prompt + optional business_type, score every
template in the registry against the user's intent and return the
top-N matches. The funnel uses this after signup to surface 3
templates instead of dumping the user into the full gallery —
sophistication that reduces bounce.

Scoring (cheap, deterministic, no LLM):

  1. business_type ↔ applicable_industries token overlap: +0.6 cap
     - Normalize both sides: lowercase, swap _ and - for space.
     - Score by the proportion of business_type tokens that appear
       in any applicable_industries entry.
  2. prompt ↔ template metadata token overlap: +0.3 cap
     - 0.05 per overlapping token, max 6 tokens contribute.
  3. Free-tier bonus: +0.1 if template.tier == "free"
     - Ensures a free user always sees at least one free option in top 3.

Tie-break by template_id asc (deterministic test runs).

LLM intent extract fallback is post-MVP — deterministic version
covers ~80% of cases at zero per-call cost. Add the LLM hop later
when low-score prompts become an observable conversion problem.
"""
from __future__ import annotations

import re
from typing import Optional

from pebble.server.templates_api import load_registry


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _normalize(text: str) -> str:
    """Lowercase + swap _ and - for space so 'tattoo_shop' matches 'tattoo shop'."""
    return (text or "").lower().replace("_", " ").replace("-", " ")


def _tokens(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(_normalize(text)))


def _score_template(
    template: dict,
    prompt_tokens: set[str],
    business_type_tokens: set[str],
) -> tuple[float, str]:
    """Return (score 0.0-1.0, human-readable reason) for one template."""
    reasons: list[str] = []
    score = 0.0

    # Signal 1: business_type token overlap with applicable_industries.
    if business_type_tokens:
        industries_text = " ".join(template.get("applicable_industries", []) or [])
        industries_tokens = _tokens(industries_text)
        bt_overlap = business_type_tokens & industries_tokens
        if bt_overlap:
            # Proportion of business_type tokens that hit, capped at 0.6.
            ratio = len(bt_overlap) / max(1, len(business_type_tokens))
            score += min(0.6, ratio * 0.6)
            reasons.append(f"matches industry ({len(bt_overlap)} tok)")

    # Signal 2: prompt token overlap with template metadata.
    template_tokens = _tokens(
        " ".join([
            template.get("name", "") or "",
            template.get("tagline", "") or "",
            template.get("vibe", "") or "",
            template.get("best_for", "") or "",
            " ".join(template.get("applicable_industries", []) or []),
        ])
    )
    p_overlap = prompt_tokens & template_tokens
    if p_overlap:
        score += min(0.3, 0.05 * len(p_overlap))
        reasons.append(f"matches {len(p_overlap)} prompt keyword(s)")

    # Signal 3: free-tier bonus.
    if template.get("tier") == "free":
        score += 0.1

    return (round(min(score, 1.0), 3), "; ".join(reasons) or "general match")


def match_templates(
    prompt: str,
    business_type: Optional[str] = None,
    max_results: int = 3,
) -> dict:
    """Score every template, return top-N. Never returns empty unless
    the registry itself is empty.

    Output shape:
      {
        "matches": [
          {"template_id": "ink_studio", "score": 0.85,
           "reason": "matches industry (1 tok); matches 2 prompt keyword(s)"},
          ...
        ]
      }
    """
    templates = load_registry().get("templates", []) or []
    prompt_tokens = _tokens(prompt)
    bt_tokens = _tokens(business_type) if business_type else set()

    scored = []
    for t in templates:
        tid = t.get("id")
        if not tid:
            continue
        score, reason = _score_template(t, prompt_tokens, bt_tokens)
        scored.append({
            "template_id": tid,
            "score":       score,
            "reason":      reason,
        })

    # Sort: high score first, ties broken by template_id asc.
    scored.sort(key=lambda m: (-m["score"], m["template_id"]))
    return {"matches": scored[:max_results]}


def run_template_match(handler) -> None:
    """Handle POST /api/template-match. Public endpoint (no auth)."""
    import json
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length"}); return
    if length <= 0:
        handler._json(400, {"error": "empty body"}); return
    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid JSON"}); return
    if not isinstance(body, dict):
        handler._json(400, {"error": "body must be a JSON object"}); return

    prompt = (body.get("prompt") or "").strip()
    business_type = (body.get("business_type") or "").strip() or None
    try:
        max_results = int(body.get("max_results") or 3)
    except (TypeError, ValueError):
        max_results = 3
    max_results = max(1, min(10, max_results))

    if not prompt:
        handler._json(400, {"error": "prompt is required"}); return

    result = match_templates(prompt, business_type, max_results)
    handler._json(200, result)
