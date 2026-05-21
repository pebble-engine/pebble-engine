# Honest Garage — Military variant

**Vibe:** Industrial Hazard-Stripe Stencil, military-precision sub-niche.
Dark-by-default diesel / fleet / heavy-duty mechanic marketing site with a
fixed-top 4px safety-orange-and-olive-charcoal diagonal hazard stripe,
JetBrains Mono ref-code labels on every section, hollow-stencil section
headings, and a parts-catalog / work-order feel for the service list.

**Source DNA:** `auto_honest_diag` (see `dna_source.json` and
`pebble/templates/dna/auto_honest_diag.json`).

**Sibling variants:**
- `honest_garage` — generic-industrial mechanic (yellow + near-black)
- `honest_garage_rust` — vintage-Americana classic-car shop
- `honest_garage_military` — this one — disciplined diesel / fleet / military-spec

**Applicable industries:** diesel mechanic · fleet maintenance · heavy-duty
truck repair · DOT inspection facility · veteran-owned auto · industrial
diesel · agricultural equipment · marine diesel · generator service. Any
buyer who wants DISCIPLINED + ACCOUNTABLE + PAPERWORK signals over flashy
marketing.

## How the template stays customizable

All copy, services, hours, phone, address, and brand name live in **one file**:
`content/site.ts`. Components import named constants from there — they never
hardcode strings. Swapping to a new customer is a single-file rewrite.

Empty arrays (`TESTIMONIALS = []`, `GALLERY_IMAGES = []`) are intentional. The
template ships honest by default: components hide sections when their content
is empty rather than inventing fake reviews. The customer fills them in after
launch.

Bracket-placeholder strings (`PHONE = "[BUSINESS PHONE]"`) are intentional too.
The instantiation step replaces them when real data is available — until then,
they're visually obvious "TODO" markers.

## Design signatures (load-bearing)

- **Hazard stripe** — a 4px-tall fixed-top `repeating-linear-gradient(45deg)`
  safety-orange / olive-charcoal bar above the nav. The industrial tell.
- **Stencil headings** — hollow-letter Anton text via `-webkit-text-stroke 1px`
  + transparent fill. Used for every section h2.
- **Ref-code labels** — every section is stamped with a JetBrains Mono
  `REF-XXX` / `SVC-XXX` / `BADGE-0X` / `IMG-REF-XXXXX` / `MAP-REF` code, like a
  parts catalog. Sets the work-order, not-marketing tone.
- **Safety-orange accent** — `#FF6B1A` accent on olive-charcoal `#1A1D14`
  background, with brass `#C8A85A` for ref-code stamps. Replaces the original
  hazard yellow with a military-spec palette.
- **No display font for the H1** — the hero h1 is deliberately Inter bold, not
  Anton, to feel work-order rather than brochure.

## Run locally

```bash
npm install
cp .env.example .env
# fill in RESEND_API_KEY etc.
npm run dev
```

Visit http://localhost:3000.

## Stack

- Next.js 14 App Router · React 18 · TypeScript 5
- Tailwind CSS 3 with HSL custom-property tokens
- Framer Motion for entrance fades + scroll reveals
- Resend for the contact form server action
- Inter (body) + Anton (display stencil) + JetBrains Mono (accent / ref codes)
  via `next/font/google`

## License

Internal Pebble Engine template. Brand placeholder "Foxtrot Motor Works" is
fictional — no real-business resemblance intended.
