"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Palette,
  Edit3,
  Image as ImageIcon,
  CheckSquare,
  CheckCircle2,
  AlertCircle,
  Circle,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  type LucideIcon,
} from "lucide-react";
import { type SSEEvent, fetchBotMessage } from "@/lib/api";
import { fadeUp, MICRO_S, SHORT_S, STANDARD_S, SLOW_S, EASE_CINEMATIC, withReducedMotion } from "@/lib/motion";
import { type } from "@/lib/type";
import { BuildChatPanel, type CollectedAnswer } from "./build-chat";

/**
 * Draft phase — "Pebble is building your draft."
 *
 * Shell-driven: the workspace shell owns the /api/generate-stream call.
 * This phase animates real progress events from the engine's SSE stream.
 * Three layers of feedback:
 *
 * 1. Pebble droplet logo with a smooth scale pulse (no rotate — rotating
 *    a glyph by small angles causes sub-pixel jitter that reads as
 *    "stuttering" even though Framer is hitting 60fps).
 * 2. The 6-step macro checklist (industry → style → pages → photos →
 *    checks → ready). Advances on real SSE events from the engine.
 * 3. The live build feed — log lines derived from real SSE events so
 *    the user sees actual engine milestones (industry resolved, DNA
 *    selected, LLM call started, files written) rather than a fake timer.
 */

type ThinkingStep = {
  id: string;
  Icon: LucideIcon;
  label: string;
  detail: string;
};

/** Format elapsed seconds as "0:42" / "2:15" — same shape as a stopwatch. */
function formatElapsed(sec: number): string {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

/** Build-specific "did you know?" facts. Each receives the build context
 *  pulled from SSE events and returns a one-line message. Returns null
 *  if the fact needs data we don't yet have — caller filters those out
 *  so the rotation stays smooth. */
type BuildCtx = { dna?: string; layout?: string; model?: string; industry?: string };
const FACTS: Array<(c: BuildCtx) => string | null> = [
  (c) => c.dna ? `Pebble picked ${c.dna} for your visual personality — one of 13 hand-tuned styles.` : null,
  (c) => c.layout ? `Your structural shape is ${c.layout} — selected from 10 architecture options.` : null,
  (c) => c.industry ? `Using a hand-written reference brief for ${c.industry} businesses to ground the copy.` : null,
  (c) => c.model ? `Writing your copy with ${c.model.replace("claude-", "Claude ").replace("gemini-", "Gemini ")} — prompt caching keeps cost down.` : null,
  () => `Every site Pebble builds is a real Next.js project. Every line of code is yours.`,
  () => `Pebble runs 32 quality checks before you see the draft.`,
  () => `Stock photos shown are placeholders — swap them with your own in one click.`,
  () => `Your site is mobile-ready by default. We test every layout at 375px before shipping.`,
  () => `You'll own your domain, your code, and your customer list. No vendor lock-in.`,
  () => `The whole site loads on a 3G connection in under 2 seconds.`,
];

/**
 * humanizeBuildEvent — translate the engine's raw file-path SSE events into
 * customer-readable build-feed lines.
 *
 * Marc's feedback 2026-05-23: "A non-technical bookstore owner has no idea
 * what `components/ui/AnimatedHeading.tsx` means." So instead of streaming
 * file paths into the live feed, we map them to friendly verbs that describe
 * what Pebble is actually doing right now ("Drawing your hero section…").
 *
 * Coverage:
 *  - All foundation components (ui/, layout/, sections/, forms/)
 *  - All page routes (homepage + named industry pages)
 *  - Config files (next.config, tailwind, postcss, package.json, etc.)
 *  - Server actions + lib helpers
 *  - Sensible fallback for anything unmapped (uses the file basename)
 *
 * Returns a string starting with a leading "+ " so the existing tone styling
 * (green check) reads naturally in the live feed.
 */
function humanizeBuildEvent(fpath: string): string {
  // Page routes — homepage gets a special label; named pages get title-cased.
  if (fpath === "app/page.tsx") return "+ Building the homepage";
  const pageMatch = fpath.match(/^app\/([^/]+)\/page\.tsx$/);
  if (pageMatch) {
    const name = pageMatch[1]
      .replace(/-/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase());
    return `+ Adding the ${name} page`;
  }

  // Exact-match lookup for the foundation files. Anything not in this map
  // falls through to the regex section / basename fallback below.
  const exact: Record<string, string> = {
    // Sections — the most user-facing
    "components/sections/Hero.tsx":         "+ Drawing your hero section",
    "components/sections/TrustBar.tsx":     "+ Adding trust signals",
    "components/sections/Services.tsx":     "+ Listing your services",
    "components/sections/SocialProof.tsx":  "+ Adding customer proof",
    "components/sections/Testimonials.tsx": "+ Pulling in testimonials",
    "components/sections/Pricing.tsx":      "+ Setting up pricing",
    "components/sections/FAQ.tsx":          "+ Writing the FAQ",
    "components/sections/Stats.tsx":        "+ Adding stats strip",
    "components/sections/CTA.tsx":          "+ Adding the call-to-action",
    "components/sections/Features.tsx":     "+ Listing features",
    "components/sections/Gallery.tsx":      "+ Adding the gallery",
    "components/sections/Booking.tsx":      "+ Wiring up booking",
    // Layout
    "components/layout/Navbar.tsx":         "+ Building the navigation",
    "components/layout/Footer.tsx":         "+ Building the footer",
    // UI primitives
    "components/ui/AnimatedHeading.tsx":    "+ Animating the headline",
    "components/ui/FadeIn.tsx":             "+ Adding fade animations",
    "components/ui/ScrollReveal.tsx":       "+ Wiring scroll reveals",
    "components/ui/GlassCard.tsx":          "+ Adding glass-effect cards",
    "components/ui/MagneticButton.tsx":     "+ Adding interactive buttons",
    "components/ui/SectionHeader.tsx":      "+ Styling section headers",
    "components/ui/GrainOverlay.tsx":       "+ Applying texture",
    // Forms
    "components/forms/ContactForm.tsx":     "+ Wiring the contact form",
    // App shell + style
    "app/layout.tsx":                       "+ Setting up the page shell",
    "app/globals.css":                      "+ Setting up styles",
    "app/sitemap.ts":                       "+ Building the SEO sitemap",
    "app/robots.ts":                        "+ Setting search-engine rules",
    "app/icon.svg":                         "+ Drawing the favicon",
    "app/actions/contact.ts":               "+ Wiring the contact form logic",
    // Lib helpers
    "lib/utils.ts":                         "+ Adding helper utilities",
    "lib/email.ts":                         "+ Wiring the email service",
    "lib/motion.ts":                        "+ Setting up animations",
    // Config / brand
    "config/brand.config.ts":               "+ Recording your brand settings",
    "config/motion.config.ts":              "+ Configuring motion preferences",
    "tailwind.config.ts":                   "+ Configuring the design system",
    "next.config.mjs":                      "+ Configuring Next.js",
    "postcss.config.mjs":                   "+ Configuring CSS pipeline",
    "tsconfig.json":                        "+ Configuring TypeScript",
    "package.json":                         "+ Listing dependencies",
    ".env.example":                         "+ Documenting environment variables",
    "vercel.json":                          "+ Configuring Vercel deployment",
    "README.md":                            "+ Writing the README",
    ".gitignore":                           "+ Configuring git",
  };
  if (exact[fpath]) return exact[fpath];

  // Generic section / layout / ui buckets for files we didn't pre-map
  if (fpath.startsWith("components/sections/")) {
    const name = fpath.replace(/^components\/sections\//, "").replace(/\.tsx?$/, "");
    return `+ Adding the ${name} section`;
  }
  if (fpath.startsWith("components/layout/")) {
    const name = fpath.replace(/^components\/layout\//, "").replace(/\.tsx?$/, "");
    return `+ Building the ${name.toLowerCase()}`;
  }
  if (fpath.startsWith("components/ui/")) {
    const name = fpath.replace(/^components\/ui\//, "").replace(/\.tsx?$/, "");
    return `+ Adding ${name}`;
  }
  if (fpath.startsWith("app/actions/")) {
    return `+ Wiring the server action`;
  }

  // Fallback: just show the file basename without the path noise.
  const base = fpath.split("/").pop() || fpath;
  return `+ ${base}`;
}


const STEPS: ThinkingStep[] = [
  { id: "industry", Icon: Search,       label: "Reading your industry",  detail: "Looking up what websites for your type of business usually include." },
  { id: "style",    Icon: Palette,      label: "Choosing a style",       detail: "Picking a visual style that matches the feeling you chose." },
  { id: "pages",    Icon: Edit3,        label: "Writing the pages",      detail: "Drafting the pages your industry typically needs." },
  { id: "photos",   Icon: ImageIcon,    label: "Finding photos",         detail: "Pulling stock photos that match your industry." },
  { id: "checks",   Icon: CheckSquare,  label: "Checking my work",       detail: "Running 32 quality checks before you see the draft." },
  { id: "ready",    Icon: CheckCircle2, label: "Ready to show you",      detail: "All set. Let's review." },
];

type Props = {
  /** When set, the phase has already encountered an error from the parent
   *  shell. Lets the shell hand back the error string for display. */
  error?: string | null;
  /** True once the shell has resolved the promise — pin the timeline to
   *  the final "Ready" step. Reset to false on re-entry. */
  done?: boolean;
  /** SSE events streamed from /api/generate-stream. When provided, the
   *  build feed and checklist advance from real engine milestones instead
   *  of the scripted fallback animation. */
  sseEvents?: SSEEvent[];
  /** Called when the user clicks "Try again" in the error banner.
   *  Shell wires this to handleGenerate for a clean retry. */
  onRetry?: () => void;
  /** Called with collected chat answers when the build finishes (or right
   *  away with [] if no answers). Shell fires enrichContent in the bg. */
  onEnrich?: (answers: CollectedAnswer[]) => void;
};

type LogLine = { ts: string; text: string; tone: "info" | "ok" | "step" };

export function DraftPhase({ error, done, sseEvents, onRetry, onEnrich }: Props) {
  const [activeIdx, setActiveIdx] = useState(0);
  const [logLines, setLogLines] = useState<LogLine[]>([]);
  const [readyPulsing, setReadyPulsing] = useState(false);
  const [elapsedSec, setElapsedSec] = useState(0);
  const [factIdx, setFactIdx] = useState(0);
  const [buildContext, setBuildContext] = useState<{ dna?: string; layout?: string; model?: string; industry?: string }>({});
  // Phase A.5: preview_ready event surfaces a URL the user can open
  // BEFORE the build finishes — homepage is on disk, inner pages still
  // streaming in. Engine emits this once per build.
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewReadyAt, setPreviewReadyAt] = useState<number | null>(null);
  // Collapsible live build feed — expanded by default; user can collapse
  // if they don't want to read the event stream.
  const [feedOpen, setFeedOpen] = useState(true);
  // Phase 25a (2026-05-20) — Plan Reveal state. Webild-parity move: each
  // piece animates in as its SSE event arrives, so the user sees the
  // bot's plan unfolding in the first 10-15 seconds instead of a blank
  // wait. Project name from `started`, palette from `style`, page list
  // from `plan`, pagesShipped derived from `file` events.
  const [planName, setPlanName] = useState<string | null>(null);
  const [palette, setPalette] = useState<string[]>([]);
  const [pages, setPages] = useState<Array<{ id: string; title: string; route: string; foundation: boolean }>>([]);
  const [pagesShipped, setPagesShipped] = useState<Set<string>>(new Set());
  // Phase 25c (2026-05-20) — bot greeting. Fetched once on the `started`
  // SSE event from /api/bot-message via cheap GPT-4o-mini. Replaces the
  // static "Hang out while Pebble builds…" headline with a warm,
  // business-specific welcome. Fallback to static copy until the LLM
  // call lands (or if it fails — endpoint returns canned text so the
  // UI never breaks).
  const [botGreeting, setBotGreeting] = useState<string | null>(null);
  const botGreetingFetchedRef = useRef(false);
  const feedRef = useRef<HTMLDivElement>(null);
  const startTsRef = useRef<number>(Date.now());
  const notifiedRef = useRef(false);

  const safeFadeUp = useMemo(() => withReducedMotion(fadeUp), []);

  // Elapsed-time ticker. Increments once per second from mount until `done`
  // or `error` fires. Lets the user see at-a-glance how long they've been
  // waiting — also feeds the soft estimate ("~90s left").
  useEffect(() => {
    startTsRef.current = Date.now();
    const id = setInterval(() => {
      setElapsedSec(Math.floor((Date.now() - startTsRef.current) / 1000));
    }, 1000);
    return () => clearInterval(id);
  }, []);

  // Tab title — shows status from another tab so the user can keep
  // working elsewhere and see when the build is done. Resets on unmount
  // so other phases get the default Pebble title back.
  useEffect(() => {
    if (typeof document === "undefined") return;
    const original = document.title;
    if (done) {
      document.title = "✓ Your site is ready — Pebble";
    } else if (error) {
      document.title = "⚠ Build needs attention — Pebble";
    } else {
      const tick = elapsedSec % 4;
      const dots = ".".repeat(tick === 0 ? 0 : tick);
      document.title = `Pebble is building${dots}`;
    }
    return () => {
      document.title = original;
    };
  }, [done, error, elapsedSec]);

  // Browser notification — asked-for once when the user lands on draft
  // (so they can switch tabs immediately), fired when `done` flips true.
  // Silent failure if the user denies permission; the in-page UI still
  // works. We only fire if the tab is HIDDEN — no point pinging a user
  // who's already looking at the page.
  useEffect(() => {
    if (typeof window === "undefined" || !("Notification" in window)) return;
    if (Notification.permission === "default") {
      Notification.requestPermission().catch(() => { /* user dismissed; fine. */ });
    }
  }, []);

  useEffect(() => {
    if (!done || notifiedRef.current) return;
    notifiedRef.current = true;
    if (typeof window === "undefined" || !("Notification" in window)) return;
    if (Notification.permission !== "granted") return;
    if (!document.hidden) return; // user is already looking — skip
    try {
      new Notification("Your Pebble site is ready", {
        body: "Click to come back and see your draft.",
        icon: "/favicon.ico",
        tag: "pebble-build-done",
      });
    } catch {
      /* notification creation can throw on some browsers — silent ok */
    }
  }, [done]);

  // Rotate the "Did you know?" facts every 7 seconds so a user staring
  // at the page during the wait gets fresh micro-content instead of one
  // stale line. Pauses on `done` so the last fact stays visible.
  useEffect(() => {
    if (done || error) return;
    const id = setInterval(() => setFactIdx((i) => i + 1), 7000);
    return () => clearInterval(id);
  }, [done, error]);

  // Auto-scroll the build feed when new lines arrive.
  //
  // Two design choices:
  //   1. behavior: "auto" (instant), not "smooth". A multi-page build
  //      fires 50+ SSE events in seconds; smooth-scrolling each one
  //      queues animations that stack up, the panel gets stuck mid-
  //      animation, and user-initiated scrolls get stomped.
  //   2. Pin-to-bottom only: if the user has scrolled UP to read an
  //      earlier line, don't snap them back to the bottom on every new
  //      event. We treat "within 80px of bottom" as still pinned (so
  //      the tiny gap from a chip-row layout shift doesn't bail).
  useEffect(() => {
    const el = feedRef.current;
    if (!el) return;
    const slack = 80; // px from bottom that still counts as pinned
    const pinned = el.scrollHeight - el.scrollTop - el.clientHeight < slack;
    if (pinned) {
      el.scrollTo({ top: el.scrollHeight, behavior: "auto" });
    }
  }, [logLines]);

  // SSE-driven build feed — map engine events to log lines and step advances.
  useEffect(() => {
    if (!sseEvents || sseEvents.length === 0) return;
    const latest = sseEvents[sseEvents.length - 1];

    const appendLog = (text: string, tone: LogLine["tone"]) =>
      setLogLines((prev) => [...prev, { ts: new Date().toLocaleTimeString(), text, tone }]);

    // Engine event names → human-readable build feed lines. Keeps the
    // terminal-style feed (Marc loves it) but the COPY reads like a
    // person describing their work, not raw event keys.
    switch (latest.type) {
      case "started":
        appendLog(`Starting your build…`, "step");
        // Phase 25a — project name pops into the Plan Reveal card the
        // moment we submit, before anything else renders. The single
        // biggest perceived-speed cue.
        if (latest.data.business_name) {
          setPlanName(String(latest.data.business_name));
        }
        // Phase 25c — fetch a warm bot greeting from /api/bot-message
        // ONCE per build. Fires-and-forgets; fallback already in state.
        if (latest.data.business_name && !botGreetingFetchedRef.current) {
          botGreetingFetchedRef.current = true;
          const bn = String(latest.data.business_name);
          const bt = ""; // business_type isn't in `started`; UI still works without it
          fetchBotMessage("greeting", { business_name: bn, business_type: bt })
            .then((res) => {
              if (res && res.message) setBotGreeting(res.message);
            })
            .catch(() => { /* silent — fallback copy stays */ });
        }
        setActiveIdx(0);
        break;
      case "industry":
        appendLog(
          latest.data.key
            ? `Reading the playbook for ${String(latest.data.key).replace(/_/g, " ")}.`
            : `Reading the playbook for your industry.`,
          "ok",
        );
        if (latest.data.key) {
          setBuildContext((c) => ({ ...c, industry: String(latest.data.key).replace(/_/g, " ") }));
        }
        setActiveIdx(1);
        break;
      case "layout":
        if (latest.data.layout_label) {
          appendLog(`Picked your structural style: ${latest.data.layout_label}.`, "ok");
          setBuildContext((c) => ({ ...c, layout: String(latest.data.layout_label) }));
        }
        setActiveIdx(1);
        break;
      case "style":
        if (latest.data.dna_label) {
          appendLog(`Locked in the visual personality: ${latest.data.dna_label}.`, "ok");
          setBuildContext((c) => ({ ...c, dna: String(latest.data.dna_label) }));
        } else {
          appendLog(`Locked in the visual personality.`, "ok");
        }
        // Phase 25a — palette swatches paint into the Plan Reveal card.
        if (Array.isArray(latest.data.palette) && latest.data.palette.length > 0) {
          setPalette((latest.data.palette as unknown[]).map(String));
        }
        setActiveIdx(1);
        break;
      case "plan":
        // Phase 25a — the engine emits this right after plan.json is
        // written, BEFORE the long LLM call. Drives the site-structure
        // checklist in the Plan Reveal card.
        if (Array.isArray(latest.data.pages)) {
          setPages(latest.data.pages as Array<{ id: string; title: string; route: string; foundation: boolean }>);
        }
        if (latest.data.name && !planName) {
          setPlanName(String(latest.data.name));
        }
        break;
      case "generating":
        appendLog(`Writing your site — copy, layout, sections, code.`, "step");
        if (latest.data.model) setBuildContext((c) => ({ ...c, model: String(latest.data.model) }));
        setActiveIdx(2);
        break;
      case "file":
        // Phase 13a — streaming live feed. Each <pebble-file> block
        // emits one event as it finishes streaming in from the LLM.
        // Shows the user real-time file generation instead of a 2-10
        // minute blank wait. Keep activeIdx at 2 ("Writing pages") —
        // we're still in that phase.
        if (latest.data.name) {
          const fpath = String(latest.data.name);
          // 2026-05-23: humanize the file path so non-technical owners can
          // follow along. Maps `components/ui/AnimatedHeading.tsx` to
          // "Animating the headline" etc. See humanizeBuildEvent above.
          appendLog(humanizeBuildEvent(fpath), "ok");
          // Phase 25a — checkmark a page in the Plan Reveal site-structure
          // list as soon as its file lands. Patterns: `app/page.tsx` is
          // the homepage; `app/<route>/page.tsx` is the named page.
          let shippedId: string | null = null;
          if (fpath === "app/page.tsx") {
            shippedId = "homepage";
          } else {
            const m = fpath.match(/^app\/([^/]+)\/page\.tsx$/);
            if (m) shippedId = m[1];
          }
          if (shippedId) {
            const id = shippedId;
            setPagesShipped((prev) => {
              if (prev.has(id)) return prev;
              const next = new Set(prev);
              next.add(id);
              return next;
            });
          }
        }
        break;
      case "heartbeat":
        // Phase 15e — silent. Server-side keep-alive that resets the
        // SSE outer timeout during slow LLM warm-up. We don't surface
        // it in the live feed because it would clutter the UX, but the
        // data IS useful for debugging (paste into devtools network
        // tab to see streaming throughput).
        break;
      case "preview_ready":
        // Phase A.5 — foundation files are on disk. User can open the
        // preview NOW even though inner pages are still streaming in.
        // This is the killer UX move: ~60-90s to clickable preview vs
        // 8-10 min of blind waiting. Fire ONCE per build.
        if (latest.data.url && !previewUrl) {
          setPreviewUrl(latest.data.url);
          setPreviewReadyAt(elapsedSec);
          appendLog(`✓ Preview ready — open in a new tab while we finish the rest`, "step");
        }
        break;
      case "writing":
        appendLog(
          latest.data.file_count
            ? `Saved ${latest.data.file_count} files to your project.`
            : `Saving files to your project.`,
          "ok",
        );
        setActiveIdx(4);
        break;
      case "evaluating":
        appendLog(`Running 32 quality checks before you see it.`, "step");
        setActiveIdx(4);
        break;
      case "repair_started": {
        // AUTO_REPAIR kicked in — baseline eval failed something. Without
        // these events the build feed goes silent for 60-120s while the
        // repair LLM call runs; users assume the build is stuck. Stay on
        // the "Checking my work" step icon — we're still in the same
        // phase conceptually, just doing more of it.
        const n = latest.data.failed_count ?? 0;
        const noun = n === 1 ? "issue" : "issues";
        appendLog(`Caught ${n} ${noun} — let me fix them before you see the draft.`, "info");
        setActiveIdx(4);
        break;
      }
      case "repair_round": {
        const r = latest.data.round ?? 1;
        const max = latest.data.max_rounds ?? 2;
        appendLog(`Fix attempt ${r} of ${max} — rewriting the affected files.`, "step");
        setActiveIdx(4);
        break;
      }
      case "repair_done": {
        if (latest.data.improved) {
          appendLog(`Fixed it. ${latest.data.final_score} checks now pass.`, "ok");
        } else {
          appendLog(`Couldn't auto-fix every check, but the site still works — you can keep editing.`, "info");
        }
        setActiveIdx(4);
        break;
      }
      case "done":
        appendLog(`Done. Your draft is ready to view.`, "ok");
        setActiveIdx(STEPS.length - 1);
        break;
      case "error":
        // Don't leak raw provider error strings (e.g. credit-balance
        // messages) — generalize so the user sees something graceful.
        // The full error string is still surfaced in the red banner
        // below if it's set on the props.
        // Don't promise auto-recovery — some errors (e.g. out of credits) are
        // terminal. The real outcome is shown in the banner below.
        appendLog(`Something interrupted this step…`, "info");
        break;
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sseEvents]);

  useEffect(() => {
    if (done) {
      setActiveIdx(STEPS.length - 1);
      setReadyPulsing(true);
      setLogLines((prev) => [
        ...prev,
        { ts: new Date().toLocaleTimeString(), text: "✓ all done. opening your draft.", tone: "ok" },
      ]);
    }
  }, [done]);

  useEffect(() => {
    if (error) {
      setLogLines((prev) => [
        ...prev,
        { ts: new Date().toLocaleTimeString(), text: `ERROR: ${error}`, tone: "info" },
      ]);
    }
  }, [error]);

  return (
    <div className="flex-1 flex overflow-hidden w-full relative">

      {/* ── Left column: Pebble chat (md+ only) ──────────────────────────────
          Hidden on mobile — the build status already fills the screen.
          The panel keeps the user engaged by asking 3 quick questions
          while the engine builds, then feeds the answers to /api/enrich-content
          immediately after the build finishes. */}
      <div className="hidden md:flex md:w-[340px] shrink-0 p-4 border-r border-border">
        <BuildChatPanel
          sseEvents={sseEvents ?? []}
          done={!!done}
          error={error ?? null}
          onAnswers={(answers) => onEnrich?.(answers)}
        />
      </div>

      {/* ── Right column: build status ──────────────────────────────────── */}
      <main className="relative flex-1 flex flex-col items-center pt-10 pb-12 px-4 overflow-y-auto">
      {/* Ambient brand photo — ripple-cream evokes the calm of waiting
          while the engine builds. Dimmed so the foreground reads cleanly. */}
      <Image
        src="/brand/ripple-cream.png"
        alt=""
        fill
        sizes="100vw"
        priority={false}
        className="pointer-events-none object-cover opacity-15 dark:opacity-10"
      />

      {/* Build status header — clean, bold, no logo fluff. */}
      <motion.section
        initial="hidden"
        animate="visible"
        variants={{
          hidden:  {},
          visible: { transition: { staggerChildren: 0.1, delayChildren: 0 } },
        }}
        className="mb-8 text-center w-full max-w-lg"
      >
        <motion.h1
          variants={safeFadeUp}
          className="text-3xl md:text-4xl font-extrabold tracking-tight text-foreground leading-tight"
        >
          {planName ? (
            <>Building <span className="text-[#3054ff]">{planName}</span>&hellip;</>
          ) : (
            "Building your site…"
          )}
        </motion.h1>

        <motion.div
          variants={safeFadeUp}
          className="mt-5 inline-flex items-center gap-2.5 px-4 py-2 rounded-full border border-border bg-card/60 backdrop-blur-sm"
        >
          <span
            className={`w-2 h-2 rounded-full ${done ? "bg-emerald-500" : "bg-[#3054ff] animate-pulse"}`}
            aria-hidden
          />
          <span className="font-mono text-sm font-semibold text-muted-foreground">
            {done ? `Finished in ${formatElapsed(elapsedSec)}` : `Building — ${formatElapsed(elapsedSec)}`}
          </span>
        </motion.div>

        {previewUrl && !done && previewReadyAt !== null && (
          <p className={`${type.mono} text-muted-foreground/70 mt-2`}>
            Homepage live at {formatElapsed(previewReadyAt)} — scroll down to preview
          </p>
        )}
      </motion.section>

      {/* Phase 25a (2026-05-20) — Plan Reveal card. Webild-parity move:
          each piece animates in as its SSE event arrives so the user
          sees Pebble's plan unfolding in the first 10-15 seconds rather
          than a blank wait. Project name from `started`, palette from
          `style`, page list from `plan`, checkmarks from `file` events. */}
      <AnimatePresence>
        {(planName || palette.length > 0 || pages.length > 0 || buildContext.dna || buildContext.layout) && (
          <motion.section
            key="plan-reveal"
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
            className="w-full max-w-lg bg-card border border-border rounded-2xl p-6 mb-6 relative z-10"
          >
            <p className={`${type.mono} text-muted-foreground uppercase tracking-wider mb-4 text-xs`}>
              Pebble's plan
            </p>

            {/* Project name — first thing to land, biggest perceived-speed win. */}
            <AnimatePresence>
              {planName && (
                <motion.h2
                  key="plan-name"
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
                  className={`${type.heading.l} text-foreground mb-4`}
                >
                  {planName}
                </motion.h2>
              )}
            </AnimatePresence>

            {/* Color palette — swatches as soon as the style event fires. */}
            <AnimatePresence>
              {palette.length > 0 && (
                <motion.div
                  key="plan-palette"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
                  className="flex gap-2 mb-5"
                >
                  {palette.map((color, i) => (
                    <motion.div
                      key={`${color}-${i}`}
                      initial={{ scale: 0, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ duration: SHORT_S, delay: i * 0.06, ease: EASE_CINEMATIC }}
                      className="w-7 h-7 rounded-full border border-border shadow-sm"
                      style={{ backgroundColor: color }}
                      aria-label={`Color ${color}`}
                    />
                  ))}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Design style chips — industry / layout / DNA as small pills. */}
            <AnimatePresence>
              {(buildContext.industry || buildContext.layout || buildContext.dna) && (
                <motion.div
                  key="plan-chips"
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
                  className="flex flex-wrap gap-2 mb-5"
                >
                  {buildContext.industry && (
                    <span className={`${type.mono} px-2.5 py-1 rounded-full border border-border bg-muted/40 text-muted-foreground text-xs`}>
                      {buildContext.industry}
                    </span>
                  )}
                  {buildContext.layout && (
                    <span className={`${type.mono} px-2.5 py-1 rounded-full border border-border bg-muted/40 text-muted-foreground text-xs`}>
                      {buildContext.layout}
                    </span>
                  )}
                  {buildContext.dna && (
                    <span className={`${type.mono} px-2.5 py-1 rounded-full border border-border bg-muted/40 text-muted-foreground text-xs`}>
                      {buildContext.dna}
                    </span>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Site structure — every page Pebble plans to build, checked
                off as each file lands. Best part of the reveal because the
                user can SEE concrete output appearing in real time. */}
            <AnimatePresence>
              {pages.length > 0 && (
                <motion.div
                  key="plan-pages"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
                >
                  <p className={`${type.mono} text-muted-foreground uppercase tracking-wider mb-2 text-xs`}>
                    Site structure
                  </p>
                  <ul className="space-y-1.5">
                    {pages.map((p, i) => {
                      const shipped = pagesShipped.has(p.id);
                      return (
                        <motion.li
                          key={p.id}
                          initial={{ opacity: 0, x: -6 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: SHORT_S, delay: i * 0.04, ease: EASE_CINEMATIC }}
                          className="flex items-center gap-2 text-sm"
                        >
                          {shipped ? (
                            <CheckCircle2 className="w-4 h-4 text-foreground shrink-0" />
                          ) : (
                            <Circle className="w-4 h-4 text-muted-foreground/40 shrink-0" />
                          )}
                          <span className={shipped ? "text-foreground" : "text-muted-foreground"}>
                            {p.title}
                          </span>
                          {p.foundation && (
                            <span className={`${type.mono} text-muted-foreground/60 text-xs ml-auto`}>
                              core
                            </span>
                          )}
                        </motion.li>
                      );
                    })}
                  </ul>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.section>
        )}
      </AnimatePresence>

      {/* Phase A.5 — inline live preview (Lovable-style). */}
      <AnimatePresence>
        {previewUrl && !done && (
          <motion.section
            key="live-preview"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
            className="w-full max-w-3xl mb-6 relative z-10"
          >
            <div className="flex items-center justify-between gap-2 mb-2 px-1">
              <p className={`${type.label} text-foreground`}>Live preview</p>
              <a
                href={previewUrl}
                target="_blank"
                rel="noopener noreferrer"
                className={`${type.body.s} text-muted-foreground hover:text-foreground underline underline-offset-2`}
              >
                Open in new tab
              </a>
            </div>
            <div className="rounded-2xl border border-border overflow-hidden bg-card shadow-[var(--shadow-1)]">
              <iframe
                title="Live site preview"
                src={previewUrl}
                className="w-full h-[min(420px,50vh)] bg-white"
                sandbox="allow-scripts allow-same-origin allow-forms"
              />
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* Macro checklist — high-level "where are we" */}
      <section className="w-full max-w-lg bg-card border border-border rounded-2xl p-6 mb-6">
        <div className="flex flex-col gap-5 relative">
          <div className="absolute left-[19px] top-4 bottom-4 w-0.5 bg-border" />
          {STEPS.map((step, i) => {
            const state = i < activeIdx ? "done" : i === activeIdx ? "active" : "pending";
            // When `done` fires, activeIdx is pinned to STEPS.length-1, making
            // the last step state === "active". We detect that specific moment
            // with readyPulsing so we can play the scale pulse instead of the
            // standard glow.
            const isFinalDone = readyPulsing && i === STEPS.length - 1;
            return (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: state === "pending" ? 0.55 : 1, x: 0 }}
                transition={{ duration: SHORT_S, ease: EASE_CINEMATIC }}
                className="flex gap-3 relative z-10"
              >
                <motion.div
                  animate={
                    isFinalDone
                      ? { scale: [1, 1.12, 1] }
                      : {
                          scale: state === "active" ? 1.05 : 1,
                          backgroundColor:
                            state === "done"
                              ? "var(--color-sage)"
                              : state === "active"
                                ? "var(--accent-1)"
                                : "var(--surface-1)",
                        }
                  }
                  transition={
                    isFinalDone
                      ? { duration: SLOW_S * 1.14, ease: EASE_CINEMATIC }
                      : { duration: STANDARD_S, ease: EASE_CINEMATIC }
                  }
                  className={`w-10 h-10 rounded-full flex items-center justify-center border border-border shrink-0 ${
                    state === "active" ? "pebble-step-active" : ""
                  }`}
                >
                  {state === "done" ? (
                    <CheckCircle2 className="w-5 h-5 text-white" />
                  ) : (
                    <step.Icon
                      className={`w-5 h-5 ${state === "active" ? "text-primary-foreground" : "text-muted-foreground"}`}
                    />
                  )}
                </motion.div>
                <div>
                  <p
                    className={`text-[15px] font-bold leading-snug flex items-center gap-2 ${state === "active" ? "text-[#3054ff]" : state === "done" ? "text-foreground" : "text-muted-foreground"}`}
                  >
                    {step.label}
                    {state === "active" && (
                      <motion.span
                        className="w-2 h-2 rounded-full bg-[#3054ff]"
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: SLOW_S * 2, repeat: Infinity }}
                      />
                    )}
                  </p>
                  <p className="text-sm text-muted-foreground mt-0.5 leading-snug">{step.detail}</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* Live build feed — collapsible. Expanded by default so the user
          sees real engine milestones, but can collapse if they'd rather
          not read the stream. Entrance after checklist settles. */}
      <motion.section
        variants={safeFadeUp}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.92, duration: STANDARD_S, ease: EASE_CINEMATIC }}
        className="w-full max-w-2xl"
      >
        {/* Feed header with collapse toggle */}
        <div className="flex items-center justify-between mb-3 px-1">
          <div className="flex items-center gap-2.5">
            <p className="text-sm font-bold text-foreground uppercase tracking-wide">
              Live Build Feed
            </p>
            <AnimatePresence>
              {logLines.length > 0 && (
                <motion.span
                  key="count"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-xs font-bold bg-muted px-2 py-0.5 rounded-full text-muted-foreground tabular-nums"
                >
                  {logLines.length}
                </motion.span>
              )}
            </AnimatePresence>
          </div>
          <button
            type="button"
            onClick={() => setFeedOpen((o) => !o)}
            className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors px-2.5 py-1.5 rounded-lg hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {feedOpen ? (
              <><ChevronUp className="w-3.5 h-3.5" /> Collapse</>
            ) : (
              <><ChevronDown className="w-3.5 h-3.5" /> Expand</>
            )}
          </button>
        </div>

        {/* Collapsible body */}
        <AnimatePresence initial={false}>
          {feedOpen && (
            <motion.div
              key="feed-body"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.24, ease: EASE_CINEMATIC }}
              style={{ overflow: "hidden" }}
            >
              <div
                ref={feedRef}
                className="bg-[#111] text-[#e8e4dc] rounded-xl p-4 font-mono text-[13px] leading-relaxed h-60 overflow-y-auto border border-[#222]"
              >
                {logLines.length === 0 && (
                  <p className="text-[#888] text-[13px]">Waiting for first event…</p>
                )}
                <AnimatePresence initial={false}>
                  {logLines.map((line, i) => (
                    <motion.p
                      key={i}
                      initial={{ opacity: 0, x: -6 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: MICRO_S, ease: EASE_CINEMATIC }}
                      className="whitespace-pre-wrap break-all mb-0.5"
                    >
                      <span className="text-[#555] text-[11px]">[{line.ts}]</span>{" "}
                      <span
                        className={
                          line.tone === "ok"
                            ? "text-emerald-400 font-semibold"
                            : line.tone === "step"
                              ? "text-[#6b8aff] font-bold"
                              : "text-[#e8e4dc]"
                        }
                      >
                        {line.text}
                      </span>
                    </motion.p>
                  ))}
                </AnimatePresence>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.section>

      {/* Rotating "Did you know?" card — the engagement honey. Pulls
          build-specific facts (DNA/layout/industry) when those events
          have fired; falls back to general Pebble facts before that.
          Rotates every 7s while building. Pauses on done/error. */}
      <motion.section
        variants={safeFadeUp}
        initial="hidden"
        animate="visible"
        transition={{ delay: 1.2, duration: STANDARD_S, ease: EASE_CINEMATIC }}
        className="w-full max-w-2xl mt-6"
      >
        {(() => {
          // Filter facts to ones whose data is available, then pick by
          // the rotating index. If no facts are available yet (very early
          // in the build), show nothing — better than a half-baked fact.
          const available = FACTS
            .map((f) => f(buildContext))
            .filter((s): s is string => !!s);
          if (available.length === 0) return null;
          const current = available[factIdx % available.length];
          return (
            <AnimatePresence mode="wait">
              <motion.div
                key={current}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: SHORT_S, ease: EASE_CINEMATIC }}
                className="rounded-xl border border-border bg-card/40 px-5 py-4 backdrop-blur-sm"
              >
                <p className={`${type.mono} text-muted-foreground mb-1`}>
                  While we work
                </p>
                <p className={`${type.body.s} text-foreground leading-relaxed`}>
                  {current}
                </p>
              </motion.div>
            </AnimatePresence>
          );
        })()}
      </motion.section>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: SHORT_S, ease: EASE_CINEMATIC }}
            className="mt-6 w-full max-w-2xl"
          >
            {/^.*(insufficient|credit|quota|out of (build|credit)).*/i.test(error) ? (
              // Out-of-credits is NOT a transient failure — retrying loops.
              // Explain it and point to the upgrade path instead of "Try again".
              <div className="p-5 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-start gap-4">
                <AlertCircle className="w-6 h-6 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-base font-bold text-foreground">You&apos;re out of build credits</p>
                  <p className="text-sm text-muted-foreground mt-1 leading-relaxed">
                    AI builds use credits, and your plan has none left. The Free plan includes
                    instant template &amp; example clones; upgrade for AI engine builds.
                  </p>
                  <div className="mt-4 flex flex-wrap items-center gap-3">
                    <Link
                      href="/pricing"
                      className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-foreground text-background text-sm font-bold hover:bg-foreground/90 transition-colors"
                    >
                      See plans &amp; upgrade
                    </Link>
                    <Link
                      href="/examples"
                      className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-border text-sm font-medium text-foreground hover:bg-accent transition-colors"
                    >
                      Start from a finished site (free) →
                    </Link>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-5 bg-destructive/10 border border-destructive/30 rounded-2xl flex items-start gap-4">
                <AlertCircle className="w-6 h-6 text-destructive shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-base font-bold text-destructive">Build failed</p>
                  <p className="text-sm text-destructive/80 mt-1 leading-relaxed break-words">{error}</p>
                  {onRetry && (
                    <button
                      type="button"
                      onClick={onRetry}
                      className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-foreground text-background text-sm font-bold hover:bg-foreground/90 transition-colors"
                    >
                      <RefreshCw className="w-4 h-4" />
                      Try again
                    </button>
                  )}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
      </main>
    </div>
  );
}
