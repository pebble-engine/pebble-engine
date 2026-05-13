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
- Distinctive heading font with authority — choose from: Oswald (condensed, commanding), Syne (geometric, modern), Manrope heavy (solid, trustworthy), Fraunces (warm editorial), or Playfair Display (established, credible)
- Do NOT use Inter, Roboto, Poppins, DM Sans, or any convergence font as a heading — these signal "generic AI output" and undermine trust
- Body text at comfortable size (17–18px), generous line height (1.7); Inter is acceptable for body only when paired with a distinctive heading face
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
