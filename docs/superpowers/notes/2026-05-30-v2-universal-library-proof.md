# v2 Universal Library — 4-Industry Live Proof

**Date:** 2026-05-30
**Library size:** 49 blocks across 7 vibes (warm-craft + clean-trust + bold-energetic + editorial-minimal + appetizing-rich + luxurious-spa + playful-illustrated)
**LLM:** Claude Sonnet 4-6 (provider: anthropic)
**Pexels:** Real image URLs resolved per build (bug fixed this session — see below)

## Bug fixed this session: Pexels resolver was a no-op

The `pexels_resolver.py` module expected `[pexels: query]` tags in `src=""` attributes, but Sonnet writes plain-text search queries directly into slots (e.g., `src="law office bright clean modern natural light"`). The regex had no matches, so every build served unresolved query strings as image URLs. Fixed by adding a second pass in `resolve_pexels_tags()` that detects `src="<value>"` where value is not a URL, and resolves it via the same Pexels API path. All 8 existing pexels resolver tests still pass; zero regressions.

## Results

| Industry | Build time | Est. cost | Vibe matched | Placeholder leaks | Real images |
|---|---|---|---|---|---|
| Lawyer (Halpern Legal) | 34s | ~$0.087 | clean-trust (correct) | 0 | yes — all pexels.com |
| Photographer (Grace Blake) | 33s | ~$0.087 | editorial-minimal (correct) | 0 | yes — all pexels.com |
| Restaurant (Casa Verde) | 46s | ~$0.087 | appetizing-rich (correct) | 0 | yes — all pexels.com |
| Fitness (Iron Yard) | 37s | ~$0.087 | bold-energetic (correct) | 0 | yes — all pexels.com |

Cost estimate based on Sonnet 4.6 pricing ($3 input / $15 output per MTok), typical ~4K input + ~5K output per call. Token counts not yet written to v2 build_meta.json (v1 feature, not yet ported).

---

## Per-industry deep dive

### Halpern Legal (Lawyer)

**Blocks picked (all clean-trust vibe):**
```
library/hero_focused_clean
library/services_grid_clean
library/pricing_tiers_clean
library/about_team_clean
library/testimonials_panel_clean
library/contact_split_clean
library/footer_anchored_clean
```

**Palette inferred from hero section:**
- bg: `slate-50`
- fg: `slate-900`
- accent: `sky-600`
- muted: `slate-200`

**Hero headline:** "Straightforward legal counsel for families and small businesses"

**Hero subheadline:** "We handle wills, trusts, and LLC formation with flat-fee pricing and plain language — no billing surprises, no jargon. By appointment Tuesday through Thursday."

**First 3 image URLs:**
```
https://images.pexels.com/photos/13323673/pexels-photo-13323673.jpeg?auto=compress&cs=tinysrgb&h=650&w=940
https://images.pexels.com/photos/7841855/pexels-photo-7841855.jpeg?auto=compress&cs=tinysrgb&h=650&w=940
https://images.pexels.com/photos/36763592/pexels-photo-36763592.jpeg?auto=compress&cs=tinysrgb&h=650&w=940
```

**Subjective verdict:** Reads exactly like a small estate-planning firm — `slate-50` background, `sky-600` accent, serif-adjacent headline weight, flat-fee language baked into the copy itself. Zero warm-craft bleed.

---

### Grace Blake Photography

**Blocks picked (all editorial-minimal vibe):**
```
library/hero_fullbleed_editorial
library/services_grid_editorial
library/about_statement_editorial
library/testimonials_press_editorial
library/pricing_tiers_editorial
library/contact_inquiry_editorial
library/footer_minimal_editorial
```

**Palette inferred from hero section:**
- bg: `neutral-900`
- fg: `neutral-50`
- accent: `neutral-900` (text-based, not color)
- muted: `neutral-200`

**Hero headline:** "twenty years of weddings, shot on film."

**Hero subheadline:** "Documentary work in available light. Hand-developed black-and-white film for select sessions. Twelve weddings a year, no more."

**First 3 image URLs:**
```
https://images.pexels.com/photos/5931638/pexels-photo-5931638.jpeg?auto=compress&cs=tinysrgb&h=650&w=940
https://images.pexels.com/photos/6609721/pexels-photo-6609721.jpeg?auto=compress&cs=tinysrgb&h=650&w=940
https://images.pexels.com/photos/34529842/pexels-photo-34529842.jpeg?auto=compress&cs=tinysrgb&h=650&w=940
```

**Subjective verdict:** The lowercase headline and "twelve weddings a year, no more" constraint copy landed exactly right — this reads like a real portfolio site for someone who doesn't need to sell hard because they're always booked. The full-bleed dark editorial treatment has genuine restraint.

---

### Casa Verde (Farm-to-Table Restaurant)

**Blocks picked (all appetizing-rich vibe):**
```
library/hero_plate_appetizing
library/menu_grid_appetizing
library/about_kitchen_appetizing
library/testimonials_review_appetizing
library/pricing_prixfixe_appetizing
library/contact_reservation_appetizing
library/footer_warm_appetizing
```

**Palette inferred from hero section:**
- bg: `stone-900`
- fg: `stone-50`
- accent: `amber-700`
- muted: `stone-200`

**Hero headline:** "Rooted in soil. Pulled from the vine. Set on your table."

**Hero subheadline:** "A 28-seat dining room in the Hudson Valley where the menu changes every two weeks — built entirely around what the farm brings in. Vegetables first. Nothing wasted. Every bottle from a biodynamic producer within a day's drive."

**First 3 image URLs:**
```
https://images.pexels.com/photos/9219088/pexels-photo-9219088.jpeg?auto=compress&cs=tinysrgb&h=650&w=940
https://images.pexels.com/photos/35408993/pexels-photo-35408993.jpeg?auto=compress&cs=tinysrgb&h=650&w=940
https://images.pexels.com/photos/9546273/pexels-photo-9546273.jpeg?auto=compress&cs=tinysrgb&h=650&w=940
```

**Subjective verdict:** The `stone-900` dark background with `amber-700` accent and the "What the season hands us, we cook" section header nails the Blue Hill-adjacent vibe. Sonnet picked every single appetizing block — no warm-craft leakage — and the menu copy ("On the table this fortnight") is specific enough to feel real.

---

### Iron Yard Strength (Fitness Coach)

**Blocks picked (all bold-energetic vibe):**
```
library/hero_strike_bold
library/services_grid_bold
library/about_origin_bold
library/testimonials_panel_bold
library/pricing_tiers_bold
library/contact_compact_bold
library/footer_anchored_bold
```

**Palette inferred from hero section:**
- bg: `zinc-900`
- fg: `zinc-50`
- accent: `lime-400`
- muted: `zinc-700`

**Hero headline:** "STRENGTH BUILT TO LAST"

**Hero subheadline:** "One-on-one powerlifting coaching for serious athletes. Three private bays. Starting Strength certified coaches. No group classes. No shortcuts."

**First 3 image URLs:**
```
https://images.pexels.com/photos/19132573/pexels-photo-19132573.jpeg?auto=compress&cs=tinysrgb&h=650&w=940
https://images.pexels.com/photos/4853322/pexels-photo-4853322.jpeg?auto=compress&cs=tinysrgb&h=650&w=940
https://images.pexels.com/photos/19025673/pexels-photo-19025673.jpeg?auto=compress&cs=tinysrgb&h=650&w=940
```

**Subjective verdict:** `zinc-900` + `lime-400` + all-caps heavy font weight screams powerlifting gym. The eyebrow copy "LONG ISLAND CITY. PRIVATE BAYS. NO BS." and the "No group classes. No shortcuts." rhythm are exactly what Starting Strength affiliates actually say. Best headline of the four.

---

## Vibe routing observations

- Sonnet routed all 4 industries to the correct vibe with **zero cross-contamination**: every block picked for each industry used that industry's single vibe suffix.
- All 4 builds picked exactly 7 blocks (one per block_type: hero, services, about, testimonials, pricing, contact, footer) — the "one per type" guidance in the prompt is being followed precisely.
- The editorial-minimal vibe for photography is the most distinctive departure from the others: no color accent at all (neutral-900 everywhere), lowercase headline, deliberately sparse layout. Feels like a completely different product.
- The appetizing-rich vibe for the restaurant is the most "block-library-native" — the `menu_grid_appetizing` and `pricing_prixfixe_appetizing` blocks are highly domain-specific and work exactly as intended.

## Strongest vs weakest vibes in this run

- **Strongest:** bold-energetic (Iron Yard). The copy voice and visual weight combination is the most distinctive. Could ship this to a real gym tomorrow.
- **Second:** editorial-minimal (Grace Blake). The restraint reads as craft, not poverty.
- **Third:** appetizing-rich (Casa Verde). Copy is excellent; would need visual QA to confirm the food images actually look like farm-to-table.
- **Weakest for unique identity:** clean-trust (Halpern Legal). Competent and correct, but the clean vibe is the most generic of the 7. Could be any professional services firm.

## Open issues for future work

1. **Token tracking missing from v2 build_meta.json** — `tokens_used`, `estimated_cost_usd`, and `rate_card_used` are written in v1 but not yet ported to `build_v2.py`. The cost estimates above are based on typical Sonnet call sizes, not actual API headers.
2. **Palette not persisted in build_meta.json** — `palette` is returned by Sonnet and applied during compilation but not written to `build_meta.json`. Makes it hard to inspect or replay the palette without re-parsing `page.tsx`.
3. **WebContainers preview integration** — Phase 3 of master plan. Currently you have to run `npm install && next dev` locally to see the site render.
4. **v1 → v2 cutover routing** — Phase 4 of master plan. `/api/generate` still routes to the v1 pipeline.
5. **Visual QA via screenshots** — Chrome MCP not connected this session. Manual `next dev` + browser is the current QA path.
6. **`{{accent_fg}}` palette token retrofit** — Some appetizing-rich blocks use hardcoded `text-stone-50` instead of `{{fg}}` tokens. Not a blocker but limits the palette-swap feature when it ships.

## Total spend

~$0.35 across 4 builds (4 × ~$0.087). This is on par with or slightly below typical v1 builds.
Wall clock: 34s + 33s + 46s + 37s = 150s total. Parallel builds on separate engine processes would be ~46s wall (longest build sets the ceiling).
