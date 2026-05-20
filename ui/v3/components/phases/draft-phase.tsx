"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Palette,
  Edit3,
  Image as ImageIcon,
  CheckSquare,
  CheckCircle2,
  AlertCircle,
  Droplet,
  type LucideIcon,
} from "lucide-react";
import { type SSEEvent } from "@/lib/api";
import { dropletPulse, fadeUp, MICRO_S, SHORT_S, STANDARD_S, SLOW_S, EASE_CINEMATIC, withReducedMotion } from "@/lib/motion";
import { type } from "@/lib/type";

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
};

type LogLine = { ts: string; text: string; tone: "info" | "ok" | "step" };

export function DraftPhase({ error, done, sseEvents }: Props) {
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
  const feedRef = useRef<HTMLDivElement>(null);
  const startTsRef = useRef<number>(Date.now());
  const notifiedRef = useRef(false);

  const safeDropletPulse = useMemo(() => withReducedMotion(dropletPulse), []);
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
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTo({ top: feedRef.current.scrollHeight, behavior: "smooth" });
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
        setActiveIdx(1);
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
          appendLog(`+ ${latest.data.name}`, "ok");
        }
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
      case "done":
        appendLog(`Done. Your draft is ready to view.`, "ok");
        setActiveIdx(STEPS.length - 1);
        break;
      case "error":
        // Don't leak raw provider error strings (e.g. credit-balance
        // messages) — generalize so the user sees something graceful.
        // The full error string is still surfaced in the red banner
        // below if it's set on the props.
        appendLog(`Something went wrong on this step. Trying to recover…`, "info");
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
    <main className="relative flex-1 flex flex-col items-center pt-10 pb-12 px-4 w-full overflow-y-auto">
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

      {/* Cinematic entrance stagger: droplet → headline → subhead. */}
      <motion.section
        initial="hidden"
        animate="visible"
        variants={{
          hidden:  {},
          visible: { transition: { staggerChildren: 0.12, delayChildren: 0 } },
        }}
        className="mb-8 text-center"
      >
        {/* Smooth scale pulse — no rotate. Rotating a small glyph by ±6°
            sub-pixel-jitters the anti-aliasing and reads as "stutter" even
            when Framer is hitting 60fps. A pure scale animation on an SVG
            stays GPU-accelerated and visually clean. The pebble-ripple
            blob behind comes from the .pebble-ripple CSS keyframe. */}
        <div className="pebble-ripple relative w-24 h-24 mx-auto mb-4 flex items-center justify-center">
          <motion.div
            variants={safeDropletPulse}
            animate="rest"
            className="text-secondary relative z-10"
            style={{ willChange: "transform" }}
          >
            <Droplet className="w-14 h-14 fill-current" strokeWidth={1.5} />
          </motion.div>
        </div>
        <motion.h1
          variants={safeFadeUp}
          className={`${type.display.m} text-foreground`}
        >
          Hang out while Pebble builds your masterpiece.
        </motion.h1>
        <motion.p
          variants={safeFadeUp}
          className={`${type.body.s} text-muted-foreground mt-2 max-w-md mx-auto`}
        >
          You can switch to another tab — we'll ping you when it's ready. Usually 2–3 minutes.
        </motion.p>
        <motion.div
          variants={safeFadeUp}
          className="mt-4 inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-card/60"
        >
          <span
            className="w-1.5 h-1.5 rounded-full bg-foreground animate-pulse"
            aria-hidden
          />
          <span className={`${type.mono} text-muted-foreground`}>
            {done ? `Finished in ${formatElapsed(elapsedSec)}` : `Building — ${formatElapsed(elapsedSec)}`}
          </span>
        </motion.div>

        {/* Phase A.5 — preview-ready CTA. Surfaces the moment the
            foundation files are on disk (~60-90s into the build) so the
            user can open the homepage in a new tab while inner pages
            continue streaming. The biggest perceived-time win in the
            whole build flow. */}
        <AnimatePresence>
          {previewUrl && !done && (
            <motion.a
              key="preview-cta"
              href={previewUrl}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, y: 12, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.96 }}
              transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
              className="mt-5 mx-auto inline-flex items-center gap-3 px-6 py-3 rounded-full bg-foreground text-background hover:bg-foreground/90 transition-colors group"
            >
              <span className={`${type.label}`}>
                View your homepage now
              </span>
              <span className={`${type.mono} text-background/70 group-hover:text-background/90 transition-colors`}>
                opens in new tab →
              </span>
            </motion.a>
          )}
        </AnimatePresence>
        {previewUrl && !done && previewReadyAt !== null && (
          <p className={`${type.mono} text-muted-foreground/70 mt-2`}>
            ready at {formatElapsed(previewReadyAt)} — inner pages still streaming in
          </p>
        )}
      </motion.section>

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
                    className={`${type.label} flex items-center gap-2 ${state === "active" ? "text-primary" : "text-foreground"}`}
                  >
                    {step.label}
                    {state === "active" && (
                      <motion.span
                        className="w-2 h-2 rounded-full bg-primary"
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: SLOW_S * 2, repeat: Infinity }} // SLOW_S*2 = 1.4s — intentional slow pulse
                      />
                    )}
                  </p>
                  <p className={`${type.caption} mt-1`}>{step.detail}</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* Live build feed — visible by default so the user can SEE the
          engine working. Eliminates the "is it frozen?" panic.
          Entrance stagger: fades up after the checklist settles (~0.92s delay). */}
      <motion.section
        variants={safeFadeUp}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.92, duration: STANDARD_S, ease: EASE_CINEMATIC }}
        className="w-full max-w-2xl"
      >
        <div className="flex items-center justify-between mb-2 px-1">
          <p className={`${type.mono} text-muted-foreground`}>
            Live build feed
          </p>
          <p className={`${type.mono} text-muted-foreground/60`}>
            {logLines.length} events
          </p>
        </div>
        <div
          ref={feedRef}
          className="bg-charcoal/95 dark:bg-stone/80 text-pebble rounded-xl p-4 font-mono text-[11px] leading-relaxed h-64 overflow-y-auto border border-charcoal/50"
        >
          {logLines.length === 0 && (
            <p className="text-pebble/50">Waiting for the first event...</p>
          )}
          <AnimatePresence initial={false}>
            {logLines.map((line, i) => (
              <motion.p
                key={i}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: MICRO_S, ease: EASE_CINEMATIC }}
                className="whitespace-pre-wrap break-all"
              >
                <span className="text-pebble/40">[{line.ts}]</span>{" "}
                <span
                  className={
                    line.tone === "ok"
                      ? "text-sage"
                      : line.tone === "step"
                        ? "text-spark-deep font-semibold"
                        : "text-pebble"
                  }
                >
                  {line.text}
                </span>
              </motion.p>
            ))}
          </AnimatePresence>
        </div>
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
            className="mt-6 p-4 bg-destructive/10 border border-destructive/40 rounded-lg text-destructive text-sm max-w-2xl flex items-start gap-3"
          >
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Build failed.</p>
              <p className="text-xs opacity-80 mt-1">{error}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
