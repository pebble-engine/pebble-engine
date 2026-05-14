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
│   ├── providers/           ← client-side wrappers (always required)
│   │   └── LenisProvider.tsx
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
    // Allow external image domains for placeholder images.
    // Add the client's CDN/host here before launch.
    remotePatterns: [
      { protocol: "https", hostname: "images.pexels.com" },
      { protocol: "https", hostname: "picsum.photos" },
      { protocol: "https", hostname: "images.unsplash.com" },
    ],
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

This is the single source of truth for brand tokens. Every color goes here as a CSS custom property. Font variables (`--font-display`, `--font-body`) are set automatically by `next/font` via the class on `<html>` — do NOT re-declare them here.

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  /* Prevent tap flash on iOS */
  * {
    -webkit-tap-highlight-color: transparent;
  }

  /* Font rendering */
  body {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  /* Safe area insets for notched iPhones */
  body {
    padding-bottom: env(safe-area-inset-bottom);
    padding-left:   env(safe-area-inset-left);
    padding-right:  env(safe-area-inset-right);
  }

  /* Prevent font size inflation on iPhone landscape */
  html {
    -webkit-text-size-adjust: 100%;
    text-size-adjust: 100%;
  }

  /* Prevent input zoom on iOS */
  input, textarea, select {
    font-size: 16px;
  }

  /* Never set scroll-behavior: smooth — Lenis handles scroll */
}

:root {
  /*
   * BRAND COLORS — replace EVERY value with the brief's design system.
   * These are NOT universal defaults. Read the BI Skill before choosing.
   *
   * Light backgrounds (home services, wellness, food, professional services):
   *   dominant: #FFFFFF   secondary: #F9FAFB   surface: #FFFFFF   text: #111827
   *   accent: trust=blue #2563EB, urgency=amber #D97706, growth=green #059669
   *
   * Dark backgrounds (luxury, tech/SaaS, creative agencies, nightlife):
   *   dominant: #0A0A0A   secondary: #1A1A1A   surface: #111111   text: #F9FAFB
   *   accent: gold #C8A96E, electric #3B82F6, emerald #10B981
   *
   * The defaults below are light-background. Override for dark industries.
   */
  --color-dominant:  #FFFFFF;
  --color-secondary: #F9FAFB;
  --color-accent:    #2563EB;
  --color-surface:   #FFFFFF;
  --color-text:      #111827;

  /*
   * Font variables are injected by next/font in app/layout.tsx.
   * --font-display and --font-body are set on <html> automatically.
   * Use via Tailwind utilities: font-display, font-body
   * Do not redeclare them here — next/font owns these values.
   */
}

html, body {
  overflow-x: hidden;
  /* Replaces Lenis 1.0.x `overscroll: false` option (removed in 1.1.x).
     Suppresses iOS rubber-band bounce that conflicts with GSAP ScrollTrigger. */
  overscroll-behavior-y: none;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
  }
}
```

---

## app/layout.tsx — Root Layout

The root layout must be a **Server Component** so it can export `metadata`. Lenis and ScrollTrigger live in a separate client provider.

**CRITICAL — two fonts must be loaded here.** If only one font is loaded, the display font fallback is browser serif and the heading will look generic. Load both:

```tsx
// app/layout.tsx — Server Component (NO "use client" here)
import type { Metadata } from "next";
import { Inter, Fraunces } from "next/font/google";
import { LenisProvider } from "@/components/providers/LenisProvider";
import "./globals.css";

// Body font — neutral and readable. Replace if the brief calls for something else.
const inter = Inter({ subsets: ["latin"], variable: "--font-body" });

// Display/heading font — MUST be distinctive (see No-Slop Skill for banned fonts).
// Replace "Fraunces" with whatever the brief specifies.
// Other acceptable imports: Oswald, Syne, Playfair_Display, Instrument_Serif,
// Space_Mono, Manrope, Bebas_Neue — match to industry and emotional direction.
const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-display",
  axes: ["opsz"],
});

export const metadata: Metadata = {
  title: "[Business Name]",
  description: "[Business tagline — specific, not vague]",
  other: {
    // viewport-fit=cover is required for iOS safe-area env() to work
    "viewport": "width=device-width, initial-scale=1, viewport-fit=cover",
    // Prevents iOS from auto-linking phone numbers and breaking layouts
    "format-detection": "telephone=no",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Pass BOTH font variables to <html> so Tailwind font-display and font-body work
  return (
    <html lang="en" className={`${inter.variable} ${fraunces.variable}`}>
      <body>
        <LenisProvider>{children}</LenisProvider>
      </body>
    </html>
  );
}
```

```tsx
// components/providers/LenisProvider.tsx — Client Component
"use client";

import { useEffect, useRef } from "react";
import Lenis from "lenis";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Register the plugin at module level — safe, does not touch window/document.
gsap.registerPlugin(ScrollTrigger);

export function LenisProvider({ children }: { children: React.ReactNode }) {
  const lenisRef = useRef<Lenis | null>(null);

  useEffect(() => {
    // CRITICAL — normalizeScroll and config MUST be inside useEffect.
    // Calling them at module level crashes Next.js SSR because they access
    // window before the browser is available. This is a confirmed build failure.
    ScrollTrigger.normalizeScroll(true);
    ScrollTrigger.config({ ignoreMobileResize: true });

    lenisRef.current = new Lenis({
      // Lenis 1.1.x API ONLY. Do NOT pass `smoothTouch` or `overscroll` —
      // they were removed and will fail TypeScript with "Object literal may only
      // specify known properties". For rubber-band suppression use the CSS
      // `overscroll-behavior-y: none` on html/body in globals.css instead.
      duration: 1.2,
      easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      syncTouch: false,     // replaces the old `smoothTouch` — leave false on iOS for native momentum
      touchMultiplier: 2,
      infinite: false,
    });

    // Refresh all ScrollTrigger positions after fonts finish loading.
    // Without this, trigger positions are wrong on slow connections (common on iPhone).
    document.fonts.ready.then(() => ScrollTrigger.refresh());

    let rafId: number;
    const animate = (time: number) => {
      lenisRef.current?.raf(time);
      rafId = requestAnimationFrame(animate);
    };
    rafId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(rafId);
      lenisRef.current?.destroy();
    };
  }, []);

  return <>{children}</>;
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
