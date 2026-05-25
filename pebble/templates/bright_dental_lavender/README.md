# Lavender Lane Dental — bright_dental_lavender variant

Color variant of `bright_dental`. Lavender-cream palette throughout: pale violet bone background, deep plum text (in place of navy), lavender primary CTA (in place of coral), light orchid accents. Intended for sensory-friendly, anxiety-aware, anti-clinical dental practices that want to feel like a spa, not an exam room.

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
