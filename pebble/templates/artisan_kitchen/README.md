# artisan_kitchen — Pebble Engine template

Tactile, warm-cream Next.js 14 (App Router) template derived from the
`bakery_warm` DNA. Placeholder brand: **Maple & Hearth** (Greenpoint, Brooklyn).

## Source DNA

- DNA: `pebble/templates/dna/bakery_warm.json`
- This template inherits the design language but uses an **original, generic
  brand** so it can be instantiated for any bakery / cafe / restaurant / deli
  / florist / candle maker / small-batch food business.

## Content tokenization

ALL static content lives in **one file**:

- `content/site.ts` — every brand string, address, headline, menu item,
  hours block, social handle. Exported as named constants.

Components import from `content/site.ts` and never hard-code business
content. To instantiate this template for a customer, the engine makes one
focused LLM call that rewrites only `content/site.ts` — components stay
stable.

## Design language

- **Fraunces** (display, opsz axis, italic-capable) + **Inter** (body) via
  `next/font/google`
- Warm cream / mustard / vermilion palette with sage and toasted-honey
  accents (11 tokens in `tailwind.config.ts` + CSS vars in `globals.css`)
- Liquid-glass cards (`liquid-glass`, `liquid-glass-strong`) with
  backdrop-blur 16-20px
- Gradient pill CTAs (`btn-primary`) — 135deg crust -> crust-soft, soft
  drop shadow, scale-on-hover
- Tilted hero photo card (-3deg) with floating est-style badge breaking
  the frame
- SVG fractalNoise grain overlay at ~3% opacity, multiply blend, site-wide
  via `body.grain-overlay`
- Decorative blurred blobs with `animate-blob-bounce` keyframe
- 1440px max container, 80px desktop / 20px mobile horizontal margin,
  120/64px section gap

## Sections shipped (homepage)

1. **Hero** — two-column. Left: eyebrow chip + Fraunces 2-line headline
   (ink line + crust-soft italic line) + body + dual CTAs. Right: tilted
   photo card with floating "Baked daily" badge. Background: warm radial
   gradient + two pulsing blobs.
2. **Features** — three rounded-4xl cards on alt-cream with emoji icons
   (deliberately analog), Fraunces titles, one-line bakery promises.
3. **About** — square photo left, story right with chip + headline +
   multi-paragraph body + secondary CTA.
4. **Menu** — filterable masonry (All / Bread / Pastry / Coffee / Sweets).
   Each tile is a `MenuCard` with photo, name, description, price, and a
   small category chip. CSS columns + Framer Motion layout transitions.
5. **Contact** — split. Left: liquid-glass info card with Visit / Hours
   table / Reach blocks. Right: form card with gradient submit.

Plus three additional routes: `/menu`, `/about`, `/contact`.

## Anti-slop notes

- `HERO_RATING = null` by default — the rating chip only renders when real
  data is provided. No invented "5.0 (237 reviews)" placeholders.
- `MENU_ITEMS` ships with 10 generic bakery items (sourdough, croissants,
  espresso, etc.) — replaceable but designed so the page never looks empty.
  The Menu section returns `null` if the array is emptied.
- `PHONE`, `ADDRESS_LINE_1`, `SOCIAL.instagram` are bracketed placeholders
  (`[BUSINESS PHONE]`, etc.) — the rewrite step must fill or remove them,
  never fabricate.
- No fake testimonials. No invented founding years. No "11 years in
  business." If a metric isn't real, it doesn't ship.

## Stack

- next 14.2 (App Router, Server Actions)
- react 18.3 + react-dom 18.3
- typescript 5.7
- tailwindcss 3.4 + autoprefixer + postcss
- framer-motion 11 — fade-in cascades, viewport reveals, layout
  transitions for menu filter, `useReducedMotion` aware
- resend 4 — `app/actions/contact.ts` server action
- clsx + tailwind-merge — `lib/cn.ts` helper

## Develop

```bash
npm install
npm run dev          # http://localhost:3000
npm run type-check   # tsc --noEmit
npm run build        # next build
```

## Deploy

`vercel.json` is preset for Next.js + iad1. Push to a Vercel-connected
repo or run `vercel`. Set `RESEND_API_KEY`, `CONTACT_FROM_EMAIL`,
`CONTACT_TO_EMAIL` in Vercel project env.
