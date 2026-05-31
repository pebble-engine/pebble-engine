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

# Available blocks
The library has many blocks across vibes. Each block has:
- `block_id`: unique ID (use this exact string in your picks)
- `block_type`: which slot it fills (hero, services, about, etc.)
- `vibe_tags`: vibe descriptors (e.g. "warm", "clean", "bold", "trust-building")
- `slots`: copy + image slots you must fill
- For image slots, the `pexels_query_template` is a STRUCTURAL HINT for the kind
  of subject the image should show (e.g. "{{founder_role}} portrait" means
  "a portrait of someone in the founder's role"). You translate it into a
  real Pexels search query based on the business's industry.

{block_menu_json}

# Your job

## 0. Extract the real business name

The "Name" field above may be a clean name ("Sudsy Paws") OR a whole
conversational sentence the user typed ("My wife and I run a mobile dog
grooming van called Sudsy Paws…"). Pull out the ACTUAL business name — the
brand a customer would say out loud. If the brief never states a name, invent
a short, fitting one (2-4 words). Return it as `business_name` in the output.
Never use the full sentence as the name.

## 1. Pick 6-8 blocks that fit the business's vibe

Match the block's `vibe_tags` to the emotional palette this business needs:
- Bakery, salon, florist, ceramic studio → warm, crafted, sensory, small-batch
- Dentist, lawyer, financial advisor → clean, trust-building, structured
- Fitness coach, esports, startup → bold, energetic, motivational
- Photographer, designer, gallery → editorial, minimal, dramatic
- Restaurant, cafe, food truck → appetizing, vibrant, warm

Use the EXACT `block_id` values from the menu — do not invent block_ids.
Prefer one block of each core `block_type` (hero, services, about, testimonials,
pricing, contact, footer). The order you list them becomes the order on
the page.

Two OPTIONAL block types add structural variety — reach for them when they fit:
- `gallery`: a visual masonry grid of images. Pick it for image-heavy
  businesses (photographer, restaurant, salon, designer, interior, products).
  Place it after the hero or about. Skip it for text-heavy services businesses.
- `scroll-story`: a pinned, step-by-step narrative ("how it works", "our
  process"). Pick it for businesses where the PROCESS matters (service
  providers, agencies, clinics, weddings, contractors). Place it after about
  or services. Skip it when there's no real sequence to tell.
Use at most one of each, and only when it genuinely fits — never both if the
business is simple.

## 2. Write copy for every slot

- Respect each slot's `max_chars` ceiling.
- Match the slot's `tone` hint when present.
- For `list` slots, provide a JSON list. Items can be strings (e.g. feature
  list) or objects (e.g. service cards with title/body/image/price).
- Make every line specific to THIS business. Never use placeholders like
  "[BUSINESS NAME]" or "Your tagline here" — write real copy or leave the
  slot out.

## 3. Resolve image slots into Pexels queries

For each `kind: "image"` slot:
- Read the slot's `pexels_query_template` — it's a hint at what the image
  should show (e.g. "{{industry_scene}} {{mood_warm}}" or "{{founder_role}}
  portrait" or "smiling person").
- Translate the hint into a real Pexels search query that:
  - Names the industry concretely (not "{{industry_scene}}" but
    "sourdough bakery interior" or "modern dental office")
  - Adds the mood/lighting/style implied by the template
  - Reads as a real search query a photographer would type
- Output the final query as the slot value, e.g.:
  - `"hero_image": "artisan sourdough bakery interior warm sunlight"`
  - `"founder_image": "baker portrait flour apron natural light"`

## 4. Pick a palette

Tailwind color tokens for `bg`, `fg`, `accent`, `accent_fg`, and `muted` (5 tokens).

- `bg`: page background (typically a 50-100 weight)
- `fg`: primary text color (typically a 900 weight)
- `accent`: brand color used for buttons + emphasis (any weight, fits the vibe)
- `accent_fg`: foreground color when text sits ON an accent background — choose for contrast. If `accent` is dark (700+), `accent_fg` should be light (50). If `accent` is light (lime-400, amber-200), `accent_fg` should be dark (zinc-900).
- `muted`: subtle background for cards, dividers (typically 100-200 weight)

Choose values that fit the brand vibe:
- Warm/crafted: `stone-50 / stone-900 / amber-700 / stone-50 / stone-200`
- Clean/trust: `slate-50 / slate-900 / sky-600 / slate-50 / slate-200`
- Bold/energetic: `zinc-900 / zinc-50 / lime-400 / zinc-900 / zinc-700`
- Editorial/minimal: `neutral-50 / neutral-900 / neutral-900 / neutral-50 / neutral-200`

# Output

Return ONLY a JSON object, no prose around it:

{{
  "business_name": "<the real brand name, 2-4 words>",
  "block_picks": [
    {{"block_id": "<from menu>", "slot_values": {{<slot_name>: <value>, ...}}}},
    ...
  ],
  "palette": {{"bg": "<tailwind>", "fg": "<tailwind>", "accent": "<tailwind>", "accent_fg": "<tailwind>", "muted": "<tailwind>"}}
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

    raw = llm_client.generate(
        system="You are an expert web designer. Follow all instructions exactly and return only valid JSON.",
        user=prompt,
    )

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
