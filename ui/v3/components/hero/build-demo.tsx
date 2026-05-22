"use client";

/**
 * BuildDemo — Phase 43.2 (2026-05-21).
 *
 * Code-driven faux build animation for §2 "From sentence to site."
 * Replaces the old SwiperSteps (text-only cards) with a single
 * always-on visual that loops through the three stages of a Pebble
 * build, end-to-end, in ~12 seconds:
 *
 *   TYPE  (0 → 3.5s):  search bar types out the user's sentence
 *   PLAN  (3.5 → 7s):  Pebble Plan card materializes with 4 rows
 *   SITE  (7 → 11s):   mock browser shows a finished bakery site
 *   HOLD  (11 → 12s):  brief dwell on the final state before looping
 *
 * Pebble pitch: in 30 seconds of scrolling, the user sees the entire
 * product narrative play out. No reading required.
 *
 * Why fake instead of a real screen recording (Marc's choice — phase
 * 43 plan): code-driven means infinitely tweakable, mobile-friendly,
 * no asset pipeline. When we eventually have a clean real recording
 * we can swap this for a <video> with the same shell.
 */

import React from "react";
import {
  motion,
  AnimatePresence,
  useReducedMotion,
  type Transition,
} from "framer-motion";
import { Globe, Lock, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

/* ----------------------------- timing ---------------------------------- */
const TYPE_MS  = 3500;
const PLAN_MS  = 3500;
const SITE_MS  = 4000;
const HOLD_MS  = 1000;
const TOTAL_MS = TYPE_MS + PLAN_MS + SITE_MS + HOLD_MS; // 12_000

type Phase = "type" | "plan" | "site";

const EASE = [0.22, 1, 0.36, 1] as const;
const EXIT: Transition = { duration: 0.35, ease: EASE };

/* ----------------------------- copy ------------------------------------ */
const TYPED_PROMPT = "Hey Pebble! Build a bakery in Brooklyn";

const PLAN_ROWS: { label: string; value: string }[] = [
  { label: "Business",    value: "Bakery · Brooklyn"     },
  { label: "Style DNA",   value: "Garden Press"          },
  { label: "Pages",       value: "Home · Menu · About"   },
  { label: "Setup",       value: "Domain · Email · Forms"},
];

const SITE_HERO_IMG = "/hero-craft/baker.jpg";

/* =====================================================================
   Sub-scenes
   ===================================================================== */

/** TYPE scene — search bar with the prompt typing in. */
function TypeScene({ prefersReduced }: { prefersReduced: boolean }) {
  const [chars, setChars] = React.useState(prefersReduced ? TYPED_PROMPT.length : 0);
  React.useEffect(() => {
    if (prefersReduced) { setChars(TYPED_PROMPT.length); return; }
    // Type the whole sentence within TYPE_MS, leaving 600ms of dwell
    // for the cursor to blink on the finished phrase.
    const typeWindow = TYPE_MS - 600;
    const perChar    = Math.floor(typeWindow / TYPED_PROMPT.length);
    let i = 0;
    const id = window.setInterval(() => {
      i += 1;
      setChars(i);
      if (i >= TYPED_PROMPT.length) window.clearInterval(id);
    }, perChar);
    return () => window.clearInterval(id);
  }, [prefersReduced]);

  return (
    <motion.div
      key="type"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12, transition: EXIT }}
      transition={{ duration: 0.5, ease: EASE }}
      className="w-full max-w-xl mx-auto"
    >
      <div className="rounded-2xl bg-white border border-border shadow-[0_12px_36px_rgba(31,29,26,0.08)] px-5 py-5 sm:px-6 sm:py-6">
        <div className="flex items-center gap-3">
          <Sparkles className="w-5 h-5 text-[#3054ff] shrink-0" aria-hidden />
          <div className="flex-1 min-w-0 text-base sm:text-lg text-foreground font-medium leading-snug">
            {TYPED_PROMPT.slice(0, chars)}
            <span
              className={cn(
                "inline-block w-[2px] h-5 sm:h-6 ml-0.5 bg-foreground align-middle",
                !prefersReduced && "animate-pulse",
              )}
              aria-hidden
            />
          </div>
        </div>
        <div className="mt-4 pl-8 text-xs text-muted-foreground">
          URL · industry · or plain English. Pebble figures it out.
        </div>
      </div>
    </motion.div>
  );
}

/** PLAN scene — fake "Pebble Plan" card with 4 rows materializing. */
function PlanScene() {
  return (
    <motion.div
      key="plan"
      initial={{ opacity: 0, y: 18, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -18, scale: 0.96, transition: EXIT }}
      transition={{ duration: 0.55, ease: EASE }}
      className="w-full max-w-xl mx-auto"
    >
      <div className="rounded-2xl bg-white border border-border shadow-[0_12px_36px_rgba(31,29,26,0.08)] overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 sm:px-6 sm:py-4 border-b border-border bg-gradient-to-r from-[#eef2ff] to-white">
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase tracking-[0.14em] font-semibold text-[#3054ff]">Pebble Plan</span>
          </div>
          <span className="text-[10px] text-muted-foreground">preview · no credit spent</span>
        </div>
        <ul className="divide-y divide-border">
          {PLAN_ROWS.map((row, i) => (
            <motion.li
              key={row.label}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.25 + i * 0.32, duration: 0.4, ease: EASE }}
              className="flex items-center justify-between px-5 py-3 sm:px-6 sm:py-3.5 text-sm"
            >
              <span className="text-muted-foreground">{row.label}</span>
              <span className="text-foreground font-medium">{row.value}</span>
            </motion.li>
          ))}
        </ul>
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.6, duration: 0.35, ease: EASE }}
          className="flex items-center justify-end gap-2 px-5 py-3 sm:px-6 sm:py-3.5 bg-muted/40"
        >
          <span className="text-xs text-muted-foreground">Looks good →</span>
          <span className="inline-flex items-center justify-center rounded-full px-3 py-1 text-xs font-semibold bg-foreground text-background">
            Build it
          </span>
        </motion.div>
      </div>
    </motion.div>
  );
}

/** SITE scene — mock browser showing a finished bakery site. */
function SiteScene() {
  return (
    <motion.div
      key="site"
      initial={{ opacity: 0, y: 24, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -16, scale: 0.96, transition: EXIT }}
      transition={{ duration: 0.6, ease: EASE }}
      className="w-full max-w-2xl mx-auto"
    >
      <div className="rounded-2xl bg-white border border-border shadow-[0_18px_44px_rgba(31,29,26,0.14)] overflow-hidden">
        {/* Browser chrome */}
        <div className="flex items-center gap-2 px-4 py-2.5 border-b border-border bg-muted/60">
          <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f57]" aria-hidden />
          <span className="w-2.5 h-2.5 rounded-full bg-[#febc2e]" aria-hidden />
          <span className="w-2.5 h-2.5 rounded-full bg-[#28c840]" aria-hidden />
          <div className="ml-3 flex items-center gap-2 flex-1 min-w-0 rounded-md bg-white border border-border px-3 py-1 text-xs text-muted-foreground">
            <Lock className="w-3 h-3 text-foreground/60 shrink-0" aria-hidden />
            <span className="truncate">brooklyn-flour-co.pebble.app</span>
            <Globe className="w-3 h-3 text-foreground/40 shrink-0 ml-auto" aria-hidden />
          </div>
        </div>
        {/* Site body */}
        <div className="relative">
          {/* Hero photo */}
          <motion.div
            initial={{ opacity: 0, scale: 1.08 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: EASE }}
            className="w-full h-44 sm:h-56 bg-muted bg-cover bg-center"
            style={{ backgroundImage: `url(${SITE_HERO_IMG})` }}
            aria-hidden
          />
          {/* Hero overlay copy — cascades in */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent flex flex-col justify-end p-5 sm:p-6 space-y-2">
            <motion.span
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.4, ease: EASE }}
              className="text-[10px] uppercase tracking-[0.18em] font-semibold text-white/90"
            >
              Brooklyn · since today
            </motion.span>
            <motion.h3
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7, duration: 0.45, ease: EASE }}
              className="text-2xl sm:text-3xl font-bold text-white leading-tight"
            >
              Brooklyn Flour Co.
            </motion.h3>
            <motion.p
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.95, duration: 0.4, ease: EASE }}
              className="text-sm text-white/85 max-w-md"
            >
              Real sourdough. Real butter. Pick up before 11 or you&apos;ll miss it.
            </motion.p>
          </div>
        </div>
        {/* Mini "page nav" + CTA row */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.4, ease: EASE }}
          className="flex items-center justify-between px-5 py-3 border-t border-border bg-white"
        >
          <div className="flex items-center gap-4 text-xs text-foreground/70">
            <span className="font-semibold text-foreground">Home</span>
            <span>Menu</span>
            <span>About</span>
          </div>
          <span className="inline-flex items-center rounded-full bg-foreground text-background text-xs font-semibold px-3 py-1">
            Order pickup
          </span>
        </motion.div>
      </div>
    </motion.div>
  );
}

/* =====================================================================
   Main loop
   ===================================================================== */

/** Convert elapsed-ms within the 12s cycle into the active scene. */
function phaseAt(elapsed: number): Phase {
  if (elapsed < TYPE_MS)                     return "type";
  if (elapsed < TYPE_MS + PLAN_MS)           return "plan";
  if (elapsed < TYPE_MS + PLAN_MS + SITE_MS + HOLD_MS) return "site";
  return "type";
}

/** Discrete "stage chip" label shown above the panel — also doubles as a
    progress indicator (3 chips, the active one is filled). */
function StageChips({ phase }: { phase: Phase }) {
  const order: Phase[] = ["type", "plan", "site"];
  const labels: Record<Phase, string> = {
    type: "1 · Tell Pebble",
    plan: "2 · Review plan",
    site: "3 · Site is live",
  };
  return (
    <div className="flex items-center justify-center gap-2 sm:gap-3">
      {order.map((p) => {
        const active = p === phase;
        return (
          <div
            key={p}
            className={cn(
              "inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] sm:text-xs font-medium",
              "transition-colors duration-300",
              active
                ? "bg-foreground text-background"
                : "bg-muted/60 text-muted-foreground",
            )}
          >
            <span
              className={cn(
                "inline-block w-1.5 h-1.5 rounded-full transition-colors duration-300",
                active ? "bg-[#3054ff]" : "bg-muted-foreground/40",
              )}
              aria-hidden
            />
            {labels[p]}
          </div>
        );
      })}
    </div>
  );
}

export interface BuildDemoProps {
  className?: string;
}

export function BuildDemo({ className = "" }: BuildDemoProps) {
  const prefersReduced = useReducedMotion() ?? false;
  const [phase, setPhase]       = React.useState<Phase>("type");
  const [active, setActive]     = React.useState(true);
  const containerRef            = React.useRef<HTMLDivElement>(null);

  // Pause the loop when the demo is offscreen — saves cycles on long
  // pages where the user might never see it, and resumes from the
  // beginning when it re-enters view (the loop feels off if it picks up
  // mid-scene with no context).
  React.useEffect(() => {
    if (typeof window === "undefined" || !containerRef.current) return;
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) setActive(e.isIntersecting);
      },
      { threshold: 0.2 },
    );
    io.observe(containerRef.current);
    return () => io.disconnect();
  }, []);

  // Drive the loop. With reduced-motion on, just sit on the SITE scene
  // (the final / most meaningful frame); no looping animation.
  React.useEffect(() => {
    if (prefersReduced) { setPhase("site"); return; }
    if (!active) return;
    let start = performance.now();
    let raf = 0;
    const tick = (now: number) => {
      const elapsed = (now - start) % TOTAL_MS;
      const next = phaseAt(elapsed);
      setPhase((cur) => (cur === next ? cur : next));
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [active, prefersReduced]);

  return (
    <div ref={containerRef} className={cn("flex flex-col gap-6 sm:gap-8 items-center", className)}>
      <StageChips phase={phase} />

      {/* Stage frame — single panel that morphs through the 3 scenes.
          The phase-tinted background wash is deliberately subtle —
          atmosphere, not decoration. */}
      <div className="relative w-full">
        <div
          aria-hidden
          className={cn(
            "absolute inset-0 -m-6 sm:-m-10 rounded-[2rem] blur-3xl transition-colors duration-700",
            phase === "type" && "bg-[#eaf0ff]/55",
            phase === "plan" && "bg-[#eaf0ff]/75",
            phase === "site" && "bg-[#f5d5b8]/45",
          )}
        />
        <div className="relative min-h-[280px] sm:min-h-[340px] flex items-center justify-center">
          <AnimatePresence mode="wait">
            {phase === "type" && <TypeScene prefersReduced={prefersReduced} />}
            {phase === "plan" && <PlanScene />}
            {phase === "site" && <SiteScene />}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

export default BuildDemo;
