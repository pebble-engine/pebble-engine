# luxe_beauty_aubergine — Pebble Engine template

Editorial luxury-beauty Next.js 14 (App Router) template derived from the
`beauty_ethereal` DNA. **Aubergine color variant** of `luxe_beauty` —
swapped palette + evening-luxury tonal voice; identical section structure.
Placeholder brand: **Atelier Vesper**.

## Palette

- Background: `#FAF7F2` (champagne ivory)
- Foreground: `#1B0F1F` (deep aubergine-black)
- Primary: `#4A1A4D` (deep aubergine purple)
- Secondary: `#7A3D7F` (mid aubergine)
- Tertiary / CTA: `#B8924A` (warm champagne gold)
- Border: `#D4CFC8` (soft taupe)
- Selection: aubergine primary at 20% opacity

Tonal register: mysterious + evening + intimate (vs. `luxe_beauty_rose`
which reads warm + feminine + inviting). Both premium, different
psychological positions.

## Source DNA

- DNA: `pebble/templates/dna/beauty_ethereal.json`
- Source brand it was distilled from: Rich Queen Beauty Supply
- This template shares the design language but uses an **original, generic
  brand** so it can be instantiated for any luxury beauty / cosmetics /
  skincare / spa / fragrance business.

## Content tokenization (the important bit)

ALL static content lives in **one file**:

- `content/site.ts` — every brand string, address, headline, copy block,
  category list, social handle. Exported as named constants.

Components import from `content/site.ts` and never hard-code business
content. To instantiate this template for a customer, the engine makes one
focused LLM call that rewrites only `content/site.ts` — components stay
stable.

## Design language

- Bodoni Moda (display, italic-capable) + Manrope (body) + Pinyon Script
  (cursive accent) via `next/font/google`
- Material Design 3 surface tokens — light-mode native (champagne ivory)
- Glass-card backdrop-blur surfaces; vapor-shadow utility for floating
  elements
- Italic Bodoni for editorial headlines, Pinyon Script for accent
  whispers, Manrope for body
- 1440px max container, 80px desktop / 20px mobile horizontal margin,
  120/64px section gap

## Sections shipped

Homepage assembles 7 sections in order:

1. **Hero** — circular logo orb on twilight aubergine/champagne cloud bg,
   italic Bodoni headline, Pinyon Script cursive accent, dual rounded-full
   CTAs
2. **ValuePillars** — 3-column grid of brand promises
3. **CategoryGrid** — 2x2 stylized image-card grid of product categories
4. **FeaturedCollection** — horizontal product row; renders nothing when
   `FEATURED_PRODUCTS` is empty (anti-slop)
5. **Editorial** — magazine-style full-bleed image + offset glass text
   panel
6. **Testimonials** — 3-column glass review cards; renders nothing when
   `TESTIMONIALS` is empty (anti-slop)
7. **Contact** — split-pane address+hours / glass form

Plus three additional routes: `/about`, `/shop`, `/contact`.

## Deviations from DNA — intentionally simplified

The DNA describes several features we did NOT port. Each call:

- **Three.js 3D WebGL runway carousel** — DNA spec calls for an ornate
  gold-extruded 3D carousel with ACES tone-mapping and a gold particle
  system. SKIPPED for this template (too complex for V1; future
  enhancement). A static 4-tile CategoryGrid takes its place.
- **Sky video as fixed background layer** — replaced with a soft cloud
  gradient (`ethereal-bg` utility) + low-opacity hero photo. Cheaper,
  no asset dependency.
- **Splash intro video overlay** — skipped; first-page load goes
  straight to hero.
- **Pixie-dust particle generator** — skipped; the logo orb sits on
  vapor-shadow instead of an animated particle field.
- **Announcement bar / promo bar** — skipped (commerce-specific; can
  be added per-customer).
- **Headless ecommerce hash-routed SPA** (cart, product detail, filter
  drawer, sticky checkout) — replaced with simple `/shop` category
  landing. Real commerce is per-customer.

## Stack

- next 14.2 (App Router, Server Actions)
- react 18.3 + react-dom 18.3
- typescript 5.7
- tailwindcss 3.4 + autoprefixer + postcss
- framer-motion 11 — fade-in cascades, viewport reveals, reduced-motion
  aware via `useReducedMotion`
- resend 4 — `app/actions/contact.ts` server action
- clsx + tailwind-merge — `lib/cn.ts` helper

## Deploy

`vercel.json` is preset for Next.js + iad1. Push to a Vercel-connected
repo or run `vercel`. Set `RESEND_API_KEY`, `CONTACT_FROM_EMAIL`,
`CONTACT_TO_EMAIL` in Vercel project env.

## Develop

```bash
npm install
npm run dev          # http://localhost:3000
npm run type-check   # tsc --noEmit
npm run build        # next build
```

## Anti-slop notes

- `FEATURED_PRODUCTS = []` and `TESTIMONIALS = []` by default. Sections
  unmount when their data is empty. Never invent products, customer
  counts, founding years, or quotes.
- Phone, email, and address are bracketed placeholders (`[BUSINESS
  PHONE]`, etc.) — the rewrite step must fill or remove them, never
  fabricate.
