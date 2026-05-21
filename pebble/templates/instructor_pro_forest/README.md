# Instructor Pro Forest — template

**Vibe:** Wilderness Forest Bronze-Gradient. Dark, authority-forward marketing
site for any outdoor-adventure instructor business — wilderness guiding,
backcountry instruction, climbing schools, paddling outfitters, hunter/angler
academies, or other small-group outdoor verticals. Color variant of
`instructor_pro` — same structure and component library, palette + voice
swapped from tactical-urban to outdoor-wilderness.

**Source DNA:** `training_authority` (see `dna_source.json`).

**Applicable industries:** wilderness guide · backcountry guide · climbing
instructor · mountaineering school · kayak / canoe outfitter · fly-fishing
academy · hunting guide · ski touring guide · survival school · adventure
travel · outdoor education. Any guide-led business where certification +
authority + small-group expedition results are the conversion drivers.

## How the template stays customizable

All copy, courses, instructor bio, hours, phone, address, and brand name
live in **one file**: `content/site.ts`. Components import named constants
from there — they never hardcode strings. Swapping to a new customer is a
single-file rewrite.

Empty arrays (`TESTIMONIALS = []`, `GALLERY_IMAGES = []`) are intentional.
The template ships honest by default: components hide sections when their
content is empty rather than inventing fake reviews. The customer fills them
in after launch.

Bracket-placeholder strings (`PHONE = "[BUSINESS PHONE]"`,
`INSTRUCTOR_NAME = "[GUIDE NAME]"`) are intentional too. The
instantiation step replaces them when real data is available — until then
they're visually obvious TODO markers.

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
- Resend for the contact-form server action
- DM Sans (body) + Outfit (display) via `next/font/google`

## Signature DNA elements

- Full-bleed looping hero video under double gradient mask
- Four-line uppercase Outfit-black headline, middle line in warm-metal gradient
- Live bronze pulse-dot eyebrow + floating glass credentials card
- Counter-up Stats section (IntersectionObserver, respects prefers-reduced-motion)
- Course cards with widening left accent bar (4px -> 5px, gray -> bronze /
  amber for featured)
- Centered blockquote on radial-dots overlay (Mission section)
- Bronze shimmer-band animation on CTAs and offer cards
- Subtle warm glow box-shadow on credentials card

## Deploy

Ship to Vercel. `vercel.json` already configured. Set `RESEND_API_KEY`,
`CONTACT_FROM_EMAIL`, and `CONTACT_TO_EMAIL` as environment variables in
the project settings.

## License

Internal Pebble Engine template. Brand placeholder "Northbound Guide Co"
is fictional — no real-business resemblance intended.
