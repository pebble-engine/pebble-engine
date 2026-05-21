# Service Pro Cream — template

**Vibe:** Cream Paper Dual-Theme. Warm cream-by-default service-industry
marketing site with a deep-forest dark mode toggle, glass-morphism navbar,
three blurred glow orbs behind the hero, an infinite marquee, and a shimmer-
swept "Call Us" chip above the phone number.

**Source DNA:** `pest_clean_safe` (see `dna_source.json`).

**Applicable industries:** landscaping · lawn care · garden design · tree
service · pressure washing · house cleaning · carpet cleaning · pool care ·
seasonal cleanup · hardscape & patio care · home & garden services. The cream
palette leans warmer and more organic than the dark `service_pro` variant —
better fit for landscaping and home-care brands than for tactical pest control.

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
- Tailwind CSS 3 with HSL custom-property tokens for dual cream/forest theme
- Framer Motion for entrance fades + scroll reveals
- Resend for the contact form server action
- Inter (body) + Outfit (display) via `next/font/google`

## License

Internal Pebble Engine template. Brand placeholder "Magnolia Home & Garden" is
fictional — no real-business resemblance intended.
