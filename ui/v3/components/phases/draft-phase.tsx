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
  const feedRef = useRef<HTMLDivElement>(null);

  const safeDropletPulse = useMemo(() => withReducedMotion(dropletPulse), []);
  const safeFadeUp = useMemo(() => withReducedMotion(fadeUp), []);

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

    switch (latest.type) {
      case "started":
        appendLog(`pebble.engine — build for "${latest.data.slug}"`, "step");
        setActiveIdx(0);
        break;
      case "industry":
        appendLog(
          latest.data.key
            ? `✓ industry intel ready (${latest.data.key})`
            : `✓ industry intel ready`,
          "ok",
        );
        setActiveIdx(1);
        break;
      case "style":
        appendLog(
          latest.data.dna_label
            ? `✓ DNA selected — ${latest.data.dna_label}`
            : `✓ style DNA selected`,
          "ok",
        );
        setActiveIdx(1);
        break;
      case "generating":
        appendLog(`calling ${latest.data.model} for full-site generation...`, "step");
        setActiveIdx(2);
        break;
      case "writing":
        appendLog(`✓ ${latest.data.file_count} files written`, "ok");
        setActiveIdx(4);
        break;
      case "evaluating":
        appendLog(`running eval suite — quality checks...`, "step");
        setActiveIdx(4);
        break;
      case "done":
        appendLog(`✓ draft ready — handing back to workspace`, "ok");
        setActiveIdx(STEPS.length - 1);
        break;
      case "error":
        appendLog(`ERROR: ${latest.data.error}`, "info");
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
          Pebble is building your draft.
        </motion.h1>
        <motion.p
          variants={safeFadeUp}
          className={`${type.body.s} text-muted-foreground mt-2`}
        >
          Usually 2–3 minutes. Feel free to keep this window open.
        </motion.p>
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
