# Cinematic Hero Template Base + 5 Service-Industry Skins — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a new template base (`cinematic_hero`) using a hero pattern not yet in the registry — full-bleed photo background + bottom-left CTA stack — and 5 industry skins (Plumber, HVAC, Construction, Landscaper, Dog Groomer) that the `/api/template-match` endpoint will surface for those signups. Adds 6 new templates total to the 21 already in `pebble/templates/registry.json`.

**Architecture:** Pebble's existing template pattern: each template is a full Next.js 14 project at `pebble/templates/<id>/` with all customer-editable content isolated in `content/site.ts` (the only file the LLM rewrites at instantiation time). Components import strings from there — never hardcoded. Each skin clones the base directory then applies a small delta (palette + copy + dna_source). This plan ships the base first (Task 1-2), then each skin in parallel (Tasks 3-7), then matcher updates + screenshots + push (Tasks 8-10).

**Tech Stack:** Next.js 14 App Router, TypeScript, Tailwind v4, Framer Motion, Inter + Archivo Black via `next/font/google`. Stock photos from the new multi-source fan-out (Pixabay → Pexels → Unsplash) shipped 2026-05-24.

**Conventions:** Tests live in `tests/test_*.py`. Per CLAUDE.md, fonts MUST be in next/font/google catalog (Archivo Black confirmed present). Commits include `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`. Push to `squitopest` (NOT `pebblewebsite`).

**Out of scope (deliberately deferred):**
- Bases 2 (Editorial Split / Fraunces serif) and 3 (Asymmetric Magazine / Inter Display) — separate plans
- Industry skins of bases 2 + 3 — separate plans
- Gallery preview enhancement (scroll left/right between pages) — Marc's separate ask, different scope (ui/v3 work)
- Audio walkthroughs / video heroes — out of scope; static photo hero only

---

## Design system (locked for this plan)

**Hero pattern — "Cinematic Hero":**
- Full-bleed background photo (16:9 hero image from new image fan-out)
- Dark gradient overlay: linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.6) 60%, rgba(0,0,0,0.85) 100%)
- Content anchored bottom-left, max-width 640px, padding 64px from edges (32px mobile)
- Pill chip top of content: "AVAILABLE TODAY" or industry-equivalent, 10px uppercase, white/90 on accent-color/20
- H1: Archivo Black 64px (mobile 40px), white, uppercase, tracking-tight, leading-[0.95]
- Subhead: Inter 18px (mobile 15px), white/85, leading-relaxed, max-w-md
- CTA row: 2 buttons side-by-side
  - Primary: accent-color background, white text, 56px tall, 24px horizontal padding, rounded-full
  - Secondary: transparent + white border, white text, same dimensions

**Palette — "Slate + Amber" (not in registry today):**
- Background base: `#fafaf9` (warmer than pure white)
- Surface 1: `#ffffff`
- Surface 2 (cards): `#f4f4f5`
- Text primary: `#18181b` (true near-black)
- Text secondary: `#52525b`
- Border: `#e4e4e7`
- Accent: `#d97706` (warm amber — energetic, evokes "service / trades / work crew")
- Accent dark (hover): `#b45309`

**Typography:**
- Display: Archivo Black 900 (Google Fonts) — uppercase, used for H1 in Hero ONLY
- Heading: Inter 800 — used for H2/H3 (section titles)
- Body: Inter 400/500/600 — used for all body, labels, captions
- Mono: JetBrains Mono 400 — used for accent stamps (phone numbers in trust bar, ref codes)

**Skin-only deltas (each skin overrides the ACCENT color only — everything else stays):**
- `cinematic_plumber`     → accent `#0369a1` (deep blue — water/pipes association)
- `cinematic_hvac`        → accent `#0891b2` (cyan — air/coolness association)
- `cinematic_construction`→ accent `#ea580c` (construction orange — safety vest)
- `cinematic_landscaper`  → accent `#65a30d` (lime green — fresh-cut grass)
- `cinematic_dog_groomer` → accent `#db2777` (warm pink — friendly/approachable)

---

## File Structure

For each template (1 base + 5 skins = 6 dirs):
```
pebble/templates/<id>/
├── app/
│   ├── about/page.tsx
│   ├── actions/contact.ts
│   ├── contact/page.tsx
│   ├── layout.tsx          (font imports — Inter + Archivo_Black)
│   ├── page.tsx            (composes Hero + Services + About + Testimonials + Contact)
│   ├── services/page.tsx
│   ├── sitemap.ts
│   └── globals.css         (palette CSS vars — accent value differs per skin)
├── components/
│   ├── forms/ContactForm.tsx
│   ├── layout/Footer.tsx
│   ├── layout/Navbar.tsx   (sticky top, accent CTA right)
│   ├── sections/Hero.tsx           (NEW — Cinematic Hero pattern)
│   ├── sections/Services.tsx       (3-up grid)
│   ├── sections/About.tsx          (split: left photo, right copy)
│   ├── sections/Testimonials.tsx   (single hero quote)
│   ├── sections/ServiceArea.tsx    (map snippet + cities list)
│   ├── sections/CTABand.tsx        (NEW — full-bleed accent band)
│   └── ui/Button.tsx
├── content/site.ts         (ALL strings — what the LLM rewrites per customer)
├── dna_source.json         (DNA metadata + accent value)
├── lib/cn.ts
├── lib/email.ts
├── next.config.mjs
└── package.json
```

Each skin clones the base, then ONLY 3 files differ from the base:
- `app/globals.css` (one CSS variable: --color-accent)
- `content/site.ts` (industry copy, service names, testimonial)
- `dna_source.json` (industry tag + accent value)

All other files are byte-identical clones of the base. This is critical for maintainability — bug fixes to the base can be propagated to skins via the same diff.

Registry: `pebble/templates/registry.json` gets 6 new entries appended to `templates: [...]`.

Engine matcher: `pebble/server/template_match.py` is already in the codebase; the new templates will be auto-discovered through `load_registry()`. The keyword map in `pebble/image_fallback.py:_INDUSTRY_KEYWORDS` already has entries for plumber/hvac/construction/landscaper/dog_groomer per the multi-source upgrade — nothing new needed.

Preview screenshots: `ui/v3/public/templates-preview/<id>.png` for each — 6 new images, ~150KB each.

---

## Task 1: Scaffold the `cinematic_hero` base — clone honest_garage, replace 5 files

**Files (clone + modify):**
- Copy: `pebble/templates/honest_garage/` → `pebble/templates/cinematic_hero/` (full directory tree, ~28 files)
- Replace: `pebble/templates/cinematic_hero/components/sections/Hero.tsx`
- Replace: `pebble/templates/cinematic_hero/app/globals.css`
- Replace: `pebble/templates/cinematic_hero/content/site.ts`
- Replace: `pebble/templates/cinematic_hero/dna_source.json`
- Replace: `pebble/templates/cinematic_hero/app/layout.tsx`
- Create: `pebble/templates/cinematic_hero/components/sections/CTABand.tsx`
- Modify: `pebble/templates/cinematic_hero/app/page.tsx` (composition order)

- [ ] **Step 1: Clone honest_garage as the scaffold base**

Run:
```bash
cp -r pebble/templates/honest_garage pebble/templates/cinematic_hero
```

Verify file count is approximately the same (~28 .tsx/.ts/.json/.mjs files):
```bash
find pebble/templates/cinematic_hero -type f \( -name '*.tsx' -o -name '*.ts' -o -name '*.json' -o -name '*.mjs' \) | wc -l
```

Expected: ≥ 25.

- [ ] **Step 2: Replace `components/sections/Hero.tsx` with Cinematic Hero pattern**

Overwrite `pebble/templates/cinematic_hero/components/sections/Hero.tsx` with EXACTLY:

```tsx
import Image from "next/image";
import { motion } from "framer-motion";
import {
  HERO_BG_IMAGE,
  HERO_PILL,
  HERO_HEADLINE,
  HERO_SUBLINE,
  HERO_CTA_PRIMARY,
  HERO_CTA_SECONDARY,
  HERO_CTA_PRIMARY_HREF,
  HERO_CTA_SECONDARY_HREF,
} from "@/content/site";

/**
 * Cinematic Hero — full-bleed photo background, dark gradient overlay,
 * bottom-left content stack. Inspired by real-estate listing heroes —
 * lets the photo carry the emotional weight while keeping copy + CTAs
 * front-and-center on entry.
 */
export function Hero() {
  return (
    <section className="relative h-[100svh] min-h-[640px] w-full overflow-hidden bg-slate-900">
      <Image
        src={HERO_BG_IMAGE}
        alt=""
        fill
        priority
        sizes="100vw"
        className="object-cover object-center"
      />
      <div
        aria-hidden
        className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/60 to-transparent"
      />
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        className="absolute bottom-0 left-0 p-8 md:p-16 max-w-[640px] text-white"
      >
        <span className="inline-block mb-4 px-3 py-1 rounded-full bg-[var(--color-accent)]/25 border border-[var(--color-accent)]/40 text-[10px] uppercase tracking-[0.18em] font-bold">
          {HERO_PILL}
        </span>
        <h1 className="font-[family-name:var(--font-display)] text-[40px] md:text-[64px] leading-[0.95] uppercase tracking-tight">
          {HERO_HEADLINE}
        </h1>
        <p className="mt-4 text-[15px] md:text-[18px] leading-relaxed text-white/85 max-w-md">
          {HERO_SUBLINE}
        </p>
        <div className="mt-7 flex flex-wrap gap-3">
          <a
            href={HERO_CTA_PRIMARY_HREF}
            className="inline-flex items-center justify-center h-14 px-6 rounded-full bg-[var(--color-accent)] hover:bg-[var(--color-accent-dark)] text-white font-semibold text-base transition-colors"
          >
            {HERO_CTA_PRIMARY}
          </a>
          <a
            href={HERO_CTA_SECONDARY_HREF}
            className="inline-flex items-center justify-center h-14 px-6 rounded-full bg-transparent border border-white/70 hover:bg-white/10 text-white font-semibold text-base transition-colors"
          >
            {HERO_CTA_SECONDARY}
          </a>
        </div>
      </motion.div>
    </section>
  );
}
```

- [ ] **Step 3: Replace `app/globals.css` with the Slate + Amber palette**

Overwrite `pebble/templates/cinematic_hero/app/globals.css` with EXACTLY:

```css
@import "tailwindcss";

/* Cinematic Hero — Slate + Amber palette.
   Skins override --color-accent and --color-accent-dark only. */
@theme {
  --color-background:    #fafaf9;
  --color-surface-1:     #ffffff;
  --color-surface-2:     #f4f4f5;
  --color-text-primary:  #18181b;
  --color-text-secondary:#52525b;
  --color-border:        #e4e4e7;
  --color-accent:        #d97706;
  --color-accent-dark:   #b45309;

  --font-sans:    var(--font-inter), system-ui, -apple-system, sans-serif;
  --font-display: var(--font-archivo-black), Impact, "Arial Black", sans-serif;
  --font-mono:    var(--font-jetbrains-mono), ui-monospace, monospace;
}

html, body {
  background: var(--color-background);
  color: var(--color-text-primary);
  font-family: var(--font-sans);
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

- [ ] **Step 4: Replace `app/layout.tsx` with the new font imports**

Overwrite `pebble/templates/cinematic_hero/app/layout.tsx` with EXACTLY:

```tsx
import type { Metadata } from "next";
import { Inter, Archivo_Black, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { SITE_TITLE, SITE_DESCRIPTION } from "@/content/site";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
});

const archivoBlack = Archivo_Black({
  variable: "--font-archivo-black",
  subsets: ["latin"],
  weight: ["400"],   // Archivo Black ships at a single 900-equivalent weight
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  weight: ["400"],
});

export const metadata: Metadata = {
  title: SITE_TITLE,
  description: SITE_DESCRIPTION,
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${archivoBlack.variable} ${jetbrainsMono.variable} antialiased`}
    >
      <body className="bg-background text-foreground">{children}</body>
    </html>
  );
}
```

- [ ] **Step 5: Replace `content/site.ts` with Cinematic Hero base content**

Overwrite `pebble/templates/cinematic_hero/content/site.ts` with EXACTLY:

```typescript
/**
 * Source of truth for every visible string in this Cinematic Hero base.
 *
 * Per Pebble convention: the LLM rewrites THIS FILE ONLY when a customer
 * instantiates the template. Components never hardcode strings.
 *
 * Unknown values are wrapped in [SQUARE BRACKETS]; arrays the customer
 * must fill ship empty.
 */

// --- Brand / site ---
export const SITE_TITLE       = "Cinematic Services";
export const SITE_DESCRIPTION = "Trusted local pros, available today. Clear pricing, no surprises.";
export const TAGLINE          = "Available today. Real pros.";

// --- Hero ---
export const HERO_BG_IMAGE          = "/hero.jpg";   // 16:9 landscape, swapped per industry
export const HERO_PILL              = "AVAILABLE TODAY";
export const HERO_HEADLINE          = "Work that gets done right.";
export const HERO_SUBLINE           = "Family-owned local pros, available today, clear pricing in writing before we start. No surprises.";
export const HERO_CTA_PRIMARY       = "Get a free quote";
export const HERO_CTA_PRIMARY_HREF  = "/contact";
export const HERO_CTA_SECONDARY     = "See our work";
export const HERO_CTA_SECONDARY_HREF = "/services";

// --- Services (3-up grid) ---
export type Service = {
  id:          string;
  title:       string;
  description: string;
  icon:        string;   // lucide-react icon name
};

export const SERVICES: Service[] = [
  { id: "svc-1", title: "[SERVICE ONE]",   description: "[1-2 sentence description of your most popular offering.]", icon: "Wrench" },
  { id: "svc-2", title: "[SERVICE TWO]",   description: "[1-2 sentence description of your second core offering.]",  icon: "Hammer" },
  { id: "svc-3", title: "[SERVICE THREE]", description: "[1-2 sentence description of your third core offering.]",   icon: "Truck"  },
];

// --- About section ---
export const ABOUT_PHOTO_IMAGE = "/about.jpg";
export const ABOUT_HEADLINE    = "Local pros you can trust.";
export const ABOUT_BODY        = "[Two paragraphs about your story — how you got started, what makes you different. Keep it human and specific. Avoid corporate-speak.]";

// --- Trust bar (4 stamps under hero) ---
export type Trust = { label: string; sub: string };
export const TRUST_BADGES: Trust[] = [
  { label: "LICENSED",     sub: "[State + license #]"      },
  { label: "INSURED",      sub: "Up to $[amount]"          },
  { label: "5-STAR RATED", sub: "[N]+ Google reviews"      },
  { label: "FAMILY-OWNED", sub: "Serving [city] since [year]" },
];

// --- Testimonial (single hero quote) ---
export const TESTIMONIAL_QUOTE  = "[A 1-2 sentence testimonial in your customer's voice. Specific results > generic praise. Include a real first name and last initial.]";
export const TESTIMONIAL_AUTHOR = "[First Name L.], [City]";

// --- Service area ---
export const SERVICE_AREA_CITIES: string[] = [];   // customer fills

// --- Contact ---
export const CONTACT_PHONE          = "[(555) 555-0100]";
export const CONTACT_EMAIL          = "[hello@example.com]";
export const CONTACT_HOURS          = "[Mon–Fri 7am–6pm · Sat 8am–2pm]";
export const CONTACT_HEADLINE       = "Ready to get started?";
export const CONTACT_BODY           = "Tell us what you need. We respond within an hour during business hours.";

// --- CTA band (above footer) ---
export const CTA_BAND_HEADLINE = "Available today.";
export const CTA_BAND_BODY     = "Most jobs quoted within 24 hours. Same-week service in most cases.";
export const CTA_BAND_LABEL    = "Get a free quote";
export const CTA_BAND_HREF     = "/contact";

// --- Footer ---
export const FOOTER_TAGLINE = "Trusted local pros, available today.";
```

- [ ] **Step 6: Replace `dna_source.json` with the Cinematic Hero DNA metadata**

Overwrite `pebble/templates/cinematic_hero/dna_source.json` with EXACTLY:

```json
{
  "dna_id":      "cinematic_hero",
  "name":        "Cinematic Hero",
  "vibe":        "Cinematic full-bleed photo with bottom-left CTA stack. Inspired by real-estate listings.",
  "hero_pattern": "fullbleed_photo_bottomleft_cta",
  "palette": {
    "background":     "#fafaf9",
    "text_primary":   "#18181b",
    "text_secondary": "#52525b",
    "accent":         "#d97706",
    "accent_dark":    "#b45309"
  },
  "fonts": {
    "display": "Archivo Black",
    "body":    "Inter",
    "mono":    "JetBrains Mono"
  },
  "signature_moves": [
    "Full-bleed hero photo with dark gradient overlay",
    "Bottom-left content anchor (not centered)",
    "Archivo Black uppercase H1",
    "Accent-tinted pill chip above headline",
    "Two-CTA row (primary filled + secondary outlined)"
  ]
}
```

- [ ] **Step 7: Create `components/sections/CTABand.tsx` (new component)**

Create `pebble/templates/cinematic_hero/components/sections/CTABand.tsx` with EXACTLY:

```tsx
import {
  CTA_BAND_HEADLINE,
  CTA_BAND_BODY,
  CTA_BAND_LABEL,
  CTA_BAND_HREF,
} from "@/content/site";

/**
 * Full-bleed accent band placed above the footer on every page.
 * Strong dopamine moment for visitors who scrolled past services without
 * clicking — the band catches them with a clear final CTA.
 */
export function CTABand() {
  return (
    <section className="bg-[var(--color-accent)] text-white">
      <div className="max-w-5xl mx-auto px-8 py-16 md:py-24 flex flex-col md:flex-row md:items-end md:justify-between gap-6">
        <div className="max-w-xl">
          <h2 className="font-[family-name:var(--font-display)] text-3xl md:text-4xl uppercase tracking-tight">
            {CTA_BAND_HEADLINE}
          </h2>
          <p className="mt-3 text-base md:text-lg text-white/90 leading-relaxed">
            {CTA_BAND_BODY}
          </p>
        </div>
        <a
          href={CTA_BAND_HREF}
          className="inline-flex items-center justify-center h-14 px-7 rounded-full bg-white text-[var(--color-accent-dark)] font-bold text-base hover:bg-white/95 transition-colors shrink-0"
        >
          {CTA_BAND_LABEL}
        </a>
      </div>
    </section>
  );
}
```

- [ ] **Step 8: Update `app/page.tsx` to compose the new section order**

Open `pebble/templates/cinematic_hero/app/page.tsx`. Replace its body (keep the export default function signature) so it imports + renders, in this exact order:

```tsx
import { Hero }         from "@/components/sections/Hero";
import { Services }     from "@/components/sections/Services";
import { About }        from "@/components/sections/About";
import { Testimonials } from "@/components/sections/Testimonials";
import { CTABand }      from "@/components/sections/CTABand";
import { Navbar }       from "@/components/layout/Navbar";
import { Footer }       from "@/components/layout/Footer";

export default function HomePage() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Services />
        <About />
        <Testimonials />
        <CTABand />
      </main>
      <Footer />
    </>
  );
}
```

- [ ] **Step 9: Verify the base template builds locally**

Run:
```bash
cd pebble/templates/cinematic_hero
npm install --silent
npx next build 2>&1 | tail -15
```

Expected: `Compiled successfully` with no errors. If TypeScript errors surface, fix them before proceeding — usually a missing import in `content/site.ts` or a forgotten lucide-react icon. The template MUST build cleanly because the instantiation flow runs `next build` to validate.

- [ ] **Step 10: Drop a hero placeholder image so the build smoke-renders**

The Hero component references `/hero.jpg` which the customer photo will overwrite at instantiation. Ship a placeholder so the dev preview doesn't 404:

```bash
# Download a free-license fallback image to public/hero.jpg
curl -s -o pebble/templates/cinematic_hero/public/hero.jpg \
  "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=1920&q=80"
# Same for /about.jpg
curl -s -o pebble/templates/cinematic_hero/public/about.jpg \
  "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1280&q=80"
```

Verify both downloaded:
```bash
ls -la pebble/templates/cinematic_hero/public/hero.jpg pebble/templates/cinematic_hero/public/about.jpg
```

Expected: both files ≥ 50 KB.

- [ ] **Step 11: Commit the base scaffold**

```bash
cd /c/Users/marci/pebble-engine/.claude/worktrees/bold-hopper-c3631f
git add pebble/templates/cinematic_hero/
git commit -m "$(cat <<'EOF'
feat(templates): cinematic_hero base — fullbleed-photo + bottomleft CTA pattern

Cloned from honest_garage scaffold, then replaced Hero.tsx, globals.css,
layout.tsx, content/site.ts, dna_source.json + added CTABand.tsx.
Palette is "Slate + Amber" (not in registry today). Font swap:
Archivo Black for the uppercase H1, Inter for body. The hero pattern is
real-estate-listing-style: full-bleed photo, dark gradient overlay,
content anchored bottom-left.

5 industry skins land in follow-up commits (plumber, hvac, construction,
landscaper, dog_groomer). Each skin clones THIS dir and overrides
3 files only: globals.css (accent var), content/site.ts (copy), and
dna_source.json (industry tag + accent value).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Add `cinematic_hero` entry to `pebble/templates/registry.json`

**Files:**
- Modify: `pebble/templates/registry.json`

- [ ] **Step 1: Read current registry shape**

Run:
```bash
python -c "import json; r=json.load(open('pebble/templates/registry.json')); print('current count:', len(r['templates'])); print('first id:', r['templates'][0]['id'])"
```

Note the current count (likely 21).

- [ ] **Step 2: Append the cinematic_hero entry**

Open `pebble/templates/registry.json`. Inside the `"templates": [` array, append (with a leading comma after the last existing element) this object:

```json
    {
      "id":                    "cinematic_hero",
      "directory":             "pebble/templates/cinematic_hero",
      "name":                  "Cinematic Hero",
      "tagline":               "Full-bleed photo, bottom-left CTA, slate + amber.",
      "vibe":                  "Cinematic Real-Estate Listing",
      "source_dna":            "cinematic_hero",
      "applicable_industries": [
        "service provider",
        "local trades",
        "home services",
        "real estate",
        "automotive detailer"
      ],
      "preview_image":         "/templates-preview/cinematic_hero.png",
      "color_swatches":        ["#fafaf9", "#18181b", "#d97706", "#b45309"],
      "fonts": {
        "display": "Archivo Black",
        "body":    "Inter",
        "mono":    "JetBrains Mono"
      },
      "best_for": "Service-industry businesses where the buyer wants TRUST + AVAILABILITY signals (licensed/insured, same-day, family-owned). The full-bleed photo carries emotional weight while the CTA anchors action.",
      "tier":                  "free",
      "preview_url":           "http://localhost:3100/cinematic_hero",
      "preview_pages": [
        { "label": "Home",     "path": "/"        },
        { "label": "About",    "path": "/about"   },
        { "label": "Services", "path": "/services"},
        { "label": "Contact",  "path": "/contact" }
      ]
    }
```

- [ ] **Step 3: Validate the JSON parses**

Run:
```bash
python -c "import json; r=json.load(open('pebble/templates/registry.json')); ids=[t['id'] for t in r['templates']]; print('new count:', len(ids)); print('cinematic_hero present:', 'cinematic_hero' in ids)"
```

Expected: count = previous + 1, present = True.

- [ ] **Step 4: Verify the matcher picks up cinematic_hero**

Run:
```bash
python -c "
from pathlib import Path
import os
for line in Path('.env').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, _, v = line.partition('='); os.environ.setdefault(k.strip(), v.strip())
from pebble.server.template_match import match_templates
result = match_templates('I run a plumbing business in Phoenix', business_type='plumber', max_results=3)
for m in result['matches']:
    print(f'{m[\"score\"]:.2f}  {m[\"template_id\"]}  -- {m[\"reason\"]}')
"
```

Expected: `cinematic_hero` appears in the top-3 results with a non-zero score (it matches "service provider" / "local trades" via token overlap with "plumbing").

- [ ] **Step 5: Commit the registry entry**

```bash
git add pebble/templates/registry.json
git commit -m "$(cat <<'EOF'
feat(templates/registry): add cinematic_hero base entry

Slates the new fullbleed-photo + bottomleft-CTA template for industries
matching "service provider / local trades / home services / real estate /
automotive detailer". Tier: free (lets free users try it as a 1-credit
template instantiation). Color swatches + fonts in the registry drive
the gallery card preview.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Skin — `cinematic_plumber` (clone + 3-file delta)

**Files:**
- Copy: `pebble/templates/cinematic_hero/` → `pebble/templates/cinematic_plumber/`
- Modify: `pebble/templates/cinematic_plumber/app/globals.css` (accent color)
- Modify: `pebble/templates/cinematic_plumber/content/site.ts` (industry copy)
- Modify: `pebble/templates/cinematic_plumber/dna_source.json` (industry tag + accent)

- [ ] **Step 1: Clone the base**

```bash
cp -r pebble/templates/cinematic_hero pebble/templates/cinematic_plumber
```

- [ ] **Step 2: Swap accent color in `app/globals.css`**

Open `pebble/templates/cinematic_plumber/app/globals.css`. Replace these two lines:

```css
  --color-accent:        #d97706;
  --color-accent-dark:   #b45309;
```

With:

```css
  --color-accent:        #0369a1;
  --color-accent-dark:   #075985;
```

- [ ] **Step 3: Replace `content/site.ts` with plumber-specific copy**

In `pebble/templates/cinematic_plumber/content/site.ts`, replace the existing string constants AND the SERVICES + TRUST_BADGES arrays. Keep the type declarations + export structure intact. The exact replacements:

```typescript
export const SITE_TITLE       = "[Your Plumbing Co.]";
export const SITE_DESCRIPTION = "Licensed plumbers, available today. Clear pricing in writing — no upsell, no surprises.";
export const TAGLINE          = "Same-day plumbing. No surprises.";

export const HERO_BG_IMAGE          = "/hero.jpg";
export const HERO_PILL              = "AVAILABLE TODAY";
export const HERO_HEADLINE          = "Pipes fixed. Right. Today.";
export const HERO_SUBLINE           = "Licensed local plumbers, family-owned. We quote in writing before we start, and only fix what you approve. Most repairs done same day.";
export const HERO_CTA_PRIMARY       = "Get a free quote";
export const HERO_CTA_PRIMARY_HREF  = "/contact";
export const HERO_CTA_SECONDARY     = "See our services";
export const HERO_CTA_SECONDARY_HREF = "/services";

export const SERVICES: Service[] = [
  { id: "svc-1", title: "Leak Repair",        description: "Burst pipes, slab leaks, hidden drips found and fixed fast. We don't tear out what doesn't need to be torn out.", icon: "Droplets" },
  { id: "svc-2", title: "Drain & Sewer",      description: "Clogged drains, root-bound sewer lines, hydro jetting. Camera-inspected so you see what we see.",                icon: "Waves"    },
  { id: "svc-3", title: "Water Heater Service", description: "Tankless installs, traditional swaps, repairs. We carry every major brand and stock common parts on the truck.", icon: "Flame"    },
];

export const ABOUT_HEADLINE    = "Licensed plumbers, family-owned.";
export const ABOUT_BODY        = "[Two paragraphs about your shop — how long you've been serving [city], what kind of work you specialize in, what makes you different from the chain shops. Mention specific certifications or specialties if you have them.]";

export const TRUST_BADGES: Trust[] = [
  { label: "LICENSED",     sub: "[State plumbing license #]" },
  { label: "INSURED",      sub: "Up to $[amount]"            },
  { label: "5-STAR RATED", sub: "[N]+ Google reviews"        },
  { label: "FAMILY-OWNED", sub: "Serving [city] since [year]" },
];

export const TESTIMONIAL_QUOTE  = "[Specific story: 'My water heater died on a Sunday. Mike from [shop] was here in 90 minutes with a new tankless unit. Done by Monday morning.']";
export const TESTIMONIAL_AUTHOR = "[Sarah K.], [City]";

export const CONTACT_PHONE          = "[(555) 555-0100]";
export const CONTACT_EMAIL          = "[service@yourplumbing.example]";
export const CONTACT_HOURS          = "[24/7 emergency · Office Mon-Fri 7am-6pm]";
export const CONTACT_HEADLINE       = "Need a plumber today?";
export const CONTACT_BODY           = "Tell us what's wrong. We respond within 60 minutes during business hours, and we have 24/7 emergency dispatch.";

export const CTA_BAND_HEADLINE = "Pipe burst? Drain backed up?";
export const CTA_BAND_BODY     = "Our emergency dispatch is 24/7. Most jobs quoted on the phone in 10 minutes.";
export const CTA_BAND_LABEL    = "Call us now";
export const CTA_BAND_HREF     = "tel:5555550100";

export const FOOTER_TAGLINE = "Licensed plumbing pros, available today.";
```

(Leave `HERO_BG_IMAGE`, `ABOUT_PHOTO_IMAGE`, `SERVICE_AREA_CITIES`, and the type declarations untouched — they're identical to the base.)

- [ ] **Step 4: Update `dna_source.json` with plumber accent**

In `pebble/templates/cinematic_plumber/dna_source.json`, change:

```json
  "dna_id":      "cinematic_hero",
```

To:

```json
  "dna_id":      "cinematic_plumber",
```

And in the `"palette"` object, change:

```json
    "accent":         "#d97706",
    "accent_dark":    "#b45309"
```

To:

```json
    "accent":         "#0369a1",
    "accent_dark":    "#075985"
```

- [ ] **Step 5: Add registry entry**

In `pebble/templates/registry.json`, inside the `"templates": [` array, append (with leading comma):

```json
    {
      "id":                    "cinematic_plumber",
      "directory":             "pebble/templates/cinematic_plumber",
      "name":                  "Pipe & Cistern Co.",
      "tagline":               "Cinematic plumbing hero. Same-day. Slate + deep-blue accent.",
      "vibe":                  "Cinematic Real-Estate Listing — Plumbing",
      "source_dna":            "cinematic_plumber",
      "applicable_industries": [
        "plumber",
        "plumbing",
        "drain cleaning",
        "water heater service",
        "leak detection",
        "sewer service",
        "pipe repair"
      ],
      "preview_image":         "/templates-preview/cinematic_plumber.png",
      "color_swatches":        ["#fafaf9", "#18181b", "#0369a1", "#075985"],
      "fonts": {
        "display": "Archivo Black",
        "body":    "Inter",
        "mono":    "JetBrains Mono"
      },
      "best_for": "Plumbing contractors emphasizing trust, licensing, and same-day availability. Deep-blue accent associates with water + reliability without going neon.",
      "tier":                  "free",
      "preview_url":           "http://localhost:3100/cinematic_plumber",
      "preview_pages": [
        { "label": "Home",     "path": "/"        },
        { "label": "About",    "path": "/about"   },
        { "label": "Services", "path": "/services"},
        { "label": "Contact",  "path": "/contact" }
      ]
    }
```

- [ ] **Step 6: Verify build + matcher pick-up**

```bash
cd pebble/templates/cinematic_plumber && npx next build 2>&1 | tail -5
```

Expected: `Compiled successfully`.

Back in repo root:
```bash
python -c "
from pathlib import Path; import os
for line in Path('.env').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, _, v = line.partition('='); os.environ.setdefault(k.strip(), v.strip())
from pebble.server.template_match import match_templates
r = match_templates('plumber in Brooklyn', business_type='plumber', max_results=3)
print([m['template_id'] for m in r['matches']])
"
```

Expected: `cinematic_plumber` in the result list.

- [ ] **Step 7: Commit the skin**

```bash
git add pebble/templates/cinematic_plumber/ pebble/templates/registry.json
git commit -m "$(cat <<'EOF'
feat(templates): cinematic_plumber — Cinematic Hero skin for plumbing

Clone of cinematic_hero with deep-blue accent (#0369a1) — associates
with water/pipes without going neon. Plumber-specific Services (Leak
Repair / Drain & Sewer / Water Heater), trust badges (state plumbing
license, 24/7 emergency dispatch), CTABand routes to tel: for true
emergencies.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Skin — `cinematic_hvac` (clone + 3-file delta)

**Files:** same shape as Task 3.

- [ ] **Step 1: Clone the base**

```bash
cp -r pebble/templates/cinematic_hero pebble/templates/cinematic_hvac
```

- [ ] **Step 2: Swap accent in globals.css**

In `pebble/templates/cinematic_hvac/app/globals.css`, change:

```css
  --color-accent:        #d97706;
  --color-accent-dark:   #b45309;
```

To:

```css
  --color-accent:        #0891b2;
  --color-accent-dark:   #0e7490;
```

- [ ] **Step 3: Replace `content/site.ts` with HVAC-specific copy**

Same surgical replacements as Task 3 step 3, but with these values:

```typescript
export const SITE_TITLE       = "[Your HVAC Co.]";
export const SITE_DESCRIPTION = "Licensed HVAC techs, same-day service. Tune-ups, repairs, full system installs.";
export const TAGLINE          = "Cool when you need it. Warm when you don't.";

export const HERO_PILL              = "AVAILABLE TODAY";
export const HERO_HEADLINE          = "Cool air. On demand.";
export const HERO_SUBLINE           = "Licensed HVAC technicians. Same-day diagnostics, written estimates, parts on the truck. Most repairs done in one visit.";
export const HERO_CTA_PRIMARY       = "Schedule service";
export const HERO_CTA_SECONDARY     = "See services";

export const SERVICES: Service[] = [
  { id: "svc-1", title: "AC Repair & Install",   description: "Central air, mini-splits, heat pumps. Same-day repairs in most cases. Major-brand-certified installers.",          icon: "Snowflake" },
  { id: "svc-2", title: "Heating & Furnace",     description: "Gas, electric, and heat-pump systems. Pre-season tune-ups catch problems before the cold snap.",                  icon: "Flame"     },
  { id: "svc-3", title: "Indoor Air Quality",    description: "Air purifiers, humidifiers, duct cleaning. Especially important if anyone in your home has allergies or asthma.", icon: "Wind"      },
];

export const ABOUT_HEADLINE    = "HVAC techs who actually pick up the phone.";
export const ABOUT_BODY        = "[Two paragraphs about your shop — service area, brands you're certified on, what makes you different from the franchise chains. Mention NATE certification or specific brand certifications if you have them.]";

export const TRUST_BADGES: Trust[] = [
  { label: "LICENSED",     sub: "[State HVAC license #]"        },
  { label: "NATE CERTIFIED", sub: "Senior technicians"          },
  { label: "5-STAR RATED", sub: "[N]+ Google reviews"           },
  { label: "FAMILY-OWNED", sub: "Serving [city] since [year]"   },
];

export const TESTIMONIAL_QUOTE  = "[Specific story: 'Our AC died during the August heat wave. They had a tech here in 3 hours, diagnosed a bad capacitor, fixed it, and were gone within an hour. Real pricing, no upsell.']";
export const TESTIMONIAL_AUTHOR = "[James M.], [City]";

export const CONTACT_PHONE          = "[(555) 555-0100]";
export const CONTACT_EMAIL          = "[service@yourhvac.example]";
export const CONTACT_HOURS          = "[Mon–Sat 7am–8pm · Sun emergency only]";
export const CONTACT_HEADLINE       = "AC out? Furnace acting up?";
export const CONTACT_BODY           = "Tell us what's wrong and we'll dispatch the closest tech. Same-day in most cases.";

export const CTA_BAND_HEADLINE = "Schedule a tune-up.";
export const CTA_BAND_BODY     = "Pre-season tune-ups catch 80% of failures before they happen. $89 for the full check, parts excluded.";
export const CTA_BAND_LABEL    = "Book online";
export const CTA_BAND_HREF     = "/contact";

export const FOOTER_TAGLINE = "Licensed HVAC techs, same-day service.";
```

- [ ] **Step 4: Update `dna_source.json`**

Change `dna_id` to `cinematic_hvac`. Change `accent` to `#0891b2` and `accent_dark` to `#0e7490`.

- [ ] **Step 5: Add registry entry**

In `pebble/templates/registry.json`, append:

```json
    {
      "id":                    "cinematic_hvac",
      "directory":             "pebble/templates/cinematic_hvac",
      "name":                  "Cool Crew HVAC",
      "tagline":               "Cinematic HVAC hero. Cyan accent. Same-day service.",
      "vibe":                  "Cinematic Real-Estate Listing — HVAC",
      "source_dna":            "cinematic_hvac",
      "applicable_industries": [
        "hvac",
        "air conditioning",
        "heating",
        "furnace repair",
        "duct cleaning",
        "heat pump installer"
      ],
      "preview_image":         "/templates-preview/cinematic_hvac.png",
      "color_swatches":        ["#fafaf9", "#18181b", "#0891b2", "#0e7490"],
      "fonts": {
        "display": "Archivo Black",
        "body":    "Inter",
        "mono":    "JetBrains Mono"
      },
      "best_for": "HVAC contractors. Cyan accent associates with cooling + airflow. Same-day availability is the headline trust signal.",
      "tier":                  "free",
      "preview_url":           "http://localhost:3100/cinematic_hvac",
      "preview_pages": [
        { "label": "Home",     "path": "/"        },
        { "label": "About",    "path": "/about"   },
        { "label": "Services", "path": "/services"},
        { "label": "Contact",  "path": "/contact" }
      ]
    }
```

- [ ] **Step 6: Build + matcher verify**

```bash
cd pebble/templates/cinematic_hvac && npx next build 2>&1 | tail -5
```

Expected: `Compiled successfully`.

- [ ] **Step 7: Commit**

```bash
git add pebble/templates/cinematic_hvac/ pebble/templates/registry.json
git commit -m "feat(templates): cinematic_hvac — Cinematic Hero skin for HVAC

Cyan accent (#0891b2), HVAC-specific services + trust badges.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Skin — `cinematic_construction` (clone + 3-file delta)

- [ ] **Step 1: Clone**

```bash
cp -r pebble/templates/cinematic_hero pebble/templates/cinematic_construction
```

- [ ] **Step 2: Accent swap in globals.css**

Change `--color-accent` to `#ea580c`, `--color-accent-dark` to `#c2410c`.

- [ ] **Step 3: Replace content/site.ts**

Apply these construction-specific values (same fields as Task 3 step 3, only the strings change):

```typescript
export const SITE_TITLE       = "[Your Construction Co.]";
export const SITE_DESCRIPTION = "Licensed general contractor. Additions, remodels, custom builds. On time, on budget.";
export const TAGLINE          = "Build it right. The first time.";

export const HERO_PILL              = "BOOKING SUMMER PROJECTS";
export const HERO_HEADLINE          = "Built right. On time.";
export const HERO_SUBLINE           = "Licensed general contractor. Fixed-price quotes, phased payments, weekly progress photos. References from every project on request.";
export const HERO_CTA_PRIMARY       = "Get a project quote";
export const HERO_CTA_SECONDARY     = "See past work";

export const SERVICES: Service[] = [
  { id: "svc-1", title: "Home Additions",     description: "Second-story adds, room extensions, garage conversions. Full architectural drawings included. Permits handled.",       icon: "Home"      },
  { id: "svc-2", title: "Kitchen & Bath",     description: "Complete remodels with fixed-price quotes. We don't touch demo until cabinets and counters are in our shop.",          icon: "ChefHat"   },
  { id: "svc-3", title: "Custom Builds",      description: "New construction from raw lot to certificate of occupancy. We handle architect, engineer, and inspector coordination.", icon: "HardHat"   },
];

export const ABOUT_HEADLINE    = "Build it right. The first time.";
export const ABOUT_BODY        = "[Two paragraphs about your firm — years in business, signature project types, what your phased-payment process looks like. Mention specific licenses (general contractor #, lead-safe cert, etc.) and any builder-of-the-year style recognition.]";

export const TRUST_BADGES: Trust[] = [
  { label: "LICENSED GC", sub: "[State GC license #]"          },
  { label: "BONDED",      sub: "[Bond amount]"                 },
  { label: "INSURED",     sub: "$[amount] liability"           },
  { label: "FAMILY-OWNED", sub: "Building in [city] since [year]" },
];

export const TESTIMONIAL_QUOTE  = "[Specific story: 'They did our 800-sqft addition. Weekly photo updates, fixed-price quote held even when we found rot in a wall, finished 5 days ahead of schedule.']";
export const TESTIMONIAL_AUTHOR = "[Daniel R.], [City]";

export const CONTACT_PHONE          = "[(555) 555-0100]";
export const CONTACT_EMAIL          = "[office@yourbuild.example]";
export const CONTACT_HOURS          = "[Mon–Fri 7am–5pm · Site visits by appointment]";
export const CONTACT_HEADLINE       = "Have a project in mind?";
export const CONTACT_BODY           = "Tell us about it. We'll schedule a site visit within a week and have a fixed-price quote inside two weeks.";

export const CTA_BAND_HEADLINE = "Booking summer projects now.";
export const CTA_BAND_BODY     = "Lead time for additions and remodels is 4-6 weeks. Get on the calendar — quotes are free.";
export const CTA_BAND_LABEL    = "Request a quote";
export const CTA_BAND_HREF     = "/contact";

export const FOOTER_TAGLINE = "Licensed general contractor.";
```

- [ ] **Step 4: Update dna_source.json**

`dna_id` → `cinematic_construction`, accent → `#ea580c`, accent_dark → `#c2410c`.

- [ ] **Step 5: Append registry entry**

```json
    {
      "id":                    "cinematic_construction",
      "directory":             "pebble/templates/cinematic_construction",
      "name":                  "Steelhouse Build Co.",
      "tagline":               "Cinematic construction hero. Safety-orange accent. Fixed-price.",
      "vibe":                  "Cinematic Real-Estate Listing — Construction",
      "source_dna":            "cinematic_construction",
      "applicable_industries": [
        "construction",
        "general contractor",
        "home builder",
        "home addition",
        "remodel contractor",
        "kitchen remodel",
        "bath remodel",
        "custom homes"
      ],
      "preview_image":         "/templates-preview/cinematic_construction.png",
      "color_swatches":        ["#fafaf9", "#18181b", "#ea580c", "#c2410c"],
      "fonts": {
        "display": "Archivo Black",
        "body":    "Inter",
        "mono":    "JetBrains Mono"
      },
      "best_for": "General contractors + remodel firms. Safety-orange accent reads as work-crew/construction-cone. Headline trust signal is fixed-price quoting.",
      "tier":                  "free",
      "preview_url":           "http://localhost:3100/cinematic_construction",
      "preview_pages": [
        { "label": "Home",     "path": "/"        },
        { "label": "About",    "path": "/about"   },
        { "label": "Services", "path": "/services"},
        { "label": "Contact",  "path": "/contact" }
      ]
    }
```

- [ ] **Step 6: Build verify**

```bash
cd pebble/templates/cinematic_construction && npx next build 2>&1 | tail -5
```

- [ ] **Step 7: Commit**

```bash
git add pebble/templates/cinematic_construction/ pebble/templates/registry.json
git commit -m "feat(templates): cinematic_construction — Cinematic Hero skin for GCs

Safety-orange accent (#ea580c), construction-specific services + trust
badges. CTABand emphasizes fixed-price quoting + summer booking lead time.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Skin — `cinematic_landscaper` (clone + 3-file delta)

- [ ] **Step 1: Clone**

```bash
cp -r pebble/templates/cinematic_hero pebble/templates/cinematic_landscaper
```

- [ ] **Step 2: Accent swap in globals.css**

Change `--color-accent` to `#65a30d`, `--color-accent-dark` to `#4d7c0f`.

- [ ] **Step 3: Replace content/site.ts**

Apply these landscaper-specific values:

```typescript
export const SITE_TITLE       = "[Your Landscape Co.]";
export const SITE_DESCRIPTION = "Landscape design + maintenance. Weekly service, full installs, water-wise designs.";
export const TAGLINE          = "Yards that work. Year-round.";

export const HERO_PILL              = "BOOKING SPRING INSTALLS";
export const HERO_HEADLINE          = "Yards. Done right.";
export const HERO_SUBLINE           = "Full-service landscape design + maintenance. Weekly mowing routes, seasonal installs, water-wise plant selection for your zone.";
export const HERO_CTA_PRIMARY       = "Get a quote";
export const HERO_CTA_SECONDARY     = "See our work";

export const SERVICES: Service[] = [
  { id: "svc-1", title: "Weekly Maintenance", description: "Mowing, edging, blowing, hedge trimming. Same crew every visit. Routes published so you know when we're coming.", icon: "Leaf"    },
  { id: "svc-2", title: "Landscape Design",   description: "Full design + install. We work with the plants that thrive in your zone — no fragile imports that die in year two.", icon: "Sprout"  },
  { id: "svc-3", title: "Seasonal Cleanups",  description: "Spring prep, fall leaf removal, gutter clearing. Most properties done in a single visit.",                          icon: "TreePine" },
];

export const ABOUT_HEADLINE    = "Local landscapers. Same crew every week.";
export const ABOUT_BODY        = "[Two paragraphs about your crew — how long you've been working in [city], your design philosophy, what makes your maintenance routes different from the chain franchises. Mention water-wise / native plant expertise if relevant.]";

export const TRUST_BADGES: Trust[] = [
  { label: "LICENSED",        sub: "[State landscape license #]"  },
  { label: "INSURED",         sub: "Up to $[amount]"              },
  { label: "5-STAR RATED",    sub: "[N]+ Google reviews"          },
  { label: "FAMILY-OWNED",    sub: "Serving [city] since [year]"  },
];

export const TESTIMONIAL_QUOTE  = "[Specific story: 'They redesigned our front yard with all native plants. Three years in, it looks better every season and our water bill is down 40%.']";
export const TESTIMONIAL_AUTHOR = "[Maria T.], [City]";

export const CONTACT_PHONE          = "[(555) 555-0100]";
export const CONTACT_EMAIL          = "[office@yourlandscape.example]";
export const CONTACT_HOURS          = "[Mon–Sat 7am–6pm · Closed Sundays]";
export const CONTACT_HEADLINE       = "Tell us about your yard.";
export const CONTACT_BODY           = "We'll schedule a walkthrough within a week. Maintenance routes start at $X/visit. Design + install quoted on site.";

export const CTA_BAND_HEADLINE = "Spring installs booking now.";
export const CTA_BAND_BODY     = "Lead time for full landscape installs is 3-4 weeks once approved. Weekly maintenance has same-week openings.";
export const CTA_BAND_LABEL    = "Schedule a walkthrough";
export const CTA_BAND_HREF     = "/contact";

export const FOOTER_TAGLINE = "Local landscape design + maintenance.";
```

- [ ] **Step 4: Update dna_source.json**

`dna_id` → `cinematic_landscaper`, accent → `#65a30d`, accent_dark → `#4d7c0f`.

- [ ] **Step 5: Append registry entry**

```json
    {
      "id":                    "cinematic_landscaper",
      "directory":             "pebble/templates/cinematic_landscaper",
      "name":                  "Greenwell Yards Co.",
      "tagline":               "Cinematic landscape hero. Lime accent. Weekly routes + full installs.",
      "vibe":                  "Cinematic Real-Estate Listing — Landscaping",
      "source_dna":            "cinematic_landscaper",
      "applicable_industries": [
        "landscaper",
        "landscaping",
        "lawn care",
        "garden design",
        "yard maintenance",
        "tree service",
        "irrigation installer"
      ],
      "preview_image":         "/templates-preview/cinematic_landscaper.png",
      "color_swatches":        ["#fafaf9", "#18181b", "#65a30d", "#4d7c0f"],
      "fonts": {
        "display": "Archivo Black",
        "body":    "Inter",
        "mono":    "JetBrains Mono"
      },
      "best_for": "Landscapers and lawn-care companies. Lime accent reads as fresh-cut grass. Headline trust signal is consistent weekly route + same crew.",
      "tier":                  "free",
      "preview_url":           "http://localhost:3100/cinematic_landscaper",
      "preview_pages": [
        { "label": "Home",     "path": "/"        },
        { "label": "About",    "path": "/about"   },
        { "label": "Services", "path": "/services"},
        { "label": "Contact",  "path": "/contact" }
      ]
    }
```

- [ ] **Step 6: Build verify**

```bash
cd pebble/templates/cinematic_landscaper && npx next build 2>&1 | tail -5
```

- [ ] **Step 7: Commit**

```bash
git add pebble/templates/cinematic_landscaper/ pebble/templates/registry.json
git commit -m "feat(templates): cinematic_landscaper — Cinematic Hero skin for landscapers

Lime-green accent (#65a30d), landscape-specific services (weekly route,
design+install, seasonal cleanups), water-wise positioning in copy.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Skin — `cinematic_dog_groomer` (clone + 3-file delta)

- [ ] **Step 1: Clone**

```bash
cp -r pebble/templates/cinematic_hero pebble/templates/cinematic_dog_groomer
```

- [ ] **Step 2: Accent swap in globals.css**

Change `--color-accent` to `#db2777`, `--color-accent-dark` to `#be185d`.

- [ ] **Step 3: Replace content/site.ts**

Apply these dog-groomer-specific values:

```typescript
export const SITE_TITLE       = "[Your Grooming Co.]";
export const SITE_DESCRIPTION = "Calm, low-stress dog grooming. Small-batch appointments. We get to know your dog.";
export const TAGLINE          = "Calm grooms. Happy dogs.";

export const HERO_PILL              = "BOOKING THIS WEEK";
export const HERO_HEADLINE          = "Grooms your dog loves.";
export const HERO_SUBLINE           = "Small-batch appointments — never crowded. We get to know your dog's quirks before the clippers come out. Most pups leave wagging.";
export const HERO_CTA_PRIMARY       = "Book an appointment";
export const HERO_CTA_SECONDARY     = "See pricing";

export const SERVICES: Service[] = [
  { id: "svc-1", title: "Full Groom",       description: "Bath, blow-dry, brush-out, trim, nail clip, ear clean. Breed-specific cuts. Includes a quick puppuccino at checkout.",   icon: "Scissors" },
  { id: "svc-2", title: "Bath & Brush",     description: "Just the basics. Perfect for in-between full grooms or for low-maintenance breeds.",                                       icon: "Droplets" },
  { id: "svc-3", title: "Anxiety-Friendly", description: "Slower pace, no dryer, one-on-one attention. Designed for rescues, seniors, and pups who don't love the groom chair yet.", icon: "Heart"    },
];

export const ABOUT_HEADLINE    = "We're not a factory. We're a salon.";
export const ABOUT_BODY        = "[Two paragraphs about your shop — small-batch philosophy, who you've trained with, what makes your shop different from the chains. Mention if you specialize in rescue/anxious dogs, breed expertise, or have any certifications (Master Groomer, Fear-Free, etc.).]";

export const TRUST_BADGES: Trust[] = [
  { label: "FEAR-FREE CERT", sub: "Anxiety-friendly handling"  },
  { label: "INSURED",        sub: "Up to $[amount]"             },
  { label: "5-STAR RATED",   sub: "[N]+ Google reviews"         },
  { label: "FAMILY-OWNED",   sub: "Serving [city] since [year]" },
];

export const TESTIMONIAL_QUOTE  = "[Specific story: 'My rescue Border Collie used to shake the whole time at the chain groomers. At [shop name] she actually wags her tail when we pull up.']";
export const TESTIMONIAL_AUTHOR = "[Rachel B.], [City]";

export const CONTACT_PHONE          = "[(555) 555-0100]";
export const CONTACT_EMAIL          = "[hello@yourgrooming.example]";
export const CONTACT_HOURS          = "[Tue–Sat 8am–5pm · Closed Sun–Mon]";
export const CONTACT_HEADLINE       = "Book your pup.";
export const CONTACT_BODY           = "Tell us about your dog — breed, age, any quirks. We'll match you with the right groomer and a time slot.";

export const CTA_BAND_HEADLINE = "Booking this week.";
export const CTA_BAND_BODY     = "Most slots fill 1-2 weeks out. Same-week openings are first-come — best to book online or call ahead.";
export const CTA_BAND_LABEL    = "Book online";
export const CTA_BAND_HREF     = "/contact";

export const FOOTER_TAGLINE = "Small-batch dog grooming, calm and unrushed.";
```

- [ ] **Step 4: Update dna_source.json**

`dna_id` → `cinematic_dog_groomer`, accent → `#db2777`, accent_dark → `#be185d`.

- [ ] **Step 5: Append registry entry**

```json
    {
      "id":                    "cinematic_dog_groomer",
      "directory":             "pebble/templates/cinematic_dog_groomer",
      "name":                  "Hush & Wag Grooming",
      "tagline":               "Cinematic dog-groomer hero. Pink accent. Small-batch, anxiety-friendly.",
      "vibe":                  "Cinematic Real-Estate Listing — Dog Grooming",
      "source_dna":            "cinematic_dog_groomer",
      "applicable_industries": [
        "dog groomer",
        "dog grooming",
        "pet grooming",
        "mobile dog grooming",
        "cat grooming",
        "pet spa"
      ],
      "preview_image":         "/templates-preview/cinematic_dog_groomer.png",
      "color_swatches":        ["#fafaf9", "#18181b", "#db2777", "#be185d"],
      "fonts": {
        "display": "Archivo Black",
        "body":    "Inter",
        "mono":    "JetBrains Mono"
      },
      "best_for": "Independent dog groomers competing against PetSmart/Petco chains. Warm-pink accent reads friendly/approachable. Headline trust signal is small-batch + anxiety-friendly handling.",
      "tier":                  "free",
      "preview_url":           "http://localhost:3100/cinematic_dog_groomer",
      "preview_pages": [
        { "label": "Home",     "path": "/"        },
        { "label": "About",    "path": "/about"   },
        { "label": "Services", "path": "/services"},
        { "label": "Contact",  "path": "/contact" }
      ]
    }
```

- [ ] **Step 6: Build verify**

```bash
cd pebble/templates/cinematic_dog_groomer && npx next build 2>&1 | tail -5
```

- [ ] **Step 7: Commit**

```bash
git add pebble/templates/cinematic_dog_groomer/ pebble/templates/registry.json
git commit -m "feat(templates): cinematic_dog_groomer — Cinematic Hero skin for dog groomers

Warm-pink accent (#db2777), dog-groomer-specific services (Full Groom,
Bath & Brush, Anxiety-Friendly), Fear-Free certification badge.
Differentiates from PetSmart/Petco chains via small-batch positioning.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: Take preview screenshots for all 6 templates

**Files:**
- Create: `ui/v3/public/templates-preview/cinematic_hero.png`
- Create: `ui/v3/public/templates-preview/cinematic_plumber.png`
- Create: `ui/v3/public/templates-preview/cinematic_hvac.png`
- Create: `ui/v3/public/templates-preview/cinematic_construction.png`
- Create: `ui/v3/public/templates-preview/cinematic_landscaper.png`
- Create: `ui/v3/public/templates-preview/cinematic_dog_groomer.png`

- [ ] **Step 1: Start each template's dev server in turn + screenshot the home page**

For each template id (`cinematic_hero`, `cinematic_plumber`, `cinematic_hvac`, `cinematic_construction`, `cinematic_landscaper`, `cinematic_dog_groomer`), run:

```bash
cd pebble/templates/<id>
nohup npx next dev -p 3199 > /tmp/preview.log 2>&1 &
sleep 8     # let Next.js compile + boot
```

Then take a screenshot of `http://localhost:3199/` at 1280×800 viewport, save to `ui/v3/public/templates-preview/<id>.png`. Use Playwright (already a dev dep):

```bash
npx playwright -V 2>/dev/null || npm i -D playwright   # install if missing
node -e "
const {chromium} = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page    = await browser.newPage({viewport: {width: 1280, height: 800}});
  await page.goto('http://localhost:3199/', {waitUntil: 'networkidle', timeout: 30000});
  await page.waitForTimeout(1500);  // hero animation
  await page.screenshot({path: '../../ui/v3/public/templates-preview/<id>.png', type: 'png'});
  await browser.close();
})();
"
```

Then kill the dev server:
```bash
pkill -f 'next dev -p 3199' 2>/dev/null
```

Repeat for all 6 templates.

- [ ] **Step 2: Verify all 6 screenshots exist and are ≥ 50KB**

```bash
ls -la ui/v3/public/templates-preview/cinematic_*.png
```

Expected: 6 files, each ≥ 50KB.

- [ ] **Step 3: Commit screenshots**

```bash
git add ui/v3/public/templates-preview/cinematic_*.png
git commit -m "feat(templates): preview screenshots for 6 cinematic templates

Renders captured at 1280×800 viewport with hero animation settled.
Drives the /templates gallery card preview for each new entry.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: Smoke-test the template gallery + matcher end-to-end

**Files:**
- No code changes; verification only.

- [ ] **Step 1: Verify the matcher surfaces the right cinematic skin per industry prompt**

Run:
```bash
python -c "
from pathlib import Path; import os
for line in Path('.env').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, _, v = line.partition('='); os.environ.setdefault(k.strip(), v.strip())
from pebble.server.template_match import match_templates

cases = [
  ('I run a plumbing business in Brooklyn', 'plumber'),
  ('HVAC contractor doing same-day service', 'hvac'),
  ('General contractor in Phoenix', 'construction'),
  ('Landscape design + weekly maintenance', 'landscaper'),
  ('Independent dog groomer, small shop', 'dog_groomer'),
]
for prompt, bt in cases:
    r = match_templates(prompt, business_type=bt, max_results=3)
    top = [m['template_id'] for m in r['matches']]
    print(f'{bt:14s} → {top}')
"
```

Expected: for each business_type, the matching `cinematic_*` template appears in the top-3 results.

- [ ] **Step 2: Verify the v3 gallery loads with the new templates visible**

Restart engine + v3 if not running, then:
```bash
curl -s http://localhost:8000/api/templates | python -c "
import sys, json
r = json.load(sys.stdin)
ids = [t['id'] for t in r['templates']]
cinematic = [i for i in ids if i.startswith('cinematic_')]
print(f'total templates in registry: {len(ids)}')
print(f'cinematic_* templates: {cinematic}')
"
```

Expected: 6 cinematic_* templates (base + 5 skins). Total registry count is previous + 6.

- [ ] **Step 3: Open the v3 gallery in browser + visual eyeball**

Open `http://localhost:3001/templates` in your own browser. Look for the 6 new cards. Click "Preview" on each — the iframe should load with the right hero pattern + accent color.

If any preview fails to load, check that `npx next dev` works in that template directory. If hero photo doesn't render, the placeholder image at Step 10 of Task 1 may not have downloaded — re-run that step for the affected template.

- [ ] **Step 4: Live-instantiate cinematic_plumber as a test build**

Run from the v3 frontend or curl:
```bash
curl -s -X POST http://localhost:8000/api/instantiate-template \
  -H 'Content-Type: application/json' \
  -d '{"template_id": "cinematic_plumber", "brief": {"business_name": "Acme Plumbing", "business_type": "plumber"}}' \
  | python -m json.tool
```

Expected: `{"ok": true, "slug": "acme-plumbing-...", "file_count": 28+, "swap_ok": true}`. Then open `http://localhost:3001/workspace/<slug>` and verify the site renders with "Acme Plumbing" populated where the placeholders were.

---

## Task 10: Final push to squitopest

**Files:**
- No code changes; final commit + push.

- [ ] **Step 1: Run full pytest suite to catch any regressions**

```bash
python -m pytest -q 2>&1 | tail -5
```

Expected: ≥ 2244 PASS (baseline post-image-fan-out). 13 pre-existing failures unchanged.

- [ ] **Step 2: Verify git log shows expected commits**

```bash
git log --oneline | head -10
```

Expected (newest first): 6 new commits — preview screenshots, dog_groomer, landscaper, construction, hvac, plumber, registry entry for base, base scaffold.

- [ ] **Step 3: Push to squitopest**

```bash
git push 2>&1 | tail -5
```

Expected: `phase56a-for-squitopest -> phase56a-for-squitopest` showing 8+ new commits pushed.

- [ ] **Step 4: Hand off to Marc with a smoke-test checklist**

Send a brief message with:
- Open `/templates` in v3 — confirm 6 new cinematic_* cards appear with correct preview images + color swatches
- Click each card's "Preview" — confirm iframe loads with the right hero + accent color
- Run the matcher cases from Task 9 Step 1 in his own terminal — confirm matches are right
- For one skin (recommend cinematic_plumber), do a full instantiate-template test from the workspace flow

---

## Self-Review

**Spec coverage:**

| Spec item | Task | Status |
|---|---|---|
| New Cinematic Hero base with real-estate-style hero | Task 1 (base scaffold, Hero.tsx + globals.css + content/site.ts) | ✓ |
| Slate + Amber palette not in registry today | Task 1 Step 3 (globals.css) | ✓ |
| Archivo Black + Inter font pair (not currently used together) | Task 1 Step 4 (layout.tsx) | ✓ |
| 5 service-industry skins: plumber, hvac, construction, landscaper, dog_groomer | Tasks 3-7 | ✓ |
| Each skin has industry-appropriate accent color | Task 3-7 Step 2 (globals.css) | ✓ |
| Each skin has industry-specific services + copy + trust badges | Task 3-7 Step 3 (content/site.ts) | ✓ |
| Registry entries so matcher surfaces the right skin per signup | Tasks 2 + 3-7 Step 5 | ✓ |
| Preview screenshots for the gallery | Task 8 | ✓ |
| End-to-end matcher verification | Task 9 | ✓ |

**Placeholder scan:** No TBD / TODO / "Add error handling" / "Similar to Task N" found. All copy strings, color values, registry JSON are explicit and complete.

**Type consistency:**
- `Service` type defined once in `content/site.ts` (Task 1 Step 5), used unchanged in all skin templates ✓
- `Trust` type defined once, used unchanged ✓
- All `HERO_*` constants imported by Hero.tsx are defined in every skin's content/site.ts ✓
- Registry entry shape (id, directory, name, tagline, vibe, source_dna, applicable_industries, preview_image, color_swatches, fonts, best_for, tier, preview_url, preview_pages) consistent across all 6 entries ✓

All checks pass.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-24-cinematic-hero-template-base.md`. Two execution options:

**1. Inline Execution (recommended for this plan)** — Execute tasks in this session. Each task is highly mechanical (clone + 3-file delta), so subagent dispatch overhead would exceed actual work time. You'd see screenshots land as each skin finishes, can redirect on look-and-feel before all 6 ship.

**2. Subagent-Driven** — Dispatch fresh subagent per task with two-stage review. Slower but isolates context. Useful if you want to fire it off and check back later — but for visual template work, inline lets you redirect faster.

Which approach? Or: want to ship base + just 1 or 2 skins first to see how it looks, then decide on the rest?
