# Cinematic Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the ControlCenter fixed chat rail with a draggable floating widget and apply cinematic visual upgrades to the Community page, Template Gallery, and Dashboard empty state.

**Architecture:** All changes are in `ui/v3/`. Task 1 (FloatingPeblet) is the foundation; Task 2 (ControlCenter) depends on it. Tasks 3–5 are independent of each other and can run after Task 2. No backend changes.

**Tech Stack:** Next.js 14 (App Router), React, Framer Motion, Tailwind CSS v4, TypeScript. All dependencies already installed.

---

## File Map

| File | Action |
|---|---|
| `ui/v3/components/floating-peblet.tsx` | **Create** — draggable/collapsible Peblet widget |
| `ui/v3/components/metallic-pebble-logo.tsx` | **Create** — animated 3D metallic "P" logo |
| `ui/v3/components/control-center.tsx` | **Modify** — strip right rail, render FloatingPeblet |
| `ui/v3/app/community/page.tsx` | **Modify** — cinematic hero, marquee ticker, filmstrip |
| `ui/v3/app/templates/page.tsx` | **Modify** — remove tier system, add industry ribbon + FloatingPeblet |
| `ui/v3/app/dashboard/page.tsx` | **Modify** — cinematic empty state with MetallicPebbleLogo |

---

## Task 1: FloatingPeblet component

**Files:**
- Create: `ui/v3/components/floating-peblet.tsx`

The floating chat widget. Mounts via React portal to `document.body` so it sits above all page stacking contexts. Two states: a 64×64 pill (collapsed) and a 380×520 chat panel (open). Framer Motion `useMotionValue` drives position; `localStorage` persists it across page loads.

- [ ] **Step 1: Create the file**

Create `ui/v3/components/floating-peblet.tsx` with this exact content:

```tsx
"use client";

/**
 * FloatingPeblet — draggable/collapsible Peblet chat widget.
 *
 * Mounts via React portal to document.body so it floats above all
 * page content. Replaces the fixed 340px ControlCenter right rail
 * on every non-workspace page.
 *
 * Position persists to localStorage ("peblet-widget-pos").
 * Defaults to bottom-right (24px margins) on first load.
 */

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { motion, AnimatePresence, useMotionValue } from "framer-motion";
import { MessageSquare, X } from "lucide-react";
import { PebbleChat } from "@/components/pebble-chat";
import { type ChatProjectContext } from "@/lib/api";

const STORAGE_KEY = "peblet-widget-pos";

function getSavedPos(): { x: number; y: number } | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const p = JSON.parse(raw) as { x: number; y: number };
    if (typeof p.x === "number" && typeof p.y === "number") return p;
  } catch {}
  return null;
}

export type FloatingPebletProps = {
  greeting?: string;
  projectContext?: ChatProjectContext | null;
};

export function FloatingPeblet({ greeting, projectContext }: FloatingPebletProps) {
  const [mounted, setMounted] = useState(false);
  const [open, setOpen] = useState(false);

  // useMotionValue avoids re-renders during drag. Initialised to 0,0
  // (safe for SSR); real position applied in useEffect after mount.
  const motionX = useMotionValue(0);
  const motionY = useMotionValue(0);

  useEffect(() => {
    const saved = getSavedPos();
    const defaultPos = {
      x: window.innerWidth - 404,   // 380px panel + 24px margin
      y: window.innerHeight - 544,  // 520px panel + 24px margin
    };
    const p = saved ?? defaultPos;
    motionX.set(p.x);
    motionY.set(p.y);
    setMounted(true);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function savePos(x: number, y: number) {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ x, y }));
    } catch {}
  }

  function handleDragEnd() {
    const panelW = open ? 380 : 64;
    const panelH = open ? 520 : 64;
    const rawX = motionX.get();
    const rawY = motionY.get();
    const x = Math.max(20, Math.min(window.innerWidth - panelW - 20, rawX));
    const y = Math.max(20, Math.min(window.innerHeight - panelH - 20, rawY));
    motionX.set(x);
    motionY.set(y);
    savePos(x, y);
  }

  if (!mounted) return null;

  return createPortal(
    <motion.div
      drag
      dragMomentum={false}
      style={{ x: motionX, y: motionY, position: "fixed", zIndex: 9999 }}
      onDragEnd={handleDragEnd}
      className="touch-none"
    >
      <AnimatePresence mode="wait">
        {!open ? (
          /* ── Collapsed: 64×64 pill ── */
          <motion.button
            key="collapsed"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ duration: 0.15 }}
            type="button"
            onClick={() => setOpen(true)}
            aria-label="Open Peblet assistant"
            className="relative w-16 h-16 rounded-full bg-foreground text-background shadow-2xl flex items-center justify-center hover:scale-105 transition-transform cursor-grab active:cursor-grabbing"
          >
            <MessageSquare className="w-6 h-6" />
            {/* Animated presence dot */}
            <span className="absolute bottom-1 right-1 w-3 h-3 rounded-full bg-emerald-500 border-2 border-background">
              <motion.span
                className="absolute inset-0 rounded-full bg-emerald-500"
                animate={{ scale: [1, 1.6, 1], opacity: [1, 0, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </span>
          </motion.button>
        ) : (
          /* ── Open: 380×520 chat panel ── */
          <motion.div
            key="open"
            initial={{ scale: 0.9, opacity: 0, y: 8 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 8 }}
            transition={{ duration: 0.2 }}
            className="w-[380px] h-[520px] rounded-2xl shadow-2xl border border-border bg-card flex flex-col overflow-hidden cursor-grab active:cursor-grabbing"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-border shrink-0">
              <span className="text-sm font-semibold text-foreground">Ask Peblet</span>
              <button
                type="button"
                onClick={() => setOpen(false)}
                aria-label="Close Peblet"
                className="p-1 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            {/* PebbleChat — stopPropagation so clicks inside don't
                trigger the drag handler above. */}
            <div
              className="flex-1 min-h-0 cursor-auto"
              onMouseDown={(e) => e.stopPropagation()}
            >
              <PebbleChat greeting={greeting} projectContext={projectContext} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>,
    document.body,
  );
}
```

- [ ] **Step 2: Verify TypeScript**

```bash
cd ui/v3 && npx tsc --noEmit
```

Expected: no errors mentioning `floating-peblet.tsx`.

- [ ] **Step 3: Commit**

```bash
git add ui/v3/components/floating-peblet.tsx
git commit -m "feat(v3): add FloatingPeblet draggable chat widget"
```

---

## Task 2: ControlCenter simplification

**Files:**
- Modify: `ui/v3/components/control-center.tsx` (full replacement)

Remove the 340px right rail, mobile pill, mobile sheet, and all chat-collapse state. The component becomes a clean 2-pane layout (sidebar + canvas) that renders FloatingPeblet via portal. External API is unchanged — all four props (`children`, `leftSidebar`, `greeting`, `projectContext`) are kept.

- [ ] **Step 1: Replace the entire file**

Overwrite `ui/v3/components/control-center.tsx` with:

```tsx
"use client";

/**
 * ControlCenter — two-pane shell for the Pebble app (2026-05-25 rev 3).
 *
 * Peblet moved from a fixed 340px right rail to a draggable floating
 * widget (FloatingPeblet). The shell now has two panes only:
 *
 *   [ DashboardSidebar (240px) ] [ canvas (flex-1) ]
 *
 * FloatingPeblet mounts via React portal to document.body so it floats
 * freely across the full viewport. The external prop API is unchanged —
 * no page-level edits needed.
 */

import { FloatingPeblet } from "@/components/floating-peblet";
import { type ChatProjectContext } from "@/lib/api";

export type ControlCenterProps = {
  /** Middle column — the actual route content. */
  children: React.ReactNode;
  /** Optional left sidebar slot (DashboardSidebar, or omit). */
  leftSidebar?: React.ReactNode;
  /** Opening line spoken by Peblet on mount. */
  greeting?: string;
  /** Optional project context for chat dispatch. */
  projectContext?: ChatProjectContext | null;
};

export function ControlCenter({
  children,
  leftSidebar,
  greeting,
  projectContext,
}: ControlCenterProps) {
  return (
    <div className="flex h-full w-full overflow-hidden bg-background">
      {/* LEFT — workspace sidebar. Hidden under lg. */}
      {leftSidebar && (
        <aside className="hidden lg:flex shrink-0 h-full">
          {leftSidebar}
        </aside>
      )}

      {/* MIDDLE — canvas. Scrolls independently. */}
      <section className="flex-1 h-full overflow-y-auto bg-background min-w-0">
        {children}
      </section>

      {/* Floating Peblet — portal-mounted to document.body */}
      <FloatingPeblet greeting={greeting} projectContext={projectContext} />
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript**

```bash
cd ui/v3 && npx tsc --noEmit
```

Expected: no errors. The `MessageSquare`, `X`, `ChevronLeft` imports from lucide that were in the old file are gone — that's correct.

- [ ] **Step 3: Verify build**

```bash
cd ui/v3 && npm run build 2>&1 | tail -20
```

Expected: `✓ Compiled successfully` or similar. No errors about missing props or type mismatches.

- [ ] **Step 4: Commit**

```bash
git add ui/v3/components/control-center.tsx
git commit -m "feat(v3): simplify ControlCenter to 2-pane, use FloatingPeblet"
```

---

## Task 3: Community page cinematic redesign

**Files:**
- Modify: `ui/v3/app/community/page.tsx`

Three visual changes: (1) hero becomes full-bleed photo + dark overlay, (2) news ticker marquee inserted between hero and activity feed, (3) showcase becomes horizontal filmstrip. Content and data wiring are unchanged.

- [ ] **Step 1: Add Marquee import**

In `ui/v3/app/community/page.tsx`, find this line near the top:

```tsx
import { type } from "@/lib/type";
```

Add the Marquee import immediately after it:

```tsx
import { type } from "@/lib/type";
import { Marquee } from "@/components/ui/marquee";
```

- [ ] **Step 2: Replace the HERO section**

Find and replace the entire hero section. The existing hero starts with the comment `{/* HERO — bold welcome + Peblet + stats strip */}` and ends just before `{/* ACTIVITY — this week in Pebble */}`.

Replace everything from:
```tsx
              {/* HERO — bold welcome + Peblet + stats strip */}
              <section className="relative overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/15 via-violet-500/8 to-amber-500/10 p-8 md:p-12">
```

...all the way to (and including) the closing `</section>` tag before `{/* ACTIVITY */}`, with:

```tsx
              {/* HERO — full-bleed cinematic photo */}
              <section className="relative overflow-hidden rounded-3xl min-h-[420px] md:min-h-[480px] flex flex-col justify-between">
                {/* Background photo — dark creative workspace */}
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src="https://images.unsplash.com/photo-1497366216548-37526070297c?w=1600&q=80"
                  alt=""
                  aria-hidden
                  className="absolute inset-0 w-full h-full object-cover"
                />
                {/* Dark overlay */}
                <div aria-hidden className="absolute inset-0 bg-black/55" />

                {/* Text + CTAs */}
                <div className="relative z-10 px-8 md:px-16 pt-14 md:pt-20 flex flex-col md:flex-row items-center gap-8">
                  <div className="flex-1 text-center md:text-left space-y-3">
                    <p className={`${type.mono} text-xs uppercase tracking-widest text-white/70 font-bold`}>
                      Pebble Community
                    </p>
                    <h1 className={`${type.dashboard.display.l} text-white leading-tight`}>
                      You&apos;re not building alone.
                    </h1>
                    <p className={`${type.body.m} text-white/80 max-w-xl`}>
                      Every kind of builder ships here — plumbers, photographers, podcasters, parents,
                      retirees, teens. All welcome. All winning at their own pace.
                    </p>
                    <div className="pt-2 flex flex-wrap items-center gap-3 justify-center md:justify-start">
                      <Link
                        href="/community/launchpad"
                        className={`${interactions.button} inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-white text-black text-sm font-semibold hover:opacity-90`}
                      >
                        <Rocket className="w-4 h-4" /> Show your work
                      </Link>
                      <Link
                        href="/community/hire-a-partner"
                        className={`${interactions.button} inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-white/10 border border-white/30 text-white text-sm font-semibold hover:bg-white/20`}
                      >
                        Find a partner
                      </Link>
                    </div>
                  </div>
                </div>

                {/* Stats strip — frosted glass cards */}
                <div className="relative z-10 grid grid-cols-3 gap-3 px-8 md:px-16 pb-8 mt-8">
                  {liveStats.map((s) => {
                    const Icon = s.Icon;
                    return (
                      <div
                        key={s.label}
                        className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-3 md:p-4 flex items-center gap-3"
                      >
                        <span className="w-9 h-9 rounded-lg bg-white/20 text-white flex items-center justify-center shrink-0">
                          <Icon className="w-4 h-4" />
                        </span>
                        <div className="min-w-0">
                          <p className="text-lg md:text-xl font-bold text-white leading-tight">
                            {s.value}
                          </p>
                          <p className="text-[11px] uppercase tracking-widest text-white/70 leading-tight">
                            {s.label}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>
```

- [ ] **Step 3: Insert news ticker between hero and activity feed**

Find this comment (the start of the ACTIVITY section):

```tsx
              {/* ACTIVITY — this week in Pebble */}
```

Insert the ticker block immediately **before** it:

```tsx
              {/* NEWS TICKER — live community activity scrolling strip */}
              <div className="overflow-hidden -mx-6 md:-mx-8 border-y border-border bg-muted/40">
                <Marquee
                  pauseOnHover
                  className="[--duration:35s] py-3"
                  ariaLabel="Community activity ticker"
                >
                  {liveActivity.map((a) => (
                    <span key={a.id} className="shrink-0 flex items-center gap-2 px-4">
                      <span
                        className={`shrink-0 text-[10px] uppercase tracking-widest font-bold px-2 py-0.5 rounded-full border ${ACTIVITY_COLORS[a.kind]}`}
                      >
                        {ACTIVITY_LABELS[a.kind]}
                      </span>
                      <span className={`${type.body.s} text-foreground whitespace-nowrap`}>
                        {a.title}
                      </span>
                      <span className="text-muted-foreground/30 mx-2 select-none">·</span>
                    </span>
                  ))}
                </Marquee>
              </div>

```

- [ ] **Step 4: Replace the showcase grid with a filmstrip**

Find and replace the showcase grid. Look for:

```tsx
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {SHOWCASE.map((s) => (
                    <Link
                      key={s.name}
```

Replace the entire `<div className="grid ...">...</div>` block with:

```tsx
                <div className="relative">
                  {/* Scroll shadows */}
                  <div aria-hidden className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-background to-transparent z-10 pointer-events-none" />
                  <div aria-hidden className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-background to-transparent z-10 pointer-events-none" />
                  <div className="flex gap-4 overflow-x-auto [&::-webkit-scrollbar]:hidden pb-2 snap-x snap-mandatory">
                    {SHOWCASE.map((s) => (
                      <Link
                        key={`${s.name}-${s.image}`}
                        href={s.href}
                        className={`${interactions.card} group relative shrink-0 snap-start w-[280px] aspect-[14/9] rounded-xl overflow-hidden border border-border bg-card`}
                      >
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={s.image}
                          alt={`${s.name} preview`}
                          className="absolute inset-0 w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-105"
                          loading="lazy"
                        />
                        <div className="absolute inset-x-0 bottom-0 p-3 bg-gradient-to-t from-black/80 via-black/40 to-transparent">
                          <p className="text-sm font-bold text-white leading-tight">{s.name}</p>
                          <p className="text-[10px] uppercase tracking-widest text-white/70 mt-0.5">{s.kind}</p>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
```

- [ ] **Step 5: Verify TypeScript**

```bash
cd ui/v3 && npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add ui/v3/app/community/page.tsx
git commit -m "feat(v3): community page — cinematic hero, news ticker, filmstrip"
```

---

## Task 4: Templates page redesign

**Files:**
- Modify: `ui/v3/app/templates/page.tsx`

Remove the tier system (tabs, locks, Pro badges). Add an industry thumbnail ribbon. Add cinematic hover overlay to cards. Add a SubmitTemplateCard at the end. Wire FloatingPeblet (the templates page doesn't use ControlCenter, so we add it directly).

- [ ] **Step 1: Update imports**

At the top of `ui/v3/app/templates/page.tsx`, find:

```tsx
import { Sparkles, Check, X, Loader2, Eye, ExternalLink, Lock, Upload } from "lucide-react";
```

Replace with:

```tsx
import { Sparkles, Check, X, Loader2, Eye, ExternalLink, Upload } from "lucide-react";
import { FloatingPeblet } from "@/components/floating-peblet";
```

(`Lock` is removed because no locked premium cards exist anymore.)

- [ ] **Step 2: Remove TierTab type and normalizeTier**

Find and delete these two blocks entirely:

```tsx
// 2026-05-23: tier-tab model. Marc's design-night ask was three tabs —
// Free / Premium / Public — where Public is user-uploaded with a
// revenue split. The backend registry still emits some templates with
// the legacy tier="paid"; we treat that as "premium" client-side via
// `normalizeTier()` below, so the UI tabs don't depend on a backend
// rename.
type TierTab = "free" | "premium" | "public";

function normalizeTier(t: TemplateSummary["tier"]): TierTab {
  if (t === "paid" || t === "premium") return "premium";
  if (t === "public") return "public";
  return "free";
}
```

- [ ] **Step 3: Replace TemplatesPage state and derived values**

Inside `export default function TemplatesPage()`, find:

```tsx
  const [previewing, setPreviewing] = useState<TemplateSummary | null>(null);
  const [picked, setPicked] = useState<TemplateSummary | null>(null);
  const [activeTab, setActiveTab] = useState<TierTab>("free");
```

Replace with:

```tsx
  const [previewing, setPreviewing] = useState<TemplateSummary | null>(null);
  const [picked, setPicked] = useState<TemplateSummary | null>(null);
  const [activeIndustry, setActiveIndustry] = useState<string | null>(null);
```

Find and delete the entire `buckets` useMemo:

```tsx
  // Pre-bucket once per templates load so the tab counters + filtered
  // list don't recompute every keystroke.
  const buckets = useMemo(() => {
    const out: Record<TierTab, TemplateSummary[]> = { free: [], premium: [], public: [] };
    (templates ?? []).forEach((t) => out[normalizeTier(t.tier)].push(t));
    return out;
  }, [templates]);

  const visible = buckets[activeTab];
```

Replace it with:

```tsx
  // Unique sorted industry list extracted from all templates.
  const industries = useMemo(() => {
    const seen = new Set<string>();
    (templates ?? []).forEach((t) =>
      t.applicable_industries.forEach((i) => seen.add(i)),
    );
    return Array.from(seen).sort();
  }, [templates]);

  // Helper: first color_swatches array for a given industry.
  function firstSwatchForIndustry(ind: string): string[] | null {
    const t = (templates ?? []).find((x) => x.applicable_industries.includes(ind));
    return t?.color_swatches?.length ? t.color_swatches : null;
  }

  const visible = (templates ?? []).filter(
    (t) => !activeIndustry || t.applicable_industries.includes(activeIndustry),
  );
```

- [ ] **Step 4: Replace the tier-tabs JSX with the industry ribbon**

Find the entire tier-tabs block:

```tsx
        {/* Tier tabs — Free / Premium / Public. Counts reflect what's
            actually in each bucket; Public is intentionally empty today
```

...through the closing `)}` of the tabs block. It ends just before `{/* Empty states + grid per tab */}`.

Replace it with:

```tsx
        {/* Industry ribbon — horizontal scrollable filter */}
        {templates && (
          <div className="relative mb-8">
            <div aria-hidden className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-background to-transparent z-10 pointer-events-none" />
            <div aria-hidden className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-background to-transparent z-10 pointer-events-none" />
            <div className="flex gap-2 overflow-x-auto [&::-webkit-scrollbar]:hidden pb-1 px-1">
              <RibbonChip
                active={!activeIndustry}
                onClick={() => setActiveIndustry(null)}
                swatch={null}
              >
                All
              </RibbonChip>
              {industries.map((ind) => (
                <RibbonChip
                  key={ind}
                  active={activeIndustry === ind}
                  onClick={() => setActiveIndustry(ind)}
                  swatch={firstSwatchForIndustry(ind)}
                >
                  {ind}
                </RibbonChip>
              ))}
            </div>
          </div>
        )}
```

- [ ] **Step 5: Replace the empty-states + grid block**

Find and delete the following three empty-state conditional blocks (they reference `activeTab` and `buckets` which no longer exist):

```tsx
        {/* Empty states + grid per tab */}
        {templates && activeTab === "public" && buckets.public.length === 0 && (
          <PublicTabPlaceholder />
        )}

        {templates && activeTab === "premium" && buckets.premium.length === 0 && (
          ...
        )}

        {templates && activeTab === "free" && buckets.free.length === 0 && (
          ...
        )}

        {templates && visible.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {visible.map((t, i) => (
              <TemplateCard
                key={t.id}
                template={t}
                index={i}
                onClick={() => setPreviewing(t)}
              />
            ))}
          </div>
        )}
```

Replace everything from `{/* Empty states + grid per tab */}` through the closing `)}` of the grid block with:

```tsx
        {/* Template grid — filtered by active industry */}
        {templates && visible.length === 0 && (
          <div className="text-center text-muted-foreground py-16">
            <p className={type.body.m}>No templates for that industry yet.</p>
          </div>
        )}

        {templates && visible.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {visible.map((t, i) => (
              <TemplateCard
                key={t.id}
                template={t}
                index={i}
                onClick={() => setPreviewing(t)}
              />
            ))}
            {/* Submit a template CTA — always last */}
            <SubmitTemplateCard />
          </div>
        )}
```

- [ ] **Step 6: Add FloatingPeblet to the page JSX**

Find the closing tags of TemplatesPage's return — right before the final `</div>`:

```tsx
      {picked && <InstantiateDialog template={picked} onClose={() => setPicked(null)} router={router} />}
    </div>
  );
}
```

Add FloatingPeblet:

```tsx
      {picked && <InstantiateDialog template={picked} onClose={() => setPicked(null)} router={router} />}
      <FloatingPeblet greeting="Looking for a template? I can help you find the right one." />
    </div>
  );
}
```

- [ ] **Step 7: Update TemplateCard to add cinematic hover overlay**

Find inside `TemplateCard`, the `<div className="relative aspect-[4/3] w-full overflow-hidden bg-muted"` block. Inside that div, after the existing `{!showFallback && (<img ... />)}` block and before the tier badge (`{/* Tier badge — top-left. ...`), add:

```tsx
        {/* Cinematic hover overlay — reveals tagline on hover */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4 z-10">
          <p className="text-white text-sm font-medium leading-snug line-clamp-2">
            {t.tagline}
          </p>
        </div>
```

- [ ] **Step 8: Remove tier badge and lock overlay from TemplateCard**

In `TemplateCard`, find and delete these two blocks:

```tsx
        {/* Tier badge — top-left. "Pro" for premium templates so users
            read it as a plan-gate signal, not a price tag. Free stays Free. */}
        <div className={`absolute top-3 left-3 px-2.5 py-0.5 rounded-full text-xs uppercase tracking-wider z-10 ${
          normalizeTier(t.tier) === "premium"
            ? "bg-violet-600/95 text-white"
            : normalizeTier(t.tier) === "public"
              ? "bg-emerald-600/95 text-white"
              : "bg-foreground/85 text-background"
        }`}>
          {(() => {
            const tier = normalizeTier(t.tier);
            if (tier === "free") return "Free";
            if (tier === "premium") return "Pro";
            return "Public";
          })()}
        </div>
        {/* Lock overlay on premium */}
        {normalizeTier(t.tier) === "premium" && (
          <div className="absolute top-3 right-3 z-10 inline-flex items-center justify-center w-7 h-7 rounded-full bg-violet-600/95 text-white shadow-lg">
            <Lock className="w-3.5 h-3.5" aria-hidden />
          </div>
        )}
```

- [ ] **Step 9: Replace TierTabButton + PublicTabPlaceholder with RibbonChip and SubmitTemplateCard**

At the bottom of `ui/v3/app/templates/page.tsx`, find and delete both `TierTabButton` and `PublicTabPlaceholder` functions entirely (they are no longer used after the tier system was removed in the steps above). Then add these two new components in their place:

```tsx
// ------------------------------------------------------------------ //
// RibbonChip — industry filter chip with optional colour swatch       //
// ------------------------------------------------------------------ //

function RibbonChip({
  active,
  onClick,
  swatch,
  children,
}: {
  active: boolean;
  onClick: () => void;
  swatch: string[] | null;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`shrink-0 inline-flex items-center gap-2 px-3 py-2 rounded-full text-sm font-semibold transition-colors ${
        active
          ? "bg-foreground text-background"
          : "bg-card border border-border text-muted-foreground hover:text-foreground"
      }`}
    >
      {swatch && (
        <span
          className="w-5 h-4 rounded-sm shrink-0"
          style={{ background: `linear-gradient(135deg, ${swatch.slice(0, 3).join(", ")})` }}
        />
      )}
      {children}
    </button>
  );
}

// ------------------------------------------------------------------ //
// SubmitTemplateCard — "Submit a template" always-visible CTA card    //
// ------------------------------------------------------------------ //

function SubmitTemplateCard() {
  return (
    <button
      type="button"
      onClick={() =>
        window.open(
          "mailto:hello@getpebble.net?subject=Template+submission&body=Tell+us+about+your+template:+industry,+design+vibe,+link+to+a+live+demo+or+Figma+file.",
        )
      }
      className="group text-left bg-card border-2 border-dashed border-border rounded-2xl overflow-hidden hover:border-primary/60 transition-colors aspect-[4/3] flex flex-col items-center justify-center gap-3 p-6"
    >
      <Upload className="w-8 h-8 text-muted-foreground group-hover:text-primary transition-colors" />
      <p className="text-base font-bold text-foreground text-center">Submit a template</p>
      <p className="text-sm text-muted-foreground text-center leading-snug">
        Earn 30% on every install
      </p>
    </button>
  );
}
```

- [ ] **Step 10: Verify TypeScript**

```bash
cd ui/v3 && npx tsc --noEmit
```

Expected: no errors. If TypeScript complains about unused `normalizeTier` somewhere, confirm the function was fully deleted in Step 2.

- [ ] **Step 11: Commit**

```bash
git add ui/v3/app/templates/page.tsx
git commit -m "feat(v3): templates — free-all, industry ribbon, cinematic hover, FloatingPeblet"
```

---

## Task 5: MetallicPebbleLogo + Dashboard empty state

**Files:**
- Create: `ui/v3/components/metallic-pebble-logo.tsx`
- Modify: `ui/v3/app/dashboard/page.tsx`

When the user has zero projects, replace the generic placeholder with a cinematic two-column layout: animated metallic P logo + CTAs on the left, existing activity feed on the right.

- [ ] **Step 1: Create MetallicPebbleLogo**

Create `ui/v3/components/metallic-pebble-logo.tsx`:

```tsx
"use client";

/**
 * MetallicPebbleLogo — animated 3D metallic "P" for the dashboard
 * empty state. Built entirely in Framer Motion + CSS; no external asset.
 *
 * Three layers:
 *   1. Conic-gradient light rays — slow 20s rotation
 *   2. The "P" — metallic silver gradient with a floating idle animation
 *   3. Light sweep — a white stripe that crosses the P on a 2.5s loop
 */

import { motion } from "framer-motion";

export function MetallicPebbleLogo() {
  return (
    <div className="relative flex items-center justify-center w-48 h-48 mx-auto">
      {/* Light rays — conic gradient disc, slow rotation */}
      <motion.div
        className="absolute inset-0 rounded-full"
        style={{
          background:
            "conic-gradient(from 0deg, transparent 0%, rgba(255,255,255,0.07) 10%, transparent 20%, rgba(255,255,255,0.07) 30%, transparent 40%, rgba(255,255,255,0.07) 50%, transparent 60%, rgba(255,255,255,0.07) 70%, transparent 80%, rgba(255,255,255,0.07) 90%, transparent 100%)",
        }}
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
      />

      {/* Soft outer glow */}
      <div className="absolute inset-6 rounded-full bg-gradient-to-br from-foreground/5 to-transparent blur-2xl" />

      {/* The P — metallic gradient + idle float */}
      <motion.div
        className="relative z-10 select-none"
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      >
        <div className="relative overflow-hidden inline-block">
          <span
            style={{
              fontSize: "120px",
              fontWeight: 900,
              lineHeight: 1,
              background:
                "linear-gradient(135deg, #888 0%, #ccc 25%, #fff 50%, #ccc 75%, #888 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
              filter: "drop-shadow(0 4px 24px rgba(0,0,0,0.12))",
              fontFamily: "var(--font-display, Georgia, serif)",
            }}
          >
            P
          </span>
          {/* Animated shine sweep — white stripe crosses the P every ~4s */}
          <motion.div
            className="absolute inset-0 pointer-events-none"
            style={{
              background:
                "linear-gradient(105deg, transparent 35%, rgba(255,255,255,0.55) 50%, transparent 65%)",
            }}
            animate={{ x: ["-120%", "220%"] }}
            transition={{
              duration: 1.2,
              repeat: Infinity,
              repeatDelay: 2.8,
              ease: "easeInOut",
            }}
          />
        </div>
      </motion.div>
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd ui/v3 && npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 3: Add MetallicPebbleLogo import to dashboard**

In `ui/v3/app/dashboard/page.tsx`, find the existing imports block. Add:

```tsx
import { MetallicPebbleLogo } from "@/components/metallic-pebble-logo";
```

Place it near the other component imports (alongside `PebletMascot`, `NotificationBell`, etc.).

- [ ] **Step 4: Insert CinematicEmptyState before the project grid**

In `ui/v3/app/dashboard/page.tsx`, find:

```tsx
          {loading && (
            <div className="text-center py-20 text-muted-foreground">Loading…</div>
          )}

          {!loading && visible.length === 0 && (
            <EmptyState filter={filter} query={query} />
          )}
```

Replace with:

```tsx
          {loading && (
            <div className="text-center py-20 text-muted-foreground">Loading…</div>
          )}

          {/* Cinematic empty state — shown only when the user has zero
              projects (not just an empty filter result). Two-column:
              MetallicP + CTAs on the left, activity feed on the right. */}
          {!loading && projects.length === 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-8 items-start py-8">
              {/* Left: animated logo + CTAs */}
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
                  <Link
                    href="/templates"
                    className={`${interactions.button} px-6 py-3 rounded-full bg-foreground text-background font-semibold hover:opacity-90 transition-opacity`}
                  >
                    Start from a template
                  </Link>
                  <Link
                    href="/workspace#phase=welcome"
                    className={`${interactions.button} px-6 py-3 rounded-full bg-card border border-border text-foreground font-semibold hover:bg-accent transition-colors`}
                  >
                    Build from a brief
                  </Link>
                </div>
              </div>

              {/* Right: activity feed — always shown even on empty state */}
              {activity.length > 0 && (
                <ActivityFeed
                  activity={activity}
                  onOpenProject={(slug) => {
                    const p = projects.find((x) => x.slug === slug);
                    if (p) openProject(p);
                  }}
                  onRestore={handleRestoreFromActivity}
                />
              )}
            </div>
          )}

          {/* Filter/search empty state — only when projects exist but
              the current filter shows nothing. */}
          {!loading && projects.length > 0 && visible.length === 0 && (
            <EmptyState filter={filter} query={query} />
          )}
```

- [ ] **Step 5: Verify TypeScript**

```bash
cd ui/v3 && npx tsc --noEmit
```

Expected: no errors. If TypeScript can't find `ActivityFeed` check that the component is defined lower in the file (it was already there — scroll to the bottom of `dashboard/page.tsx` to confirm).

- [ ] **Step 6: Full build verification**

```bash
cd ui/v3 && npm run build 2>&1 | tail -30
```

Expected: `✓ Compiled successfully`. No type errors, no missing imports.

- [ ] **Step 7: Commit**

```bash
git add ui/v3/components/metallic-pebble-logo.tsx ui/v3/app/dashboard/page.tsx
git commit -m "feat(v3): dashboard cinematic empty state — metallic P logo + 2-col layout"
```

---

## Final verification

After all 5 tasks commit:

```bash
cd ui/v3 && npm run build 2>&1 | tail -20
```

Expected: clean build. Then push:

```bash
git push origin HEAD
git push pebblewebsite HEAD:main
```
