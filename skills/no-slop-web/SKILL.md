# No-Slop Web Skill

## Purpose

This skill prevents AI-generated websites from looking AI-generated. Every rule in this file comes from a confirmed pattern observed across multiple real builds. Apply every rule. None are optional.

---

## PHONE NUMBERS — Read this first

**This is the single most common mistake. It appears on every build that doesn't have a real phone number.**

**Rule:** If the client's phone number is not in the brief, use EXACTLY this: `[BUSINESS PHONE]`

- Square brackets
- All caps
- No area code
- No numbers
- Nothing else

**What is forbidden:**
- `(631) 555-0199` — forbidden. 555 numbers are Hollywood fictional placeholders.
- `(516) 555-0198` — forbidden. Same.
- Any number with 555 in the exchange position — forbidden.
- Any phone number you invent — forbidden.
- Any "example" number — forbidden.

555 numbers look real to clients. A client who sees `(631) 555-0199` on their website will think their real number is there. It is not. Use `[BUSINESS PHONE]` every single time, in every location: header, footer, hero CTA, anywhere.

For businesses where a phone number is NOT appropriate (tech companies, SaaS, AI firms, online-only brands): omit the phone entirely. Do not invent one to fill the space.

---

## FORBIDDEN SUBTEXT PHRASES

These sentence constructions appear on thousands of AI-generated websites. They will be recognized immediately as AI output. Do not use any of them:

**Forbidden openers and constructions:**
- "Where [X] meets [Y]." — forbidden. ("Where precision meets tradition." "Where innovation meets excellence.")
- "Your next chapter starts here." — forbidden.
- "Step into [Business] for [adjective] [noun]." — forbidden.
- "Precision meets [anything]." — forbidden. The word "precision" in subtext is a red flag.
- "Elevate your [experience/journey/results]." — forbidden.
- "Discover the [adjective] difference." — forbidden.
- "Experience [adjective] [noun] like never before." — forbidden.
- "We are passionate about [anything]." — forbidden.
- "Your success is our [mission/priority/goal]." — forbidden.
- "[Adjective] solutions for [adjective] results." — forbidden.

**What subtext must do instead:**
- Name a specific place, person, or product.
- State a specific outcome, number, or timeframe.
- Speak to the exact moment the visitor is in right now.
- Richies Plumbing example: *"Family-owned, fully licensed plumbing serving Nassau County. We stand by our work, and we pick up the phone when you call."* — three specific claims.
- Generic fallback if nothing specific is known: use the business category, location, and the primary action. Still more specific than "where precision meets tradition."

---

## FORBIDDEN HEADLINE PATTERNS

Headlines must be specific and arguable. Vague superlatives are forbidden.

**Forbidden words in headlines:**
- "Unrivaled" — forbidden ("Unrivaled Maritime Excellence.")
- "World-class" — forbidden
- "Premier" — forbidden when used alone without specifics
- "Cutting-edge" — forbidden
- "Next-level" — forbidden
- "Unleash your inner [anything]" — forbidden. Every beauty brand uses this.
- "Welcome to [Business Name]" — forbidden. Says nothing.

**Good headlines name something real:**
- A specific problem: "When it breaks, you need it fixed right now."
- A specific standard: "The Standard in Men's Grooming."
- A specific capability: "Architecting the AI Frontier."
- A specific place or name: "Long Island's Only Bait-Station Pest Service."

---

## FORBIDDEN FONTS

**Never use any of these as a primary heading or display font:**

- Inter
- Roboto
- Poppins
- Geist
- Plus Jakarta Sans
- Space Grotesk
- DM Sans
- Nunito
- Lato
- Open Sans

These fonts appear on millions of AI-generated websites. Visitors recognize them subconsciously as "AI output." A distinctive display font is non-negotiable.

**Acceptable display fonts** (not exhaustive):
- Fraunces (editorial serif — warmth + distinction)
- Playfair Display (elegant serif — premium/timeless)
- Syne (geometric — Y2K/bold)
- Manrope (heavy geometric — authority/tech)
- Instrument Serif (refined — modern editorial)
- Canela (luxury serif)
- Bebas Neue (condensed — impact/sport)
- Oswald (condensed — local service/authority)
- Space Mono (monospace — tech/terminal)

**Body fonts:** Inter is acceptable for body text ONLY when paired with a distinctive display font. Never as the sole or heading font.

---

## HERO SECTIONS — A flat background is not acceptable

**Every hero must have a visual element.** Text on a plain solid or flat-gradient background is not a hero. It is a colored div with words in it.

**Required: at least one of the following:**
- A full-bleed photograph (from `/public/images/hero/`)
- A video background (from `/public/videos/`)
- A Three.js / WebGL canvas (when animation intensity calls for it)
- An animated CSS element (see below)
- A particle system or SVG animation

**When no media is provided, use an animated CSS fallback:**
```css
/* Animated mesh gradient — at minimum, do this */
@keyframes gradientShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.hero-bg {
  background: linear-gradient(-45deg, var(--color-dominant), var(--color-secondary), var(--color-accent), var(--color-dominant));
  background-size: 400% 400%;
  animation: gradientShift 12s ease infinite;
}
```

Or use an SVG geometric pattern, an animated grid, a slow-rotating shape — anything that moves and creates visual depth. The hero is the first impression. It cannot be empty.

---

## BACKGROUND COLOR — Light vs Dark

Dark backgrounds are NOT a universal default. The choice of light vs dark must match the business type and emotional direction.

**Default to DARK backgrounds for:**
- Premium/luxury brands (yachts, fashion, high-end services)
- Tech, AI, SaaS companies
- Nightlife, entertainment, music
- Photography portfolios
- "Premium, high-end" or "Impressed and curious" emotional direction

**Default to LIGHT backgrounds for:**
- Local service businesses (plumbing, pest control, HVAC, cleaning)
- Health and wellness (dentist, therapist, yoga, massage)
- Food and hospitality (bakery, café, restaurant)
- Family-focused or community businesses
- "Calm and comfortable" or "Trusting and confident" emotional direction

**A plumber on a near-black background looks like a hacker collective.** A bakery on a dark background looks like a nightclub. Match the temperature to the category.

Light background palette examples for local service:
- Dominant: warm cream (#F8F4EF) or cool white (#F7F9FC)
- Surface: pure white (#FFFFFF)
- Text: dark charcoal (#1A1A1A)
- Accent: the brand color pops MORE on light backgrounds

---

## BOOKING TOOLS — Category-locked

Each booking tool is appropriate for specific business categories ONLY. Cross-category recommendations are a confirmed failure pattern.

| Tool | Use for | Never use for |
|---|---|---|
| Booksy | Hair salons, barbers, spas, nail salons, beauty services | Plumbing, pest control, AI firms, restaurants, retail |
| Housecall Pro / Jobber | Plumbing, HVAC, electrical, pest control, cleaning, landscaping | Beauty, tech, coaching, food |
| Mindbody | Fitness studios, yoga, pilates, wellness | Everything else |
| Calendly / Cal.com | Tech, AI, consulting, coaching, professional services | Emergency services, food, retail |
| Jane App | Healthcare, physiotherapy, mental health | Everything else |
| OpenTable / Resy | Restaurants | Everything else |
| Booksy for a plumbing company | NEVER | ALWAYS WRONG |
| Calendly for a restaurant | NEVER | ALWAYS WRONG |

**Decision process:** Read the business type first. Find the matching row. Use the tool in that row. If the brief specifies an existing system, use that instead and do not recommend a different one.

---

## SECTION LAYOUT — Break the default

The following section order is the AI default and must not be used:

**Forbidden layout formula:**
> Hero → 3 feature cards → testimonials → pricing → CTA → footer

**Rules:**
- Never put three equal-width cards in a row as the primary feature section. If features need to be displayed, use: numbered list, alternating left-right, staggered grid, or a single large featured item with smaller supporting items.
- Testimonials must not be invented. If real ones are not provided, omit the section.
- Section spacing should vary — not every section has the same padding.
- At least one section should break the standard left-right-centered flow.

---

## SplitText — Word break protection

When using GSAP SplitText on heading elements, mid-word line breaks are a confirmed rendering bug. Apply this to every heading that uses SplitText:

```tsx
// Heading wrapper — prevents "Q / ueen" style breaks
<h1
  className="font-display text-6xl leading-none"
  style={{ wordBreak: 'keep-all', overflowWrap: 'normal', hyphens: 'none' }}
>
  {/* SplitText targets this */}
</h1>
```

If the heading is long enough that `keep-all` still causes line breaks, use `type: "words,lines"` in SplitText instead of `type: "chars"`. Character-level splits on headings that wrap will always produce word breaks at viewport edges.

---

## Specific copy words that are forbidden everywhere

These words must not appear anywhere in generated copy:

- "solutions" — always vague
- "innovative" / "innovation" — always vague
- "leverage" — corporate filler
- "seamless" — meaningless
- "cutting-edge" — meaningless
- "world-class" — unverifiable
- "bespoke" — overused in luxury copy (see BenYachts: "bespoke cognitive models")
- "curated" — overused in beauty/retail copy
- "passionate about" — tells the visitor nothing about the business
- "synergy" — forbidden, always
- "holistic" — unless it is literally a holistic medicine practice

**Replacement strategy:** Every time you would use one of these words, replace it with a specific detail. "Innovative pest control solutions" → "Bait-station treatment that eliminates the colony, not just the surface pests."
