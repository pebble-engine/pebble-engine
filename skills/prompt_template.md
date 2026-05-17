<!--
  Pebble Engine — master prompt template.

  This file is loaded by pebble_engine.build_prompt() and rendered via Python's
  str.format(). Two consequences:

    1. Variables use single braces: {business_name}, {industry_intel_block}, etc.
    2. Any LITERAL brace in the prose (TypeScript objects, JSX, CSS rules) MUST be
       doubled — {{ and }} — or str.format() will try to parse it as a field
       and 500 the build. This is the same rule as Python f-strings.

  When editing: keep the doubled braces in code samples. The test suite
  (tests/test_smoke.py::test_build_prompt_renders_with_minimal_inputs) will
  catch a regression on the next pytest run.
-->
# Website Build Brief -- {business_name}

You are building a complete, production-quality website. Read every section of this brief before writing a single line of code. The skills embedded in this brief contain thousands of words of specific, researched direction. Apply all of it.

---

## INDUSTRY INTELLIGENCE — Design DNA For This Industry

This block is sourced from `industries.json` (a curated database of 50+ industries) or researched + cached on first use. Every value below is industry-specific and non-negotiable. The Resolved Design Contract that follows derives its palette, hero type, and Three.js variant from these values.

{industry_intel_block}

---

## RESOLVED DESIGN CONTRACT — Read This First

These values were computed from the Industry Intelligence above + the quiz answers before any skill content was loaded. Skills in later sections are implementation guides — they do not override these values. When any skill content seems to suggest a different choice, the contract wins. Concrete beats ambiguous.

{resolved_contract}

---

## 1. Project Overview

- **Business name:** {business_name}
- **Type of business:** {business_type}
- **Audience:** {audience}
- **Location / service area:** {location}
- **Services offered:** {services_offered}
- **Phone:** {phone}
- **Email:** {email}
- **Address:** {address}
- **Primary visitor action:** {visitor_action}
- **Booking or payment system:** {booking_system}

**Contact info usage:** When a value above is set, use it directly in `<a href="tel:...">`, `<a href="mailto:...">`, and address blocks. When a value is the literal placeholder (`[BUSINESS PHONE]`, `[EMAIL]`, `[ADDRESS]`) or empty, keep the placeholder verbatim — never invent a number, email, or street.

---

## 2. MANDATORY OUTPUT STRUCTURE

The Design DNA block at the top of this prompt names this build's aesthetic identity (Swiss Magazine, Brutalist Editorial, Terminal Operator, Cinematic IMAX, etc.). The structure below is a **fallback default** — when the DNA describes a different hero structure, motion intensity, or section pattern, the DNA wins. The constants below (page list, full pages, no card grids, headline presence) still apply.

### Required Pages

**FOUNDATION PAGES (every build, always):**

1. **Homepage** (`app/page.tsx`) — landing page, full of life, follows the DNA's posture
2. **Services** (`app/services/page.tsx`) — full-bleed alternating layout, NOT a generic card grid
3. **About** (`app/about/page.tsx`) — editorial story
4. **Contact** (`app/contact/page.tsx`) — REAL working form (Server Action + Resend SDK — see Code Pattern 8). NOT an `onSubmit` with a hardcoded success state. The form posts to a Next.js Server Action, which calls `resend.emails.send(...)` and returns `{{ ok: true | false, error?: string }}`. When `RESEND_API_KEY` is unset (development without keys), the Server Action returns `{{ ok: true }}` without sending — the eval and the UX still flow cleanly. Map embed below the form.

**INDUSTRY-AWARE PAGES (rendered dynamically per build):**

{pages_block}

### Homepage — Default Section Structure (override per DNA)

**Section 1: Hero — FOUNDATION (MANDATORY — overrides all DNA hero variants)**

This hero is the engine's universal foundation. Every build uses this exact structure. The Design DNA layers accent color, copy voice, and signature decorative moves on TOP of this structure but does not redefine the structure itself. When a DNA card's hero_structure description conflicts with what follows, the foundation wins.

**Visual layout:**
- `<section>` is `relative min-h-[100dvh] overflow-hidden bg-black` (always a dark base — text is always light over the video)
- Full-bleed `<video>` is `absolute inset-0 w-full h-full object-cover`, with attributes `autoPlay muted loop playsInline` (all four, always) AND a `poster="…"` attribute (MANDATORY — the eval `hero_video_has_poster` enforces this)
- **CRITICAL: NO dark overlay on the video.** No `bg-black/40`, no `bg-gradient-to-b from-black/...`, no semi-transparent layer above the video. The video plays raw. The chosen Pexels video must already have inherent darkness/contrast where text sits. Legibility is provided by `textShadow` on the headline and subhead (built into `AnimatedHeading` and mandated on the subhead `<p>`), NOT by a background dimming layer.
- Video `src` is `/videos/hero.mp4` when the post-build chain has localized the Pexels video (preferred); otherwise the Pexels CDN URL is the fallback. The `poster` attribute should reference a still image — use one of the Pexels image URLs from Section 8b, or a static path like `/images/hero-poster.jpg`. The poster paints instantly while the video is loading, so it MUST visually match the chosen video (same mood, similar darkness profile) — otherwise the first 100-300 ms look like a different page.
- **The `<section>` itself MUST be `flex flex-col`** in addition to `relative min-h-[100dvh] overflow-hidden bg-black`. Without `flex flex-col` on the section, the inner content's `justify-end` has nothing to push against and the hero text ends up top-aligned. This is the #1 visual regression in foundation builds — copy the exact classlist.
- **Inner content container** sits at the BOTTOM of the viewport via `flex-1 flex flex-col justify-end` (use `flex-1`, NOT `h-full`): `relative z-10 flex-1 flex flex-col justify-end px-6 md:px-12 lg:px-16 pb-12 lg:pb-16 text-white`. The `flex-1` is required so the container expands to fill the section's flex column space; `justify-end` then pushes the grid to the bottom edge.
- On large screens, content uses a 2-column grid: `lg:grid lg:grid-cols-2 lg:items-end gap-8`

**Left column — primary content (vertical order):**
1. `<AnimatedHeading text="line one\nline two" className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-normal mb-4" />` — the h1 with per-character entrance animation. Two lines separated by `\n`. Use the brand's value prop in two beats — example: `"Shaping tomorrow\nwith vision and action."` for a VC firm, `"Roasted slow.\nServed fresh."` for a coffee roaster. **THE HEADING IS THE H1 — never a styled div.**
2. `<FadeIn delay={{800}} duration={{1000}}>` wrapping `<p className="text-base md:text-lg text-gray-300 mb-5" style={{{{ textShadow: "0 2px 16px rgba(0,0,0,0.5)" }}}}>…subhead sentence…</p>` — one sentence naming the outcome the visitor gets. The inline `textShadow` is MANDATORY; the foundation has no dark overlay above the video, so the subhead carries its own legibility scaffolding. The eval `hero_text_has_legibility_safeguard` enforces this.
3. `<FadeIn delay={{1200}} duration={{1000}}>` wrapping `<div className="flex flex-wrap gap-4">` containing two CTAs. Both CTAs MUST include the focus-visible utility chain `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black` so keyboard users see a visible focus ring against the liquid-glass / video surface. The eval `interactive_elements_have_focus_visible` enforces this on hero CTAs, navbar links, and the Call Us pill.
   - Primary: white pill — `bg-white text-black px-8 py-3 rounded-lg font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black` — links to `tel:[BUSINESS PHONE]` (or `#contact` if the brief lacks a phone)
   - Secondary: glass — `liquid-glass border border-white/20 text-white px-8 py-3 rounded-lg font-medium hover:bg-white hover:text-black transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black` — links to `/services` or another primary route

**Right column — optional brand tag (`hidden lg:flex items-end justify-start lg:justify-end`):**
- `<FadeIn delay={{1400}} duration={{1000}}>` wrapping a `liquid-glass border border-white/20 px-6 py-3 rounded-xl` card
- Inside: `<p className="text-lg md:text-xl lg:text-2xl font-light">Three. Short. Words.</p>` — three or four short phrases summarizing the business posture. Example: "Roasted. Direct. Local." or "Plumbing · HVAC · Electrical"

**Navbar — liquid-glass chip floating at the top:**
- Outer wrapper: `absolute top-0 inset-x-0 z-50 px-6 md:px-12 lg:px-16 pt-6`
- Inner navbar element: `<nav className="liquid-glass rounded-xl px-4 py-2 flex items-center justify-between text-white">`
- Left: logo wordmark in `<Link href="/" className="text-2xl font-semibold tracking-tight">…business name…</Link>`
- Center (`hidden md:flex gap-8 text-sm`): nav links — hover transitions to `text-gray-300`
- Right: primary CTA — `<a href="tel:[BUSINESS PHONE]" className="bg-white text-black px-6 py-2 rounded-lg text-sm font-medium hover:bg-gray-100">Call Us</a>`

**Accessibility (mandatory):**
- `app/globals.css` includes `@media (prefers-reduced-motion: reduce)` that disables transitions globally
- The `AnimatedHeading` component checks `prefers-reduced-motion` at mount and renders all characters at final state immediately when set
- Video has `muted` (iOS Safari blocks unmuted autoplay) and no `controls`
- Hero h1 is a real `<h1>` tag (not a styled `<div>`)

DO NOT do any of the following, regardless of DNA:
- A plain white centered hero with only CTA buttons and no headline
- A flat-color hero with no background video
- A dark overlay on top of the video (no `bg-black/...`, no gradients, nothing dimming the video)
- The video set up as `<source>` without `autoPlay muted loop playsInline` on the `<video>` itself
- Skipping the `AnimatedHeading` and `FadeIn` components in favor of inline GSAP timelines on the hero
- Using a `display_font` from the DNA as the h1 typeface — the h1 is always Inter (the DNA's display_font is reserved for accent / decorative uses elsewhere on the page)

**Section 2: Trust Bar — Counting Stats**
- Dark or brand-accent background strip — NOT white
- 3–4 numbers that count up on scroll: years in business, jobs completed, rating, insured/certified
- Each number uses `data-target` attribute + GSAP textContent counter (see Code Patterns)
- Single horizontal row — NOT cards, NOT icons in a grid

**Section 3: Services — Full-Bleed Alternating Sections**
Stack services as full-width vertical sections — a 3-column card grid is forbidden, and horizontal scroll is forbidden. Each service is a full-width section. Image fills one half, text the other. Alternate: image-left/text-right, text-left/image-right. Every image uses clip-path reveal (see Code Patterns). For 4+ services, stack all of them — vertical rhythm is the point, no carousels.

**Section 4: Social Proof — Dark Editorial**
- Dark background
- ONE large quote, 3–4rem font size, centered — not a carousel of small cards
- Stars above the quote, attribution below (name + specific result: "saved $3,200" / "back in 2 days")
- If no testimonials: bold credibility statement with a striking number ("Over 1,200 vehicles restored")

**Section 5: About / Story — Parallax Editorial**
- Full-bleed parallax background image (see Code Patterns)
- Owner story: specific, first-person, human — NOT "we are committed to excellence"
- Credentials woven into narrative — not a badge row
- Link to full About page

**Section 6: FAQ or Feature Callout**
- FAQ: 4–6 accordion questions, industry-specific, genuinely useful answers
- Alternative if few questions: a "Why us" section with 2–3 bold differentiating claims

**Section 7: Final CTA — Full Bleed, One Action**
- Full-width section, brand dark or strong accent color
- ONE headline + ONE large centered CTA button
- Phone number as secondary option beneath it
- NO competing buttons

**Section 8: Footer — MANDATORY 3-column sitemap layout**

File location: `components/layout/Footer.tsx`. Imported into `app/layout.tsx` so it appears on every page (matches the Navbar pattern). The eval looks for the footer at this path; do not inline it into individual pages.

The footer is the user's (and Google's) only complete map of the site. Every page listed in the INDUSTRY-AWARE PAGES section above (FAQ, Privacy, Terms, plus the industry-specific extras like Menu/Team/Booking/etc.) MUST appear as a link in the footer's sitemap column, otherwise the page is effectively invisible after the homepage loads.

Structure: full-width section, dark background (`bg-black` or industry's deep tone), three columns on `md:` breakpoint, stacked single-column on mobile. Render as `<footer className="border-t border-white/10 bg-black text-white/80">` with an inner `max-w-7xl mx-auto px-6 md:px-12 lg:px-16 py-16 grid gap-12 md:grid-cols-3`.

Column 1 — **Contact**:
- Business name (h3, semibold)
- One-sentence positioning line
- `tel:` link (real number from brief, MUST start with `tel:`)
- `mailto:` link (real email from brief, MUST start with `mailto:`)
- Street address (one line, no map)

Column 2 — **Sitemap** (THIS IS THE MULTI-PAGE DISCOVERY MOMENT — every page in the build appears here):
- Heading "Explore" or "Site" (h3, semibold)
- A `<ul className="space-y-2">` with one `<li><Link href="/...">Title</Link></li>` per generated page
- Order: Home, Services, About, Contact, then industry-specific pages (in the order they appear above), then FAQ, Privacy, Terms last
- The Link MUST use Next.js `import Link from "next/link"`, NOT a raw `<a>` (a raw `<a>` triggers a full reload and breaks the SPA navigation experience)
- No empty href="#" placeholders. Every link points to a route this build generates.

Column 3 — **Hours & social**:
- Business hours (one line per day, or "Mon-Fri 9-5 · Sat 10-2")
- Social icons row (only platforms the brief mentions; if none, omit this row entirely — never invent profiles)
- Copyright line at the bottom of the column: `© {{new Date().getFullYear()}} [Business Name]. All rights reserved.` — the year comes from `new Date().getFullYear()` so it auto-rolls over, and the business name is the one from the brief

Bottom strip below the 3 columns: `border-t border-white/10 mt-12 pt-6 text-xs text-white/50` row with "Built with [Pebble](https://getpebble.net)" attribution on the left and "Privacy · Terms" links on the right.

The eval `footer_lists_all_pages` parses the footer file and FAILS the build if any page declared in `plan.json` is missing from the sitemap column. Don't ship a footer without the sitemap.

### Navigation — Animated Header

- Fixed position, `className="navbar"` on `<header>` (required for animation below)
- Logo left · nav links center · phone CTA right
- Mobile: hamburger → fullscreen overlay with staggered link reveals
- CTA button: `<a href="tel:[BUSINESS PHONE]">` — never a dead link

---

### REQUIRED TECH STACK

```json
{{
  "dependencies": {{
    "next": "^15.0.0",
    "react": "^19.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "gsap": "^3.12.0",
    "@gsap/react": "^2.1.0",
    "lenis": "^1.1.0",
    "framer-motion": "^11.0.0",
    "resend": "^4.0.0"
  }}
}}
```

`resend` is required because the contact form is a real Server Action (Code Pattern 8) that sends email when `RESEND_API_KEY` is set in `.env.local`. The dev-time fallback (no key set → returns `{{ ok: true }}` without sending) means the build still runs cleanly without credentials; the eval `resend_in_dependencies` enforces the package is declared so the import resolves.

**Performance non-negotiables:**
- `next/image` for ALL images — never raw `<img>` tags. Use `fill` + `object-cover` for full-bleed, explicit `width`/`height` for fixed-size. `priority` on hero image only.
- `next/font/google` for fonts — zero layout shift
- `gsap.registerPlugin(ScrollTrigger)` at module level — never inside useEffect (SplitText is forbidden — paid Club plugin)
- `dynamic()` with `{{ ssr: false }}` for any component using `window` or `document`
- `will-change: transform` only during active animation — remove after with `gsap.set(el, {{ clearProps: "willChange" }})`
- `@media (prefers-reduced-motion: reduce) {{ * {{ animation-duration: 0.01ms !important; transition-duration: 0.01ms !important }} }}` in globals.css

**Typography — MANDATORY GLOBAL FOUNDATION:**

Inter is the engine's universal sans-serif. Every build loads it via `next/font/google` with weights 300, 400, 500, 600. Apply it globally via Tailwind's `font-sans` so every element picks it up automatically. The DNA's `display_font` (Cormorant Garamond, Tektur, etc.) is reserved for ACCENT/decorative use — pull-quotes, drop caps, stat numbers, the optional right-column hero tag — NEVER the hero h1 or body copy.

In `app/layout.tsx`:

```tsx
import {{ Inter }} from "next/font/google";
import type {{ Metadata }} from "next";
import {{ Footer }} from "@/components/layout/Footer";
import "./globals.css";

const inter = Inter({{
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  variable: "--font-inter",
  display: "swap",
}});

// MANDATORY: viewport export so mobile renders at device width, not desktop.
// Eval `mobile_optimized_responsive` will fail without it.
export const viewport = {{
  width: "device-width",
  initialScale: 1,
}};

// MANDATORY: OG + Twitter Card for rich social previews — eval `og_social_meta_present` requires both.
export const metadata: Metadata = {{
  title: "{{business_name}}",
  description: "{{one-sentence tagline summarising what the business does}}",
  openGraph: {{
    title: "{{business_name}}",
    description: "{{one-sentence tagline summarising what the business does}}",
    type: "website",
  }},
  twitter: {{
    card: "summary_large_image",
    title: "{{business_name}}",
    description: "{{one-sentence tagline summarising what the business does}}",
  }},
}};

export default function RootLayout({{ children }}: {{ children: React.ReactNode }}) {{
  return (
    <html lang="en" className={{inter.variable}}>
      <head>
        {{/* MANDATORY: preload the hero poster image so the first paint lands
            before JS hydrates. Eval `perf_budget_or_lighter` will fail without
            a <link rel="preload"> OR an <Image priority> somewhere. */}}
        <link rel="preload" as="image" href="/images/hero-poster.jpg" />
      </head>
      <body className={{`${{inter.className}} antialiased`}}>
        {{children}}
        <Footer />
      </body>
    </html>
  );
}}
```

In `tailwind.config.ts`:

```ts
import type {{ Config }} from "tailwindcss";

const config: Config = {{
  content: ["./app/**/*.{{ts,tsx}}", "./components/**/*.{{ts,tsx}}"],
  theme: {{
    extend: {{
      fontFamily: {{
        sans: ["var(--font-inter)", "Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      }},
    }},
  }},
  plugins: [],
}};
export default config;
```

In `app/globals.css` (above the Tailwind directives):

```css
body {{
  font-family: var(--font-inter), Inter, ui-sans-serif, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}
```

This is non-negotiable. Every Tailwind `font-sans` usage picks up Inter automatically. The DNA's display_font, when used, is loaded as a SECOND font via `next/font/google` (or `<link>` in head for non-Google fonts) and applied via its own utility class — never replacing Inter as the default.

**Schema.org JSON-LD — MANDATORY GLOBAL FOUNDATION:**

Every site must emit Schema.org structured data so search engines AND modern AI agents (Perplexity, ChatGPT browse, Gemini Search) can identify the business. Emit it from `app/layout.tsx` as a `<script type="application/ld+json">` tag inside the document — the body works fine; the parser doesn't care where in the page the tag lives as long as it's in the served HTML.

For most Pebble builds (local-service businesses: plumbing, real estate, medical, restaurants, etc.), use `LocalBusiness`. For purely online services (SaaS, consultancies with no physical presence), use `Organization`.

```tsx
// inside app/layout.tsx, somewhere inside the <body>:
const ld = {{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",   // or "Organization" for online-only
  "name": "{{business_name}}",
  "description": "{{one-sentence summary of what the business does}}",
  // Optional but recommended when available in the brief:
  // "telephone": "+1-555-555-5555",
  // "url": "https://example.com",
  // "address": {{
  //   "@type": "PostalAddress",
  //   "streetAddress": "123 Main St",
  //   "addressLocality": "Austin",
  //   "addressRegion": "TX",
  //   "postalCode": "78701",
  //   "addressCountry": "US"
  // }},
}};

<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{{{ __html: JSON.stringify(ld) }}}}
/>
```

The eval `schema_org_jsonld_present` verifies `app/layout.tsx` contains BOTH `application/ld+json` MIME type AND a `"@context": "https://schema.org"` declaration. Without the `@context`, the structured data is invisible to crawlers.

**Favicon — MANDATORY GLOBAL FOUNDATION:**

Every site must have a favicon so browser tabs and bookmarks show the business identity instead of a blank icon. Use the Next.js App Router file convention: create `app/icon.svg` and Next.js automatically generates the correct `<link rel="icon">` tag — no `metadata.icons` configuration needed.

```svg
<!-- app/icon.svg — use the DNA's primary accent color for fill. First letter of business_name. -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="16" fill="{{dna_accent_color}}"/>
  <text x="50" y="72" text-anchor="middle" font-family="-apple-system,system-ui,sans-serif"
        font-size="60" font-weight="700" fill="white">{{first_letter_of_business_name}}</text>
</svg>
```

The eval `favicon_defined` verifies `app/icon.svg`, `app/favicon.ico`, or `app/icon.png` exists. A purely typographic monogram SVG is always acceptable — do NOT invent a complex logo that requires assets you don't have.

**Crawler discoverability — MANDATORY GLOBAL FOUNDATION (sitemap + robots):**

Every site must ship Next.js 14 convention files that emit `sitemap.xml` and `robots.txt`. Together they make every page in the build findable by search engines AND modern AI agents (GPTBot, ClaudeBot, PerplexityBot, Google-Extended). Without them, only the homepage gets indexed reliably.

```tsx
// app/sitemap.ts — Next.js 14 convention. Returns MetadataRoute.Sitemap.
import type {{ MetadataRoute }} from "next";

export default function sitemap(): MetadataRoute.Sitemap {{
  const base = process.env.NEXT_PUBLIC_SITE_URL || "https://example.com";
  // List every page route in the build. Homepage first, then the rest.
  const routes = ["", "/about", "/services", "/contact", "/faq", "/privacy", "/terms"];
  return routes.map((route) => ({{
    url:        `${{base}}${{route}}`,
    lastModified: new Date(),
    changeFrequency: "monthly" as const,
    priority:   route === "" ? 1.0 : 0.7,
  }}));
}}
```

```tsx
// app/robots.ts — Next.js 14 convention. Returns MetadataRoute.Robots.
import type {{ MetadataRoute }} from "next";

export default function robots(): MetadataRoute.Robots {{
  const base = process.env.NEXT_PUBLIC_SITE_URL || "https://example.com";
  return {{
    rules: [
      {{
        userAgent: "*",
        allow:     "/",
      }},
    ],
    sitemap: `${{base}}/sitemap.xml`,
  }};
}}
```

The eval `sitemap_and_robots_present` verifies both files exist and each has a default-export function. Replace the placeholder `routes` array with the actual pages the build emits (homepage + every page in INDUSTRY-AWARE PAGES).

---

### CINEMATIC CODE PATTERNS — Implement Verbatim

#### 1. Hero Entrance — AnimatedHeading + FadeIn Components (FOUNDATION)

**Two reusable client components that compose every hero.** Both go in `components/ui/`. Both are required artifacts — the eval suite verifies their presence. The hero h1 uses `AnimatedHeading`; the subhead, CTA row, and right-column tag each wrap in `FadeIn` with cascading delays (800ms → 1200ms → 1400ms).

These are NOT optional. Do NOT replace them with a GSAP timeline or framer-motion equivalent. The components must exist at the exact paths below.

##### `components/ui/AnimatedHeading.tsx`

Per-character entrance: each char starts at `opacity:0, translateX(-18px)` and transitions to `opacity:1, translateX(0)` with a staggered delay calculated from char index. Lines split on `\n`. Spaces render as non-breaking. Respects `prefers-reduced-motion` — when the user has it set, all chars render at final state immediately.

**Accessibility (mandatory, eval-enforced):** Inside the `<h1>`, the full text is rendered ONCE inside a `<span className="sr-only">` so assistive technologies announce the heading as a coherent phrase. The per-character animation lives in a sibling `<span aria-hidden="true">` and is decoration only. Without this split, a screen reader announces "Design" as "D... e... s... i... g... n" — a P0 a11y regression. The eval `animated_heading_screen_reader_safe` checks for BOTH `sr-only` AND `aria-hidden` in this file.

The `<h1>` also carries a `textShadow` inline style. Because the foundation forbids a dark overlay on the hero video, the heading needs its own legibility scaffolding so it reads against any video frame — the shadow is built into the component so the LLM cannot forget it.

```tsx
"use client";
import {{ useEffect, useState }} from "react";

type Props = {{
  text: string;          // use \n for explicit line breaks
  charDelay?: number;    // ms between chars; default 30
  initialDelay?: number; // ms before first char animates; default 200
  duration?: number;     // ms per char transition; default 500
  className?: string;
}};

export function AnimatedHeading({{ text, charDelay = 30, initialDelay = 200, duration = 500, className }}: Props) {{
  const [ready, setReady] = useState(false);
  const [reduce, setReduce] = useState(false);

  useEffect(() => {{
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduce(mq.matches);
    const t = setTimeout(() => setReady(true), initialDelay);
    return () => clearTimeout(t);
  }}, [initialDelay]);

  const lines = text.split("\n");
  return (
    <h1 className={{className}} style={{{{ letterSpacing: "-0.04em", textShadow: "0 2px 24px rgba(0,0,0,0.5)" }}}}>
      <span className="sr-only">{{text}}</span>
      <span aria-hidden="true">
      {{lines.map((line, lineIndex) => {{
        const lineOffset = lineIndex * line.length * charDelay;
        return (
          <span key={{lineIndex}} style={{{{ display: "block" }}}}>
            {{Array.from(line).map((ch, charIndex) => {{
              const delay = reduce ? 0 : lineOffset + charIndex * charDelay;
              return (
                <span
                  key={{charIndex}}
                  style={{{{
                    display: "inline-block",
                    opacity: ready || reduce ? 1 : 0,
                    transform: ready || reduce ? "translateX(0)" : "translateX(-18px)",
                    transition: `opacity ${{duration}}ms ease, transform ${{duration}}ms ease`,
                    transitionDelay: `${{delay}}ms`,
                  }}}}
                >
                  {{ch === " " ? " " : ch}}
                </span>
              );
            }})}}
          </span>
        );
      }})}}
      </span>
    </h1>
  );
}}
```

##### `components/ui/FadeIn.tsx`

Wraps children, starts at `opacity:0`, transitions to `opacity:1` after `delay` ms. Configurable duration. Respects `prefers-reduced-motion`.

```tsx
"use client";
import {{ ReactNode, useEffect, useState }} from "react";

type Props = {{
  children: ReactNode;
  delay?: number;     // ms before fade starts; default 0
  duration?: number;  // ms transition; default 1000
  className?: string;
}};

export function FadeIn({{ children, delay = 0, duration = 1000, className }}: Props) {{
  const [visible, setVisible] = useState(false);
  const [reduce, setReduce] = useState(false);

  useEffect(() => {{
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduce(mq.matches);
    const t = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(t);
  }}, [delay]);

  return (
    <div
      className={{className}}
      style={{{{
        opacity: visible || reduce ? 1 : 0,
        transition: `opacity ${{duration}}ms ease`,
      }}}}
    >
      {{children}}
    </div>
  );
}}
```

##### Usage in `components/sections/Hero.tsx` and `app/page.tsx`

```tsx
import {{ AnimatedHeading }} from "@/components/ui/AnimatedHeading";
import {{ FadeIn }} from "@/components/ui/FadeIn";

export function Hero() {{
  return (
    <section className="relative min-h-[100dvh] overflow-hidden bg-black flex flex-col">
      <video
        autoPlay muted loop playsInline
        preload="metadata"
        className="absolute inset-0 w-full h-full object-cover"
        src="/videos/hero.mp4"
        poster="/images/hero-poster.jpg"
      />
      {{/* NO overlay. The video plays raw. */}}

      <div className="relative z-10 flex-1 flex flex-col justify-end px-6 md:px-12 lg:px-16 pb-12 lg:pb-16 text-white">
        <div className="lg:grid lg:grid-cols-2 lg:items-end gap-8">
          <div>
            <AnimatedHeading
              text={{"Shaping tomorrow\nwith vision and action."}}
              className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-normal mb-4"
            />
            <FadeIn delay={{800}} duration={{1000}}>
              <p className="text-base md:text-lg text-gray-300 mb-5" style={{{{ textShadow: "0 2px 16px rgba(0,0,0,0.5)" }}}}>
                We back visionaries and craft ventures that define what comes next.
              </p>
            </FadeIn>
            <FadeIn delay={{1200}} duration={{1000}}>
              <div className="flex flex-wrap gap-4">
                <a href="tel:[BUSINESS PHONE]" className="bg-white text-black px-8 py-3 rounded-lg font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black">Start a Chat</a>
                <a href="/services" className="liquid-glass border border-white/20 text-white px-8 py-3 rounded-lg font-medium hover:bg-white hover:text-black transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black">Explore Now</a>
              </div>
            </FadeIn>
          </div>
          <FadeIn delay={{1400}} duration={{1000}} className="hidden lg:flex items-end justify-start lg:justify-end">
            <div className="liquid-glass border border-white/20 px-6 py-3 rounded-xl">
              <p className="text-lg md:text-xl lg:text-2xl font-light">Investing. Building. Advisory.</p>
            </div>
          </FadeIn>
        </div>
      </div>
    </section>
  );
}}
```

The h1 and the FadeIn cascades replace the legacy `splitWords()` helper entirely. The `gsap/SplitText` import remains forbidden — it's a paid Club plugin and the eval suite will reject any import of it.

#### 2. Liquid-Glass Navbar — Rounded Chip Pattern (FOUNDATION)

Not a page-wide blur bar. The navbar is a centered rounded chip floating at the top of the viewport, with horizontal page padding around it and the `.liquid-glass` utility class for the backdrop blur + gradient stroke border.

```tsx
"use client";
import Link from "next/link";

export function Navbar({{ businessName }}: {{ businessName: string }}) {{
  return (
    <div className="absolute top-0 inset-x-0 z-50 px-6 md:px-12 lg:px-16 pt-6">
      <nav className="liquid-glass rounded-xl px-4 py-2 flex items-center justify-between text-white">
        <Link href="/" className="text-2xl font-semibold tracking-tight rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black/40">
          {{businessName}}
        </Link>
        <div className="hidden md:flex gap-8 text-sm">
          <Link href="/services" className="hover:text-gray-300 transition-colors rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black/40">Services</Link>
          <Link href="/about" className="hover:text-gray-300 transition-colors rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black/40">About</Link>
          <Link href="/contact" className="hover:text-gray-300 transition-colors rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black/40">Contact</Link>
        </div>
        <a href="tel:[BUSINESS PHONE]" className="bg-white text-black px-6 py-2 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black">
          Call Us
        </a>
      </nav>
    </div>
  );
}}
```

The navbar is `absolute` (not `fixed`) so it sits over the hero video without floating during scroll. For pages without a hero video (services, about, contact), wrap the navbar's outer div with `relative bg-black` and switch its position to `fixed top-0 inset-x-0` so it persists during scroll there. Either way the `.liquid-glass` chip stays the visual signature.

The mobile menu (links < md breakpoint) collapses to a hamburger → fullscreen overlay with staggered link reveals. Use the same `<FadeIn>` component from Code Pattern 1 to fade each menu link in with `delay` proportional to its index.

#### 2b. Liquid-Glass Utility — globals.css (FOUNDATION)

The `.liquid-glass` class produces an iOS 26 / visionOS-style frosted panel: dark translucent background, backdrop blur, and a gradient stroke border via `mask-composite`. Apply to navbar chip, hero right-column tag, secondary CTAs, modal cards — anywhere that should feel premium-glass.

In `app/globals.css`:

```css
.liquid-glass {{
  background: rgba(0, 0, 0, 0.4);
  background-blend-mode: luminosity;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: none;
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}}
.liquid-glass::before {{
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1.4px;
  background: linear-gradient(180deg,
    rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.1) 20%,
    rgba(255,255,255,0) 40%, rgba(255,255,255,0) 60%,
    rgba(255,255,255,0.1) 80%, rgba(255,255,255,0.3) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
          mask-composite: exclude;
  pointer-events: none;
}}
```

Both `-webkit-mask-composite: xor` and `mask-composite: exclude` are required — first for Safari, second for spec-compliant browsers. The `border-radius: inherit` line means the gradient border follows whatever `rounded-*` class the parent has (rounded-xl on the navbar, rounded-xl on the hero tag, etc.).

#### 3. Clip-Path Image Reveal

```tsx
useGSAP(() => {{
  gsap.utils.toArray<HTMLElement>(".reveal-image").forEach((img) => {{
    gsap.fromTo(img,
      {{ clipPath: "inset(0 100% 0 0)" }},
      {{
        clipPath: "inset(0 0% 0 0)",
        duration: 1.1,
        ease: "expo.out",
        scrollTrigger: {{ trigger: img, start: "top 78%" }},
      }}
    )
  }})
}})
```

Add `className="reveal-image"` to every `<Image>` that should reveal on scroll.

#### 4. Counting Stats

```tsx
useGSAP(() => {{
  gsap.utils.toArray<HTMLElement>(".stat-number").forEach((el) => {{
    const target = parseInt(el.dataset.target ?? "0", 10)
    gsap.fromTo(el,
      {{ textContent: 0 }},
      {{
        textContent: target,
        duration: 2,
        ease: "power2.out",
        snap: {{ textContent: 1 }},
        scrollTrigger: {{ trigger: el, start: "top 85%" }},
      }}
    )
  }})
}})
```

JSX: `<span className="stat-number" data-target={{500}}>0</span>`

#### 5. Parallax Background — Wrap `<Image>` In A `<div ref>`

**CRITICAL: `next/image` does NOT forward refs.** Attaching a `ref` directly to `<Image>` throws `Function components cannot be given refs` at runtime. The fix is always the same: wrap the `<Image>` in a `<div ref={{...}}>` and animate the wrapper.

```tsx
"use client"
import {{ useRef }} from "react"
import Image from "next/image"
import {{ useGSAP }} from "@gsap/react"
import gsap from "gsap"
import {{ ScrollTrigger }} from "gsap/ScrollTrigger"

export function ParallaxHero() {{
  const sectionRef = useRef<HTMLElement>(null)
  const bgRef      = useRef<HTMLDivElement>(null)   // ← ref goes on the DIV, never the <Image>

  useGSAP(() => {{
    if (!bgRef.current) return
    gsap.to(bgRef.current, {{
      yPercent: -25,
      ease: "none",
      scrollTrigger: {{
        trigger: sectionRef.current,
        start: "top top",
        end: "bottom top",
        scrub: 1,
      }},
    }})
  }}, {{ scope: sectionRef }})

  return (
    <section ref={{sectionRef}} className="relative overflow-hidden min-h-[100dvh]">
      <div ref={{bgRef}} className="absolute inset-0 parallax-bg">
        <Image src="..." alt="..." fill className="object-cover" priority />
      </div>
      {{/* content above the parallax bg */}}
    </section>
  )
}}
```

Same rule applies anywhere you animate an image: **the ref goes on a wrapping div, never on `<Image>`**. This includes clip-path reveals — `className="reveal-image"` should be applied to a `<div>` wrapper, not the `<Image>` itself.

Apply `className="parallax-bg"` to the wrapper div, not the `<Image>`.

#### 6. FAQ Accordion — Use `transitionend`, NOT `setTimeout`

When an accordion opens, `ScrollTrigger.refresh()` must fire AFTER the layout actually settles. Using `setTimeout(refresh, 300)` is fragile — if the CSS transition is interrupted or slower than expected, trigger positions are stale. Always listen for `transitionend` on the panel.

```tsx
"use client"
import {{ useRef, useState }} from "react"
import {{ ScrollTrigger }} from "gsap/ScrollTrigger"

export function FAQItem({{ question, answer }}: {{ question: string; answer: string }}) {{
  const panelRef = useRef<HTMLDivElement>(null)
  const [open, setOpen] = useState(false)

  const toggle = () => {{
    const next = !open
    setOpen(next)
    const panel = panelRef.current
    if (!panel) return

    // Wait for the CSS height/maxHeight transition to finish, then refresh ScrollTrigger.
    const onTransitionEnd = (e: TransitionEvent) => {{
      if (e.target !== panel) return
      ScrollTrigger.refresh()
      panel.removeEventListener("transitionend", onTransitionEnd)
    }}
    panel.addEventListener("transitionend", onTransitionEnd)
  }}

  return (
    <div className="border-b border-white/10">
      <button onClick={{toggle}} className="w-full flex justify-between py-6">
        <span>{{question}}</span>
        <span className={{`transition-transform ${{open ? "rotate-180" : ""}}`}}>↓</span>
      </button>
      <div
        ref={{panelRef}}
        className="overflow-hidden transition-[max-height] duration-300 ease-out"
        style={{{{ maxHeight: open ? "500px" : "0px" }}}}
      >
        <p className="pb-6 text-on-surface-variant">{{answer}}</p>
      </div>
    </div>
  )
}}
```

Never call `ScrollTrigger.refresh()` inside a bare `setTimeout` after an animation. Always wait for the actual `transitionend` (or `animationend`).

---

#### 7. Three.js Hero Background (when industry intel says so)

Only include Three.js if Section "INDUSTRY INTELLIGENCE" → `threejs_type` is **not** `none`. Use dynamic import with `ssr: false`. The hero `<video>` and Three.js canvas are mutually exclusive — pick the one the contract names.

Variants (drive the renderer choice from `threejs_type`):
- `particles` — tech, services, security, IT: drifting particle field, slow camera dolly
- `aurora_mesh` — beauty, wellness, med-spa: soft gradient mesh, slow undulation
- `wireframe_geometry` — architecture, marketing-agency: rotating wireframe forms, low-poly
- `ripple_plane` — pools, cleaning, plumbing: subtle water-ripple shader plane, scroll-reactive

Performance rules (iOS-safe):
```tsx
const Hero3D = dynamic(() => import("@/components/three/Hero3D"), {{ ssr: false }})

<Canvas
  gl={{ antialias: false, powerPreference: "high-performance" }}
  dpr={{[1, 2]}}
  camera={{ position: [0, 0, 5], fov: 45 }}
>
  {{/* variant geometry */}}
</Canvas>
```

Mandatory: context-lost handler, dispose geometries/materials on unmount, cap DPR at 2.

---

#### 8. Contact Form — Real Server Action + Resend (FOUNDATION-MANDATORY)

The contact form is the only path a visitor has to actually reach the business. Every Pebble build today emits a form, but the form is fake — `onSubmit` calls `e.preventDefault()` then sets a local "Thanks!" state. Real visitors filling that form send nothing, anywhere. This is the engine's most visible functionality gap; the foundation closes it.

The contact form is a real Next.js Server Action that calls `resend.emails.send(...)` and returns `{{ ok: boolean, error?: string }}`. The client renders the success / error state from that return value. When `RESEND_API_KEY` is unset (development without credentials), the Server Action takes a graceful no-send path and returns `{{ ok: true }}` so the UX still completes cleanly. The eval suite enforces both the wiring (`contact_form_uses_server_action`) and the dependency (`resend_in_dependencies`).

Three required artifacts:

##### `lib/email.ts` — Resend client wrapper (server-only)

```ts
import "server-only";
import {{ Resend }} from "resend";

// Centralized client so the Resend SDK is only ever instantiated on the server.
// Returns `null` when the key is unset — callers must handle the no-send path
// so local dev without an API key still works.
export function getResendClient(): Resend | null {{
  const key = process.env.RESEND_API_KEY;
  if (!key) return null;
  return new Resend(key);
}}

export const CONTACT_TO_EMAIL = process.env.CONTACT_TO_EMAIL || process.env.RESEND_TO_EMAIL || "";
export const CONTACT_FROM_EMAIL = process.env.CONTACT_FROM_EMAIL || "onboarding@resend.dev";
```

##### `app/actions/contact.ts` — Server Action

```ts
"use server";
import {{ getResendClient, CONTACT_TO_EMAIL, CONTACT_FROM_EMAIL }} from "@/lib/email";

export type ContactFormState = {{
  ok: boolean;
  message?: string;
  error?: string;
}};

export async function submitContactForm(
  _prevState: ContactFormState | null,
  formData: FormData,
): Promise<ContactFormState> {{
  const name = String(formData.get("name") ?? "").trim();
  const email = String(formData.get("email") ?? "").trim();
  const phone = String(formData.get("phone") ?? "").trim();
  const message = String(formData.get("message") ?? "").trim();

  if (!name || !email || !message) {{
    return {{ ok: false, error: "Please provide a name, email, and message." }};
  }}
  if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)) {{
    return {{ ok: false, error: "That email address doesn't look right." }};
  }}

  const resend = getResendClient();
  if (!resend || !CONTACT_TO_EMAIL) {{
    // No-key path: succeed silently so local dev runs without credentials.
    // Production with no key configured is a hard misconfig — log it.
    console.warn("[contact] RESEND_API_KEY or CONTACT_TO_EMAIL not set — message not delivered");
    return {{ ok: true, message: "Thanks — we'll be in touch." }};
  }}

  try {{
    await resend.emails.send({{
      from: CONTACT_FROM_EMAIL,
      to: [CONTACT_TO_EMAIL],
      subject: `New contact form: ${{name}}`,
      replyTo: email,
      text: `From: ${{name}} <${{email}}>${{phone ? ` (${{phone}})` : ""}}\n\n${{message}}`,
    }});
    return {{ ok: true, message: "Thanks — we'll be in touch." }};
  }} catch (err) {{
    const reason = err instanceof Error ? err.message : "Unknown error";
    return {{ ok: false, error: `Could not send right now (${{reason}}). Please call or email directly.` }};
  }}
}}
```

##### `components/forms/ContactForm.tsx` — Client form

```tsx
"use client";
import {{ useActionState }} from "react";
import {{ useFormStatus }} from "react-dom";
import {{ submitContactForm, type ContactFormState }} from "@/app/actions/contact";

function SubmitButton() {{
  const {{ pending }} = useFormStatus();
  return (
    <button
      type="submit"
      disabled={{pending}}
      className="bg-white text-black px-8 py-3 rounded-lg font-medium disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black"
    >
      {{pending ? "Sending…" : "Send Message"}}
    </button>
  );
}}

export function ContactForm() {{
  const [state, action] = useActionState<ContactFormState | null, FormData>(submitContactForm, null);
  return (
    <form action={{action}} className="space-y-4 max-w-xl">
      <input name="name" placeholder="Your name" required className="w-full bg-black/40 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70" />
      <input type="email" name="email" placeholder="Email" required className="w-full bg-black/40 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70" />
      <input name="phone" placeholder="Phone (optional)" className="w-full bg-black/40 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70" />
      <textarea name="message" placeholder="How can we help?" rows={{5}} required className="w-full bg-black/40 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70" />
      <SubmitButton />
      {{state?.ok && (
        <p role="status" className="text-green-300">{{state.message ?? "Sent."}}</p>
      )}}
      {{state && state.ok === false && (
        <p role="alert" className="text-red-300">{{state.error}}</p>
      )}}
    </form>
  );
}}
```

##### `.env.example` (mandatory at project root)

```
# Resend transactional email — Pebble's contact form Server Action delivers
# submissions through this account. Create a key at https://resend.com/api-keys
# and a verified domain at https://resend.com/domains, then drop in:
RESEND_API_KEY=
CONTACT_FROM_EMAIL=onboarding@resend.dev
CONTACT_TO_EMAIL=
```

Why this shape:
- **`useActionState` + `useFormStatus`** are the React 19 idiomatic primitives. They give us a pending state, a returned state object, and progressive enhancement (the form submits even without JS). No `onSubmit` / `e.preventDefault()` plumbing — the form posts straight to the Server Action.
- **`Resend` SDK** is the 2026 standard for transactional email from JAMstack apps. Lovable uses it as one of its preferred App Connectors; Base44 uses a proprietary wrapper. Going through Resend keeps Pebble builds portable.
- **Graceful no-key path** means local development without `RESEND_API_KEY` set still flows cleanly — submissions return `ok: true` and log a warning instead of crashing.
- **`server-only` import in `lib/email.ts`** is a Next.js guard that throws at build time if a client component accidentally imports the Resend client.
- **`replyTo`** on the outbound email is the visitor's address so the recipient can hit Reply in their inbox to respond.

The `<a href="mailto:...">` / `<a href="tel:...">` links elsewhere on the site remain as direct contact paths. The Server Action form is the path for visitors who prefer typing a message in.

---

### Working CTAs — Zero Dead Links

| CTA | Implementation |
|---|---|
| Phone | `<a href="tel:[BUSINESS PHONE]">` |
| Email | `<a href="mailto:[EMAIL]">` |
| Book | External booking URL or `onClick` scroll to `#contact` |
| Form submit | Next.js Server Action (`"use server"`) wired via `useActionState` — see Code Pattern 8. Never `onSubmit` with a fake success state, never `href="#"`. |
| Page nav | `<Link href="/services">` — real Next.js routes only |

---

### Image Usage

Section 8b provides Pexels photo URLs. Use `next/image` — never raw `<img>`:

```tsx
import Image from "next/image"

<div className="relative overflow-hidden">
  <Image
    src="https://images.pexels.com/photos/..."
    alt="descriptive alt text"
    fill
    className="object-cover reveal-image"
    priority={{false}}
  />
</div>
```

Hero image only: add `priority` prop. All others: lazy load (default).

### Delivery Checklist

**FOUNDATION (every item required — eval suite enforces):**
- [ ] `Inter` loaded via `next/font/google` (weights 300/400/500/600) in `app/layout.tsx`
- [ ] `tailwind.config.ts` `fontFamily.sans` extended with `var(--font-inter)` + `Inter`
- [ ] `app/globals.css` `body` rule sets `font-family: var(--font-inter), Inter, ui-sans-serif, system-ui, sans-serif` + `-webkit-font-smoothing: antialiased`
- [ ] `components/ui/AnimatedHeading.tsx` present, verbatim from Code Pattern 1
- [ ] `components/ui/FadeIn.tsx` present, verbatim from Code Pattern 1
- [ ] `.liquid-glass` class in `app/globals.css` with `::before` mask-composite gradient border
- [ ] `components/layout/Navbar.tsx` uses `liquid-glass rounded-xl` chip pattern from Code Pattern 2
- [ ] `components/sections/Hero.tsx` composes AnimatedHeading + FadeIn + full-bleed `<video autoPlay muted loop playsInline>` with NO overlay
- [ ] Hero section is `min-h-[100dvh]`, `bg-black`, content `flex justify-end` at bottom
- [ ] Hero h1 uses `AnimatedHeading` with `\n` line break and `letterSpacing: '-0.04em'`
- [ ] Subhead in `FadeIn delay={{800}}`, CTAs in `FadeIn delay={{1200}}`, optional right-tag in `FadeIn delay={{1400}}`
- [ ] `prefers-reduced-motion` media query in globals.css (transition + animation duration to 0.01ms)
- [ ] `AnimatedHeading.tsx` includes BOTH `<span className="sr-only">` (full text for screen readers) AND `<span aria-hidden="true">` (decorative char animation) — eval `animated_heading_screen_reader_safe`
- [ ] Every `<a>` and `<button>` with a `className` in the navbar + hero CTAs includes the `focus-visible:` utility chain — eval `interactive_elements_have_focus_visible`
- [ ] Hero `<video>` element includes a `poster="..."` attribute — eval `hero_video_has_poster`
- [ ] Hero h1 and subhead carry `textShadow` (inline `style` or Tailwind `drop-shadow-*`) for legibility against the un-overlaid video — eval `hero_text_has_legibility_safeguard`

**FOUNDATION perf + conversion + mobile (May 2026 NLM research addendum):**
- [ ] Hero `<video>` element includes a `preload=` attribute (`preload="metadata"` is the default recommendation; `preload="auto"` also acceptable). Without it, browser defaults drift and LCP regresses. — eval `perf_budget_or_lighter`
- [ ] `app/layout.tsx` `<head>` includes a `<link rel="preload" as="image" href="/images/hero-poster.jpg" />` (OR the hero renders the poster via `<Image priority>`) so the first paint lands before JS hydrates. — eval `perf_budget_or_lighter`
- [ ] Any hand-rolled `@font-face` block in `app/globals.css` (or any CSS) MUST declare `font-display: swap` (or `optional` / `fallback`). FOIT hides text for up to 3s on slow connections. `next/font/google` already handles this — only flag hand-rolled @font-face. — eval `perf_budget_or_lighter`
- [ ] If `three` or any `@react-three/*` package is used, import it via `next/dynamic({{ ssr: false }})` in `app/page.tsx`. Static imports of these ~700kb libs block first paint. — eval `perf_budget_or_lighter`
- [ ] Any raw `<img>` (use `next/image` instead — but defense in depth) MUST declare both `width` and `height` attributes so layout doesn't shift when the image loads. — eval `perf_budget_or_lighter`
- [ ] Hero section MUST contain at least ONE qualifying CTA above the fold: an `<a>` or `<button>` with (1) an action-verb first word (Get / Start / Try / Book / Contact / Schedule / Learn / Call / Discover / Explore etc.), (2) a real href (`/path`, `tel:`, `mailto:`, `#section`, `https://...` — never `href="#"` alone), and (3) a visually-prominent `bg-*` className. 70% of small-business sites lack a clear homepage CTA — Pebble doesn't. — eval `hero_cta_above_fold`
- [ ] `app/layout.tsx` MUST export viewport via `export const viewport = {{ width: "device-width", initialScale: 1 }}` (or include `<meta name="viewport" content="width=device-width, initial-scale=1">` in `<head>`). Without it, mobile renders at desktop width and forces user-zoom. — eval `mobile_optimized_responsive`
- [ ] Hero file uses at least one Tailwind responsive prefix (`sm:`, `md:`, `lg:`, `xl:`, or `2xl:`). Desktop-only classes hit mobile at desktop scale — 58% of traffic is mobile. — eval `mobile_optimized_responsive`
- [ ] Hero CTAs meet the 44px touch-target minimum via VERTICAL-axis padding/height: `p-3+`, `py-3+`, `min-h-11`, `min-h-[44px]`, `min-h-[3rem]` (decimals like `2.75rem` OK). `px-N` alone does NOT count — horizontal padding doesn't lift the tap target. WCAG 2.5.5 / Apple HIG / Material all converge on 44px. — eval `mobile_optimized_responsive`
- [ ] `tailwind.config.ts` must NOT explicitly empty the `screens` key (`screens: {{}}`) — that disables all `sm:`/`md:`/`lg:` utilities globally. Leave `screens` unset to keep Tailwind defaults. — eval `mobile_optimized_responsive`

**SECTIONS BELOW HERO:**
- [ ] Trust bar: counting stats with `data-target` + GSAP textContent
- [ ] Services: full-bleed vertical alternating sections — NEVER 3-column card grid, NEVER horizontal scroll
- [ ] Social proof: dark section, one large quote
- [ ] All section images: `next/image` + clip-path reveal on scroll

**LINKS, FORMS, COPY:**
- [ ] All phone CTAs: `href="tel:..."` — zero `href="#"` links
- [ ] Contact form: Next.js Server Action at `app/actions/contact.ts` + Resend SDK in `lib/email.ts` + `components/forms/ContactForm.tsx` using `useActionState` — eval `contact_form_uses_server_action`
- [ ] `resend` declared in `package.json` dependencies — eval `resend_in_dependencies`
- [ ] `.env.example` at project root naming `RESEND_API_KEY`, `CONTACT_FROM_EMAIL`, `CONTACT_TO_EMAIL`
- [ ] All copy is industry-specific — no Lorem ipsum, no "Where X meets Y", no invented testimonials
- [ ] All `@/` imports resolve to files emitted in the same build (no orphan imports)
- [ ] Every npm package imported is declared in `package.json` dependencies (do NOT import `react-icons` or `lucide-react` without adding them — prefer inline SVG)

**COMPONENT REUSE — no duplicated UI primitives:**
- [ ] Any UI primitive that appears on more than one page MUST live in `components/` and be imported, never duplicated inline. Specifically: the literal `<form>` opening tag MUST appear in `components/forms/ContactForm.tsx` and nowhere else — `app/contact/page.tsx` imports `ContactForm`, it does NOT redefine the form inline. Same rule for testimonials, pricing tables, FAQ accordions, and CTA sections. — eval `no_duplicate_inline_forms`
- [ ] Industry-specific page-content sections (service-area maps, booking widgets, menu blocks) live in `components/sections/<Name>.tsx` and are imported by the page that uses them. A page file is composition only; no inline section definitions longer than a few lines of JSX.

**STRUCTURE + DELIVERABLES:**
- [ ] 4 pages: Homepage, Services, About, Contact
- [ ] All docs: README, HANDOFF, TODO_ASSETS, STYLE_GUIDE
- [ ] README MUST include a `## What This Site Does NOT Include` section listing 2-5 concrete capabilities the build did NOT cover (e.g. for a therapist site: HIPAA-compliant patient intake; for an HVAC site: real-time technician dispatch; for an ecommerce site: payment-processing certification). Each gap names a recommended third-party tool or workaround. This is honesty, not failure — surface it so the user knows where Pebble stops. — eval `limitations_disclosed_in_readme`
- [ ] `next.config.mjs` is plain JS (JSDoc, not `import type` — that's TS and crashes Node's ESM loader)

---

## 3. Visual Reference & Inspiration

{reference_block}

### Design Reference (Figma / Screenshot)

{design_reference_block}

---

## 4. Additional Context

{extra_context}

---

## 5. No-Slop Rules
{no_slop_block}

---

## 6. Business Intelligence
{business_intelligence_block}

---

## 6b. Industry Research — Data-Driven Insights

{industry_research_block}

---

## 7. iOS / iPhone Compatibility
{ios_skill_block}

---

## 8. Recommended Design System
{design_system_block}

---

## 8b. Placeholder Images (Pexels / Picsum)

{images_block}

---

## 8c. Hero Video (Pexels Video API)

{hero_video_block}

---

## 9. Stack, Motion System, and Build Instructions
{stack_block}

### Self-audit before delivering

**FOUNDATION CHECKS (hero + typography — all MANDATORY):**

| Check | Required |
|---|---|
| Inter global | `Inter` loaded via `next/font/google` with weights 300/400/500/600 in `app/layout.tsx`; Tailwind `fontFamily.sans` extends to use it |
| `body` font-family | `var(--font-inter)` (or `Inter`) in `app/globals.css` `body` rule; `-webkit-font-smoothing: antialiased` + `-moz-osx-font-smoothing: grayscale` |
| AnimatedHeading component | `components/ui/AnimatedHeading.tsx` exists with the exact per-char animation logic from Code Pattern 1, used as the hero h1 |
| FadeIn component | `components/ui/FadeIn.tsx` exists, used for the hero subhead (delay 800), CTA row (delay 1200), and right-column tag (delay 1400) |
| Liquid-glass utility | `.liquid-glass` class in `app/globals.css` with `backdrop-filter: blur(4px)` + `::before` gradient stroke via `mask-composite` |
| Navbar | Liquid-glass rounded chip at top with `px-6 md:px-12 lg:px-16 pt-6` outer wrapper — NOT a full-width blur bar |
| Hero structure | `min-h-[100dvh]` section, `bg-black`, full-bleed `<video autoPlay muted loop playsInline>` with `object-cover`, content `flex justify-end` at bottom |
| Hero video overlay | **ZERO dark overlay** — no `bg-black/40`, no `bg-gradient-to-b from-black/...`, no semi-transparent div above the video. The video plays raw. |
| Hero h1 | Real `<h1>` tag, set via `AnimatedHeading`, sized `text-4xl md:text-5xl lg:text-6xl xl:text-7xl`, `font-normal`, `letterSpacing: '-0.04em'` |
| Hero CTAs | Primary white pill + secondary liquid-glass pill, both wrapped in a FadeIn at 1200ms |
| Right column tag | Optional liquid-glass card with three short words; FadeIn at 1400ms; `hidden lg:flex` |
| DNA display_font scope | If used at all, ONLY in accent decorations (pull-quotes, drop caps, stat numbers, optional hero tag) — NEVER the hero h1, NEVER `body` default |

**MOTION + ACCESSIBILITY:**

| Check | Required |
|---|---|
| reduced-motion | `@media (prefers-reduced-motion: reduce)` in globals.css disabling animation-duration AND transition-duration to 0.01ms |
| AnimatedHeading respects reduced-motion | Component reads `window.matchMedia("(prefers-reduced-motion: reduce)")` on mount and skips per-char delays when set |
| FadeIn respects reduced-motion | Same — renders at final opacity immediately when user has reduced-motion set |
| AnimatedHeading screen-reader safe | `<span className="sr-only">{{text}}</span>` (semantic content for ATs) + `<span aria-hidden="true">` (decorative per-char animation) — both required inside `<h1>` |
| Focus-visible on interactives | Every `<a>` / `<button>` with a `className` (hero CTAs, navbar links, Call Us pill) carries `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black` |
| Hero text legibility | `textShadow` on hero h1 (built into AnimatedHeading) AND on hero subhead `<p>` (inline `style`). Foundation has no dark overlay, so text carries its own shadow. |
| Hero video poster | `<video>` element has a `poster="..."` attribute. Painted instantly while the video loads — should visually match the chosen video (mood / darkness). |

**ANTI-SLOP + CONTENT:**

| Check | Required |
|---|---|
| Phone number | `[BUSINESS PHONE]` — NEVER a 555 number or invented number |
| Subtext | No "Where X meets Y" — specific claim, number, or location |
| Headline | No "Unrivaled / World-class / Unleash" — specific and arguable |
| Booking tool | Matches industry — Booksy ONLY for beauty/wellness |
| Testimonials | Real only or omitted — never fabricated |

**SECTIONS BELOW THE HERO:**

| Check | Required |
|---|---|
| Services layout | Full-bleed vertical alternating sections — NEVER 3-column card grid, NEVER horizontal scroll |
| Stats | GSAP counting numbers — never static text |
| Social proof | Dark section, large single quote — never a carousel of small cards |
| Section images | Clip-path reveal on scroll (wrapper div, not on `<Image>`) |
| Services CTA | Phone (`href="tel:[BUSINESS PHONE]"`) and contact route — zero `href="#"` |

**TOOLING + SAFETY:**

| Check | Required |
|---|---|
| **GSAP SplitText** | **NEVER import `gsap/SplitText`** — paid Club plugin, crashes on free GSAP. The hero uses `AnimatedHeading` instead (Code Pattern 1). |
| **`next/image` refs** | **NEVER attach a `ref` directly to `<Image>`** — Next's Image component does not forward refs. Always wrap in a `<div ref={{...}}>` and animate the wrapper. |
| Images | `next/image` everywhere — never raw `<img>` |
| Video | `autoPlay muted loop playsInline` — always all four attributes |
| Hero video src | Use `/videos/hero.mp4` (local) when provided — Pexels CDN URL only as fallback |
| Form | Real Next.js Server Action calling Resend (see Code Pattern 8) — `useActionState` on the client, `"use server"` on the action |
| Input font | Minimum `font-size: 16px` — prevents iOS zoom |
| Safe area | `env(safe-area-inset-*)` in globals.css |
| SSR safety | `normalizeScroll` + `ScrollTrigger.config` inside `useEffect` — NEVER at module level |
| FAQ accordion | `ScrollTrigger.refresh()` triggered by `transitionend` — NEVER a bare `setTimeout` |
| **Lenis config** | Only Lenis 1.1.x options: `duration`, `easing`, `smoothWheel`, `syncTouch`, `touchMultiplier`, `infinite`. `smoothTouch` and `overscroll` are REMOVED in 1.1.x. |
| Overscroll | Use CSS `overscroll-behavior-y: none` on `html, body` — not the Lenis option |
| `.gitignore` | Present at project root with `node_modules/`, `.next/`, `.env*.local`, `.DS_Store`, `*.log` |
| `next.config.mjs` | PLAIN JavaScript — NO `import type {{ NextConfig }}` (that's TS syntax in an .mjs file and Node's ESM loader will crash). Use `/** @type {{import('next').NextConfig}} */` JSDoc instead. |
| Package imports | Every npm import must be declared in `package.json` dependencies. Do NOT import `react-icons`, `lucide-react`, etc. without adding them. Prefer inline SVG. |
| `@/` aliases | Every `@/...` import must resolve to a file you also emit. No orphan imports. |

---

## 10. Anti-Slop Audit
{anti_slop_block}

---

## 11. Output -- NO QUESTIONS, BUILD IMMEDIATELY

**Do not write a plan. Do not ask questions. Build now.**

Output every file the project needs. Follow the Stack Skill project structure.

Required files (paths are PROJECT-ROOT relative — match the Stack Skill's tsconfig
`"paths": {{ "@/*": ["./*"] }}`. DO NOT prefix with `src/` — imports written as
`@/components/...` would not resolve if files lived under `src/`, and the build
would fail at compile time):

- `README.md` (MUST include a `## Deploy` section explaining: 1) push the project to GitHub, 2) import the repo at https://vercel.com/new, 3) add `RESEND_API_KEY`, `CONTACT_TO_EMAIL`, `CONTACT_FROM_EMAIL` env vars in the Vercel dashboard. Also reference the `vercel.json` already at the project root.), `HANDOFF.md`, `TODO_ASSETS.md`, `STYLE_GUIDE.md`, `CLIENT_ANSWERS.md`
- `vercel.json` — minimal Vercel platform config so the import flow auto-detects Next.js framework. Verbatim:

```json
{{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "nextjs"
}}
```

The eval `deploy_to_vercel_scaffold` verifies BOTH the README has a `Deploy` heading AND the `vercel.json` exists. The user owns the deployed site (their own Vercel project, their own domain, no Pebble lock-in).
- `content/site.ts`, `content/sections.ts`, `content/services.ts`, `content/faqs.ts`, `content/testimonials.ts`
- **FOUNDATION COMPONENTS (mandatory — eval suite verifies presence):**
  - `components/ui/AnimatedHeading.tsx` — per-character hero h1 entrance, verbatim from Code Pattern 1 (must include sr-only span + aria-hidden wrapper + textShadow)
  - `components/ui/FadeIn.tsx` — opacity transition wrapper, verbatim from Code Pattern 1
  - `components/layout/Navbar.tsx` — liquid-glass chip from Code Pattern 2 (with focus-visible utilities on all links)
  - `components/layout/Footer.tsx` — 3-column sitemap-bearing footer from Section 8 above (every page in this build appears as a Next.js Link in the sitemap column; eval `footer_lists_all_pages` enforces this)
  - `components/sections/Hero.tsx` — composes AnimatedHeading + FadeIn + video bg, imported by `app/page.tsx`
  - `components/forms/ContactForm.tsx` — Server Action + Resend client form, verbatim from Code Pattern 8
  - `app/actions/contact.ts` — Server Action that calls Resend, verbatim from Code Pattern 8
  - `lib/email.ts` — Resend client wrapper (server-only), verbatim from Code Pattern 8
  - `.env.example` — names `RESEND_API_KEY`, `CONTACT_FROM_EMAIL`, `CONTACT_TO_EMAIL`
- `lib/motion.ts`, `components/motion/Reveal.tsx`, `components/motion/Parallax.tsx`, `components/motion/SmoothScroll.tsx`
  - Note: `components/motion/SplitText.tsx` is REMOVED — the hero h1 uses `AnimatedHeading`, not a SplitText wrapper. Do not emit a SplitText component.
- `config/brand.config.ts`, `config/motion.config.ts`
- `next.config.mjs` (NOT `.ts` — and the file body must be PLAIN JS, not TypeScript: `/** @type {{import('next').NextConfig}} */` JSDoc, no `import type`, no `: NextConfig` annotation)
- `tailwind.config.ts` — must extend `fontFamily.sans` to include `var(--font-inter)` and `Inter` so every Tailwind `font-sans` usage picks up Inter automatically
- `app/globals.css` — must contain the `.liquid-glass` class (Code Pattern 2b) AND a `body` rule setting `font-family: var(--font-inter), Inter, ui-sans-serif, system-ui, sans-serif`
- `postcss.config.js`, `tsconfig.json`, `package.json` (must declare `resend` in dependencies), `.gitignore`

Every import statement uses the `@/` alias rooted at the project. Examples:
`import {{ Reveal }} from "@/components/motion/Reveal"`,
`import {{ SITE_TITLE }} from "@/content/site"`,
`import {{ cn }} from "@/lib/utils"`.

Where contact info is missing: use `[BUSINESS PHONE]`, `[EMAIL]`, `[ADDRESS]`. Never invent.
