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
  ChevronDown,
  AlertCircle,
  type LucideIcon,
} from "lucide-react";
import { getBrief } from "@/lib/state";

/**
 * Draft phase — the "Pebble is building your draft" animation.
 *
 * Visually identical to the old /thinking page but with one structural
 * difference: it doesn't OWN the /api/generate request. The shell
 * kicks the request off when it transitions into this phase and passes
 * the resulting promise via ``promise``. The phase just animates the
 * checklist on a soft cadence and shows any error if the promise
 * rejects. On success the shell switches to design phase.
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

export function DraftPhase({ error, done }: Props) {
  const [activeIdx, setActiveIdx] = useState(0);
  const [logLines, setLogLines] = useState<{ ts: string; text: string }[]>([]);
  const startedRef = useRef(false);

  const appendLog = (text: string) => {
    setLogLines((prev) => [
      ...prev,
      { ts: new Date().toLocaleTimeString(), text },
    ]);
  };

  useEffect(() => {
    if (startedRef.current) return;
    startedRef.current = true;
    const brief = getBrief();
    appendLog(`Starting build for "${brief.business_name || "your project"}"`);

    // Soft cadence: advance the visible step every ~30s. The real
    // /api/generate call usually takes 90-180s so we want the timeline
    // to feel alive without racing past the actual work.
    const interval = setInterval(() => {
      setActiveIdx((idx) => {
        const next = Math.min(idx + 1, STEPS.length - 2);  // pin one step short of "ready"
        if (next !== idx) appendLog(`${STEPS[next].label}…`);
        return next;
      });
    }, 30_000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (done) {
      setActiveIdx(STEPS.length - 1);
      appendLog("Draft ready.");
    }
  }, [done]);

  useEffect(() => {
    if (error) appendLog(`Error: ${error}`);
  }, [error]);

  return (
    <main className="flex-1 flex flex-col items-center pt-10 pb-12 px-4 max-w-3xl mx-auto w-full">
      <section className="mb-8 text-center">
        <div className="pebble-ripple relative w-24 h-24 mx-auto mb-4 flex items-center justify-center">
          <motion.div
            animate={{ rotate: [0, 6, 0, -6, 0] }}
            transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
            className="text-secondary text-5xl"
          >
            ●
          </motion.div>
        </div>
        <h1 className="font-display text-2xl md:text-3xl font-bold text-foreground">
          Pebble is building your draft.
        </h1>
        <p className="text-sm text-muted-foreground mt-2">
          Usually 2–3 minutes. Feel free to keep this window open.
        </p>
      </section>

      <section className="w-full max-w-lg bg-card border border-border rounded-2xl p-6 mb-6">
        <div className="flex flex-col gap-5 relative">
          <div className="absolute left-[19px] top-4 bottom-4 w-0.5 bg-border" />
          {STEPS.map((step, i) => {
            const state = i < activeIdx ? "done" : i === activeIdx ? "active" : "pending";
            return (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: state === "pending" ? 0.55 : 1, x: 0 }}
                transition={{ duration: 0.35 }}
                className="flex gap-3 relative z-10"
              >
                <motion.div
                  animate={{
                    scale: state === "active" ? 1.05 : 1,
                    backgroundColor:
                      state === "done"
                        ? "var(--color-sage)"
                        : state === "active"
                          ? "var(--accent-1)"
                          : "var(--surface-1)",
                  }}
                  transition={{ duration: 0.3 }}
                  className="w-10 h-10 rounded-full flex items-center justify-center border border-border shrink-0"
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
                        transition={{ duration: 1.4, repeat: Infinity }}
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

      <section className="w-full max-w-lg">
        <details className="bg-card border border-border rounded-lg overflow-hidden group">
          <summary className="flex justify-between items-center p-3 cursor-pointer hover:bg-accent transition-colors">
            <span className="text-sm font-semibold text-muted-foreground">
              Show me what Pebble is actually doing
            </span>
            <ChevronDown className="w-4 h-4 group-open:rotate-180 transition-transform" />
          </summary>
          <div className="p-3 pt-0 font-mono text-xs text-muted-foreground bg-background border-t border-border">
            <div className="space-y-1">
              {logLines.length === 0 && <p className="opacity-60">Awaiting events…</p>}
              {logLines.map((line, i) => (
                <p key={i}>
                  <span className="text-primary">[{line.ts}]</span> {line.text}
                </p>
              ))}
            </div>
          </div>
        </details>
      </section>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 p-4 bg-destructive/10 border border-destructive/40 rounded-lg text-destructive text-sm max-w-lg flex items-start gap-3"
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
