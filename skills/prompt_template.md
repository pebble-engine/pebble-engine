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

## 2. OUTPUT STRUCTURE

**READ THE LAYOUT DNA BLOCK AT THE TOP OF THIS PROMPT FIRST.**

The Layout DNA block defines this build's structural architecture — hero type, nav
pattern, section flow, and which foundation components to use. The section below
is the **gradient_mesh fallback** — it applies ONLY when no Layout DNA block is
present, or when the Layout DNA id is `gradient_mesh`.

If a Layout DNA block is present and its id is NOT `gradient_mesh`:
- Follow the Layout DNA's `hero_structure` exactly for the hero
- Follow the Layout DNA's `nav_structure` for the navbar
- Respect the Layout DNA's component table (AnimatedHeading, FadeIn, liquid-glass, GrainOverlay)
- Use the Layout DNA's `section_flow` for homepage section order
- The Style DNA block (colors, fonts, tokens) still applies — paint the surface with Style DNA on top of the Layout DNA structure

### Required Pages

**FOUNDATION PAGES (every build, always):**

1. **Homepage** (`app/page.tsx`) — landing page, follows the Layout DNA's structure
2. **Services** (`app/services/page.tsx`) — full-bleed alternating layout, NOT a generic card grid (unless Layout DNA specifies otherwise)
3. **About** (`app/about/page.tsx`) — editorial story
4. **Contact** (`app/contact/page.tsx`) — REAL working form (Server Action + Resend SDK — see Code Pattern 8). NOT an `onSubmit` with a hardcoded success state. The form posts to a Next.js Server Action, which calls `resend.emails.send(...)` and returns `{{ ok: true | false, error?: string }}`. When `RESEND_API_KEY` is unset (development without keys), the Server Action returns `{{ ok: true }}` without sending — the eval and the UX still flow cleanly. Map embed below the form.

> **Exception:** Layout DNA `single_screen` renders the entire site in `app/page.tsx`
> with anchor navigation — no sub-routes. When this layout is active, skip the
> individual page files and put all content in the homepage.

**INDUSTRY-AWARE PAGES (rendered dynamically per build):**

{pages_block}

### Homepage — Gradient Mesh Structure (DEFAULT — used when Layout DNA is `gradient_mesh` or absent)

**Section 1: Hero — GRADIENT MESH HERO**

The Design DNA provides the `:root {{}}` CSS token values that drive the gradient
mesh palette. There is **NO `<video>` tag**, **NO Pexels**, **NO external media** in the hero.

**Visual layout:**
- `<section>` is `relative min-h-[100dvh] overflow-hidden flex flex-col` with `style={{{{ background: "var(--color-bg)" }}}}` (use the CSS variable instead of `bg-black` — the post-gen editor swaps palettes by patching only `globals.css`).
- **Gradient mesh blobs** — two or three absolutely-positioned `<div>` elements with `pointer-events-none` and `aria-hidden="true"`. Use `background: radial-gradient(circle at center, var(--color-accent-glow) 0%, transparent 65%)` and `filter: blur(80px)` (primary blob, ~600–800px square, upper-right) or `filter: blur(60px)` (secondary blob, ~400px, lower-left). Always include the blobs — they are the ambient light bloom that gives each DNA card its visual fingerprint.
- **`GrainOverlay`** is a singleton — render it ONCE in `app/layout.tsx` as a `fixed` layer covering the entire app, NOT inside `Hero.tsx` or any section component. (See Code Pattern 9.)
- **The `<section>` MUST be `flex flex-col`** — without it, the inner content's `justify-end` has nothing to push against and the hero text ends up top-aligned. This is the #1 visual regression — copy the exact classlist.
- **Inner content container** sits at the BOTTOM of the viewport via `flex-1 flex flex-col justify-end` (use `flex-1`, which gives the section room to grow; `h-full` collides with `min-h-[100dvh]`): `relative z-10 flex-1 flex flex-col justify-end px-6 md:px-12 lg:px-16 pb-12 lg:pb-16` with `style={{{{ color: "var(--color-text-primary)" }}}}` — use the CSS token instead of a hardcoded `text-white` class.
- On large screens, content uses a 2-column grid: `lg:grid lg:grid-cols-2 lg:items-end gap-8`

**Left column — primary content (vertical order):**
1. `<AnimatedHeading text="line one\nline two" className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-normal mb-4" />` — the h1 with per-character entrance animation. Two lines separated by `\n`. Use the brand's value prop in two beats. **THE HEADING IS A REAL `<h1>` TAG** — render it semantically so screen readers, search engines, and the accessibility eval all recognize the page title. Inter always (the DNA's display_font is for accent use only). `textShadow` is built into the component.
2. `<FadeIn delay={{800}} duration={{1000}}>` wrapping `<p className="text-base md:text-lg mb-5" style={{{{ color: "var(--color-text-secondary)" }}}}>…subhead sentence…</p>` — one sentence naming the outcome the visitor gets. CSS token, not hardcoded `text-gray-300`.
3. `<FadeIn delay={{1200}} duration={{1000}}>` wrapping `<div className="flex flex-wrap gap-4">` containing two CTAs. Both CTAs MUST include the focus-visible utility chain `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent` so keyboard users see a visible focus ring. The eval `interactive_elements_have_focus_visible` enforces this.
   - Primary: `<MagneticButton href="tel:[BUSINESS PHONE]">Get Started</MagneticButton>` (see Code Pattern 12) — uses `var(--color-accent)` for background via inline style. Substitute action verb per industry.
   - Secondary: glass pill — `liquid-glass border border-white/20 px-8 py-3 rounded-lg font-medium hover:opacity-80 transition-opacity focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent` with `style={{{{ color: "var(--color-text-primary)" }}}}` — links to `/services` or another primary route

**Right column — optional brand tag (`hidden lg:flex items-end justify-end`):**
- `<FadeIn delay={{1400}} duration={{1000}}>` wrapping `<GlassCard className="px-6 py-3">` (see Code Pattern 10)
- Inside: `<p className="text-lg md:text-xl lg:text-2xl font-light" style={{{{ color: "var(--color-text-primary)" }}}}>Three. Short. Words.</p>` — three or four short phrases summarizing the business posture. Example: "Roasted. Direct. Local." or "Plumbing · HVAC · Electrical"

**Navbar — liquid-glass chip floating at the top (gradient_mesh default only):**
- Outer wrapper: `absolute top-0 inset-x-0 z-50 px-6 md:px-12 lg:px-16 pt-6`
- Inner navbar element: `<nav className="liquid-glass rounded-xl px-4 py-2 flex items-center justify-between" style={{{{ color: "var(--color-text-primary)" }}}}>` 
- Left: logo wordmark in `<Link href="/" className="text-2xl font-semibold tracking-tight">…business name…</Link>`
- Center (`hidden md:flex gap-8 text-sm`): nav links — hover transitions to reduced opacity
- Right: primary CTA — `<a href="tel:[BUSINESS PHONE]" className="bg-white text-black px-6 py-2 rounded-lg text-sm font-medium hover:bg-gray-100">Call Us</a>`

**Accessibility (always required, regardless of Layout DNA):**
- `app/globals.css` includes `@media (prefers-reduced-motion: reduce)` that disables transitions globally
- When `AnimatedHeading` IS used: it checks `prefers-reduced-motion` at mount and renders all characters at final state immediately when set
- When `AnimatedHeading` is NOT used (per Layout DNA): the plain `<h1>` still needs `textShadow` for legibility
- Gradient mesh blobs (when present) have `aria-hidden="true"` and `pointer-events-none`
- Hero h1 is always a real `<h1>` tag — never a styled `<div>`
- All interactive elements carry `focus-visible:` ring utilities

**Universal hero rules (apply regardless of Layout DNA):**
- Hero background is built with CSS (gradient mesh blobs, animated gradients, or a still color token) — the engine does not use `<video>` in the hero, and external CDN URLs (Pexels, Unsplash, Picsum) stay out of the hero so the build has no external media dependencies.
- Use CSS variable tokens exclusively for color (`var(--color-bg)`, `var(--color-accent)`, etc.) so the palette editor can swap an entire build by patching `globals.css`. Hardcoded hex values break that contract.
- For dark surfaces use `style={{{{ background: "var(--color-bg)" }}}}` instead of `bg-black` / `bg-gray-900`. The token resolves to the DNA's chosen dark value and keeps the palette swap working.
- The hero h1 typeface is Inter in every Layout and Style DNA combination. The Style DNA's `display_font` stays in accent decorations (pull-quotes, drop caps, stat numbers, optional hero tag).

**Section 2: Trust Bar — Counting Stats**
- Dark or brand-accent background strip — NOT white
- 3–4 numbers that count up on scroll: years in business, jobs completed, rating, insured/certified
- Each number uses `data-target` attribute + GSAP textContent counter (see Code Patterns)
- Single horizontal row — NOT cards, NOT icons in a grid

**Section 3: Services — Full-Bleed Alternating Sections**
Stack services as full-width vertical sections so the page reads as a magazine spread instead of a generic card wall. Each service is a full-width section. Image fills one half, text the other. Alternate: image-left/text-right, text-left/image-right. Every image uses clip-path reveal (see Code Patterns). For 4+ services, stack all of them vertically — the rhythm of alternating sections IS the visual identity of this part of the page. (Avoid 3-column card grids, horizontal scrollers, and carousels for the services list — they collapse the alternating cadence.)

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
- Keep this section to a single visual focal point — every additional button competes with the conversion target and dilutes the call

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
- **For in-app routes use Next.js `<Link href="/...">`** imported from `next/link` — gives client-side navigation that preserves the SPA experience. Raw `<a href="tel:...">` and `<a href="mailto:...">` are still the correct choice for phone/email links elsewhere on the site.
- Every link points to a route this build actually generates — use real `/path` values instead of `href="#"` placeholders so every footer click lands somewhere real.

Column 3 — **Hours & social**:
- Business hours (one line per day, or "Mon-Fri 9-5 · Sat 10-2")
- Social icons row (only platforms the brief mentions; if none, omit this row entirely — never invent profiles)
- Copyright line at the bottom of the column: `© {{new Date().getFullYear()}} [Business Name]. All rights reserved.` — the year comes from `new Date().getFullYear()` so it auto-rolls over, and the business name is the one from the brief

Bottom strip below the 3 columns: `border-t border-white/10 mt-12 pt-6 text-xs text-white/50` row with "Built with [Pebble](https://pebbleapp.ai)" attribution on the left and "Privacy · Terms" links on the right.

The eval `footer_lists_all_pages` parses the footer file and FAILS the build if any page declared in `plan.json` is missing from the sitemap column. Always ship the footer with a complete sitemap column — every page in `plan.json` should appear there.

### Navigation

> **If a Layout DNA block is present:** follow its `nav_structure` exactly.
> The patterns below apply to the `gradient_mesh` default only, or when no Layout DNA specifies otherwise.

**gradient_mesh default nav** (liquid-glass floating chip):
- Fixed position, `className="navbar"` on `<header>` (required for animation below)
- Logo left · nav links center · phone CTA right
- Mobile: hamburger → fullscreen overlay with staggered link reveals
- CTA button: `<a href="tel:[BUSINESS PHONE]">` always points to a real `tel:` URL so a tap places the call directly

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
- Use `next/image` for ALL images so Next.js handles lazy-loading, responsive sizing, and AVIF/WebP conversion automatically. Use `fill` + `object-cover` for full-bleed, explicit `width`/`height` for fixed-size. `priority` on hero image only. (Raw `<img>` tags skip these optimizations and trip the eval suite.)
- `next/font/google` for fonts — zero layout shift
- Call `gsap.registerPlugin(ScrollTrigger)` ONCE at module scope (top of the file, after the imports). Module-level registration runs before any component mounts, so every component using ScrollTrigger sees the plugin. Calling it inside `useEffect` re-runs the registration on every mount and races with other effects. (Skip `gsap/SplitText` — paid Club plugin, see Code Pattern 1 for the free `AnimatedHeading` substitute.)
- `dynamic()` with `{{ ssr: false }}` for any component using `window` or `document`
- `will-change: transform` only during active animation — remove after with `gsap.set(el, {{ clearProps: "willChange" }})`
- `@media (prefers-reduced-motion: reduce) {{ * {{ animation-duration: 0.01ms !important; transition-duration: 0.01ms !important }} }}` in globals.css

**Typography — MANDATORY GLOBAL FOUNDATION:**

Inter is the engine's universal sans-serif. Every build loads it via `next/font/google` with weights 300, 400, 500, 600. Apply it globally via Tailwind's `font-sans` so every element picks it up automatically. The DNA's `display_font` (Cormorant Garamond, Tektur, etc.) is reserved for ACCENT/decorative use ONLY — pull-quotes, drop caps, stat numbers, the optional right-column hero tag. The hero h1 and the body copy always render in Inter so the page has one consistent reading texture.

In `app/layout.tsx`:

```tsx
import {{ Inter }} from "next/font/google";
import type {{ Metadata }} from "next";
import {{ Footer }} from "@/components/layout/Footer";
import {{ GrainOverlay }} from "@/components/ui/GrainOverlay";
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
      <body className={{`${{inter.className}} antialiased`}}>
        {{/* GrainOverlay is a fixed singleton — renders over every page including the hero. */}}
        <GrainOverlay />
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

In `app/globals.css` — the FIRST thing in the file, BEFORE the Tailwind directives and BEFORE `.liquid-glass`:

**Step 1:** Copy the `:root {{}}` block verbatim from the **DESIGN DNA** section at the very top of this prompt. Those values are this build's design tokens — every color, surface, border, and blur in every component derives from them. Refer to colors via `var(--color-*)` in inline `style` props so the post-gen palette editor can swap the entire build by patching only this `:root` block.

**Step 2:** Add the standard body and motion rules below the `:root` block.

```css
/* === DESIGN TOKENS — copy :root {{}} from the DNA block at top of prompt === */
:root {{
  --color-bg:             #0A0A0A;             /* actual values come from DNA */
  --color-surface-1:      rgba(255,255,255,0.04);
  --color-surface-2:      rgba(255,255,255,0.08);
  --color-border:         rgba(255,255,255,0.08);
  --color-border-bright:  rgba(255,255,255,0.18);
  --color-text-primary:   rgba(255,255,255,0.92);
  --color-text-secondary: rgba(255,255,255,0.52);
  --color-text-muted:     rgba(255,255,255,0.32);
  --color-accent:         #FF3A1F;
  --color-accent-glow:    rgba(255,58,31,0.20);
  --color-accent-subtle:  rgba(255,58,31,0.08);
  --glass-blur:           12px;
  --font-display: 'Unbounded', serif;           /* accent font from DNA */
  --font-body: var(--font-inter), 'Inter', ui-sans-serif, system-ui, sans-serif;
}}

body {{
  font-family: var(--font-inter), Inter, ui-sans-serif, system-ui, sans-serif;
  background: var(--color-bg);
  color: var(--color-text-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}
```

The values shown above are illustrative. The DESIGN DNA block at the top of this prompt replaces them with personality-specific values. The variable NAMES are always the same — `--color-bg`, `--color-accent`, etc. — every component uses them, so the post-gen palette editor can swap an entire build's visual identity by patching only this `:root` block.

This is non-negotiable. Every Tailwind `font-sans` usage picks up Inter automatically. The DNA's display_font, when used, is loaded as a SECOND font via `next/font/google` and applied via its own utility class (e.g. `font-display`) — never replacing Inter as the default body/heading typeface.

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

#### 1. Hero h1 + entrance animation

**Build per Layout DNA's component table.** If the Layout DNA card says `use_animated_heading: True`, build a per-character entrance animation component (named `AnimatedHeading`) using framer-motion. If `False`, use a plain `<h1>` with Inter font and CSS text-shadow for legibility. EITHER WAY the component file `components/ui/AnimatedHeading.tsx` must exist (eval-enforced) — even if your hero doesn't mount it. Same rule for FadeIn / FadeIn cascade per the Layout DNA's `use_fade_in_cascade` flag.

#### 2. Navbar

**Build per Layout DNA's `nav_pattern` + `nav_structure` description.** If the DNA says `use_liquid_glass_nav: True`, render a liquid-glass rounded chip using the `.liquid-glass` CSS utility (see Code Pattern 2b). If False, build the nav pattern the DNA prescribes (utility bar, transparent fixed, terminal prompt, etc.). EVERY anchor and `<Link>` in the nav MUST carry an explicit Tailwind `className` covering color + hover + font weight, so the link is visually styled and keyboard-focusable. (A `className`-less link inherits browser defaults and looks like a 1995 hyperlink.)

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

#### 3. ScrollReveal — Framer Motion whileInView (FOUNDATION)

**The standard below-fold entrance pattern.** Every service card, stat block, testimonial, and content section uses this component to scroll-reveal. It replaces manual GSAP ScrollTrigger setups — more declarative, React-idiomatic, and LLM-predictable.

```tsx
// components/ui/ScrollReveal.tsx
"use client";
import {{ motion }} from "framer-motion";
import {{ ReactNode }} from "react";

type Direction = "up" | "down" | "left" | "right";

type Props = {{
  children: ReactNode;
  direction?: Direction;
  delay?: number;       // seconds (Framer uses seconds, not ms)
  duration?: number;    // seconds; default 0.7
  className?: string;
}};

const initial: Record<Direction, object> = {{
  up:    {{ opacity: 0, y: 40 }},
  down:  {{ opacity: 0, y: -40 }},
  left:  {{ opacity: 0, x: 40 }},
  right: {{ opacity: 0, x: -40 }},
}};

export function ScrollReveal({{ children, direction = "up", delay = 0, duration = 0.7, className }}: Props) {{
  return (
    <motion.div
      initial={{initial[direction]}}
      whileInView={{{{ opacity: 1, x: 0, y: 0 }}}}
      viewport={{{{ once: true, margin: "-80px" }}}}
      transition={{{{ duration, ease: [0.16, 1, 0.3, 1], delay }}}}
      className={{className}}
    >
      {{children}}
    </motion.div>
  );
}}
```

Usage — wrap any below-fold element:

```tsx
import {{ ScrollReveal }} from "@/components/ui/ScrollReveal";

<ScrollReveal direction="up" delay={{0.1}}>
  <GlassCard>…</GlassCard>
</ScrollReveal>

// Staggered grid — increment delay by 0.1s per item
{{services.map((s, i) => (
  <ScrollReveal key={{s.id}} direction="up" delay={{i * 0.1}}>
    <div>…</div>
  </ScrollReveal>
))}}
```

**Important:** For section images, wrap the `<Image>` in a `<div>` first (next/image does not forward refs), then wrap that div in `<ScrollReveal>`. The `ScrollReveal` component always wraps a host DOM element (e.g. `<div>`, `<section>`) so it can attach its motion ref cleanly.

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

Always wait for the actual `transitionend` (or `animationend`) before calling `ScrollTrigger.refresh()` after an animation. The event fires when the browser finishes the transition for real, so trigger positions are recalculated against the settled layout instead of a guessed timeout window.

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
      <input aria-label="Your name" name="name" placeholder="Your name" required className="w-full bg-black/40 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70" />
      <input aria-label="Email address" type="email" name="email" placeholder="Email" required className="w-full bg-black/40 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70" />
      <input aria-label="Phone number (optional)" name="phone" placeholder="Phone (optional)" className="w-full bg-black/40 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70" />
      <textarea aria-label="Message" name="message" placeholder="How can we help?" rows={{5}} required className="w-full bg-black/40 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70" />
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

#### 9. GrainOverlay (conditional)

**Only when Layout DNA says `use_grain_overlay: True`** — render a fixed `<div>` in app/layout.tsx with an SVG feTurbulence pattern at opacity ~0.04, mix-blend-mode: overlay, pointer-events: none, z-index above content but below the nav. Singleton, not per-page. When False, omit entirely.

---

#### 10. GlassCard (conditional)

When the build needs a glassmorphism card, use `backdrop-filter: blur(var(--glass-blur))`, semi-transparent surface, hairline ring in `var(--color-border)`. Skip entirely when the Layout DNA doesn't call for glass treatment.

---

#### 11. BentoGrid (only if Layout DNA calls for it)

Most Layout DNAs don't use bento grids. Build one inline with CSS Grid only when the DNA explicitly requests it; otherwise omit.

---

#### 12. MagneticButton (conditional)

When you build a magnetic-hover CTA, use Framer Motion's `useSpring` on x/y translation, dampening ~25, stiffness ~150, rest at 0. Only use magnetic hover for layouts where the DNA's signature_moves call for it (typically gradient_mesh, cinematic). Plain hover states are fine for the rest.

---

#### 13. Section headers

Style section openings per Layout DNA's voice — magazine_scroll uses chapter labels (`Chapter 02 · Services`), terminal uses command-line framing (`$ cat services.txt`), weather_report uses status rows, etc. Let each DNA's voice drive the section header pattern; the generic eyebrow+h2+subhead template is fine for `gradient_mesh` but the others should signature their own.

---

#### 14. Gradient-mesh hero (only when Layout DNA is gradient_mesh)

If and only if Layout DNA is `gradient_mesh`, build the full-viewport ambient-blob hero with radial-gradient + filter:blur, AnimatedHeading anchored to the bottom of the viewport, liquid-glass chip in the right column. For all 9 other Layout DNAs, build the hero per that DNA's `hero_structure` description instead.

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

The hero uses a CSS gradient mesh background — no external photo URLs are injected by default.
When `PEBBLE_USE_IMAGEN=true`, Imagen 4 generates `/images/<slot>.jpg` files after the build.
In that case, use `next/image` with local paths — never raw `<img>`:

```tsx
import Image from "next/image"

<div className="relative overflow-hidden">
  <Image
    src="/images/hero.jpg"
    alt="descriptive alt text"
    fill
    className="object-cover reveal-image"
    priority
  />
</div>
```

Hero image only: add `priority` prop. All others: lazy load (default).
If Imagen is not enabled, implement the hero purely with CSS (gradient mesh, animated gradients, or `bg-black`).

### Delivery Checklist

**FOUNDATION (every item required — eval suite enforces):**
- [ ] `app/layout.tsx` MUST NOT have a `"use client"` directive — it is a Server Component. Metadata (`export const metadata`) and viewport (`export const viewport`) only work in Server Components. If you need client-side logic (scroll listener, context provider), wrap it in a child component with `"use client"` and import it from `layout.tsx`. — eval `layout_is_server_component`
- [ ] `Inter` loaded via `next/font/google` (weights 300/400/500/600) in `app/layout.tsx`
- [ ] `tailwind.config.ts` `fontFamily.sans` extended with `var(--font-inter)` + `Inter`
- [ ] `app/globals.css` `body` rule sets `font-family: var(--font-inter), Inter, ui-sans-serif, system-ui, sans-serif` + `-webkit-font-smoothing: antialiased`
- [ ] `app/globals.css` MUST begin with the `:root {{}}` CSS token block copied verbatim from the DESIGN DNA section at the top of this prompt. All 12 `--color-*` custom properties plus `--glass-blur`, `--font-display`, and `--font-body` must be present. — eval `design_tokens_defined`
- [ ] No hardcoded hex color utilities anywhere in `app/` or `components/`: no `bg-[#...]`, `text-[#...]`, `border-[#...]`. Use `var(--color-*)` in inline `style` props, or Tailwind utilities that don't encode a specific hex. — eval `no_hardcoded_color_utilities`
- [ ] `components/ui/GrainOverlay.tsx` present — the SVG `feTurbulence` grain singleton. Rendered once in `app/layout.tsx` as a `fixed` layer; NOT inside `Hero.tsx` or any other page component.
- [ ] `components/ui/AnimatedHeading.tsx` present, verbatim from Code Pattern 1
- [ ] `components/ui/FadeIn.tsx` present, verbatim from Code Pattern 1
- [ ] `components/ui/ScrollReveal.tsx` present — Framer Motion `whileInView` wrapper, verbatim from Code Pattern 3
- [ ] `components/ui/GlassCard.tsx` present — multi-layer glassmorphism with variant system, from Code Pattern 10
- [ ] `components/ui/MagneticButton.tsx` present — Framer Motion magnetic hover CTA, from Code Pattern 12
- [ ] `.liquid-glass` class in `app/globals.css` with `::before` mask-composite gradient border
- [ ] `components/layout/Navbar.tsx` — pattern per Layout DNA: liquid-glass chip for `gradient_mesh`, or the nav_structure described in the Layout DNA block
- [ ] `components/sections/Hero.tsx` — structure per Layout DNA; NO `<video>` tag, NO external image URLs; for `gradient_mesh` layout: composes AnimatedHeading + FadeIn + CSS gradient mesh blobs
- [ ] Hero section has `style={{{{ background: "var(--color-bg)" }}}}` on its container — every layout uses CSS tokens for background
- [ ] Hero h1 is a semantic `<h1>` tag in EVERY layout — AnimatedHeading when Layout DNA uses it, plain `<h1>` otherwise
- [ ] When AnimatedHeading IS used: `\n` line break, `letterSpacing: '-0.04em'`, subhead in FadeIn delay={{800}}, CTAs delay={{1200}}, right-tag delay={{1400}}
- [ ] `prefers-reduced-motion` media query in globals.css (transition + animation duration to 0.01ms)
- [ ] `components/ui/AnimatedHeading.tsx`, `components/ui/FadeIn.tsx`, `components/ui/ScrollReveal.tsx`, `components/ui/MagneticButton.tsx`, and `components/forms/ContactForm.tsx` MUST each have `"use client";` at the top — they use React hooks which are forbidden in Server Components. Missing this directive causes a Next.js runtime crash. — eval `client_components_have_directive`
- [ ] `AnimatedHeading.tsx` includes BOTH `<span className="sr-only">` (full text for screen readers) AND `<span aria-hidden="true">` (decorative char animation) — eval `animated_heading_screen_reader_safe`
- [ ] Every `<a>` and `<button>` with a `className` in the navbar + hero CTAs includes the `focus-visible:` utility chain — eval `interactive_elements_have_focus_visible`
- [ ] Every `<input>`, `<textarea>`, `<select>` has EITHER `aria-label="..."` OR an associated `<label htmlFor="...">` — eval `a11y_static_audit`. Icon-only `<button>` and `<a>/<Link>` elements also need `aria-label` or `title`. Placeholder text alone is NOT sufficient.
- [ ] Heading levels are strictly sequential: `h1` = page title (one per page), `h2` = section/group headings within the page (e.g. "What We Offer", "Our Values", "Questions & Answers"), `h3` = card/item titles within a section. The most common failure: inner pages jump h1 → h3 and omit h2 entirely. Every section that groups multiple h3 cards MUST have an h2 above it. — eval `a11y_static_audit`

**FOUNDATION perf + conversion + mobile (May 2026 NLM research addendum):**
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
- [ ] Services: full-bleed vertical alternating sections (image-left / text-right, then text-left / image-right). The alternating cadence IS the layout — skip 3-column card grids and horizontal scrollers/carousels for this section.
- [ ] Social proof: dark section, one large quote
- [ ] All below-fold content: wrapped in `<ScrollReveal>` (Code Pattern 3) for Framer Motion `whileInView` entrance. Wrap a `<div>` around `<Image>` first — `next/image` does not forward refs.

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
- [ ] No hardcoded `http://localhost:...` or `http://127.0.0.1:...` URLs in `app/`, `components/`, or `lib/`. API calls must use relative paths (`/api/...`) or `process.env.NEXT_PUBLIC_*`. Hardcoded dev URLs ship broken to production and are invisible at build time. — eval `no_hardcoded_localhost`
- [ ] No Next.js Pages Router APIs in an App Router build: no `import Head from 'next/head'` (use `export const metadata`), no `getServerSideProps`/`getStaticProps`/`getStaticPaths` (use async Server Components), no `import {{ useRouter }} from 'next/router'` (use `next/navigation`). Mixing router APIs causes silent failures or runtime crashes. — eval `no_pages_router_patterns`
- [ ] `app/services/page.tsx`, `app/about/page.tsx`, and `app/contact/page.tsx` MUST all exist. The Navbar links to `/services`, `/about`, and `/contact` by default — missing page files produce dead 404s on every navbar click. The LLM sometimes drops one when context is long. — eval `foundation_pages_present`
- [ ] `components/forms/ContactForm.tsx` MUST have at least one `<input>`, `<textarea>`, or `<select>` element with a `name="..."` attribute. An empty `<form action={{action}} />` with no fields submits nothing. Minimum: name, email, message fields, each with both `name=` and `aria-label=`. — eval `contact_form_has_inputs`

---

## 3. Visual Reference & Inspiration

{reference_block}

### Design Reference (Figma / Screenshot)

{design_reference_block}

---

## 4. Additional Context

{extra_context}

### URL-Extracted Brand Signals

{url_extraction_block}

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

## 8b. Hero Imagery Notes

{images_block}

---

## 9. Stack, Motion System, and Build Instructions
{stack_block}

### Self-audit before delivering

**FOUNDATION CHECKS (hero + typography — all MANDATORY):**

| Check | Required |
|---|---|
| CSS token layer | `app/globals.css :root {{}}` contains all 12 `--color-*` variables + `--glass-blur` + `--font-display` + `--font-body`, copied verbatim from the DNA block |
| No hardcoded colors | Zero `bg-[#...]`, `text-[#...]`, `border-[#...]` utilities anywhere — use `var(--color-*)` in `style` props |
| GrainOverlay | `components/ui/GrainOverlay.tsx` exists; imported and rendered once in `app/layout.tsx` — NOT inside `Hero.tsx` |
| Inter global | `Inter` loaded via `next/font/google` with weights 300/400/500/600 in `app/layout.tsx`; Tailwind `fontFamily.sans` extends to use it |
| `body` font-family | `var(--font-inter)` (or `Inter`) in `app/globals.css` `body` rule; `background: var(--color-bg)`, `-webkit-font-smoothing: antialiased` |
| AnimatedHeading component | `components/ui/AnimatedHeading.tsx` exists with the exact per-char animation logic from Code Pattern 1, used as the hero h1 |
| FadeIn component | `components/ui/FadeIn.tsx` exists, used for the hero subhead (delay 800ms), CTA row (delay 1200ms), and right-column tag (delay 1400ms) |
| ScrollReveal component | `components/ui/ScrollReveal.tsx` exists — Framer Motion `whileInView` wrapper used for all below-fold entrances |
| GlassCard component | `components/ui/GlassCard.tsx` exists — used in hero right-column tag and throughout the build |
| MagneticButton component | `components/ui/MagneticButton.tsx` exists — used as primary CTA in hero and high-impact sections |
| Liquid-glass utility | `.liquid-glass` class in `app/globals.css` with `backdrop-filter: blur(4px)` + `::before` gradient stroke via `mask-composite` |
| Navbar | Liquid-glass rounded chip at top with `px-6 md:px-12 lg:px-16 pt-6` outer wrapper — NOT a full-width blur bar |
| Hero structure | `min-h-[100dvh] flex flex-col` section, `style={{{{ background: "var(--color-bg)" }}}}`, gradient mesh blobs with `var(--color-accent-glow)`, NO `<video>` |
| Hero h1 | Real `<h1>` tag, set via `AnimatedHeading`, sized `text-4xl md:text-5xl lg:text-6xl xl:text-7xl`, `font-normal`, `letterSpacing: '-0.04em'` |
| Hero CTAs | Primary `<MagneticButton>` + secondary liquid-glass pill, both wrapped in a FadeIn at 1200ms |
| Right column tag | `<GlassCard>` with three short words; FadeIn at 1400ms; `hidden lg:flex` |
| DNA display_font scope | If used at all, ONLY in accent decorations: pull-quotes, drop caps, stat numbers, optional hero tag. The hero h1 and `body` default stay in Inter so the reading texture is consistent. |

**MOTION + ACCESSIBILITY:**

| Check | Required |
|---|---|
| reduced-motion | `@media (prefers-reduced-motion: reduce)` in globals.css disabling animation-duration AND transition-duration to 0.01ms |
| AnimatedHeading respects reduced-motion | Component reads `window.matchMedia("(prefers-reduced-motion: reduce)")` on mount and skips per-char delays when set |
| FadeIn respects reduced-motion | Same — renders at final opacity immediately when user has reduced-motion set |
| AnimatedHeading screen-reader safe | `<span className="sr-only">{{text}}</span>` (semantic content for ATs) + `<span aria-hidden="true">` (decorative per-char animation) — both required inside `<h1>` |
| Focus-visible on interactives | Every `<a>` / `<button>` with a `className` (hero CTAs, navbar links, Call Us pill) carries `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black` |
| Form input labels | Every `<input>` / `<textarea>` / `<select>` has `aria-label="..."` OR an associated `<label htmlFor="...">`. Placeholder text does NOT count. |
| Icon-only interactives | Any `<button>` or `<a>` whose sole child is an icon component (e.g. `<X />`, `<ChevronRight />`) needs `aria-label="..."` or `title="..."` |
| Heading order | Strictly sequential: h1 = page title, h2 = section heading, h3 = card/item heading. Inner pages must NOT jump h1 → h3 — each group of h3 cards needs an h2 above it. — eval `a11y_static_audit` |
| Hero text legibility | `textShadow` built into `AnimatedHeading` for the h1. Subhead uses `color: var(--color-text-secondary)` which is already low-opacity against the dark `--color-bg` — sufficient contrast without a shadow. |

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
| Services layout | Full-bleed vertical alternating sections (image-left/text-right, text-left/image-right). The alternating rhythm IS the visual identity — keep 3-column card grids and horizontal scrollers out of this section. |
| Stats | GSAP counting numbers — never static text |
| Social proof | Dark section, large single quote — never a carousel of small cards |
| Section images | `<ScrollReveal>` wrapper from Code Pattern 3. Wrap a `<div>` around `<Image>` first — next/image does not forward refs. |
| Services CTA | Phone (`href="tel:[BUSINESS PHONE]"`) and contact route — zero `href="#"` |

**TOOLING + SAFETY:**

| Check | Required |
|---|---|
| **GSAP SplitText** | **The hero uses `AnimatedHeading` (Code Pattern 1) for per-character entrance animation.** `gsap/SplitText` is the paid Club plugin and crashes on free GSAP — `AnimatedHeading` is the framer-motion substitute already wired into the foundation. |
| **`next/image` refs** | **Attach refs to a wrapping `<div ref={{...}}>` and animate the wrapper** — Next's Image component does not forward refs, so refs go on the parent div. This pattern applies to parallax, clip-path reveals, and any GSAP target containing an image. |
| Images | `next/image` everywhere — never raw `<img>` |
| Hero background | CSS gradient mesh only — NO `<video>`, NO external CDN URLs, NO `bg-black` (use `var(--color-bg)`) |
| Hardcoded colors | Always reference colors as `var(--color-*)` in inline `style` props so the palette editor can swap the build by patching `globals.css`. Arbitrary-value utilities like `bg-[#...]` or `text-[#...]` encode the hex literally and break that contract. |
| Form | Real Next.js Server Action calling Resend (see Code Pattern 8) — `useActionState` on the client, `"use server"` on the action |
| Input font | Minimum `font-size: 16px` — prevents iOS zoom |
| Safe area | `env(safe-area-inset-*)` in globals.css |
| **layout.tsx directive** | **`app/layout.tsx` stays a Server Component** (no `"use client"` directive) so `export const metadata` and `export const viewport` work. Wrap any client-side logic (context providers, scroll listeners) in a child component that carries its own `"use client";` and import it from layout. |
| **Client Component directives** | `AnimatedHeading.tsx`, `FadeIn.tsx`, `ContactForm.tsx` MUST each begin with `"use client";` (no exceptions). Omitting it causes a Next.js crash: "hooks cannot be called from a Server Component". |
| SSR safety | Place `normalizeScroll` + `ScrollTrigger.config` inside a `useEffect` so they only run in the browser. Module-level calls execute during Next.js SSR (where `window` is undefined) and crash the build. |
| FAQ accordion | Trigger `ScrollTrigger.refresh()` from the panel's `transitionend` event so it fires after layout settles. The settled-layout signal is more reliable than a guessed `setTimeout` window. |
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
`"paths": {{ "@/*": ["./*"] }}`. Emit files directly at the project root (e.g. `app/page.tsx`,
`components/ui/AnimatedHeading.tsx`) so the `@/components/...` alias resolves — the
`@/*` mapping points at `./*`, not `./src/*`, and a `src/` prefix would break every alias
import at compile time):

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
  - `components/ui/GrainOverlay.tsx` — fixed SVG grain singleton, verbatim from Code Pattern 9. Rendered in `app/layout.tsx`, nowhere else.
  - `components/ui/AnimatedHeading.tsx` — per-character hero h1 entrance, verbatim from Code Pattern 1 (must include sr-only span + aria-hidden wrapper + textShadow)
  - `components/ui/FadeIn.tsx` — opacity transition wrapper, verbatim from Code Pattern 1
  - `components/ui/ScrollReveal.tsx` — Framer Motion `whileInView` wrapper, verbatim from Code Pattern 3
  - `components/ui/GlassCard.tsx` — multi-layer glassmorphism card, verbatim from Code Pattern 10
  - `components/ui/MagneticButton.tsx` — Framer Motion magnetic CTA, verbatim from Code Pattern 12
  - `components/ui/SectionHeader.tsx` — eyebrow / h2 / subheading component, verbatim from Code Pattern 13
  - `components/layout/Navbar.tsx` — liquid-glass chip from Code Pattern 2 (with focus-visible utilities on all links)
  - `components/layout/Footer.tsx` — 3-column sitemap-bearing footer from Section 8 above (every page in this build appears as a Next.js Link in the sitemap column; eval `footer_lists_all_pages` enforces this)
  - `components/sections/Hero.tsx` — CSS gradient mesh hero from Code Pattern 14 (AnimatedHeading + FadeIn + GlassCard + MagneticButton + gradient blobs; NO `<video>`)
  - `components/forms/ContactForm.tsx` — Server Action + Resend client form, verbatim from Code Pattern 8
  - `app/actions/contact.ts` — Server Action that calls Resend, verbatim from Code Pattern 8
  - `lib/email.ts` — Resend client wrapper (server-only), verbatim from Code Pattern 8
  - `.env.example` — names `RESEND_API_KEY`, `CONTACT_FROM_EMAIL`, `CONTACT_TO_EMAIL`
- `lib/motion.ts`, `components/motion/Reveal.tsx`, `components/motion/Parallax.tsx`, `components/motion/SmoothScroll.tsx`
  - Note: `components/motion/SplitText.tsx` is REMOVED — the hero h1 uses `AnimatedHeading`, not a SplitText wrapper. Do not emit a SplitText component.
- `config/brand.config.ts`, `config/motion.config.ts`
- `next.config.mjs` (NOT `.ts` — and the file body must be PLAIN JS, not TypeScript: `/** @type {{import('next').NextConfig}} */` JSDoc, no `import type`, no `: NextConfig` annotation)
- `tailwind.config.ts` — must extend `fontFamily.sans` to include `var(--font-inter)` and `Inter` so every Tailwind `font-sans` usage picks up Inter automatically
- `app/globals.css` — must begin with the `:root {{}}` CSS token block (all 12 `--color-*` + `--glass-blur` + fonts), then `.liquid-glass` (Code Pattern 2b), then `body` rule setting `font-family: var(--font-inter), Inter, ui-sans-serif, system-ui, sans-serif` and `background: var(--color-bg)`
- `postcss.config.js`, `tsconfig.json`, `package.json` (must declare `resend` in dependencies), `.gitignore`
- `app/icon.svg` — branded favicon via Next.js App Router file convention; Next.js auto-generates the `<link rel="icon">` tag — no `metadata.icons` config needed. Use a simple SVG with the business initial or a relevant icon shape. Eval `favicon_defined` verifies this file exists.
- `app/sitemap.ts` — Next.js dynamic sitemap export. Must return an array of `{{ url, lastModified }}` entries covering every page generated in this build. Eval `sitemap_and_robots_present` verifies.
- `app/robots.ts` — Next.js robots.txt export. Must include a `Sitemap` entry pointing to the absolute sitemap URL. Eval `sitemap_and_robots_present` verifies.

Every import statement uses the `@/` alias rooted at the project. Examples:
`import {{ Reveal }} from "@/components/motion/Reveal"`,
`import {{ SITE_TITLE }} from "@/content/site"`,
`import {{ cn }} from "@/lib/utils"`.

`lib/utils.ts` MUST be implemented WITHOUT external packages (no `clsx`, no `tailwind-merge`) so that the eval `imports_resolve_to_dependencies` doesn't reject the build. Use this exact implementation:

```ts
export function cn(...classes: (string | undefined | null | false | 0)[]): string {{
  return classes.filter(Boolean).join(" ");
}}
```

Where contact info is missing: use `[BUSINESS PHONE]`, `[EMAIL]`, `[ADDRESS]`. Never invent.
