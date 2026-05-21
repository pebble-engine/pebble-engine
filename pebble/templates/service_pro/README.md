# Service Pro — template

**Vibe:** Glow Emerald Dual-Theme. Dark-by-default service-industry marketing site
with a warm cream light mode, glass-morphism navbar, three blurred glow orbs
behind the hero, an infinite marquee, and a shimmer-swept "Call Now" chip above
the phone number.

**Source DNA:** `pest_clean_safe` (see `dna_source.json`).

**Applicable industries:** pest control · lawn care · landscaping · tree service
· carpet cleaning · house cleaning · pressure washing · HVAC · plumbing ·
electrician · solar installer · junk removal · moving company · home inspection
· mold remediation. Any local trade with a phone-number-first conversion model.

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
- Tailwind CSS 3 with HSL custom-property tokens for dual light/dark theme
- Framer Motion for entrance fades + scroll reveals
- Resend for the contact form server action
- Inter (body) + Outfit (display) via `next/font/google`

## License

Internal Pebble Engine template. Brand placeholder "Coastal Pro Services" is
fictional — no real-business resemblance intended.
