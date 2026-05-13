# Website Build Brief -- Baez HVAC

You are building a complete, production-quality website. Read every section of this brief before writing a single line of code. The skills embedded in this brief contain thousands of words of specific, researched direction. Apply all of it.

---

## 1. Project Overview

- **Business name:** Baez HVAC
- **Type of business:** HVAC- Heating and Cooling
- **Location / service area:** Suffolk County
- **Primary visitor action:** portfolio / gallery of past work; business presence (hours, location, contact)
- **Booking or payment system:** None yet -- recommend the best option for this business type.

---

## 2. Visual Reference & Inspiration

A reference site has been provided: **https://dribbble.com/shots/27365521-Greyson-Web-Exploration**

Browse this URL before writing any code. Extract and apply:
- Dominant colors and color temperature (warm vs cool, light vs dark)
- Typography weight, rhythm, and personality
- Spacing philosophy -- how tight or generous the layout feels
- Animation style and intensity
- Layout approach -- grid, asymmetric, editorial, etc.
- Overall brand feeling

**Important:** Abstract the FEELING, not the layout. Do not copy structure or content from this site. Use it to calibrate the aesthetic direction only. If this is a Dribbble link, extract the visual composition and color mood.

---

## 3. Visitor Experience Direction

**How visitors should feel:** Trusting and confident
**Visual experience level:** Cinematic scrolling — big visual moments



# Visitor Experience Skill

## Purpose

This skill translates two simple business-owner answers — how they want visitors to feel, and what kind of visual experience they want — into specific, actionable design direction. Every typography choice, motion speed, copy tone, color decision, and library selection must be consistent with the combination of these two answers.

Read both answers, find the matching interpretations below, and apply them to every section of the build. These settings override generic defaults. If there is a conflict between this skill and a "standard" approach, this skill wins.

---

## Emotional Direction Interpretations

The emotional direction answer defines the underlying personality of the entire site. It governs: typography weight and rhythm, copy tone, color saturation and warmth, motion speed, spacing generosity, and the overall brand feeling.

---

### Trusting and Confident

**The goal:** The visitor should feel reassured within the first 3 seconds. Doubt must be eliminated before it forms.

**Typography:**
- Clean, legible heading font — geometric or humanist sans-serif with strong weight contrast
- No decorative or experimental typefaces
- Body text at comfortable size (17–18px), generous line height (1.7)
- Font weight contrast: bold headings, regular body, no thin weights

**Motion:**
- Calm, measured entrance animations — nothing flashy or fast
- GSAP ease: `power2.out` or `expo.out` — smooth arrival, no bounce
- Duration: 0.6–0.9s per element
- No aggressive scroll effects — subtle `opacity + translateY` only
- Stagger reveals feel deliberate, not urgent

**Copy tone:**
- Direct and specific — numbers, names, credentials, service areas
- No vague superlatives ("best in class", "world-class")
- Third-person proof: testimonials, statistics, years in business
- Headlines name what the visitor gets, not how the company feels about itself
- Short sentences. No filler.

**Color:**
- Calm dominant color — deep navy, forest green, slate, or warm charcoal
- One clean accent — not aggressive. A trustworthy blue, a grounded green, or a warm amber
- Never: neon, electric, or saturated backgrounds
- Light sections dominate — dark sections used sparingly and purposefully

**Layout:**
- Strong visual hierarchy — the eye must never be confused about where to go
- Generous whitespace between sections
- Credibility signals (badges, review counts, certification logos) near CTAs
- No clutter. Every element earns its place.

**Social proof placement:**
- Above the fold or immediately below the hero
- Real names, real companies, specific outcomes
- Star ratings + quote + name + role format minimum

---

### Excited and Inspired

**The goal:** The visitor should feel energy, momentum, and possibility within the first scroll.

**Typography:**
- Bold, expressive heading font — extended or condensed width, high impact
- Headlines can be large (6rem+) — let them dominate
- Accent color used in headlines for emphasis words
- Body text tight but readable (16–17px, 1.6 line height)

**Motion:**
- Energetic entrance — text slides in with momentum, not just fades
- GSAP ease: `power4.out` or `back.out(1.4)` — arrival has punch
- Duration: 0.5–0.7s — fast enough to feel alive
- Stagger: 0.08–0.12s — rapid sequence that builds energy
- Hero should have an entrance timeline that builds section by section

**Copy tone:**
- Aspirational and outcome-focused
- Second person ("You're about to..." "Your next chapter starts here")
- Verbs over nouns — action, movement, possibility
- Short punchy headlines. Long-form copy in subtext only.

**Color:**
- High contrast palette — dark background with bright accent, or bright background with bold type
- Accent color used boldly — not just on buttons, but in headlines, dividers, and highlights
- Gradient accents acceptable but not purple-to-blue defaults
- Energy lives in saturation and contrast, not decoration

**Layout:**
- Asymmetric — not centered everything
- Breaking the grid occasionally: overlapping elements, unexpected alignment
- Large imagery or bold color blocks between text sections
- Sections feel like chapters building toward a climax

---

### Impressed and Curious

**The goal:** The visitor should feel like they've discovered something special. Intrigue over information.

**Typography:**
- Distinctive display font — editorial serif, variable font, or highly specific sans-serif
- Headlines used sparingly but with maximum impact
- Mixing weights within a heading for emphasis
- Generous letter spacing on uppercase labels

**Motion:**
- Cinematic reveals — elements emerge rather than appear
- GSAP ease: `expo.out` or `sine.inOut` — elegant, not mechanical
- Scroll-triggered image masks (clip-path reveals)
- Text reveals line-by-line (SplitText pattern)
- Parallax on background images — layers create depth
- Hover states are rich: image zooms, color shifts, revealed text

**Copy tone:**
- Less is more — powerful short lines over comprehensive explanations
- Questions and provocations: "What would it mean if...?"
- Elevated vocabulary — not academic, but considered
- White space in copy is intentional — short paragraphs breathe

**Color:**
- Sophisticated palette — deep, rich dominants with precise accents
- Neutrals that feel intentional (warm black, off-white, putty)
- One unexpected accent that creates intrigue
- Avoid safe palettes — something specific to this brand

**Layout:**
- Editorial — full-bleed images, unexpected column counts
- Text and images overlap intentionally
- Horizontal scroll sections for gallery moments
- Each section feels designed, not templated

---

### Calm and Comfortable

**The goal:** The visitor should feel at ease immediately. No friction, no pressure, no confusion.

**Typography:**
- Warm, approachable font — humanist sans-serif or friendly serif
- Never: angular, ultra-condensed, or aggressive weights
- Comfortable sizes, relaxed line height (1.8)
- Soft weight contrast — regular and medium, avoiding heavy/black weights

**Motion:**
- Gentle — almost invisible at first glance
- GSAP ease: `sine.inOut` or `power1.out` — nothing sharp
- Duration: 0.8–1.2s — slower feels more relaxed
- Minimal stagger — sections arrive softly, not dramatically
- No scroll-locked sequences or pinned sections

**Copy tone:**
- Warm and conversational — first or second person where appropriate
- Empathy first: acknowledge the visitor's situation before selling
- Short paragraphs, friendly vocabulary
- CTAs are invitations, not demands: "Let's talk" not "GET STARTED NOW"

**Color:**
- Warm, muted palette — creams, warm grays, sage, terracotta accents
- Never: high saturation or electric colors
- Background whites should be warm (F5EFE6) not cool (FFFFFF)
- One soft accent — dusty rose, warm amber, muted teal

**Layout:**
- Generous padding — sections breathe, nothing feels cramped
- Rounded corners throughout (but not uniform — vary intentionally)
- Imagery: natural, human, everyday — no dramatic lighting or high-contrast shots
- Form fields: spacious and labeled clearly, not compact or complex

---

### Premium, High-End, or Elite

**The goal:** The visitor should feel like they've entered a different category. Not just better — fundamentally different.

**Typography:**
- Refined serif or high-quality variable font — Fraunces, Canela, Tiempos, PP Hatton
- Headlines: large, light or thin weight — luxury lives in restraint
- Generous letter spacing on all caps elements
- Body: precise, not conversational — slightly formal

**Motion:**
- Slow and deliberate — luxury never rushes
- GSAP ease: `expo.inOut` or custom cubic bezier — nothing standard
- Duration: 1.0–1.5s — let each element land with gravity
- Stagger: 0.15–0.2s — measured pace
- Horizontal scroll sections for portfolio/product reveals
- Mouse-follow effects if appropriate
- Cursor customization (hide default cursor, replace with brand dot)

**Copy tone:**
- Restrained — say less, mean more
- No superlatives — the quality is self-evident
- Third person where appropriate for distance and authority
- Headlines are statements of fact, not sales claims
- Omit what doesn't need to be said

**Color:**
- Monochromatic or near-monochromatic — one dominant, minimal accent
- Black and off-white with a single precise accent
- Never: multiple competing accent colors
- Dark mode default often appropriate

**Layout:**
- Dramatic whitespace — content is an island in space
- Full-bleed moments between tight content sections
- Typography IS the design — not a vehicle for information
- Minimal navigation — trust that visitors will seek what they need

---

## Visual Experience Interpretations

The visual experience answer defines the animation intensity, interaction richness, and technical complexity of the build. It governs: which libraries to use, how many scroll effects are appropriate, whether Three.js is warranted, and what the performance budget is.

---

### Smooth and Professional — Subtle Animations

**Animation intensity:** Low to medium. The site feels polished, not static, but animation never distracts.

**Libraries:** GSAP core + ScrollTrigger. No Three.js. Lenis for smooth scroll.

**Required animations:**
- Hero entrance: `opacity + translateY` staggered timeline, 0.6s per element
- Section reveals: `fromTo` with ScrollTrigger, `start: "top 80%"`, `toggleActions: "play none none none"`
- Hover states: subtle color shift, underline reveal, or slight scale (1.02) on cards
- Button hover: background fill animation or color transition only

**Avoid:**
- Scroll-scrubbed sequences (elements tied to scroll position)
- Pinned sections
- Parallax that shifts more than 15px
- Page transitions beyond a simple opacity fade
- Three.js or WebGL

**Performance target:** Lighthouse performance score 90+ on mobile.

---

### Cinematic Scrolling — Big Visual Moments

**Animation intensity:** High. The scroll itself is the experience. Sections feel like scenes.

**Libraries:** GSAP + ScrollTrigger (required). Lenis (required). Three.js only if concept warrants.

**Required animations:**
- Hero: full entrance timeline with layered reveals — eyebrow → heading (SplitText) → sub → CTA → background element
- At least one scroll-scrubbed sequence (element properties tied to scroll position)
- At least one pinned section with `scrub: 1` and `anticipatePin: 1`
- Parallax on hero background: `yPercent: -30` scrubbed with scroll
- Image reveals: clip-path animation (`inset(0 100% 0 0)` to `inset(0 0% 0 0)`)
- Text: SplitText line-by-line reveals
- Section transitions: overlapping elements create depth as scroll progresses

**iOS adjustments:**
- All pinned sections require `anticipatePin: 1` and `scrub: 1`
- `ScrollTrigger.normalizeScroll(true)` is non-negotiable
- Reduce parallax intensity to 50% on mobile

**Performance target:** Lighthouse 80+ on mobile. Some trade-off acceptable for cinematic quality.

---

### Interactive and Playful — Hover Effects

**Animation intensity:** Medium. The site responds to the user. Interactions feel tactile and alive.

**Libraries:** GSAP + Framer Motion for component transitions. Lenis.

**Required interactions:**
- Card hover: image zoom (scale 1.05 with overflow hidden) + content reveal
- Button hover: magnetic effect or fill animation
- Navigation hover: underline draws in, color shifts
- Custom cursor: replace browser cursor with brand-colored dot that scales on hover
- At least one micro-interaction per section: a number that counts up, a progress bar that fills, an element that follows mouse
- Gallery: lightbox with smooth Framer Motion transitions

**Page transitions:** Framer Motion `AnimatePresence` with slide or fade between pages.

**Mobile:** Hover effects convert to tap-triggered animations. Custom cursor disabled on touch devices.

---

### High-End Product or Brand Showcase

**Animation intensity:** Medium-High. The product is the hero. Every animation serves the product.

**Libraries:** GSAP + ScrollTrigger. Framer Motion for product reveal transitions. Lenis.

**Required animations:**
- Product hero: large imagery entrance, parallax background, overlay text reveal
- Feature sections: image switches as user scrolls (scroll-driven product views)
- Comparison sections: before/after slider with drag interaction
- Gallery: grid that expands to full-screen with smooth Framer Motion transition
- Product cards: hover reveals secondary image, price appears, CTA slides up
- Testimonial carousel: smooth Lenis-aware slide

**Content requirements:**
- Image slots clearly defined for hero, product detail, lifestyle, feature highlights
- `/public/images/products/` folder required
- All image slots have aspect-ratio containers that degrade gracefully to gradient if no image provided

---

### 3D, Motion-Heavy, or Experimental

**Animation intensity:** Maximum. The site IS the experience.

**Libraries:** GSAP + ScrollTrigger (required). Three.js + React Three Fiber (required). Lenis (required). `@react-three/drei` for helpers.

**Required elements:**
- At least one Three.js canvas — hero background, floating 3D object, or scroll-driven 3D scene
- GSAP scroll-driven 3D rotation (mesh rotation tied to scroll position)
- Particle system or geometry animation for ambient movement
- SplitText headline reveal with 3D transform (`rotateX` or `perspective`)
- At least one scroll-pinned section with scroll-scrubbed 3D progression

**iOS requirements (non-negotiable for Three.js):**
- `dynamic import` with `ssr: false` — always
- `dpr={[1, 2]}` on Canvas — never higher
- `antialias: false` on Canvas gl
- WebGL context lost/restored event handlers
- All geometries and materials disposed on unmount
- Mobile fallback: if `navigator.deviceMemory < 4`, render static image instead of Three.js canvas

**Performance target:** Lighthouse 70+ on mobile. Quality over score for this category.

---

## Combined Direction Examples

### Trusting + Smooth and Professional
Classic professional service website. Law firm, accountant, dentist. Calm entrance animations, strong trust signals, minimal interaction. No Three.js. GSAP reveals only.

### Excited + Cinematic Scrolling
Sports brand, fitness coaching, event company. Bold hero timeline, scroll-pinned sections, SplitText reveals, energetic color palette. GSAP heavy, no Three.js unless specifically warranted.

### Impressed + Cinematic Scrolling
Fashion, architecture, creative agency. Editorial layout, horizontal scroll moments, clip-path image reveals, slow deliberate motion. The most demanding build — allow extra sections.

### Calm + Interactive and Playful
Therapy practice, wellness brand, family service. Gentle card hover effects, soft micro-interactions, warm palette. Framer Motion for page transitions, GSAP for entrance only.

### Premium + 3D / Experimental
Luxury product, high-end architecture, collector's item. Three.js canvas in hero, scroll-driven 3D, dramatic motion pace. Full iOS safety checklist required.

---

## What NOT to Do Regardless of Answers

- Do not use generic hover: box-shadow appears on card
- Do not animate everything — unrelated elements should be still
- Do not use `will-change: transform` on more than 5 elements simultaneously
- Do not build scroll effects that fight iOS rubber-band scrolling
- Do not skip the `prefers-reduced-motion` media query
- Do not build an animation that causes layout shift (CLS)
- Do not use Three.js if the budget is "Smooth and Professional" — overkill kills performance
- Do not mix Framer Motion and GSAP on the same element — they fight over transform values


Apply the matching interpretations from the Visitor Experience Skill above to EVERY decision:
- Typography weight, rhythm, and size
- Motion speed, easing, and intensity
- Copy tone and vocabulary
- Color saturation and warmth -- light vs dark background
- Layout density and whitespace
- Which animation libraries are appropriate
- Whether Three.js is warranted

These two settings override all generic defaults.

---

## 4. Additional Context

Visual feel: Cinematic 3D & WebGL

---

## 5. No-Slop Rules


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


---

## 6. Business Intelligence


# Business Intelligence Skill

## Purpose

Provide the engine with deep, pre-researched knowledge about business website
patterns so that a 5-question brief produces output as good as a 15-question
brief. When this skill is loaded, the engine does NOT need to ask the business
owner about their target customer, their trust signals, their CTA hierarchy, or
their recommended tech stack — it already knows these things from the business
type and the visitor action. The questions focus the engine; this skill drives it.

---

## How the Engine Uses This Skill

When a brief arrives with a business type and a visitor action, the engine:

1. Identifies the business category below
2. Applies the conversion principles for that category
3. Selects the appropriate booking/payment implementation
4. Chooses trust signals and page structure for that category
5. Writes copy that speaks to that category's customer psychology

This skill overrides generic web design defaults. Local plumber sites are built
differently from law firms. Bakeries are built differently from HVAC companies.
The engine reads the category and builds accordingly.

---

## Business Categories and What They Need

### Local Service (pest control, plumbing, HVAC, electrical, cleaning, landscaping, roofing, painting, locksmith)

**Customer psychology:** Urgency and trust. They're usually searching because something is broken or they're anxious. They want proof you're legitimate and a way to contact you in the next 30 seconds.

**Page structure:**
- Hero: Service area + phone number above fold. Big. Not hidden.
- Second section: The specific problem you solve + proof you've solved it (photos, numbers, years).
- Services list: Specific, not vague. "German cockroach treatment" not "pest solutions."
- Service area: Map or clear city/region list. If they don't see their town, they leave.
- Social proof: Real reviews, star rating count, Google/Yelp badge if available.
- Final CTA: Second call prompt. "Still here? Call us: [number]."
- Footer: License number, insurance badge, BBB if applicable.

**Copy rules:**
- First sentence names the problem, not the company.
- Use the owner's name or face. People hire people, not logos.
- "Family owned" and years in business are trust signals worth using.
- Emergency availability is a conversion multiplier — if they offer it, it leads.
- NEVER: "solutions," "innovative," "leading provider," "world-class service."

**CTA hierarchy:** Call now > Book online > Get a free estimate
**Booking:** Square Appointments, Jobber, Housecall Pro, ServiceTitan, or phone-primary (if owner prefers)
**Payment:** Stripe, Square, or collect on-site — offer both card and cash

---

### Professional Services (lawyer, accountant, financial advisor, therapist, consultant, architect, engineer)

**Customer psychology:** Trust and credibility. They're making a high-stakes decision about who to trust with something important. They're reading carefully. They want to know who you are, what your credentials are, and that you've done this before.

**Page structure:**
- Hero: Specific practice area + one-line outcome statement. Not generic.
- Who it's for: Narrow down the client type early. "We work with small business owners in Suffolk County" is better than "we serve all clients."
- How it works: 3-step process. Consultation → work → outcome. Reduces perceived friction.
- Credentials: Bar membership, CPA designation, years practicing, notable cases/work (within ethics rules).
- Social proof: Written testimonials preferred over star ratings for professional trust.
- FAQ: Pre-empts the top 5 questions every prospect asks. Reduces email/phone volume.
- CTA: Schedule a free consultation. A clear, low-commitment first step.

**Copy rules:**
- Specificity builds more trust than authority claims. "We've helped 300 small businesses in Nassau County" > "We're the area's leading firm."
- Never invent testimonials. Real or omit.
- Write to the prospect's fear, not their aspiration. "Facing an audit?" not "Achieve financial success."

**CTA hierarchy:** Schedule consultation > Free 15-minute call > Send a message
**Booking:** Calendly (simplest), Acuity Scheduling (more professional feel), Jane App (healthcare)
**Payment:** Invoiced after engagement; Stripe if retainer/online payment needed

---

### Health and Wellness (dentist, chiropractor, physical therapist, personal trainer, yoga studio, med spa, massage)

**Customer psychology:** Comfort and trust. They're putting their body or health in your hands. Warmth matters more here than in most categories. They also want frictionless booking — they've decided to go; make it easy.

**Page structure:**
- Hero: What transformation you provide + a warm photo of the space or provider.
- Services: Card layout works here. Clear prices help conversion when appropriate.
- Meet the team: Photos and short bios. Patients pick providers based on personality.
- Location + hours: Always visible. Missing hours is a common conversion killer.
- Booking widget: Inline, not a button that opens a new tab. Friction kills bookings.
- Insurance / accepted payment: If you take insurance, say so prominently.

**Copy rules:**
- Use "you" and "your." Warmth over authority.
- First visit anxiety is real. Describe what to expect on a first appointment.
- Patient/client pronouns over "individuals" or "patients" (unless clinical context requires).

**CTA hierarchy:** Book appointment > New patient form > Call the office
**Booking:** Jane App (healthcare), Mindbody (fitness/wellness), Acuity Scheduling (massage/spa), Booksy (beauty)
**Payment:** Stripe, Square, or practice management software (SimplePractice, Jane, Mindbody have built-in payment)

---

### Food and Hospitality (restaurant, bakery, café, catering, food truck, bar)

**Customer psychology:** Appetite and atmosphere. They want to know if they'll like the food and if the place feels right for the occasion. Photos carry more weight here than in almost any other category.

**Page structure:**
- Hero: One full-bleed food or atmosphere photo. No stock.
- Hours and location: Second section. Always. This is the top search for restaurant sites.
- Menu: Accessible, text-based (not PDF). Google reads it; PDFs get ignored.
- About / Story: Brief. One paragraph on who you are and why the food matters.
- Order / Reserve: Inline order form or OpenTable widget if applicable.
- Contact / Find us: Map embed, parking notes if relevant.

**Copy rules:**
- Describe food with texture, temperature, and origin — not adjectives like "delicious."
- "Baked fresh at 5am with local flour" > "artisan fresh-baked goods."
- Allergy info near menu. Prominent. Missing it loses customers.

**CTA hierarchy:** Order online > Reserve a table > View the menu
**Booking/ordering:** OpenTable, Resy (restaurants), Toast, Square for Restaurants, or direct online ordering via their POS
**Payment:** Integrated with POS — Square, Toast, Lightspeed. Separate from website usually.

---

### Retail and E-commerce (boutique, vintage shop, specialty goods, gift shop)

**Customer psychology:** Discovery and desire. They're browsing, not searching for a specific solution. Make them want to stay. Make finding and buying something feel effortless.

**Page structure:**
- Hero: Featured product or collection with direct "shop now" link.
- Featured / New arrivals: 4–6 products. Not the whole catalog.
- About: One paragraph. Who is behind this, where the products come from.
- Social proof: Real photos of people using the product beat studio shots.
- Email capture: Lower priority if they're local; high priority for online-only.

**CTA hierarchy:** Shop now > See new arrivals > Learn about us
**E-commerce:** Shopify (easiest for most retail), WooCommerce (WordPress), Squarespace Commerce
**Payment:** Handled by the e-commerce platform (Shopify Payments, Stripe via WooCommerce)

---

### Education and Coaching (tutor, coach, course creator, workshop provider, music teacher, driving instructor)

**Customer psychology:** Transformation and credibility. They want to believe this person can get them from where they are to where they want to be. Success stories and a clear methodology matter.

**Page structure:**
- Hero: The outcome, not the course. "Go from no clients to fully booked in 90 days" > "Business coaching."
- Who it's for: Specific. Narrow is powerful.
- How it works: The method or process. 3–5 steps.
- Results: Named testimonials with specifics. "Increased revenue by $40k in 6 months" > "Great coach."
- Offer: Pricing or pricing range. Hidden pricing creates friction.
- CTA: Book a free call or enroll.

**CTA hierarchy:** Book a discovery call > Enroll now > Read the curriculum
**Booking:** Calendly, Cal.com (open source), Acuity
**Payment:** Stripe (custom), Teachable/Kajabi/Podia (if course platform), ThriveCart for digital products

---

## Booking System Decision Tree

Use this when the visitor action involves booking or scheduling:

```
Does the business already have a system?
  → Yes: Integrate with it. Don't replace it.
  → No: Use the following recommendations:

Appointment-based service (1:1, in-person):
  • Simple / free: Calendly free tier (15 min, 30 min, 1hr blocks)
  • Professional: Acuity Scheduling ($16/mo) — custom branding, packages, coupons
  • Healthcare: Jane App — HIPAA-compliant, intake forms, insurance
  • Beauty/wellness: Booksy — industry-standard, marketplace exposure
  • Home service: Housecall Pro or Jobber — includes invoicing and job tracking

Group bookings / classes:
  • Fitness/yoga: Mindbody
  • Workshops/events: Eventbrite (free) or Acuity with group bookings

Restaurant reservations:
  • OpenTable (exposure to diner network) or Resy

Online payment collection (not tied to booking):
  • Simple: Stripe Payment Links — generate in 60 seconds, no code
  • On-site + online: Square — POS + online in one ecosystem
  • Invoicing: Wave (free) or QuickBooks + Stripe
  • Subscriptions: Stripe Billing or Paddle
```

When embedding booking into the site:
- Use the provider's embed code, not an external link. A button that says "Book now"
  and opens Calendly in the same page (inline embed) converts better than a new tab.
- Pre-fill fields where possible using URL parameters (name, email, service type).

---

## Conversion Principles (Always Apply)

These apply across all business categories:

### Above the fold
Every visitor should see, without scrolling:
1. What you do (specific, not vague)
2. Who you serve (area or audience)
3. How to contact you or take action

If any of these three are missing above the fold, the page is underperforming.

### The phone number rule
For any business where people might call: the phone number should be in the header, clickable on mobile (`tel:` link), and repeated at the bottom of the page. This applies to local service, health, professional services, and food.

### Social proof placement
Put social proof as close to the primary CTA as possible. The moment someone is about to take action is the moment they most need reassurance.

### Load time and mobile
Local service customers in particular are usually on mobile searching in a moment of need. Pages that load in under 2 seconds convert significantly better. Avoid autoplay video, large hero images without compression, and heavy JavaScript.

### Forms: fewer fields convert better
If you have a contact form:
- 3 fields (name, email or phone, message) convert better than 6.
- Required vs. optional: only mark fields required if they actually are.
- "Get a free quote" converts better than "Contact us."

---

## What Kills Local Business Websites

In order of damage:

1. **No phone number above the fold** — the most common killer
2. **Vague headline** — "Welcome to [Business Name]" tells nobody anything
3. **No service area listed** — people want to know if you serve their zip code
4. **PDF menu or pricing** — Google ignores PDFs; so do mobile users
5. **No real photos** — stock imagery signals inauthenticity
6. **Broken booking flow** — if booking requires account creation, expect abandonment
7. **Not mobile-optimized** — 60–70% of local business searches happen on mobile
8. **Slow load time** — every extra second costs conversions
9. **No reviews or social proof visible** — trust is built with others' words
10. **Missing hours and location** — the most searched information after "what do you do"


---

## 7. iOS / iPhone Compatibility


# iOS / iPhone Compatibility Skill

## Authority

This skill overrides any "general" knowledge about CSS, JavaScript, or animation when building for iPhone. Safari on iOS does not behave like Chrome or Firefox. Many standard web practices WILL break silently on iPhone. This skill documents every known failure and the exact fix. You MUST read and apply everything here before writing a single line of animation or scroll code.

If a rule in this skill conflicts with something you "know" about web development, this skill wins. iOS is the exception to almost every rule.

---

## The Fundamental iOS Problem

Apple forces all browsers on iOS — including Chrome, Firefox, and Edge — to use WebKit under the hood. This means every user on an iPhone is running Safari's rendering engine regardless of which browser app they choose. There is no escape hatch. Fix it for Safari, and it works for all browsers on iPhone.

---

## CRITICAL FAILURES — These WILL break on iPhone without intervention

### 1. `100vh` is wrong. Always.

`100vh` on iOS Safari does NOT equal the visible viewport. The browser chrome (address bar) is included in the calculation, causing the page to overflow and create a scroll gap at the bottom.

**YOU MUST NEVER USE `100vh` FOR HERO SECTIONS OR FULL-SCREEN ELEMENTS.**

```tsx
// WRONG — will overflow on iPhone
<section className="h-screen">          {/* h-screen = 100vh */}
<section style={{ height: "100vh" }}>

// CORRECT — use dvh (dynamic viewport height, iOS 15.4+)
<section className="min-h-[100dvh]">
<section style={{ minHeight: "100dvh" }}>

// FALLBACK for iOS < 15.4 — use a JS-calculated height
// In useEffect: document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
// Then: height: calc(var(--vh, 1vh) * 100);
```

### 2. `scroll-behavior: smooth` breaks GSAP ScrollTrigger on iOS

If `scroll-behavior: smooth` appears ANYWHERE in your CSS — including inside Tailwind utilities like `html { scroll-behavior: smooth }` — GSAP ScrollTrigger will malfunction on iOS 16+. The symptom is the page scrolling back to the top after an animation completes.

**YOU MUST NEVER SET `scroll-behavior: smooth` IN CSS.**

Let Lenis handle smooth scroll. Remove the property from globals.css entirely. Do not add it to any element.

### 3. GSAP ScrollTrigger needs normalizeScroll on iOS

iOS Safari misreports scroll position data. These bugs have existed since 2017 and Apple has not fixed them. Without the normalize call, ScrollTrigger animations stutter, jitter, fire at wrong positions, or fail to fire at all on iPhone.

**YOU MUST ADD THESE TWO LINES when registering ScrollTrigger:**

```tsx
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);

// Required on iOS — add ONCE at the top level (app/layout.tsx or a providers file)
ScrollTrigger.normalizeScroll(true);
ScrollTrigger.config({ ignoreMobileResize: true });
```

`normalizeScroll(true)` intercepts native touch scroll events and manages them in JavaScript, working around iOS position misreporting.

`ignoreMobileResize: true` prevents ScrollTrigger from recalculating all trigger positions when the iOS address bar shows/hides (which fires a resize event). Without this, every time the address bar appears or disappears, all animations jump.

### 4. Autoplay video REQUIRES all three attributes

On iOS, a `<video>` with `autoPlay` will NOT play unless it also has `muted` AND `playsInline`. Missing either attribute causes the video to open fullscreen, refuse to play, or show a blank element.

**ALL autoplay video elements MUST have all three:**

```tsx
// WRONG — will not autoplay on iPhone
<video autoPlay loop>

// CORRECT — required exactly as written
<video autoPlay muted loop playsInline>
  <source src="/videos/hero.webm" type="video/webm" />
  <source src="/videos/hero.mp4" type="video/mp4" />
</video>
```

### 5. Form input font-size must be 16px minimum

Any `<input>`, `<textarea>`, or `<select>` with a computed font-size below 16px will cause iOS Safari to automatically zoom the entire page when the user taps it. This breaks the layout and cannot be fixed by the user.

**ALL form elements MUST have font-size: 16px or larger.**

```css
/* In globals.css — already included in the base styles */
input, textarea, select {
  font-size: 16px; /* minimum — never set below this */
}
```

Setting via Tailwind: `className="text-base"` (1rem = 16px) is the minimum.

### 6. `position: fixed` inside `overflow: hidden` breaks on iOS

If any parent element has `overflow: hidden` (or `overflow: clip`), a child with `position: fixed` will NOT be fixed — it will scroll with the parent. This breaks sticky headers, overlays, and modals.

**Never put `overflow: hidden` on a parent that contains `position: fixed` children.**

The pattern to avoid:
```tsx
// WRONG — the fixed header will scroll with the wrapper on iOS
<div className="overflow-hidden">
  <Header />  {/* position: fixed inside — will break */}
  <main>...</main>
</div>

// CORRECT — fixed elements must be children of the root
<>
  <Header />  {/* position: fixed at root level */}
  <div className="overflow-hidden">
    <main>...</main>
  </div>
</>
```

---

## Three.js / WebGL on iOS — Strict Rules

WebGL on iOS is unreliable. Follow every rule below or accept crashes and broken experiences.

### Rule 1: WebGL Context Lost (Critical — M3/M4, iOS 18.3+)

As of March 2025, Three.js crashes with "WebGL Context Lost" on Apple M3/M4 devices running iOS 18.3+. The error is: `THREE.WebGLRenderer: Context Lost. TypeError: null is not an object (evaluating 'gl.getShaderPrecisionFormat(...)')`. This is an Apple/WebKit bug with no complete upstream fix yet.

**MANDATORY: Add a context restore handler to every Three.js canvas:**

```tsx
useEffect(() => {
  const canvas = gl.domElement;

  const handleContextLost = (event: Event) => {
    event.preventDefault(); // prevent default crash behavior
    console.warn("WebGL context lost — pausing render loop");
    // Stop animation frame
  };

  const handleContextRestored = () => {
    console.log("WebGL context restored");
    // Reinitialize renderer, restart animation frame
    gl.setSize(gl.domElement.width, gl.domElement.height);
    invalidate(); // R3F: request a re-render
  };

  canvas.addEventListener("webglcontextlost", handleContextLost);
  canvas.addEventListener("webglcontextrestored", handleContextRestored);

  return () => {
    canvas.removeEventListener("webglcontextlost", handleContextLost);
    canvas.removeEventListener("webglcontextrestored", handleContextRestored);
  };
}, [gl]);
```

For React Three Fiber, use the `useThree` hook to access `gl`.

### Rule 2: Pixel ratio cap

iOS devices have a device pixel ratio (DPR) of 2 or 3. Rendering at full DPR for complex scenes will drop to unacceptable frame rates.

**Cap the pixel ratio at 2:**

```tsx
// In R3F Canvas props:
<Canvas dpr={[1, 2]}>  {/* min=1, max=2 — never render at DPR 3 */}
```

### Rule 3: Disable antialiasing on the renderer

Hardware MSAA antialiasing is expensive on iOS GPU. Replace with FXAA (post-processing pass) or disable entirely for most business website use cases.

```tsx
<Canvas
  gl={{
    antialias: false,          // disable MSAA — use FXAA if needed
    powerPreference: "high-performance",
    failIfMajorPerformanceCaveat: false,
  }}
  dpr={[1, 2]}
>
```

### Rule 4: Texture size limits

iOS has a maximum texture size of 4096×4096. Textures larger than this WILL fail silently or crash. Keep all textures at or below 2048×2048 for safety on older devices.

### Rule 5: Dispose everything on unmount

iOS aggressively garbage collects GPU memory. If you don't manually dispose, textures and geometries accumulate and crash the WebGL context.

```tsx
useEffect(() => {
  return () => {
    // In every Three.js component's cleanup
    geometry.dispose();
    material.dispose();
    if (material.map) material.map.dispose();
    texture.dispose();
    renderer.dispose();
  };
}, []);
```

### Rule 6: Dynamic import Three.js — always

Three.js is ~500KB. Never import it at the page level. Always dynamic import with SSR disabled:

```tsx
import dynamic from "next/dynamic";
const Scene = dynamic(() => import("@/components/three/Scene"), {
  ssr: false,
  loading: () => <div className="w-full h-full bg-black" />, // placeholder while loading
});
```

### Rule 7: No shadows on mobile

Shadow maps are extremely expensive on iOS. Disable them on mobile:

```tsx
import { useThree } from "@react-three/fiber";

function DisableShadowsOnMobile() {
  const { gl } = useThree();
  useEffect(() => {
    const isMobile = /iPhone|iPad|iPod/i.test(navigator.userAgent);
    if (isMobile) {
      gl.shadowMap.enabled = false;
    }
  }, [gl]);
  return null;
}
// Place inside Canvas
```

### Rule 8: Reduce geometry complexity on mobile

Detect mobile and use lower-poly geometry:

```tsx
const isMobile = typeof navigator !== "undefined"
  ? /iPhone|iPad|iPod/i.test(navigator.userAgent)
  : false;

// Use 32 segments on mobile, 128 on desktop
<sphereGeometry args={[1, isMobile ? 32 : 128, isMobile ? 32 : 128]} />
```

---

## GSAP Animations on iOS — Rules

### Rule 1: normalizeScroll and ignoreMobileResize are not optional

Already documented above. Repeat: add both calls. Without them, every scroll animation on iPhone is unreliable.

### Rule 2: Never use `will-change` on more than 5 elements simultaneously

`will-change: transform` forces GPU compositing. On iOS, having more than ~5 composited layers simultaneously causes dropped frames and memory pressure. GSAP applies `will-change` automatically via `force3D: true`.

To prevent overuse, set globally:

```tsx
gsap.defaults({ force3D: false }); // let GSAP decide per-animation
```

Only set `force3D: true` explicitly for elements that need it (hero text, key interactive elements).

### Rule 3: `pin: true` in ScrollTrigger is janky on iPhone — use alternatives

Pinned sections (where an element stays fixed while scrolling continues) are notoriously problematic on iOS. They jump when the pin activates/deactivates because the browser renders scroll on a separate thread.

Required config for any pinned element:
```tsx
scrollTrigger: {
  trigger: ref.current,
  pin: true,
  anticipatePin: 1,    // pre-renders the pin state to reduce jump
  pinSpacing: true,    // ensure layout space is preserved
  scrub: 1,            // smooth scrub reduces jarring on iOS
}
```

If pinning is still unacceptable on iPhone, use CSS sticky positioning instead and animate with `scrub` without pinning.

### Rule 4: Refresh ScrollTrigger after fonts and images load

GSAP calculates trigger positions at initialization. If fonts haven't loaded yet, all heading heights are wrong and trigger positions are off. This causes animations to fire too early or too late on iPhone where cellular networks load assets slower.

```tsx
useGSAP(() => {
  // ... set up animations ...

  // Refresh after everything loads
  window.addEventListener("load", () => ScrollTrigger.refresh());
  document.fonts.ready.then(() => ScrollTrigger.refresh());
}, { scope: containerRef });
```

### Rule 5: Cleanup — always return from useGSAP

Every `useGSAP` hook must return a cleanup function via the built-in `revert()` mechanism:

```tsx
useGSAP(() => {
  const ctx = gsap.context(() => {
    // animations
  }, scope);

  return () => ctx.revert(); // cleanup on unmount
}, { scope: containerRef });
```

Without cleanup, ScrollTrigger instances accumulate in memory on iOS, causing crashes on subsequent page navigations in Next.js.

---

## Loading Screen / Splash Screen — iOS Pattern

A loading screen on iOS has specific requirements. Standard patterns break.

### The correct iOS loading screen implementation

```tsx
// components/ui/LoadingScreen.tsx
"use client";
import { useEffect, useState } from "react";
import { gsap } from "gsap";

export function LoadingScreen() {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    // Minimum display time — even on fast connections, hold for 1.2s
    // This prevents the flash of an unstyled loading screen
    const minDisplayTime = 1200;
    const startTime = Date.now();

    const dismiss = () => {
      const elapsed = Date.now() - startTime;
      const remaining = Math.max(0, minDisplayTime - elapsed);

      setTimeout(() => {
        // Animate out — DO NOT use display:none, use opacity + pointer-events
        gsap.to("#loading-screen", {
          opacity: 0,
          duration: 0.5,
          ease: "power2.inOut",
          onComplete: () => setVisible(false),
        });
      }, remaining);
    };

    // Wait for fonts AND page load
    Promise.all([
      document.fonts.ready,
      new Promise(resolve => {
        if (document.readyState === "complete") resolve(null);
        else window.addEventListener("load", resolve, { once: true });
      }),
    ]).then(dismiss);
  }, []);

  if (!visible) return null;

  return (
    <div
      id="loading-screen"
      // CRITICAL: use fixed positioning, 100dvh, not 100vh
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-brand-dominant"
      style={{ height: "100dvh" }}  // override in case Tailwind generates vh
    >
      {/* Logo */}
      <div className="flex flex-col items-center gap-6">
        <img
          src="/images/logos/logo-white.svg"
          alt="Loading"
          className="w-24 h-auto animate-pulse"
        />
        {/* Progress bar */}
        <div className="w-48 h-0.5 bg-white/20 overflow-hidden">
          <div className="h-full bg-brand-accent origin-left animate-[loadbar_1.5s_ease-in-out_forwards]" />
        </div>
      </div>
    </div>
  );
}
```

Add to `app/globals.css`:
```css
@keyframes loadbar {
  from { width: 0%; }
  to   { width: 100%; }
}
```

Add to `app/layout.tsx` at the top of `<body>`:
```tsx
<body>
  <LoadingScreen />
  {children}
</body>
```

### What NOT to do on a loading screen
- Do NOT use `setTimeout` with a fixed delay and hope for the best. Use `document.fonts.ready`.
- Do NOT use `display: none` to remove it — use `opacity: 0` + `pointer-events: none`, then unmount.
- Do NOT use `height: 100vh` on the loading screen container.
- Do NOT animate with CSS `@keyframes` that start immediately — fonts may not be loaded yet, causing a layout shift that restarts the animation.

---

## CSS — What Works and What Doesn't on iOS

### iOS version requirements for modern CSS

| Feature | iOS Support | Fallback needed? |
|---|---|---|
| `dvh` / `dvw` units | iOS 15.4+ | Yes — use JS fallback for older |
| `container queries` | iOS 16+ | Yes — use media queries |
| `@layer` | iOS 15.4+ | No — Next.js targets modern iOS |
| `aspect-ratio` | iOS 15+ | No |
| `gap` on flex | iOS 14.5+ | No |
| `backdrop-filter: blur()` | iOS 9+ (with `-webkit-` prefix) | Add `-webkit-` prefix |
| `overscroll-behavior` | iOS 16+ | Use JS for older |
| `subgrid` | iOS 16+ | No |
| `color-mix()` | iOS 16.4+ | No |

### `backdrop-filter` — always include webkit prefix

```css
/* WRONG — won't work on iOS */
.element { backdrop-filter: blur(10px); }

/* CORRECT */
.element {
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
}
```

In Tailwind, use: `className="backdrop-blur-md [-webkit-backdrop-filter:blur(12px)]"`

### `position: sticky` limitations

`position: sticky` does not work inside a `display: flex` parent on older iOS versions. If sticky elements are not sticking, check if any parent has `overflow: hidden` or `display: flex` without `flex-direction: column`.

### `-webkit-font-smoothing` — required

Without this, fonts render differently on iOS than designed:
```css
/* In globals.css body or html selector */
-webkit-font-smoothing: antialiased;
-moz-osx-font-smoothing: grayscale;
```

### Touch target size — enforced

All interactive elements must be at least 44×44px on screen. This is Apple's Human Interface Guideline and also an accessibility requirement. Use this utility class in Tailwind config or inline:

```tsx
// Add to tailwind.config.ts utilities
// Or use min-h-[44px] min-w-[44px] on all buttons and links
```

---

## Safe Area Insets — Required on Every Project

iPhone X and later have a notch (or Dynamic Island on iPhone 14 Pro+) and a home indicator. Content placed under these is hidden or unclickable.

**Every project MUST include safe area handling in globals.css:**

```css
body {
  /* Pushes content below home indicator on iPhone */
  padding-bottom: env(safe-area-inset-bottom);
  /* Respects notch/Dynamic Island on iPhone X+ */
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}
```

For fixed headers — add padding-top:
```css
.fixed-header {
  padding-top: env(safe-area-inset-top);
}
```

For fixed bottom CTAs or navbars:
```tsx
<div
  className="fixed bottom-0 left-0 right-0"
  style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
>
```

This MUST be in the `<head>` of layout.tsx for safe areas to work:
```tsx
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
```

`viewport-fit=cover` is what enables `env(safe-area-inset-*)`. Without it, safe areas are ignored.

---

## Overscroll / Bounce Prevention

iOS has rubber-band bounce scrolling. During animations (especially page transitions or scroll-locked sequences), this rubber-band effect can conflict with the animation and cause the user to accidentally scroll past the intended section.

**Prevent overscroll during animations:**

```css
/* In globals.css */
html {
  overscroll-behavior: none; /* Supported iOS 16+ */
}

/* For older iOS — use this with JS: */
document.body.addEventListener('touchmove', (e) => {
  if (e.target === document.body) e.preventDefault();
}, { passive: false });
```

If using Lenis, overscroll is already handled. Do not add `overscroll-behavior: none` to the `body` when Lenis is active — let Lenis manage it.

---

## Lenis Configuration for iOS

Use this exact Lenis config in `app/layout.tsx`:

```tsx
lenisRef.current = new Lenis({
  duration: 1.2,
  easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smoothWheel: true,
  smoothTouch: false,   // IMPORTANT: false on touch — Lenis uses native momentum on touch
  touchMultiplier: 2,   // faster touch response
  infinite: false,
  overscroll: false,    // prevent rubber-band conflict
});
```

`smoothTouch: false` is critical. Enabling smooth touch on Lenis conflicts with iOS's native momentum scroll and causes lag. Let iOS handle touch scroll natively; Lenis enhances mouse wheel only.

---

## Navbar on iOS — Specific Requirements

The iOS address bar appears and disappears when scrolling, firing a window resize event. This can cause the navbar to jump or flicker.

**Required additions to the Header component:**

```tsx
useEffect(() => {
  const header = headerRef.current;
  if (!header) return;

  let lastScrollY = window.scrollY;
  let ticking = false;

  const handleScroll = () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        const currentY = window.scrollY;
        // Only trigger hide/show after 80px to prevent address bar sensitivity
        if (currentY > lastScrollY && currentY > 80) {
          gsap.to(header, { yPercent: -100, duration: 0.3, ease: "power2.in" });
        } else if (currentY < lastScrollY) {
          gsap.to(header, { yPercent: 0, duration: 0.4, ease: "power2.out" });
        }
        lastScrollY = currentY;
        ticking = false;
      });
      ticking = true;
    }
  };

  // passive: true is required on iOS for non-blocking scroll listener
  window.addEventListener("scroll", handleScroll, { passive: true });
  return () => window.removeEventListener("scroll", handleScroll);
}, []);
```

`{ passive: true }` on the scroll listener is required on iOS. Without it, iOS Safari assumes the listener might call `preventDefault()`, which forces it to wait before scrolling — creating noticeable lag.

---

## iOS Performance Budget by Device

| Device | CPU | GPU | Safe animation level |
|---|---|---|---|
| iPhone 15 Pro / 16 | A17/A18 | Excellent | Full GSAP + Lenis + light 3D |
| iPhone 14 / 15 | A15/A16 | Very good | Full GSAP + Lenis + minimal 3D |
| iPhone 12 / 13 | A14/A15 | Good | Full GSAP + Lenis, no 3D |
| iPhone 11 | A13 | Moderate | GSAP with caution, no 3D |
| iPhone SE (2nd/3rd gen) | A13/A15 | Moderate | GSAP entrance only, no scroll-scrub |

**Use this detection to conditionally load Three.js:**

```tsx
const canHandle3D = () => {
  if (typeof navigator === "undefined") return false;
  // Rough detection: A14 chip and later can handle light 3D
  // No reliable chip detection in browser — use feature + memory check
  const memory = (navigator as Navigator & { deviceMemory?: number }).deviceMemory;
  return !memory || memory >= 4; // 4GB RAM roughly corresponds to modern iPhone
};
```

If the device cannot handle 3D, render a static image or CSS gradient fallback instead of the Three.js canvas.

---

## Meta Tags — Required in app/layout.tsx

```tsx
export const metadata: Metadata = {
  title: "[Business Name]",
  description: "[Specific one-line description]",
  other: {
    // Required for safe area env() to work
    "viewport": "width=device-width, initial-scale=1, viewport-fit=cover",
    // Prevent automatic phone number detection messing up layouts
    "format-detection": "telephone=no",
  },
  // For PWA-like feel (optional but professional)
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "[Business Name]",
  },
};
```

Or in the `<head>` directly:
```tsx
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="format-detection" content="telephone=no" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="default" />
</head>
```

---

## iOS Pre-Delivery Checklist

Run through this on every project before calling it complete. Test on an actual iPhone if possible — iOS Simulator does not reproduce all Safari bugs accurately.

### Layout
- [ ] Hero section uses `min-h-[100dvh]`, NOT `min-h-screen` or `100vh`
- [ ] No `scroll-behavior: smooth` anywhere in CSS
- [ ] `viewport-fit=cover` in the viewport meta tag
- [ ] Safe area insets applied to body and any fixed bottom elements
- [ ] No `overflow: hidden` parent containing `position: fixed` children

### Animations
- [ ] `ScrollTrigger.normalizeScroll(true)` called once at app root
- [ ] `ScrollTrigger.config({ ignoreMobileResize: true })` called once at app root
- [ ] `ScrollTrigger.refresh()` called in `document.fonts.ready` handler
- [ ] All `useGSAP` hooks have cleanup via `ctx.revert()`
- [ ] Pinned sections use `anticipatePin: 1` and `scrub: 1`

### Video
- [ ] All autoplay video has `autoPlay muted loop playsInline` — all four attributes
- [ ] Video files under 10MB, or using external hosting

### Three.js (if used)
- [ ] Imported with `dynamic({ ssr: false })`
- [ ] `dpr={[1, 2]}` on Canvas — never higher
- [ ] `antialias: false` on Canvas gl prop
- [ ] `powerPreference: "high-performance"` on Canvas gl prop
- [ ] WebGL context lost/restored event handlers added
- [ ] All geometries and materials disposed on unmount
- [ ] Shadows disabled on mobile detection
- [ ] Fallback UI for devices that can't handle 3D

### Forms
- [ ] All inputs have `font-size: 16px` minimum — prevents iOS zoom
- [ ] All buttons and links are at least 44px tall

### Performance
- [ ] `-webkit-tap-highlight-color: transparent` in globals.css
- [ ] `{ passive: true }` on all scroll event listeners
- [ ] No `will-change` applied to more than 5 elements at once


---

## 8. Recommended Design System

*(ui-ux-pro-max engine unavailable -- derive design system from the visitor experience direction and business category.)*


---

## 9. Stack, Motion System, and Build Instructions


Read and follow the Stack Skill below for project structure, dependencies, motion components, and handoff files.

# Stack Skill — Cinematic Web Stack

## Purpose

Every project built by Pebble Engine uses this stack unless explicitly told otherwise. Read this skill fully before scaffolding any project. It tells you the project structure, the exact dependencies, and working code patterns for animations, smooth scroll, and 3D.

---

## The Stack

| Tool | Role | Version |
|---|---|---|
| Next.js | Framework (App Router, SSR/SSG, routing) | ^14.2 |
| React | UI component layer | ^18.3 |
| TypeScript | Type safety | ^5.4 |
| Tailwind CSS | Utility-first styling | ^3.4 |
| GSAP + ScrollTrigger | Animations, scroll-driven sequences | ^3.12 |
| @gsap/react | GSAP hooks for React | ^2.1 |
| Lenis | Smooth scroll (pairs with GSAP ScrollTrigger) | ^1.1 |
| Three.js | 3D rendering | ^0.165 |
| @react-three/fiber | React renderer for Three.js | ^8.16 |
| @react-three/drei | Three.js helpers (cameras, controls, loaders) | ^9.105 |
| clsx + tailwind-merge | Conditional className utility | latest |

---

## Project Structure

Every project must follow this structure exactly. The `public/` directory is pre-organized so the client can drop their media files in without touching code:

```
project-name/
├── app/
│   ├── layout.tsx           ← root layout: fonts, Lenis provider, metadata
│   ├── page.tsx             ← homepage
│   ├── globals.css          ← Tailwind base + CSS custom properties
│   └── [page]/
│       └── page.tsx         ← additional pages (services, contact, etc.)
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   └── SectionHeading.tsx
│   ├── sections/            ← page sections (Hero, Services, Contact, etc.)
│   │   ├── Hero.tsx
│   │   ├── Services.tsx
│   │   └── Contact.tsx
│   ├── layout/
│   │   ├── Header.tsx
│   │   └── Footer.tsx
│   └── three/               ← Three.js / R3F components (only if 3D needed)
│       └── Scene.tsx
├── lib/
│   └── utils.ts             ← cn() utility for className merging
├── public/
│   ├── images/
│   │   ├── hero/            ← hero section images (hero.jpg, hero-mobile.jpg)
│   │   ├── about/           ← owner photo, team photos (owner.jpg)
│   │   ├── services/        ← one image per service (service-1.jpg, service-2.jpg, ...)
│   │   ├── gallery/         ← before/after, portfolio, project photos (01.jpg, 02.jpg, ...)
│   │   ├── logos/           ← client logo (logo.svg, logo-white.svg, favicon.ico)
│   │   └── og/              ← Open Graph image for social sharing (og-image.jpg)
│   ├── videos/
│   │   ├── hero.mp4         ← hero background video (if used)
│   │   └── hero.webm        ← WebM version for browser compatibility
│   ├── fonts/               ← self-hosted fonts (if not using Google Fonts)
│   └── models/              ← .glb / .gltf 3D models (if Three.js is used)
├── package.json
├── tailwind.config.ts
├── next.config.ts
├── postcss.config.js
└── tsconfig.json
```

---

## Media Convention — CRITICAL

**Every component must reference media using these exact paths.** The client drops their files into the correct folder and they appear immediately — no code changes.

### Image paths (use Next.js `<Image>` component)

```tsx
import Image from "next/image";

// Hero image
<Image src="/images/hero/hero.jpg" alt="[Business name] — [location]" fill className="object-cover" priority />

// Owner / about photo
<Image src="/images/about/owner.jpg" alt="[Owner name], [Business name]" width={600} height={800} />

// Service images — use index to match the services array
<Image src={`/images/services/service-${index + 1}.jpg`} alt={service.title} width={800} height={600} />

// Gallery
<Image src={`/images/gallery/${String(index + 1).padStart(2, "0")}.jpg`} alt={`${businessName} — work sample`} width={1200} height={900} />

// Logo
<Image src="/images/logos/logo.svg" alt="[Business name] logo" width={160} height={48} />
```

### Video (hero background)

```tsx
// Use native <video> — Next.js Image doesn't handle video
<video
  autoPlay
  muted
  loop
  playsInline
  className="absolute inset-0 w-full h-full object-cover"
>
  <source src="/videos/hero.webm" type="video/webm" />
  <source src="/videos/hero.mp4" type="video/mp4" />
</video>
```

### README.md — always include this file

Every project must include a `README.md` at the root that tells the client exactly where to put their files:

```markdown
# [Business Name] Website

## Getting started
\`\`\`bash
npm install
npm run dev
\`\`\`
Site runs at http://localhost:3000

## Adding your media

Drop your files into the correct folder — the site picks them up automatically.

| What | Where to put it | File name |
|---|---|---|
| Main hero image | `public/images/hero/` | `hero.jpg` |
| Mobile hero (optional) | `public/images/hero/` | `hero-mobile.jpg` |
| Owner photo | `public/images/about/` | `owner.jpg` |
| Service images | `public/images/services/` | `service-1.jpg`, `service-2.jpg`, ... |
| Gallery / portfolio | `public/images/gallery/` | `01.jpg`, `02.jpg`, ... |
| Logo (color) | `public/images/logos/` | `logo.svg` |
| Logo (white, for dark bg) | `public/images/logos/` | `logo-white.svg` |
| Hero background video | `public/videos/` | `hero.mp4` + `hero.webm` |

## Recommended image sizes
- Hero: 1920×1080px minimum, JPG, compressed to under 300KB
- Service images: 800×600px, JPG
- Gallery: 1200×900px, JPG
- Owner photo: 600×800px (portrait), JPG
- Logo: SVG preferred; PNG fallback at 2x resolution

## Deploying
\`\`\`bash
npm run build    # build for production
npx vercel       # deploy to Vercel (free tier available)
\`\`\`
\`\`\`
```

---

## package.json

Always output this exact `package.json`. Do not omit dependencies:

```json
{
  "name": "project-name",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "three": "^0.165.0",
    "@react-three/fiber": "^8.16.0",
    "@react-three/drei": "^9.105.0",
    "gsap": "^3.12.5",
    "@gsap/react": "^2.1.1",
    "lenis": "^1.1.6",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.3.0"
  },
  "devDependencies": {
    "typescript": "^5.4.0",
    "@types/node": "^20.14.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@types/three": "^0.165.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^14.2.0"
  }
}
```

---

## Config Files

### tailwind.config.ts

```ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // Add brand colors as Tailwind tokens — derive from the brief
      colors: {
        brand: {
          dominant: "var(--color-dominant)",
          secondary: "var(--color-secondary)",
          accent:   "var(--color-accent)",
          surface:  "var(--color-surface)",
          text:     "var(--color-text)",
        },
      },
      fontFamily: {
        // Derive from the brief's design system — replace Display/Body with actual font names
        display: ["var(--font-display)", "serif"],
        body:    ["var(--font-body)", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
```

### next.config.ts

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // Allow external image domains if used
    remotePatterns: [],
  },
};
export default nextConfig;
```

### postcss.config.js

```js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

## app/globals.css

This is the single source of truth for brand tokens. Every color and font goes here as a CSS custom property so Tailwind and plain CSS both use the same values:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  /* Brand colors — replace values with those from the brief */
  --color-dominant: #1a1a1a;
  --color-secondary: #f5f0e8;
  --color-accent:    #c8432a;
  --color-surface:   #ffffff;
  --color-text:      #1a1a1a;

  /* Typography — replace with actual font names from the brief */
  --font-display: "Fraunces", serif;
  --font-body:    "Inter", sans-serif;

  /* Smooth scroll via Lenis — do not set scroll-behavior: smooth here */
}

html, body {
  overflow-x: hidden;
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## app/layout.tsx — Root Layout with Lenis

```tsx
"use client";

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { useEffect, useRef } from "react";
import Lenis from "lenis";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-body" });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const lenisRef = useRef<Lenis | null>(null);

  useEffect(() => {
    // Initialize Lenis smooth scroll
    lenisRef.current = new Lenis({
      duration: 1.2,
      easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
    });

    // Integrate Lenis with GSAP ticker for ScrollTrigger compatibility
    const raf = (time: number) => {
      lenisRef.current?.raf(time);
    };

    // Use requestAnimationFrame loop
    let rafId: number;
    const animate = (time: number) => {
      raf(time);
      rafId = requestAnimationFrame(animate);
    };
    rafId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(rafId);
      lenisRef.current?.destroy();
    };
  }, []);

  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}
```

---

## GSAP Animation Patterns

### Pattern 1 — Entrance animation on scroll (most common)

Use this for any section that should animate in as the user scrolls to it:

```tsx
"use client";
import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(ScrollTrigger);

export function AnimatedSection({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    if (!ref.current) return;
    gsap.fromTo(
      ref.current.querySelectorAll("[data-animate]"),
      { opacity: 0, y: 40 },
      {
        opacity: 1,
        y: 0,
        duration: 0.9,
        stagger: 0.12,
        ease: "power3.out",
        scrollTrigger: {
          trigger: ref.current,
          start: "top 80%",
          toggleActions: "play none none none",
        },
      }
    );
  }, { scope: ref });

  return <div ref={ref}>{children}</div>;
}
```

Tag elements with `data-animate` to include them in the animation sequence.

### Pattern 2 — Horizontal scroll section

```tsx
useGSAP(() => {
  const sections = gsap.utils.toArray<HTMLElement>(".panel");
  gsap.to(sections, {
    xPercent: -100 * (sections.length - 1),
    ease: "none",
    scrollTrigger: {
      trigger: containerRef.current,
      pin: true,
      scrub: 1,
      snap: 1 / (sections.length - 1),
      end: () => `+=${containerRef.current!.offsetWidth}`,
    },
  });
}, { scope: containerRef });
```

### Pattern 3 — Text reveal (cinematic)

```tsx
useGSAP(() => {
  const chars = headingRef.current?.querySelectorAll(".char");
  if (!chars) return;
  gsap.fromTo(
    chars,
    { y: "110%", opacity: 0 },
    {
      y: "0%",
      opacity: 1,
      duration: 0.7,
      stagger: 0.04,
      ease: "power4.out",
      scrollTrigger: {
        trigger: headingRef.current,
        start: "top 85%",
      },
    }
  );
}, { scope: headingRef });
```

Split heading text into `.char` spans using a utility or manually in JSX.

### Pattern 4 — Parallax background

```tsx
useGSAP(() => {
  gsap.to(imageRef.current, {
    yPercent: -20,
    ease: "none",
    scrollTrigger: {
      trigger: sectionRef.current,
      start: "top bottom",
      end: "bottom top",
      scrub: true,
    },
  });
}, { scope: sectionRef });
```

---

## Three.js / React Three Fiber Patterns

### When to include Three.js

Only include Three.js / R3F if:
- The brief explicitly calls for 3D elements
- The aesthetic direction calls for 3D geometry, particle systems, or 3D product views
- There is a `components/three/` directory in the project

If in doubt, skip Three.js and use CSS transforms for visual depth. Three.js adds ~500KB to the bundle.

### Basic R3F Canvas setup

```tsx
// components/three/Scene.tsx
"use client";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment } from "@react-three/drei";
import { Suspense } from "react";

export function Scene() {
  return (
    <Canvas
      camera={{ position: [0, 0, 5], fov: 45 }}
      style={{ width: "100%", height: "100%" }}
    >
      <Suspense fallback={null}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <Environment preset="city" />
        <OrbitControls enableZoom={false} enablePan={false} />
        {/* Add your geometry here */}
        <mesh>
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial color="#c8432a" />
        </mesh>
      </Suspense>
    </Canvas>
  );
}
```

### Loading a .glb model

```tsx
import { useGLTF } from "@react-three/drei";

function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url);
  return <primitive object={scene} />;
}
// Preload for performance
useGLTF.preload("/models/model.glb");
```

### GSAP + Three.js (scroll-driven 3D rotation)

```tsx
import { useFrame } from "@react-three/fiber";
import { useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

function RotatingMesh() {
  const meshRef = useRef<THREE.Mesh>(null);
  const rotation = useRef({ y: 0 });

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);
    gsap.to(rotation.current, {
      y: Math.PI * 2,
      ease: "none",
      scrollTrigger: {
        trigger: "#canvas-section",
        start: "top top",
        end: "bottom top",
        scrub: true,
      },
    });
  }, []);

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y = rotation.current.y;
    }
  });

  return (
    <mesh ref={meshRef}>
      <torusKnotGeometry args={[1, 0.3, 128, 32]} />
      <meshStandardMaterial color="#c8432a" metalness={0.8} roughness={0.2} />
    </mesh>
  );
}
```

---

## Performance Rules and Vercel Size Limits

Vercel enforces a **100MB limit on the total deployment output**. The biggest risk is large media files committed to `/public/`. Follow these rules on every project:

### Video rules
- `/public/videos/` is for short hero clips only. Max file size: **10MB per video file**.
- If the client's video is larger than 10MB, do NOT include it in the project. Instead:
  - Embed from YouTube: `<iframe src="https://www.youtube.com/embed/VIDEO_ID" />`
  - Or use Cloudinary: `<video src="https://res.cloudinary.com/[account]/video/upload/[id].mp4" />`
  - Document the choice in `README.md` under a "Video hosting" note.
- Always output both `.mp4` (H.264) and `.webm` (VP9) for cross-browser support.
- The `.gitkeep` files in `public/videos/` remind the client where to drop their video — they don't add size.

### 3D model rules
- `.glb` / `.gltf` files go in `public/models/`. Max per model: **5MB**.
- Recommend Draco compression in `README.md` for any model over 2MB.
- If no 3D content is needed, do NOT include the `components/three/` directory or Three.js imports — they add ~500KB to the bundle unnecessarily.

### Image rules
- Raw images in `/public/` are NOT optimized by Next.js at build time — they get optimized on-demand via the Image component. This means a 4MB JPG in `/public/images/` counts toward the 100MB limit but is fine otherwise.
- Recommend clients compress photos to under 500KB before dropping in (use Squoosh, TinyPNG, or similar). Note this in `README.md`.
- Always use `<Image>` from `next/image`, never a raw `<img>` tag. `<Image>` handles lazy loading, srcset, and WebP conversion automatically.

### Bundle size
- Never import Three.js or R3F at the top level — only import inside the component that uses it, and use dynamic imports with `ssr: false`:
```tsx
const Scene = dynamic(() => import("@/components/three/Scene"), { ssr: false });
```
- Never import all of GSAP — import only what you need:
```tsx
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
// NOT: import * as gsap from "gsap"
```

### .gitignore — always include
```
node_modules/
.next/
.env*.local
.DS_Store
*.log
```

---

## Animation Standards — Required on Every Project

Animation is not optional. Every project must include all three of these as a baseline:

### 1. Animated hero section (required)

The hero must animate in on page load. This is the cinematic first impression. Use this pattern:

```tsx
// components/sections/Hero.tsx
"use client";
import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import { gsap } from "gsap";

export function Hero() {
  const container = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    const tl = gsap.timeline({ defaults: { ease: "power4.out" } });
    tl.fromTo("[data-hero-eyebrow]", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6 })
      .fromTo("[data-hero-heading]", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.9 }, "-=0.3")
      .fromTo("[data-hero-sub]",     { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7 }, "-=0.5")
      .fromTo("[data-hero-cta]",     { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6 }, "-=0.4");
  }, { scope: container });

  return (
    <section ref={container} className="relative min-h-[100dvh] flex items-center overflow-hidden">
      {/* Video background — client drops file into /public/videos/hero.mp4 */}
      <div className="absolute inset-0 z-0">
        <video autoPlay muted loop playsInline className="w-full h-full object-cover">
          <source src="/videos/hero.webm" type="video/webm" />
          <source src="/videos/hero.mp4"  type="video/mp4"  />
        </video>
        {/* Overlay so text is readable over video */}
        <div className="absolute inset-0 bg-black/50" />
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-6 py-32 md:py-0">
        <p data-hero-eyebrow className="text-sm tracking-widest uppercase text-brand-accent mb-4">
          [Location] · [Industry]
        </p>
        <h1 data-hero-heading className="font-display text-5xl md:text-7xl lg:text-8xl leading-none mb-6 text-white">
          [Hero headline — specific and arguable]
        </h1>
        <p data-hero-sub className="font-body text-xl text-white/80 mb-10 max-w-xl">
          [Supporting sentence — names the outcome, not the service]
        </p>
        <div data-hero-cta>
          <a href="tel:[BUSINESS PHONE]"
             className="inline-block bg-brand-accent text-white font-semibold px-8 py-4 text-lg hover:bg-brand-accent/90 transition-colors">
            [Primary CTA]
          </a>
        </div>
      </div>
    </section>
  );
}
```

**If no video is provided:** Replace the video block with an animated CSS gradient or a Next.js `<Image>` with `fill` and `priority`. Never leave the hero as a plain colored background.

### 2. Scroll-triggered section reveals (required on every section)

Every section below the hero animates in as it scrolls into view. Apply this to every `<section>` component:

```tsx
"use client";
import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);

export function AnySection() {
  const ref = useRef<HTMLElement>(null);

  useGSAP(() => {
    gsap.fromTo(
      ref.current!.querySelectorAll("[data-animate]"),
      { opacity: 0, y: 50 },
      {
        opacity: 1, y: 0,
        duration: 0.8,
        stagger: 0.15,
        ease: "power3.out",
        scrollTrigger: {
          trigger: ref.current,
          start: "top 75%",
          toggleActions: "play none none none",
        },
      }
    );
  }, { scope: ref });

  return (
    <section ref={ref} className="py-24 px-6">
      <h2 data-animate className="font-display text-4xl mb-4">[Heading]</h2>
      <p data-animate className="font-body text-lg">[Body]</p>
      {/* Add data-animate to every element that should animate in */}
    </section>
  );
}
```

### 3. Scroll-aware navbar (required)

Every project needs a navbar that hides when the user scrolls down and reappears when they scroll up:

```tsx
// components/layout/Header.tsx
"use client";
import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Image from "next/image";
import Link from "next/link";
gsap.registerPlugin(ScrollTrigger);

export function Header() {
  const headerRef = useRef<HTMLElement>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  let lastScrollY = useRef(0);

  useEffect(() => {
    const header = headerRef.current;
    if (!header) return;

    const handleScroll = () => {
      const currentY = window.scrollY;
      if (currentY > lastScrollY.current && currentY > 80) {
        // Scrolling down — hide
        gsap.to(header, { yPercent: -100, duration: 0.3, ease: "power2.in" });
      } else {
        // Scrolling up — show
        gsap.to(header, { yPercent: 0, duration: 0.4, ease: "power2.out" });
      }
      lastScrollY.current = currentY;
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header ref={headerRef} className="fixed top-0 left-0 right-0 z-50 bg-brand-dominant/95 backdrop-blur-sm">
      <nav className="container mx-auto px-6 h-16 md:h-20 flex items-center justify-between">
        <Link href="/">
          <Image src="/images/logos/logo-white.svg" alt="[Business] logo" width={140} height={40} />
        </Link>

        {/* Desktop nav */}
        <ul className="hidden md:flex items-center gap-8 font-body">
          {["Services", "About", "Contact"].map(item => (
            <li key={item}>
              <Link href={`/${item.toLowerCase()}`}
                    className="text-white/80 hover:text-white transition-colors text-sm tracking-wide uppercase">
                {item}
              </Link>
            </li>
          ))}
          <li>
            <a href="tel:[BUSINESS PHONE]"
               className="bg-brand-accent text-white px-5 py-2.5 text-sm font-semibold hover:bg-brand-accent/90 transition-colors">
              [BUSINESS PHONE]
            </a>
          </li>
        </ul>

        {/* Mobile hamburger */}
        <button
          className="md:hidden flex flex-col gap-1.5 p-2"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          <span className={`block w-6 h-0.5 bg-white transition-transform ${menuOpen ? "rotate-45 translate-y-2" : ""}`} />
          <span className={`block w-6 h-0.5 bg-white transition-opacity ${menuOpen ? "opacity-0" : ""}`} />
          <span className={`block w-6 h-0.5 bg-white transition-transform ${menuOpen ? "-rotate-45 -translate-y-2" : ""}`} />
        </button>
      </nav>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden bg-brand-dominant border-t border-white/10">
          <ul className="flex flex-col py-4">
            {["Services", "About", "Contact"].map(item => (
              <li key={item}>
                <Link href={`/${item.toLowerCase()}`}
                      className="block px-6 py-3 text-white/80 hover:text-white hover:bg-white/5 transition-colors"
                      onClick={() => setMenuOpen(false)}>
                  {item}
                </Link>
              </li>
            ))}
            <li className="px-6 pt-3">
              <a href="tel:[BUSINESS PHONE]"
                 className="block bg-brand-accent text-white text-center py-3 font-semibold">
                Call [BUSINESS PHONE]
              </a>
            </li>
          </ul>
        </div>
      )}
    </header>
  );
}
```

---

## iOS and Mobile — Non-Negotiable Rules

iOS Safari has specific behaviors that break standard CSS. Every project must handle all of these:

### app/globals.css — required iOS fixes

Add these to the base layer of every project:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  /* Prevent tap flash on iOS */
  * {
    -webkit-tap-highlight-color: transparent;
  }

  /* iOS momentum scrolling in scroll containers */
  .overflow-scroll, .overflow-y-scroll, .overflow-x-scroll {
    -webkit-overflow-scrolling: touch;
  }

  /* Prevent font size inflation on iPhone landscape */
  html {
    -webkit-text-size-adjust: 100%;
    text-size-adjust: 100%;
  }

  /* Safe area padding for notched iPhones (iPhone X and newer) */
  body {
    padding-bottom: env(safe-area-inset-bottom);
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right);
  }

  /* Prevent input zoom on iOS — font-size must be >= 16px */
  input, textarea, select {
    font-size: 16px;
  }
}

:root {
  --color-dominant: #1a1a1a;
  --color-secondary: #f5f0e8;
  --color-accent: #c8432a;
  --color-surface: #ffffff;
  --color-text: #1a1a1a;
  --font-display: "Fraunces", serif;
  --font-body: "Inter", sans-serif;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
  }
}
```

### Hero height — use dvh not vh

`100vh` is broken on iOS Safari — the address bar makes the viewport taller than expected, causing overflow. Always use:

```tsx
// WRONG — breaks on iOS
<section className="min-h-screen">

// CORRECT — respects iOS browser chrome
<section className="min-h-[100dvh]">
```

### Touch-friendly tap targets

All buttons and links must be at least 44×44px on mobile (Apple's Human Interface Guideline). Minimum:

```tsx
// Use py-3 px-4 minimum on all interactive elements
<button className="py-3 px-6 min-h-[44px]">...</button>
```

### Lenis config for iOS

iOS requires `prevent` to be handled carefully with Lenis. Use this config in `app/layout.tsx`:

```tsx
lenisRef.current = new Lenis({
  duration: 1.2,
  easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smoothWheel: true,
  touchMultiplier: 2,   // faster on touch devices
  infinite: false,
});
```

### Bottom fixed bars — clear the safe area

If any element is fixed to the bottom (mobile CTA bar, cookie banner, chat widget):

```tsx
<div className="fixed bottom-0 left-0 right-0 pb-[env(safe-area-inset-bottom)] bg-white">
  {/* content */}
</div>
```

### Mobile self-audit — add to every project's checklist

Before delivering any project, verify on an iPhone screen width (390px):

| Check | What to verify |
|---|---|
| Hero height | Fills screen without overflow, no blank gap at bottom |
| Navigation | Hamburger menu opens and closes, all links work, no text overflow |
| Font sizes | Body text min 16px, headings readable at 390px |
| Tap targets | All buttons/links at least 44px tall |
| Images | No horizontal scroll, all images contained within viewport |
| Forms | Inputs don't cause page zoom when tapped |
| Fixed elements | No elements obscuring content on small screens |
| Safe area | Content not cut off by iPhone notch or home indicator |

---

## lib/utils.ts

```ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

---

## Performance Rules

- **Canvas elements:** Wrap in `Suspense` with a fallback. Never block the main thread.
- **GSAP ScrollTrigger:** Call `ScrollTrigger.refresh()` after any layout change (font load, image load, accordion open). Clean up in `useEffect` return.
- **Images:** Use Next.js `<Image>`, never `<img>`. Always specify `width`/`height` or use `fill`. Add `priority` to the hero image.
- **Fonts:** Use `next/font/google`. Never a `<link>` tag — it blocks rendering.
- **Three.js:** Dynamic import with `ssr: false`. Dispose geometries and materials on unmount.
- **Lenis + ScrollTrigger:** Connect Lenis's `raf` to a `requestAnimationFrame` loop (not GSAP ticker, to avoid double-ticking). Use `ScrollTrigger.refresh()` after Lenis initializes.

---

## How to Run the Generated Project

```bash
cd project-name
npm install
npm run dev       # → http://localhost:3000
```

Production build and deploy:
```bash
npm run build
npx vercel        # deploys to Vercel in ~60 seconds
```


### Self-audit before delivering

| Check | Required |
|---|---|
| Phone number | `[BUSINESS PHONE]` placeholder -- NEVER a 555 number or invented number |
| Primary heading font | NOT Inter/Geist/Poppins/Space Grotesk/DM Sans -- named distinct face |
| Subtext | No "Where X meets Y" -- contains specific claim, number, or place name |
| Headline | No "Unrivaled/World-class/Unleash your inner" -- specific and arguable |
| Hero visual | Has photo, video, 3D, or animated CSS element -- NOT flat background behind text |
| Background | Dark for premium/tech -- Light for local service/wellness/food |
| Booking tool | Matches business category -- Booksy is ONLY for beauty/wellness |
| Page structure | NOT Hero + 3 cards + testimonials + pricing + footer |
| Testimonials | Real only, or omitted -- never fabricated |
| SplitText headings | `word-break: keep-all` on heading wrapper |
| Hero height | `min-h-[100dvh]` not `min-h-screen` |
| Scroll animations | Match visual experience level |
| Navbar | Scroll-aware hide/show + mobile hamburger |
| Input font size | Minimum `font-size: 16px` |
| Safe area | `env(safe-area-inset-*)` in globals.css |
| Video | `autoPlay muted loop playsInline` |

---

## 10. Anti-Slop Audit

*(No conflicts detected. Design rules below still apply.)*

---

## 11. Output -- NO QUESTIONS, BUILD IMMEDIATELY

**Do not write a plan. Do not ask questions. Build now.**

Output every file the project needs. Follow the Stack Skill project structure.

Required files:
- `README.md`, `HANDOFF.md`, `TODO_ASSETS.md`, `STYLE_GUIDE.md`, `CLIENT_ANSWERS.md`
- `src/content/site.ts`, `src/content/sections.ts`, `src/content/services.ts`, `src/content/faqs.ts`, `src/content/testimonials.ts`
- `src/lib/motion.ts`, `src/components/motion/Reveal.tsx`, `src/components/motion/Parallax.tsx`, `src/components/motion/SplitText.tsx`, `src/components/motion/SmoothScroll.tsx`
- `src/config/brand.config.ts`, `src/config/motion.config.ts`

Where contact info is missing: use `[BUSINESS PHONE]`, `[EMAIL]`, `[ADDRESS]`. Never invent.
