# ink_studio_oxblood — Pebble Engine template

Warm-gothic blackletter gold-glow Next.js 14 (App Router) template derived
from the `tattoo_studio` DNA. Placeholder brand: **Cathedral Ink Society**.

This is the **warm** color variant of `ink_studio`. Same structure,
components, content shape — swapped palette + tonal voice. Where the
original is cold-gothic (pitch-black + cold gold + Brooklyn atelier), this
one is warm-gothic (oxblood-charcoal + parchment + warmed gold +
cigar-lounge / whiskey-house / cathedral old-world voice).

## Source DNA

- DNA: `pebble/templates/dna/tattoo_studio.json`
- Source brand it was distilled from: Bound By Flesh
- This template shares the design language but uses an **original, generic
  brand** so it can be instantiated for any tattoo parlour / cigar lounge
  / whiskey house / leather workshop / barber / speakeasy that wants the
  oxblood + warm-gold + blackletter aesthetic.

## Content tokenization (the important bit)

ALL static content lives in **one file**:

- `content/site.ts` — every brand string, address, headline, copy block,
  gallery item, service tier. Exported as named constants.

Components import from `content/site.ts` and never hard-code business
content. To instantiate this template for a customer, the engine makes one
focused LLM call that rewrites only `content/site.ts` — components stay
stable.

## Design language

- **UnifrakturCook** (blackletter display) + **Source Sans 3** (body) +
  **Bebas Neue** (uppercase accent) via `next/font/google`
- Warm oxblood-charcoal `#1A0E0E` background, parchment `#F3E9D7`
  foreground, warmed-gold `#B8924A` accent, deep-oxblood `#8B1A1A` spark
- Warm dark border `#3D2020` throughout
- Gold-glow text-shadow on all hero / booking headlines (stacked
  text-shadow at 20px + 40px) — now in warmed gold
- Gold-border-glow utility (1px gold border + inset + outer shadow) wraps
  the about portrait + the carousel center image
- Animated SVG `fractalNoise` grain overlay (fixed, low opacity, 10-step
  translate keyframe — disabled by `prefers-reduced-motion`)
- Scratchy 12-stop linear-gradient divider above the footer bottom strip
- Gold wavy SVG dividers between major sections
- Selection: oxblood at 30% opacity
- 1440px max container, 80px desktop / 20px mobile horizontal margin,
  128px desktop / 72px mobile section gap

## Sections shipped

Homepage assembles 8 elements in order:

1. **Hero** — full-bleed dark backdrop with looping video (poster
   fallback), giant UnifrakturCook wordmark with gold-glow, dual gold
   CTAs (outline + filled)
2. **GoldWavyDivider** — decorative double-stroke gold SVG
3. **GalleryStrip** — three-column portfolio preview; center card gets
   gold border + corner brackets (DNA carousel center-image treatment).
   Links out to the dedicated `/gallery` page.
4. **Services** — three-column "the craft" block (bespoke / house flash /
   cover-ups) on elevated card surface
5. **GoldWavyDivider**
6. **About** — two-column portrait (gold border + corner brackets) +
   text block
7. **Testimonials** — three-column quote cards; **renders nothing** when
   `TESTIMONIALS` is empty (anti-slop default)
8. **BookingCta** — full-bleed video-background section with gold
   top+bottom rules, centered blackletter h2 + filled gold CTA

Plus three additional routes: `/about`, `/gallery`, `/contact`.

## Deviations from DNA — intentionally simplified

The DNA describes several features we did NOT port. Each call:

- **Click-to-enter intro overlay with sessionStorage gate** — skipped.
  Adds JS bundle weight + friction for cold visitors. The Hero already
  ships the cinematic video backdrop, so the first impression is intact.
- **Statue-of-Liberty hand-illustrated SVG mascot** — skipped. The
  source-brand mascot is regional to East Islip / NY and would have to
  be redesigned per customer industry. Future enhancement: a
  per-template mascot slot.
- **Auto-advancing three-column image carousel** — replaced with a
  static three-up `GalleryStrip` + a full `/gallery` grid. Easier to
  maintain, no JS dependency for the headline section, accessible by
  default.
- **Three.js / WebGL effects** — none in this template; the cinematic
  feel comes from video + gold-glow + grain.

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

- `TESTIMONIALS = []` by default. Section unmounts when the array is
  empty. Never invent customer quotes, founding years, or client lists.
- Phone, email, and address are bracketed placeholders (`[BUSINESS
  PHONE]`, etc.) — the rewrite step must fill or remove them, never
  fabricate.
- `GALLERY_ITEMS` ships with placeholder Unsplash imagery + generic
  `Untitled I`/`II` titles so the section is visually complete on first
  paint. The customer replaces these with their real portfolio post-launch.
