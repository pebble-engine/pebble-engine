# Honest Garage (Rust) — template

**Vibe:** Vintage-Americana Hazard-Stripe Stencil. Color variant of
`honest_garage` that swaps the industrial yellow + near-black palette for warm
rust + bone — same dark mechanic-shop layout, different cultural register.
Reads classic-car restoration shop / old-school neighborhood garage rather
than caution-tape industrial supply.

**Source DNA:** `auto_honest_diag` (see `dna_source.json` and
`pebble/templates/dna/auto_honest_diag.json`).

**Applicable industries:** classic / vintage auto restoration · independent
mechanic / family garage · hot-rod shop · auto body / paint · motorcycle
restoration · welding · machine shop · neighborhood blue-collar trades where
the buyer wants HONEST + HANDS-ON + AMERICAN-MADE signals over flashy
marketing or chrome-and-steel industrial.

## Color palette (vintage Americana)

- Background `#1A1714` — warm dark (not pure black)
- Foreground `#F4EDE0` — warm bone
- Primary `#C9501C` — rust orange (CTAs + hazard stripe)
- Secondary `#7A4528` — deep rust-brown (hover / depth)
- Accent `#E89E3C` — warm amber (ref-code stamps + IMG-REF lot tags)
- Border `#2D241D` — warm dark hairline

The hazard stripe keeps the 45° diagonal `repeating-linear-gradient` from
`honest_garage` but pairs rust (`#C9501C`) with dark rust (`#2D241D`) instead
of yellow + black. Same DNA tell, different register.

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

## Design signatures (load-bearing — unchanged from honest_garage)

- **Hazard stripe** — a 4px-tall fixed-top `repeating-linear-gradient(45deg)`
  rust/dark-rust bar above the nav. The vintage-Americana tell.
- **Stencil headings** — hollow-letter Anton text via `-webkit-text-stroke 1px`
  + transparent fill. Used for every section h2.
- **Ref-code labels** — every section is stamped with a JetBrains Mono
  `REF-XXX` / `SVC-XXX` / `BADGE-0X` / `IMG-REF-XXXXX` / `MAP-REF` code, like a
  parts catalog. Sets the work-order, not-marketing tone.
- **Rust accent** — `#C9501C` on a warm-dark `#1A1714` background, used
  sparingly for CTAs, ref codes, and the photo corner tags.
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

Internal Pebble Engine template. Brand placeholder "Rust Belt Garage" is
fictional — no real-business resemblance intended.
