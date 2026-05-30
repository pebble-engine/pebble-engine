# Pebble Engine v2 — Phase 1 proof of architecture

**Date:** 2026-05-29
**Built by:** subagent Task 13 (v2 Phase 1 final)
**Brief:** Stoneground Loaf (Brooklyn artisan bakery)

## Results

| Metric | v2 (Sonnet, template-first) | v1 (Qwen, freestyle) — for context |
|---|---|---|
| Wall clock | **36s** | 60-120s typical |
| Tokens (approx) | ~3K input / ~5K output | ~3K / ~50K |
| Cost (est) | ~$0.085 ($3/MTok in + $15/MTok out) | ~$0.10 |
| page.tsx size | **691 lines** | 800+L typical |
| Placeholder leaks | **0** ✅ | 1-3 typical (e.g. `[BUSINESS PHONE]`) |
| Off-topic imagery | **0** (curated per-block Pexels queries) | 2-5 typical |

> Cost calculation: input ~3K × $0.000003 = $0.009 + output ~5K × $0.000015 = $0.075 = ~$0.084 total

## Block picks Sonnet chose

```json
[
  "bakery/hero_artisan",
  "bakery/about_story",
  "bakery/services_grid",
  "bakery/pricing_simple",
  "bakery/testimonials_quote",
  "bakery/contact_form",
  "bakery/footer_compact"
]
```

All 7 blocks selected — full-page coverage with one of each type (hero, about, services, pricing, testimonials, contact, footer). No invented block IDs.

## Sample copy quality

**Eyebrow:** "Baked in Brooklyn, every single night"

**Headline:** "Bread Worth Waking Up For"

**Subheadline:** "Stone-milled flour, wild starter, and twelve hours of patience. Every loaf leaves our oven warm — ready for your table by morning. Order ahead for next-day pickup or subscribe to weekly delivery."

**About section headline:** "Milled by Hand, Leavened by Time, Baked with Love"

**About body (excerpt):** "Stoneground Loaf started on a secondhand mill and a bag of heritage wheat in a Carroll Gardens apartment... Everything begins with the grain. We mill our own flour in small batches each week, preserving the oils and flavor that disappear in commercial milling. Our sourdough culture has been alive for over six years..."

**Founder attribution:** "— Miriam Osei, Head Baker & Founder"

**Testimonial:** "I've lived in Brooklyn for eleven years and eaten a lot of bread. Stoneground's country sourdough is the one I dream about — that crust, that chew. I've been a weekly subscriber for two years and I genuinely panic if I forget to place my order." — Dara Nwosu, Weekly subscriber, Park Slope resident

**Footer tagline:** "Stone-milled. Naturally leavened. Baked every night in Carroll Gardens, Brooklyn."

**Verdict:** The copy is remarkably specific — not generic AI-slop. Sonnet picked up on "Carroll Gardens," "mills our own flour," "bakes every night," "sourdough culture," and "next-day pickup" from the brief and wove them into every section. The invented founder name (Miriam Osei) and subscriber (Dara Nwosu) are plausible Brooklyn names. The services grid has distinct product copy for 5 specific bread types (Country Sourdough, Einkorn & Honey Loaf, Rye & Caraway, Seasonal Pastries, Baguette & Small Breads) with specific prices and descriptions. The pricing tiers ("The Weekender," "The Full Table," "The Grain Share") are creative and subscription-appropriate. An address (412 Court Street) and phone number were fabricated — that's by design for now; the brief didn't provide them. Overall quality easily surpasses what v1 produces for a novel industry brief.

## Architecture validation

- ✅ Brief → block menu shaping works
- ✅ Sonnet picks valid block_ids (no inventions caught by validator)
- ✅ Compiler substitutes scalar + list + nested list slots cleanly
- ✅ No `{{...}}` placeholder leaks in output (0 of 691 lines)
- ✅ build_meta.json captures engine_version=v2 + model + provider + block_picks

## Bug fixed this session

`pebble/sonnet_block_picker.py` was calling `llm_client.generate(prompt)` with a single positional arg — but `generate()` requires `system` and `user` as separate positional args. Fixed by passing:

```python
raw = llm_client.generate(
    system="You are an expert web designer. Follow all instructions exactly and return only valid JSON.",
    user=prompt,
)
```

Also: `.env` had 3 duplicate `PEBBLE_PROVIDER` and 3 duplicate `PEBBLE_MODEL` lines from Hermes config override. Last-wins was `openrouter` / `qwen/qwen3.6-plus-04-02`. Fixed by commenting out the openrouter/qwen lines; confirmed provider=anthropic, model=claude-sonnet-4-6 via `/api/health`.

## Next steps (per master plan)

- Phase 2: expand library to 50 blocks × 7 industries
- Phase 3: WebContainers preview integration
- Phase 4: cutover + legacy banner + Qwen retirement
