# boutique_brokerage_sage — Pebble Engine template

Light editorial luxury real-estate Next.js 14 (App Router) template — a sage
+ bronze color variant of `boutique_brokerage`. Same structure, same DNA,
calmer temperament. Placeholder brand: **Willow & Slate Estates** (generic
Hudson Valley boutique brokerage, Hudson, NY).

## Source DNA

- DNA: `pebble/templates/dna/real_estate_luxury.json`
- Vibe: Hudson Valley sage-bronze — countryside-luxury, garden-state
- Sibling template: `boutique_brokerage` (vermilion-on-black, urban-coastal
  Sag Harbor temperament). Same components, same sections, opposite palette
  and geography.

## Content tokenization (the important bit)

ALL static content lives in **one file**:

- `content/site.ts` — every brand string, address, headline, listing entry,
  social handle. Exported as named constants.

Components import from `content/site.ts` and never hard-code business
content. To instantiate this template for a customer, the engine makes one
focused LLM call that rewrites only `content/site.ts` — components stay
stable.

## Design language

- Unbounded (display, weights 400/700/900) + Inter (body, 300/400/500/600)
  via `next/font/google`
- Sage-bronze token palette: bg cream `#FAF8F2`, fg charcoal `#1F2421`,
  accent bronze `#9B7B47` (CTAs), primary deep-sage `#4A5840` (brand mark),
  secondary mid-sage `#6E7A60`, surface `#EFEDE4`, muted `#6E7A60`,
  border `#E0DDD3`
- Signature 2px micro-rounding (`.cinematic-radius`) — sharp slab aesthetic
- `mix-blend-difference` floating navbar inverts through any background
- `mix-blend-overlay` hero h1 interacts with the photo behind it
- `.cinematic-img` filter (soft contrast + slight desaturation) — editorial
  grade tuned for the cream background
- Bronze `//` divider between BEDS // BATHS on property cards
- Numbered slab dividers (`01`, `02`, `03`, `04`) between major sections

## Sections shipped

Homepage assembles 5 sections in order:

1. **Hero** — full-bleed mansion image, mix-blend-overlay headline, dual CTAs, scroll indicator
2. **Intro** — split text + 2x2 stat grid (stats hidden by default — no invented numbers)
3. **Listings** — three-col aspect-4/5 property cards (hidden by default — no invented inventory; honest placeholder routes to contact)
4. **Principal** — sticky split-screen with portrait slab + pinned content panel
5. **Contact** — confidential-inquiries pill, 2-col form grid + full-width bronze CTA

Plus `/about` and `/contact` standalone pages.

## Anti-slop defaults

- `LISTINGS = []` — never invent property addresses, beds/baths, or prices
- `STATS = []` — never invent transaction volume or close rates
- `TESTIMONIALS` not used — never invent client quotes
- `PRINCIPAL_IMAGE_URL = ""` — collapses to a deep-sage slab when unset
- `PRINCIPAL_STATS = []` — never invent years-in-business or awards

The customer populates these only when they can substantiate.

## Validation

```bash
npm install
npx tsc --noEmit
npx next build
```
