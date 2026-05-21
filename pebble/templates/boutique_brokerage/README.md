# boutique_brokerage — Pebble Engine template

Cinematic luxury real-estate Next.js 14 (App Router) template derived from the
`real_estate_luxury` DNA. Placeholder brand: **Beacon & Bay Realty**
(generic Northeast-shoreline boutique brokerage, Sag Harbor, NY).

## Source DNA

- DNA: `pebble/templates/dna/real_estate_luxury.json`
- Vibe: Cinematic IMAX Vermilion-Slab
- This template shares the design language but uses an **original, generic
  brand** so it can be instantiated for any luxury real-estate, architecture,
  yacht-broker, private-aviation, wealth-management, or auction-house client.

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
- 6-color token system: bg `#0A0A0A`, fg `#FFFFFF`, accent vermilion
  `#FF3A1F`, surface `#141414`, muted `#A0A0A0`, border `#2A2A2A`
- Signature 2px micro-rounding (`.cinematic-radius`) — sharp slab aesthetic
- `mix-blend-difference` floating navbar inverts through any background
- `mix-blend-overlay` hero h1 interacts with the photo behind it
- `.cinematic-img` filter (contrast 1.1 + brightness 0.9) on every photo
- Vermilion `//` divider between BEDS // BATHS on property cards
- Numbered slab dividers (`01`, `02`, `03`, `04`) between major sections

## Sections shipped

Homepage assembles 5 sections in order:

1. **Hero** — full-bleed mansion image, mix-blend-overlay headline, dual CTAs, scroll indicator
2. **Intro** — split text + 2x2 stat grid (stats hidden by default — no invented numbers)
3. **Listings** — three-col aspect-4/5 property cards (hidden by default — no invented inventory; honest placeholder routes to contact)
4. **Principal** — sticky split-screen with portrait slab + pinned content panel
5. **Contact** — confidential-inquiries pill, 2-col form grid + full-width vermilion CTA

Plus `/about` and `/contact` standalone pages.

## Anti-slop defaults

- `LISTINGS = []` — never invent property addresses, beds/baths, or prices
- `STATS = []` — never invent transaction volume or close rates
- `TESTIMONIALS` not used — never invent client quotes
- `PRINCIPAL_IMAGE_URL = ""` — collapses to a vermilion slab when unset
- `PRINCIPAL_STATS = []` — never invent years-in-business or awards

The customer populates these only when they can substantiate.

## Validation

```bash
npm install
npx tsc --noEmit
npx next build
```
