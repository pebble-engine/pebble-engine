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

**YOU MUST ADD THESE TWO LINES — INSIDE `useEffect`, NEVER at module level:**

```tsx
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Module level — safe. registerPlugin does not touch window or document.
gsap.registerPlugin(ScrollTrigger);

// Inside useEffect ONLY. These access window — calling them at module level
// crashes Next.js SSR with "Cannot read properties of undefined".
useEffect(() => {
  ScrollTrigger.normalizeScroll(true);
  ScrollTrigger.config({ ignoreMobileResize: true });
  // ... rest of Lenis/GSAP setup
}, []);
```

**Why module level fails:** Next.js runs your component code on the server during SSR. `ScrollTrigger.normalizeScroll` immediately tries to access `window` and `document`, which don't exist on the server. The page crashes with a 500 before reaching the browser. `gsap.registerPlugin()` is safe at module level because it only registers the plugin internally without touching the DOM.

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
  // Lenis 1.1.x API. Older props `smoothTouch` and `overscroll` were REMOVED.
  // TypeScript will reject them. Use the new names below.
  duration: 1.2,
  easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smoothWheel: true,
  syncTouch: false,      // replaces `smoothTouch` — keep false on iOS for native momentum
  touchMultiplier: 2,    // faster touch response
  infinite: false,
});

// Rubber-band suppression now lives in CSS, not Lenis:
//   html, body { overscroll-behavior-y: none; }
```

`syncTouch: false` is critical. Enabling sync touch (the 1.1.x replacement for the old `smoothTouch`) conflicts with iOS's native momentum scroll and causes lag. Let iOS handle touch scroll natively; Lenis enhances mouse wheel only. The old `overscroll: false` flag was removed — use the CSS `overscroll-behavior-y: none` declaration in `globals.css` instead.

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
