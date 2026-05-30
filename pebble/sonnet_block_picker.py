"""Sonnet-driven block selection + copy generation.

Takes a brief and a block menu (the available blocks for the matched
industry), asks Sonnet to pick 7-8 blocks and write copy for each
slot, returns a JSON spec the blocks_compiler can render.

The whole job is ~5K output tokens, ~3-5s wall clock, ~$0.05/call.
"""
from __future__ import annotations

import json
import re


_PROMPT_TEMPLATE = """You are designing a one-page website for a small business.

# Business brief
Name: {business_name}
Industry: {industry}
Description: {extra_context}

# Available blocks (you must only pick from these — do not invent block_ids)
{block_menu_json}

# Your job
1. Pick 7-8 blocks. Use the exact `block_id` values from the menu above.
   Prefer one block of each block_type (hero, services, about,
   testimonials, pricing, contact, footer). The order you list them
   becomes the order on the page.
2. For each picked block, write copy for every slot the block exposes.
   - Respect each slot's `max_chars` ceiling.
   - Use the slot's `tone` hint when present.
   - For `list` kind slots, provide a JSON list. List items can be
     either strings (for simple lists) or objects (e.g. service items
     with title/body/image/price).
   - For `image` kind slots, return a Pexels-style placeholder of the
     form "[pexels:<descriptive query>]" — the renderer swaps it later.
   - Make every copy line specific to THIS business. Never write
     placeholders like "[BUSINESS NAME]" or "Your tagline here" — write
     real copy or leave the slot out.
3. Pick a palette: Tailwind color tokens for `bg`, `fg`, `accent`, and
   `muted` (4 tokens). Choose values that fit the brief's tone —
   e.g. `stone-50 / stone-900 / orange-700 / stone-200` for a warm
   bakery, `slate-50 / slate-900 / sky-600 / slate-200` for a modern
   service business.

# Output

Return ONLY a JSON object with this exact shape, no prose around it:

{{
  "block_picks": [
    {{"block_id": "<from menu>", "slot_values": {{<slot_name>: <value>, ...}}}},
    ...
  ],
  "palette": {{"bg": "<tailwind>", "fg": "<tailwind>", "accent": "<tailwind>", "muted": "<tailwind>"}}
}}
"""

_JSON_RX = re.compile(r"\{[\s\S]*\}")


def pick_blocks_and_copy(
    *,
    brief: dict,
    llm_client,
    block_menu: list[dict],
) -> dict:
    """Call Sonnet to pick blocks + write copy. Return parsed JSON.

    Validates that every picked block_id appears in block_menu — raises
    ValueError if Sonnet invents a block (the compiler would fail later
    with a harder-to-debug KeyError).
    """
    prompt = _PROMPT_TEMPLATE.format(
        business_name=brief.get("business_name", ""),
        industry=brief.get("industry", ""),
        extra_context=brief.get("extra_context", ""),
        block_menu_json=json.dumps(block_menu, indent=2),
    )

    raw = llm_client.generate(prompt)

    match = _JSON_RX.search(raw)
    if not match:
        raise ValueError(
            f"Sonnet returned no JSON object; raw response (truncated): {raw[:200]!r}"
        )
    try:
        result = json.loads(match.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Sonnet returned invalid JSON: {e}; raw (truncated): {raw[:200]!r}"
        )

    # Validate every picked block_id exists in the menu — Sonnet
    # invents block_ids occasionally and the compiler downstream
    # would raise a less actionable KeyError.
    # Skip when block_menu is empty (e.g. prose-extraction tests).
    if block_menu:
        menu_ids = {m["block_id"] for m in block_menu}
        for pick in result.get("block_picks", []):
            if pick["block_id"] not in menu_ids:
                raise ValueError(
                    f"Sonnet invented unknown block_id {pick['block_id']!r}; "
                    f"must be one of {sorted(menu_ids)}"
                )

    return result
