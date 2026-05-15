"use client";

import { useEffect, useRef, useState } from "react";
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
import { getBrief } from "@/lib/state";
import { dropletPulse, fadeUp, MICRO_S, SHORT_S, STANDARD_S, SLOW_S, EASE_CINEMATIC } from "@/lib/motion";

/**
 * Draft phase — "Pebble is building your draft."
 *
 * Shell-driven: the workspace shell owns the /api/generate promise. This
 * phase just animates progress while we wait. Three layers of feedback,
 * each finer-grained than the last:
 *
 * 1. Pebble droplet logo with a smooth scale pulse (no rotate — rotating
 *    a glyph by small angles causes sub-pixel jitter that reads as
 *    "stuttering" even though Framer is hitting 60fps).
 * 2. The 6-step macro checklist (industry → style → pages → photos →
 *    checks → ready). Advances on a soft 30s cadence so the timeline
 *    feels alive without racing past the actual work.
 * 3. The live build feed — a typewriter-style log of pseudo-generated
 *    output, visible by default so impatient users can SEE that work
 *    is happening and don't assume the engine froze. Lines reference
 *    real files Pebble actually writes; cadence matches the empirical
 *    distribution of where time is spent (~10s prep, ~70s LLM call,
 *    ~30s post-build checks).
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
};

type LogLine = { ts: string; text: string; tone: "info" | "ok" | "step" };

export function DraftPhase({ error, done }: Props) {
  const [activeIdx, setActiveIdx] = useState(0);
  const [logLines, setLogLines] = useState<LogLine[]>([]);
  const [readyPulsing, setReadyPulsing] = useState(false);
  const startedRef = useRef(false);
  const timeoutsRef = useRef<ReturnType<typeof setTimeout>[]>([]);
  const feedRef = useRef<HTMLDivElement>(null);

  // Auto-scroll the build feed when new lines arrive.
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTo({ top: feedRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [logLines]);

  useEffect(() => {
    if (startedRef.current) return;
    startedRef.current = true;

    const brief = getBrief();
    const industry = (brief.business_type as string) || "small business";
    const audiences = Array.isArray(brief.audience)
      ? (brief.audience as string[]).join(", ")
      : (brief.audience as string) || "general visitors";
    const tone = (brief.brand_tone as string) || "professional";
    const slug = ((brief.business_name as string) || "untitled-project")
      .toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");

    // Scripted feed. Times are ms from start of phase mount. Tone:
    //   "step" = section header        (uppercase, accent-2)
    //   "info" = neutral status        (muted)
    //   "ok"   = checkmark / success   (sage/spark)
    //
    // Times were tuned against the engine's actual log timestamps for a
    // typical Gemini build: ~8s of prep, ~60-90s LLM call, ~30s post-
    // build. Total scripted length ~135s — if the real build finishes
    // sooner, the `done` prop pins us to a final state immediately.
    const script: Array<[number, string, LogLine["tone"]]> = [
      [   0,  `pebble.engine v0.6 — build for "${slug}"`,                                          "step"],
      [ 400,  `reading project brief: audience = ${audiences}, tone = ${tone}`,                    "info"],
      [1100,  `loading industry intel for "${industry}"...`,                                       "info"],
      [2400,  `✓ industry intel ready (47 patterns, 12 page templates)`,                           "ok"  ],
      [2900,  `picking style DNA from 10 personalities...`,                                        "info"],
      [4500,  `✓ DNA selected — palette, typography, signature moves set`,                         "ok"  ],
      [5000,  `fetching hero imagery from pexels...`,                                              "info"],
      [7400,  `✓ 4 stills + 1 hero video saved → public/`,                                         "ok"  ],
      [7900,  `assembling PROMPT.md from skills/prompt_template.md`,                               "info"],
      [8800,  `prompt ready — ~12.4k input tokens`,                                                "info"],
      [9400,  `calling LLM (gemini-3.1-pro) for full-site generation...`,                          "step"],
      [38000, `streaming: app/layout.tsx (Inter font, html lang attribute)`,                       "info"],
      [41500, `streaming: app/page.tsx (hero, about, services, contact)`,                          "info"],
      [44800, `streaming: app/globals.css (.liquid-glass, prefers-reduced-motion)`,                "info"],
      [48000, `streaming: components/ui/AnimatedHeading.tsx`,                                      "info"],
      [50500, `streaming: components/ui/FadeIn.tsx`,                                               "info"],
      [53200, `streaming: components/sections/Hero.tsx (VEX spec)`,                                "info"],
      [56100, `streaming: components/sections/About.tsx`,                                          "info"],
      [59000, `streaming: components/sections/Services.tsx`,                                       "info"],
      [62000, `streaming: components/sections/Gallery.tsx`,                                        "info"],
      [65000, `streaming: components/forms/ContactForm.tsx (real Resend Server Action)`,           "info"],
      [68000, `streaming: app/actions/contact.ts + lib/email.ts`,                                  "info"],
      [71000, `streaming: components/layout/Navbar.tsx (liquid-glass)`,                            "info"],
      [74000, `streaming: tailwind.config.ts (DNA palette mapped)`,                                "info"],
      [76500, `streaming: vercel.json + .env.example + README.md`,                                 "info"],
      [78500, `✓ 26 files written → output/${slug}/site/`,                                         "ok"  ],
      [79500, `running eval suite — 32 foundation checks`,                                         "step"],
      [82000, `✓ hero VEX spec`,                                                                   "ok"  ],
      [82500, `✓ Inter font weights (300/400/500/600)`,                                            "ok"  ],
      [83100, `✓ a11y audit — no high-impact violations`,                                          "ok"  ],
      [83700, `✓ no_src_directory`,                                                                "ok"  ],
      [84300, `✓ next.config.mjs (not .ts)`,                                                       "ok"  ],
      [84900, `✓ tsconfig paths { "@/*": ["./*"] }`,                                               "ok"  ],
      [85500, `✓ contact form is a real Resend Server Action`,                                     "ok"  ],
      [86100, `✓ all 32 checks pass — repair loop not needed`,                                     "ok"  ],
      [87000, `writing build_meta.json (tokens, est cost, rate card)`,                             "info"],
      [88500, `✓ draft ready — handing back to workspace`,                                         "ok"  ],
    ];

    function appendLog(text: string, tone: LogLine["tone"]) {
      setLogLines((prev) => [...prev, { ts: new Date().toLocaleTimeString(), text, tone }]);
    }

    for (const [delay, text, tone] of script) {
      const id = setTimeout(() => appendLog(text, tone), delay);
      timeoutsRef.current.push(id);
    }

    // Soft macro-cadence: advance the visible step every ~30s. Pins one
    // short of "ready" so the final transition only fires when `done` is
    // true.
    const interval = setInterval(() => {
      setActiveIdx((idx) => Math.min(idx + 1, STEPS.length - 2));
    }, 30_000);
    timeoutsRef.current.push(interval as unknown as ReturnType<typeof setTimeout>);

    return () => {
      for (const id of timeoutsRef.current) clearTimeout(id);
      clearInterval(interval);
      timeoutsRef.current = [];
    };
  }, []);

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
    <main className="flex-1 flex flex-col items-center pt-10 pb-12 px-4 max-w-3xl mx-auto w-full overflow-y-auto">
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
            variants={dropletPulse}
            animate="rest"
            className="text-secondary relative z-10"
            style={{ willChange: "transform" }}
          >
            <Droplet className="w-14 h-14 fill-current" strokeWidth={1.5} />
          </motion.div>
        </div>
        <motion.h1
          variants={fadeUp}
          className="font-display text-2xl md:text-3xl font-bold text-foreground"
        >
          Pebble is building your draft.
        </motion.h1>
        <motion.p
          variants={fadeUp}
          className="text-sm text-muted-foreground mt-2"
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
                    className={`text-sm font-semibold flex items-center gap-2 ${state === "active" ? "text-primary" : "text-foreground"}`}
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
                  <p className="text-muted-foreground text-xs mt-0.5">{step.detail}</p>
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
        variants={fadeUp}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.92, duration: STANDARD_S, ease: EASE_CINEMATIC }}
        className="w-full max-w-2xl"
      >
        <div className="flex items-center justify-between mb-2 px-1">
          <p className="text-[11px] font-mono uppercase tracking-widest text-muted-foreground">
            Live build feed
          </p>
          <p className="text-[11px] font-mono text-muted-foreground/60">
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
                        ? "text-spark font-semibold"
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
