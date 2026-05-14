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

1. **Homepage** (`app/page.tsx`) — landing page, full of life, follows the DNA's posture
2. **Services** (`app/services/page.tsx`) — full-bleed alternating layout, NOT a generic card grid
3. **About** (`app/about/page.tsx`) — editorial story
4. **Contact** (`app/contact/page.tsx`) — working form with success state, map embed

### Homepage — Default Section Structure (override per DNA)

**Section 1: Hero — Full Viewport** (default; DNA may redefine the hero entirely)
- `min-h-[100dvh]` always — never `min-h-screen`
- The Design DNA's `Hero structure` section is authoritative. The defaults below apply only if the DNA's hero is silent on a detail.
- **Default video hero** (when DNA permits and Resolved Contract says video): `<video autoPlay muted loop playsInline>` — use the hero Pexels URL as `poster` attribute
- **Default image hero** (when DNA permits and no video): full-bleed `next/image` with `priority` and a `className="parallax-bg"` wrapper
- **Default content layout** (DNA may rearrange or replace):
  1. `<p className="hero-eyebrow">` — location · industry tagline
  2. `<h1 className="hero-heading">` — the main headline, set in the DNA's display font at the size the DNA specifies. **THIS MUST BE PRESENT AND VISIBLE. No hero without a large headline.**
  3. `<p className="hero-sub">` — supporting sentence naming the outcome
  4. `<div className="hero-cta flex gap-4">` — primary + secondary CTA
  5. `<div className="hero-badge">` — floating trust signal (years · certified · insured)
- DO NOT (regardless of DNA): plain white centered hero with only CTA buttons and no headline, dead links, placeholder Lorem ipsum
- The DNA may legitimately call for: a typographic-only hero (no image/video), a split-screen asymmetric hero, a centered editorial hero, a boot-sequence terminal hero, a layered chaotic hero. Follow the DNA.

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

**Section 8: Footer**
- tel: links, mailto: links, address, hours, social icons, copyright

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
    "framer-motion": "^11.0.0"
  }}
}}
```

**Performance non-negotiables:**
- `next/image` for ALL images — never raw `<img>` tags. Use `fill` + `object-cover` for full-bleed, explicit `width`/`height` for fixed-size. `priority` on hero image only.
- `next/font/google` for both fonts — zero layout shift
- `gsap.registerPlugin(ScrollTrigger, SplitText)` at module level — never inside useEffect
- `dynamic()` with `{{ ssr: false }}` for any component using `window` or `document`
- `will-change: transform` only during active animation — remove after with `gsap.set(el, {{ clearProps: "willChange" }})`
- `@media (prefers-reduced-motion: reduce) {{ * {{ animation-duration: 0.01ms !important }} }}` in globals.css

---

### CINEMATIC CODE PATTERNS — Implement Verbatim

#### 1. Hero Entrance — Vanilla Word Splitter (NO SplitText)

**DO NOT import `gsap/SplitText`.** SplitText is a paid Club GSAP plugin — importing it crashes with `Module not found: gsap/SplitText` on any project without a Club license. Use this vanilla splitter instead. It's free, lightweight, and produces the same staggered word reveal.

```tsx
"use client"
import {{ useGSAP }} from "@gsap/react"
import gsap from "gsap"

// Vanilla word splitter — wraps each word in nested spans so we can clip + translate
function splitWords(el: HTMLElement): HTMLElement[] {{
  const text = (el.textContent ?? "").trim()
  el.innerHTML = text
    .split(/\s+/)
    .filter(Boolean)
    .map(w => `<span class="word" style="display:inline-block;overflow:hidden"><span class="word-inner" style="display:inline-block">${{w}}</span></span>`)
    .join(" ")
  return Array.from(el.querySelectorAll<HTMLElement>(".word-inner"))
}}

useGSAP(() => {{
  const heading = document.querySelector<HTMLElement>(".hero-heading")
  const words = heading ? splitWords(heading) : []

  const tl = gsap.timeline({{ delay: 0.1, defaults: {{ ease: "expo.out" }} }})
  tl.from(".hero-eyebrow", {{ opacity: 0, y: 16, duration: 0.6 }})
    .from(words,           {{ opacity: 0, y: 52, stagger: 0.06, duration: 0.85 }}, "-=0.3")
    .from(".hero-sub",     {{ opacity: 0, y: 20, duration: 0.7 }}, "-=0.5")
    .from(".hero-cta",     {{ opacity: 0, y: 20, stagger: 0.1, duration: 0.6 }}, "-=0.4")
    .from(".hero-badge",   {{ opacity: 0, scale: 0.9, duration: 0.5 }}, "-=0.3")
}})
```

Apply: `className="hero-eyebrow"`, `"hero-heading"`, `"hero-sub"`, `"hero-cta"` (on each CTA), `"hero-badge"`.

#### 2. Navbar — Hide/Show + Background Fill (No Flicker On Load)

**Initialize the navbar with an opaque background on first paint** — never transparent. A transparent navbar above a dark hero looks fine, but the moment the loading screen dismisses you get an ugly flicker because GSAP hasn't read scroll position yet. The fix: read `window.scrollY` synchronously on mount and apply the right state before the first paint.

```tsx
"use client"
import {{ useEffect, useRef }} from "react"
import {{ useGSAP }} from "@gsap/react"
import gsap from "gsap"
import {{ ScrollTrigger }} from "gsap/ScrollTrigger"

export function Header() {{
  const ref = useRef<HTMLElement>(null)

  // Set the initial bg state synchronously after mount so the navbar
  // never appears unstyled — even for one frame.
  useEffect(() => {{
    const el = ref.current
    if (!el) return
    const darkSite = document.body.dataset.theme === "dark"
    const atTop = window.scrollY <= 60
    el.style.backgroundColor = atTop ? "transparent" : (darkSite ? "rgba(10,10,10,0.92)" : "rgba(255,255,255,0.92)")
    el.style.backdropFilter  = atTop ? "blur(0px)" : "blur(14px)"
    el.style.boxShadow       = atTop ? "none"      : "0 1px 0 rgba(0,0,0,0.08)"
  }}, [])

  useGSAP(() => {{
    let lastY = 0
    const darkSite = document.body.dataset.theme === "dark"

    ScrollTrigger.create({{
      onUpdate: () => {{
        const y = window.scrollY
        const scrollingDown = y > lastY && y > 80
        gsap.to(ref.current, {{
          yPercent: scrollingDown ? -100 : 0,
          duration: 0.35,
          ease: "power2.out",
          overwrite: "auto",
        }})

        const bg = darkSite ? "rgba(10,10,10,0.92)" : "rgba(255,255,255,0.92)"
        gsap.to(ref.current, {{
          backgroundColor: y > 60 ? bg : "transparent",
          backdropFilter:  y > 60 ? "blur(14px)" : "blur(0px)",
          boxShadow:       y > 60 ? "0 1px 0 rgba(0,0,0,0.08)" : "none",
          duration: 0.3,
          overwrite: "auto",
        }})
        lastY = y
      }},
    }})
  }})

  // Header must NOT be a child of any `overflow:hidden` container — iOS will break the fixed positioning.
  return <header ref={{ref}} className="navbar fixed top-0 inset-x-0 z-50">{{/* ... */}}</header>
}}
```

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

### Working CTAs — Zero Dead Links

| CTA | Implementation |
|---|---|
| Phone | `<a href="tel:[BUSINESS PHONE]">` |
| Email | `<a href="mailto:[EMAIL]">` |
| Book | External booking URL or `onClick` scroll to `#contact` |
| Form submit | `onSubmit` with `e.preventDefault()` + success state — never just `href="#"` |
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

- [ ] Hero: video OR full-bleed image with overlay — no flat backgrounds
- [ ] Hero headline: `<h1 className="hero-heading">` present, visible, and large (min text-6xl) — a hero with only CTA buttons is incomplete
- [ ] Hero entrance: SplitText word-by-word headline on mount
- [ ] Navbar: hides scroll-down, returns scroll-up, fills blur at 60px
- [ ] Trust bar: counting stats with `data-target` + GSAP textContent
- [ ] Services: full-bleed vertical alternating sections — NEVER 3-column card grid, NEVER horizontal scroll
- [ ] Social proof: dark section, one large quote
- [ ] All section images: `next/image` + clip-path reveal on scroll
- [ ] All phone CTAs: `href="tel:..."` — zero `href="#"` links
- [ ] Contact form: `onSubmit` + success state
- [ ] `prefers-reduced-motion` in globals.css
- [ ] 4 pages: Homepage, Services, About, Contact
- [ ] All docs: README, HANDOFF, TODO_ASSETS, STYLE_GUIDE

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

| Check | Required |
|---|---|
| Phone number | `[BUSINESS PHONE]` — NEVER a 555 number or invented number |
| Heading font | NOT Inter / Geist / Poppins / DM Sans / Space Grotesk — named distinctive face from Contract |
| Subtext | No "Where X meets Y" — specific claim, number, or location |
| Headline | No "Unrivaled / World-class / Unleash" — specific and arguable |
| Hero | Full-bleed image or video with overlay — NEVER flat color behind text |
| Hero headline | `<h1 className="hero-heading">` PRESENT and LARGE (min text-6xl) — CTAs alone are not a hero |
| Hero height | `min-h-[100dvh]` — never `min-h-screen` |
| Hero animation | Vanilla word-splitter (NOT `gsap/SplitText`) + 5-element staggered timeline on mount |
| **GSAP SplitText** | **NEVER import `gsap/SplitText`** — it's a paid Club plugin and crashes on free GSAP. Use the `splitWords()` helper in Code Pattern 1. |
| **`next/image` refs** | **NEVER attach a `ref` directly to `<Image>`** — Next's Image component does not forward refs. Always wrap in a `<div ref={{...}}>` and animate the wrapper. |
| Navbar | Hides scroll-down, returns scroll-up, blur fill at 60px |
| Navbar initial paint | Synchronously set background in `useEffect` based on `window.scrollY` — never start transparent and let GSAP fill it later (flicker on load) |
| Images | `next/image` everywhere — never raw `<img>` |
| Services layout | Full-bleed vertical alternating sections — NEVER 3-column card grid, NEVER horizontal scroll |
| Stats | GSAP counting numbers — never static text |
| Social proof | Dark section, large single quote — never a carousel of small cards |
| Section images | Clip-path reveal on scroll (wrapper div, not on `<Image>`) |
| Video | `autoPlay muted loop playsInline` — always all four attributes |
| Hero video src | Use `/videos/hero.mp4` (local) when provided — Pexels CDN URLs only as fallback |
| CTAs | `href="tel:..."` for phone — zero dead `href="#"` links |
| Form | `onSubmit` handler with success state |
| Input font | Minimum `font-size: 16px` — prevents iOS zoom |
| Safe area | `env(safe-area-inset-*)` in globals.css |
| SSR safety | `normalizeScroll` + `ScrollTrigger.config` inside `useEffect` — NEVER at module level |
| FAQ accordion | `ScrollTrigger.refresh()` triggered by `transitionend` — NEVER a bare `setTimeout` |
| **Lenis config** | Only Lenis 1.1.x options: `duration`, `easing`, `smoothWheel`, `syncTouch`, `touchMultiplier`, `infinite`. `smoothTouch` and `overscroll` are REMOVED in 1.1.x. |
| Overscroll | Use CSS `overscroll-behavior-y: none` on `html, body` — not the Lenis option |
| reduced-motion | `prefers-reduced-motion` media query in globals.css |
| `.gitignore` | Present at project root with `node_modules/`, `.next/`, `.env*.local`, `.DS_Store`, `*.log` |
| Booking tool | Matches industry — Booksy ONLY for beauty/wellness |
| Testimonials | Real only or omitted — never fabricated |

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

- `README.md`, `HANDOFF.md`, `TODO_ASSETS.md`, `STYLE_GUIDE.md`, `CLIENT_ANSWERS.md`
- `content/site.ts`, `content/sections.ts`, `content/services.ts`, `content/faqs.ts`, `content/testimonials.ts`
- `lib/motion.ts`, `components/motion/Reveal.tsx`, `components/motion/Parallax.tsx`, `components/motion/SplitText.tsx`, `components/motion/SmoothScroll.tsx`
- `config/brand.config.ts`, `config/motion.config.ts`
- `next.config.mjs` (NOT `.ts` — Next 14 does not support TypeScript config files)
- `tailwind.config.ts`, `postcss.config.js`, `tsconfig.json`, `package.json`, `.gitignore`

Every import statement uses the `@/` alias rooted at the project. Examples:
`import {{ Reveal }} from "@/components/motion/Reveal"`,
`import {{ SITE_TITLE }} from "@/content/site"`,
`import {{ cn }} from "@/lib/utils"`.

Where contact info is missing: use `[BUSINESS PHONE]`, `[EMAIL]`, `[ADDRESS]`. Never invent.
