"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Palette,
  Edit3,
  Image as ImageIcon,
  CheckSquare,
  CheckCircle2,
  ChevronDown,
  type LucideIcon,
} from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { getBrief, patchBrief, setPlan } from "@/lib/state";
import { fetchPlan } from "@/lib/api";

type ThinkingStep = {
  id: string;
  Icon: LucideIcon;
  label: string;
  detail: string;
};

const STEPS: ThinkingStep[] = [
  { id: "industry", Icon: Search,      label: "Reading your industry",  detail: "Looking up what websites for your type of business usually include." },
  { id: "style",    Icon: Palette,     label: "Choosing a style",       detail: "Picking a visual style that matches the feeling you chose." },
  { id: "pages",    Icon: Edit3,       label: "Writing the pages",      detail: "Drafting the pages your industry typically needs." },
  { id: "photos",   Icon: ImageIcon,   label: "Finding photos",         detail: "Pulling stock photos that match your industry." },
  { id: "checks",   Icon: CheckSquare, label: "Checking my work",       detail: "Running 32 quality checks before you see the draft." },
  { id: "ready",    Icon: CheckCircle2, label: "Ready to show you",     detail: "All set. Let's review." },
];

export default function ThinkingPage() {
  const router = useRouter();
  const [activeIdx, setActiveIdx] = useState(0);
  const [logLines, setLogLines] = useState<{ ts: string; text: string }[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
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

    // Soft cadence: advance the visible step ~every 1.4s while /api/plan is
    // in flight. Snap to the final state on response.
    const interval = setInterval(() => {
      setActiveIdx((idx) => {
        const next = Math.min(idx + 1, STEPS.length - 1);
        appendLog(`${STEPS[next].label}...`);
        return next;
      });
    }, 1400);

    fetchPlan(brief)
      .then((result) => {
        clearInterval(interval);
        setActiveIdx(STEPS.length - 1);
        setPlan(result.plan);
        patchBrief({
          _industry_intel_key: result.industry_key || undefined,
          _design_dna_id: result.dna_id || undefined,
        });
        appendLog(`Plan ready — ${result.plan.pages.length} pages, ${result.plan.features.length} features.`);
        setTimeout(() => router.push("/plan-review"), 700);
      })
      .catch((e: Error) => {
        clearInterval(interval);
        setErrorMsg(e.message);
        appendLog(`Error: ${e.message}`);
      });

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <TopNav />
      <main className="flex-1 flex flex-col items-center pt-12 pb-24 px-4 max-w-4xl mx-auto w-full">
        {/* Rippling pebble glyph */}
        <section className="mb-10 text-center">
          <div className="pebble-ripple relative w-32 h-32 mx-auto mb-6 flex items-center justify-center">
            <motion.div
              animate={{ rotate: [0, 6, 0, -6, 0] }}
              transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
              className="text-secondary text-6xl"
            >
              ●
            </motion.div>
          </div>
          <h1 className="font-display text-3xl md:text-4xl font-bold text-foreground">
            Pebble is building your draft.
          </h1>
        </section>

        {/* Vertical Timeline */}
        <section className="w-full max-w-lg bg-card border border-border rounded-2xl p-6 mb-8">
          <div className="flex flex-col gap-6 relative">
            <div className="absolute left-[19px] top-4 bottom-4 w-0.5 bg-border" />
            {STEPS.map((step, i) => {
              const state = i < activeIdx ? "done" : i === activeIdx ? "active" : "pending";
              return (
                <motion.div
                  key={step.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: state === "pending" ? 0.55 : 1, x: 0 }}
                  transition={{ duration: 0.35 }}
                  className="flex gap-4 relative z-10"
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
                      <step.Icon className={`w-5 h-5 ${state === "active" ? "text-primary-foreground" : "text-muted-foreground"}`} />
                    )}
                  </motion.div>
                  <div>
                    <p className={`text-sm font-semibold flex items-center gap-2 ${state === "active" ? "text-primary" : "text-foreground"}`}>
                      {step.label}
                      {state === "active" && (
                        <motion.span
                          className="w-2 h-2 rounded-full bg-primary"
                          animate={{ opacity: [0.3, 1, 0.3] }}
                          transition={{ duration: 1.4, repeat: Infinity }}
                        />
                      )}
                    </p>
                    <p className="text-muted-foreground text-sm mt-1">{step.detail}</p>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </section>

        {/* AI Log (collapsible) */}
        <section className="w-full max-w-lg">
          <details className="bg-card border border-border rounded-lg overflow-hidden group">
            <summary className="flex justify-between items-center p-4 cursor-pointer hover:bg-accent transition-colors">
              <span className="text-sm font-semibold text-muted-foreground">
                Show me what Pebble is actually doing
              </span>
              <ChevronDown className="w-4 h-4 group-open:rotate-180 transition-transform" />
            </summary>
            <div className="p-4 pt-0 font-mono text-sm text-muted-foreground bg-background border-t border-border">
              <div className="space-y-1.5">
                {logLines.length === 0 && <p className="opacity-60">Awaiting events...</p>}
                {logLines.map((line, i) => (
                  <motion.p
                    key={i}
                    initial={{ opacity: 0, x: -4 }}
                    animate={{ opacity: 1, x: 0 }}
                  >
                    <span className="text-primary">[{line.ts}]</span> {line.text}
                  </motion.p>
                ))}
              </div>
            </div>
          </details>
        </section>

        <AnimatePresence>
          {errorMsg && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 p-4 bg-destructive/10 border border-destructive/40 rounded-lg text-destructive text-sm max-w-lg"
            >
              {errorMsg}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
