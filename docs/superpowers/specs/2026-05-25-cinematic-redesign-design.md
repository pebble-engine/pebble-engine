# Cinematic Redesign — FloatingPeblet + Community + Templates + Dashboard

> **For agentic workers:** Design spec. Implementation plan lives at `docs/superpowers/plans/` once writing-plans runs.

**Goal:** Replace the fixed 340px ControlCenter chat panel with a draggable floating widget, then apply a cinematic visual upgrade to the Community page, Template Gallery, and Dashboard empty state.

**Scope:** 4 changes, all in `ui/v3/`. No backend changes required.

---

## 1. Architecture

### Where the right-rail chat lives today vs. after

| Location | Before | After |
|---|---|---|
| `/dashboard` | ControlCenter 3-pane (left \| canvas \| 340px chat) | ControlCenter 2-pane (left \| canvas) + FloatingPeblet |
| `/community` | Same | Same |
| `/templates` | No ControlCenter (TopNav only) | FloatingPeblet added |
| `/workspace/[slug]` | WorkspaceShell (never used ControlCenter) | **Unchanged** |

The workspace keeps its focused build layout. FloatingPeblet is the casual, always-there companion on every other page.

### FloatingPeblet — `ui/v3/components/floating-peblet.tsx`

**Behaviour:**
- Mounted via `ReactDOM.createPortal` to `document.body` — renders outside any parent stacking context so it can be freely dragged across the full viewport
- Two states: `collapsed` and `open`
  - **Collapsed:** 64×64 rounded-full circle, Peblet icon centred, animated green pulse dot (bottom-right of circle, `animate={{ scale: [1, 1.4, 1] }}` on 2s loop)
  - **Open:** 380px wide × 520px tall panel, same `PebbleChat` component inside, `X` button top-right to collapse
- Framer Motion `drag` with `dragConstraints` set to viewport bounds minus 20px padding on each edge (computed via `useEffect` reading `window.innerWidth/Height`)
- Default position: bottom-right (`{ x: window.innerWidth - 404, y: window.innerHeight - 544 }`)
- Position persisted to `localStorage` key `"peblet-widget-pos"` — restored on mount
- `projectContext?: ChatProjectContext | null` prop passes straight through to `PebbleChat`
- Accessible: `aria-label="Open Peblet assistant"` on collapsed button, focus-trapped when open

**Framer Motion details:**
```tsx
<motion.div
  drag
  dragMomentum={false}
  dragConstraints={boundsRef}  // ref to viewport rect
  initial={savedPos}
  animate={savedPos}
  onDragEnd={(_, info) => savePos(info.point)}
>
  {collapsed ? <CollapsedBubble /> : <OpenPanel />}
</motion.div>
```

### ControlCenter changes — `ui/v3/components/control-center.tsx`

- Remove the 340px right-rail `<aside>` and all chat-related state (`chatCollapsed`, `mobileChatOpen`)
- Remove the mobile "Ask Peblet" floating pill (FloatingPeblet replaces it)
- Remove the `<PebbleChat>` render from ControlCenter
- Add `<FloatingPeblet greeting={greeting} projectContext={projectContext} />` as the last child of the root `<div>` — renders via portal so placement in the tree doesn't matter
- Props: `children`, `leftSidebar?`, `greeting?`, `projectContext?` — same external interface, no page-level changes needed
- Result: ControlCenter becomes a clean 2-pane flex container

---

## 2. Community Page — `ui/v3/app/community/page.tsx`

Content, data fetching, and CTAs are unchanged. Visual treatment only.

### 2a. Hero — full-bleed photo background

**Replace:** The `rounded-3xl border bg-gradient-to-br` hero card.

**With:** A full-width section (no border-radius, `overflow-hidden`) containing:
- A background `<img>` (or CSS `background-image`) using a dark creative/urban Unsplash photo. Use `https://images.unsplash.com/photo-1497366216548-37526070297c?w=1600&q=80` (open office, dark, cinematic) as the default. `object-cover` + `absolute inset-0 w-full h-full`.
- Dark overlay: `absolute inset-0 bg-black/55`
- All existing text/CTA content sits above the overlay (`relative z-10`), text forced white
- Stats strip: same 3-card grid, cards get `bg-white/10 backdrop-blur-md border-white/20 text-white` treatment
- Minimum height: `min-h-[420px] md:min-h-[480px]`
- Padding: `px-8 md:px-16 py-14 md:py-20`

### 2b. News ticker — between hero and activity feed

Use the existing `Marquee` component (`components/ui/marquee.tsx`).

Feed it the `liveActivity` array formatted as a single string per item:
```
"🚀 {title}" for launch/feature · "💡 {title}" for tip · "👋 {title}" for join · "💬 {title}" for discussion
```
Items separated by a `·` spacer span with `mx-6 opacity-30`.

Marquee speed: `duration-[30s]`. Container: `py-3 border-y border-border bg-muted/40 overflow-hidden`.

### 2c. Showcase — horizontal filmstrip

**Replace:** The `grid grid-cols-2 md:grid-cols-3` static grid.

**With:** A horizontally scrollable rail:
```tsx
// Note: project uses Tailwind v4 — use overflow-x-auto [&::-webkit-scrollbar]:hidden
// instead of scrollbar-hide (that's a v3 plugin class not available here).
<div className="flex gap-4 overflow-x-auto [&::-webkit-scrollbar]:hidden pb-2 snap-x snap-mandatory">
  {SHOWCASE.map(s => (
    <Link className="shrink-0 snap-start w-[280px] aspect-[14/9] relative rounded-xl overflow-hidden ...">
      <img ... className="... group-hover:scale-105 transition-transform duration-500" />
      <div className="absolute inset-x-0 bottom-0 p-3 bg-gradient-to-t from-black/80 ...">
        {/* name + kind */}
      </div>
    </Link>
  ))}
</div>
```
Scroll shadows on left/right: `before:absolute before:left-0 before:inset-y-0 before:w-8 before:bg-gradient-to-r before:from-background` on the wrapper.

Hover: `scale-103` on the image, `shadow-xl` lift on the card.

---

## 3. Template Gallery — `ui/v3/app/templates/page.tsx`

### 3a. Remove tier system

- Delete `TierTabButton` component and the 3-tab row
- Delete `TierTab` type and `normalizeTier()` function
- Delete `buckets` useMemo and `activeTab` state
- Replace `visible` (filtered by tab) with the full `templates` array filtered by `activeIndustry` (new state, see 3b)
- Remove tier badge from `TemplateCard` (the coloured pill top-left)
- Remove lock icon from `TemplateCard`
- Remove `normalizeTier(t.tier) === "premium"` lock overlay
- `PublicTabPlaceholder` component deleted; replace with a `SubmitTemplateCard` at the end of the grid (always visible)

### 3b. Industry thumbnail ribbon

New state: `activeIndustry: string | null` (null = All).

**Industry extraction:**
```ts
const industries = useMemo(() => {
  const seen = new Set<string>();
  (templates ?? []).forEach(t => t.applicable_industries.forEach(i => seen.add(i)));
  return Array.from(seen).sort();
}, [templates]);
```

**Ribbon component (inline):**
```tsx
<div className="relative mb-8">
  {/* left/right scroll shadows */}
  <div className="flex gap-2 overflow-x-auto [&::-webkit-scrollbar]:hidden pb-1">
    <RibbonChip active={!activeIndustry} onClick={() => setActiveIndustry(null)} swatch={null}>
      All
    </RibbonChip>
    {industries.map(ind => (
      <RibbonChip
        key={ind}
        active={activeIndustry === ind}
        onClick={() => setActiveIndustry(ind)}
        swatch={firstSwatchForIndustry(ind, templates ?? [])}
      >
        {ind}
      </RibbonChip>
    ))}
  </div>
</div>
```

`RibbonChip` props: `active`, `onClick`, `swatch: string[] | null`, `children`.

Each chip layout:
- If `swatch`: small 40×28px `div` with `background: linear-gradient(135deg, ${swatch.join(", ")})` rounded-md, then the label
- If no swatch (All chip): just the label
- Active: `bg-foreground text-background`, inactive: `bg-card border border-border text-muted-foreground hover:text-foreground`

`firstSwatchForIndustry(ind, templates)`: returns `color_swatches` from the first template where `applicable_industries.includes(ind)`, or `null`.

**Filtering:**
```ts
const visible = (templates ?? []).filter(t =>
  !activeIndustry || t.applicable_industries.includes(activeIndustry)
);
```

### 3c. Cinematic card hover overlay

In `TemplateCard`, inside the image container, add a hover-reveal overlay:
```tsx
<div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent
                opacity-0 group-hover:opacity-100 transition-opacity duration-300
                flex flex-col justify-end p-4">
  <p className="text-white text-sm font-medium leading-snug line-clamp-2">{t.tagline}</p>
</div>
```
This already works because the parent has `group` class.

### 3d. SubmitTemplateCard at end of grid

A card matching the grid item size, shown after the real template cards:
```tsx
<button onClick={() => window.open("mailto:hello@getpebble.net?subject=Template+submission")}
  className="group text-left bg-card border-2 border-dashed border-border rounded-2xl overflow-hidden
             hover:border-primary/60 transition-colors aspect-[4/3] flex flex-col items-center
             justify-center gap-3 p-6">
  <Upload className="w-8 h-8 text-muted-foreground group-hover:text-primary transition-colors" />
  <p className={`${type.dashboard.heading.m} text-center`}>Submit a template</p>
  <p className={`${type.body.s} text-muted-foreground text-center`}>
    Earn 30% on every install
  </p>
</button>
```

---

## 4. Dashboard Empty State — `ui/v3/app/dashboard/page.tsx`

### 4a. Trigger condition

Existing code already has a `projects.length === 0` branch after loading. That's where the new empty state renders. If projects exist, the existing grid renders as-is.

### 4b. MetallicPebbleLogo component

New file: `ui/v3/components/metallic-pebble-logo.tsx`

```tsx
"use client";
import { motion } from "framer-motion";

export function MetallicPebbleLogo() {
  return (
    <div className="relative flex items-center justify-center w-48 h-48 mx-auto">
      {/* Light rays — conic gradient disc, slow rotation */}
      <motion.div
        className="absolute inset-0 rounded-full"
        style={{
          background: "conic-gradient(from 0deg, transparent 0%, rgba(255,255,255,0.08) 10%, transparent 20%, rgba(255,255,255,0.08) 30%, transparent 40%, rgba(255,255,255,0.08) 50%, transparent 60%, rgba(255,255,255,0.08) 70%, transparent 80%, rgba(255,255,255,0.08) 90%, transparent 100%)",
        }}
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
      />

      {/* Outer glow ring */}
      <div className="absolute inset-4 rounded-full bg-gradient-to-br from-white/5 to-white/0 blur-xl" />

      {/* The P — metallic gradient text + float animation */}
      <motion.div
        className="relative z-10 select-none"
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      >
        {/* Light sweep overlay */}
        <div className="relative overflow-hidden inline-block">
          <span
            style={{
              fontSize: "120px",
              fontWeight: 900,
              lineHeight: 1,
              background: "linear-gradient(135deg, #888 0%, #ddd 30%, #fff 50%, #ddd 70%, #888 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
              filter: "drop-shadow(0 4px 24px rgba(255,255,255,0.15))",
              fontFamily: "var(--font-display, Georgia, serif)",
            }}
          >
            P
          </span>
          {/* Animated shine sweep */}
          <motion.div
            className="absolute inset-0 pointer-events-none"
            style={{
              background: "linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.4) 50%, transparent 60%)",
            }}
            animate={{ x: ["-100%", "200%"] }}
            transition={{ duration: 2.5, repeat: Infinity, repeatDelay: 1.5, ease: "easeInOut" }}
          />
        </div>
      </motion.div>
    </div>
  );
}
```

### 4c. Empty state layout

Two-column layout (on lg+), single column on mobile:

```
[ MetallicPebbleLogo                    ] [ Recent Activity ]
[ "Your first site is one click away." ]
[ [Start from a template] [Build from a brief] ]
```

```tsx
// When projects.length === 0 and !loading:
<div className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-8 items-start py-12">
  {/* Left: logo + CTAs */}
  <div className="flex flex-col items-center text-center gap-6">
    <MetallicPebbleLogo />
    <div className="space-y-2">
      <h2 className={`${type.dashboard.display.m} text-foreground`}>
        Your first site is one click away.
      </h2>
      <p className={`${type.body.m} text-muted-foreground max-w-md mx-auto`}>
        Pick a template and fill in your business info — you'll have something
        real to look at in under a minute.
      </p>
    </div>
    <div className="flex items-center gap-3 flex-wrap justify-center">
      <Link href="/templates"
        className="px-6 py-3 rounded-full bg-foreground text-background font-semibold hover:bg-foreground/90 transition-opacity">
        Start from a template
      </Link>
      <Link href="/workspace#phase=welcome"
        className="px-6 py-3 rounded-full bg-card border border-border text-foreground font-semibold hover:bg-accent transition-colors">
        Build from a brief
      </Link>
    </div>
  </div>

  {/* Right: activity feed — same ActivityFeed component already on the page */}
  <ActivityFeedPanel activity={activity} onRestore={handleRestoreFromActivity} />
</div>
```

`ActivityFeedPanel` is extracted from the existing inline activity JSX — same data, same `handleRestoreFromActivity` handler. No new API calls needed.

---

## 5. Files Changed

| File | Change type |
|---|---|
| `ui/v3/components/floating-peblet.tsx` | **Create** |
| `ui/v3/components/metallic-pebble-logo.tsx` | **Create** |
| `ui/v3/components/control-center.tsx` | **Modify** — remove right rail, add FloatingPeblet |
| `ui/v3/app/community/page.tsx` | **Modify** — hero, ticker, filmstrip |
| `ui/v3/app/templates/page.tsx` | **Modify** — remove tiers, add ribbon, hover overlay, submit card |
| `ui/v3/app/dashboard/page.tsx` | **Modify** — empty state layout + MetallicPebbleLogo |

No backend changes. No new dependencies (Framer Motion already installed, Marquee component already exists).

---

## 6. Out of Scope (deferred)

- Camera roll upload → image-swap via Supabase Storage (noted, not in this plan)
- AI-SLOP combating pass on template copy (separate session)
- Phase 23b: Restore cinematic Code Patterns (separate backlog item)
- FloatingPeblet mobile-specific safe-area treatment beyond viewport clamping
