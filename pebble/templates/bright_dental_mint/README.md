# Sage Family Dental — bright_dental_mint variant

Color variant of `bright_dental`. Sage-green palette throughout: soft mint background, deep forest text (in place of navy), sage-green primary CTA (in place of coral), pale mint accents. Intended for calm, holistic, wellness-leaning dental practices where the navy/coral combo feels too sharp.

Multi-page Next.js 14 App Router project:

- `/` — Home (hero + trust strip + services grid + 3-step process + testimonial)
- `/team` — Meet the team
- `/faq` — FAQ accordion + insurance carrier grid + hours
- `/booking` — Appointment request form + map/hours sidebar

## Stack

- Next.js 14 (App Router)
- React 18
- Tailwind CSS v4 via `@tailwindcss/postcss`
- Framer Motion 11
- Resend for contact email (server action)
- Outfit + Inter via `next/font/google`

## Deploy

Standard Next.js 14 deploy. Required env vars:

- `RESEND_API_KEY`
- `CONTACT_FROM_EMAIL`
- `CONTACT_TO_EMAIL`
