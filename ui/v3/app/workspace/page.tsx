"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Lightbulb,
  Map,
  Edit3,
  Palette,
  Puzzle,
  Settings,
  Rocket,
  Smile,
  Award,
  Sparkles,
  CalendarDays,
  type LucideIcon,
} from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { getBrief, getLastBuild, getPlan, type PebblePlan } from "@/lib/state";

type Step = { id: string; label: string; Icon: LucideIcon };

const BUILD_PLAN: Step[] = [
  { id: "idea",     label: "Idea",     Icon: Lightbulb },
  { id: "plan",     label: "Plan",     Icon: Map },
  { id: "draft",    label: "Draft",    Icon: Edit3 },
  { id: "design",   label: "Design",   Icon: Palette },
  { id: "features", label: "Features", Icon: Puzzle },
  { id: "setup",    label: "Setup",    Icon: Settings },
  { id: "publish",  label: "Publish",  Icon: Rocket },
];

const REFINE_CHIPS = [
  { id: "friendlier",   label: "Make it friendlier",  Icon: Smile },
  { id: "professional", label: "More professional",   Icon: Award },
  { id: "simpler",      label: "Simpler",             Icon: Sparkles },
  { id: "colors",       label: "Change colors",       Icon: Palette },
  { id: "booking",      label: "Add booking",         Icon: CalendarDays },
];

export default function WorkspacePage() {
  const router = useRouter();
  const [activeStep, setActiveStep] = useState("draft");
  const [plan, setPlan] = useState<PebblePlan | null>(null);
  const [build, setBuild] = useState<ReturnType<typeof getLastBuild>>(null);
  const [brief, setBrief] = useState<ReturnType<typeof getBrief>>({});

  useEffect(() => {
    setPlan(getPlan());
    setBuild(getLastBuild());
    setBrief(getBrief());
    if (!getLastBuild()) router.push("/");
  }, [router]);

  const projectName = (brief.business_name as string) || "Untitled Project";
  const previewUrl = build?.preview_url || "about:blank";
  const slugForUrl = (build?.slug as string) || "your-site";

  return (
    <div className="min-h-screen flex flex-col">
      <TopNav projectName={projectName} />

      <div className="flex flex-1 overflow-hidden">
        {/* Left rail */}
        <motion.aside
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
          className="flex flex-col gap-1 p-4 w-[240px] bg-card border-r border-border"
        >
          <div className="mb-6 px-1">
            <h2 className="font-display text-xl font-semibold text-primary leading-tight">Your Build Plan</h2>
            <p className="text-xs text-muted-foreground opacity-70">AI-Guided Strategy</p>
          </div>
          <nav className="flex flex-col gap-1">
            {BUILD_PLAN.map((s, i) => {
              const isActive = activeStep === s.id;
              return (
                <motion.button
                  key={s.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.06 * i, duration: 0.3 }}
                  onClick={() => setActiveStep(s.id)}
                  className={`flex items-center gap-2 p-2.5 rounded-lg text-sm font-semibold transition-colors ${
                    isActive
                      ? "bg-primary/15 text-primary"
                      : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  }`}
                >
                  <s.Icon className="w-5 h-5 shrink-0" />
                  <span>{s.label}</span>
                </motion.button>
              );
            })}
          </nav>
        </motion.aside>

        {/* Center preview */}
        <main className="flex-1 bg-background p-6 relative overflow-hidden flex flex-col">
          <motion.div
            initial={{ opacity: 0, scale: 0.99 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
            className="flex-1 rounded-2xl border border-border bg-card shadow-[var(--shadow-1)] overflow-hidden flex flex-col"
          >
            {/* Faux browser chrome */}
            <div className="h-10 bg-accent flex items-center px-4 gap-2 border-b border-border">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-border" />
                <div className="w-3 h-3 rounded-full bg-border opacity-60" />
                <div className="w-3 h-3 rounded-full bg-border opacity-30" />
              </div>
              <div className="bg-background border border-border px-4 py-0.5 rounded-full text-xs text-muted-foreground mx-auto truncate max-w-[60%]">
                {slugForUrl}.pebble.site
              </div>
            </div>
            <iframe src={previewUrl} className="flex-1 bg-white w-full" />
          </motion.div>

          {/* Refinement chips + educational nudge.
              The "Style tweaks are free" hint borrows from Lovable's
              "Visual Edits — faster than chatting" pattern. It directly
              counters the credit-slot-machine fear users have about
              competitors. */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.15 }}
            className="fixed bottom-6 left-[240px] right-[320px] flex flex-col items-center gap-2 pointer-events-none"
          >
            <p className="text-[11px] font-mono uppercase tracking-widest text-muted-foreground bg-card/80 backdrop-blur px-3 py-1 rounded-full border border-border pointer-events-auto">
              ✨ Style tweaks are free — try them
            </p>
            <nav className="bg-card border border-border shadow-lg rounded-full px-3 py-2 flex gap-1 pointer-events-auto">
              {REFINE_CHIPS.map((c) => (
                <motion.button
                  key={c.id}
                  whileHover={{ y: -3 }}
                  whileTap={{ scale: 0.95 }}
                  className="text-muted-foreground px-4 py-1.5 text-sm font-semibold flex items-center gap-1.5 hover:bg-accent hover:text-foreground rounded-full transition-colors"
                >
                  <c.Icon className="w-4 h-4" />
                  {c.label}
                </motion.button>
              ))}
            </nav>

            {/* Plan-driven next steps appear as a secondary suggestion strip.
                Borrowed from Lovable's post-response suggestion chips — keeps
                the user momentum-forward instead of staring at "what now?". */}
            {plan && plan.next_steps && plan.next_steps.length > 0 && (
              <div className="flex flex-wrap justify-center gap-2 max-w-2xl mt-2 pointer-events-auto">
                {plan.next_steps.slice(0, 3).map((step, i) => (
                  <button
                    key={i}
                    className="text-xs text-foreground bg-card/90 backdrop-blur border border-border rounded-full px-3 py-1.5 hover:bg-accent transition-colors"
                    title={step}
                  >
                    {step.length > 60 ? step.slice(0, 57) + "…" : step}
                  </button>
                ))}
              </div>
            )}
          </motion.div>
        </main>

        {/* Right rail */}
        <motion.aside
          initial={{ opacity: 0, x: 8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
          className="flex flex-col gap-3 p-4 w-[320px] bg-card border-l border-border overflow-y-auto"
        >
          <div className="mb-4 px-1">
            <h2 className="font-display text-xl font-semibold text-primary">Launch Setup</h2>
            <p className="text-xs text-muted-foreground opacity-70">
              {plan ? `${plan.setup_needs.filter((s) => s.status !== "auto").length} items remaining` : "Loading..."}
            </p>
          </div>
          <div className="space-y-2 flex-1">
            {plan?.setup_needs.map((s, i) => (
              <motion.div
                key={s.id}
                initial={{ opacity: 0, x: 8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.04 * i, duration: 0.3 }}
                className="p-3 rounded-lg bg-background border border-border flex flex-col gap-1"
                title={s.notes}
              >
                <div className="flex justify-between items-center">
                  <span className="text-sm font-semibold">{s.label}</span>
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${
                      s.status === "auto"
                        ? "bg-earth/20 text-earth"
                        : s.status === "pending"
                          ? "bg-spark/15 text-spark"
                          : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {s.status === "auto" ? "Auto-done" : s.status === "pending" ? "Coming soon" : "You'll do this"}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
          <div className="pt-3 mt-auto border-t border-border">
            <motion.button
              whileTap={{ scale: 0.97 }}
              onClick={() => router.push("/publish")}
              className="w-full bg-secondary text-secondary-foreground py-3 rounded-xl font-bold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
            >
              <Rocket className="w-4 h-4" /> Go Live
            </motion.button>
          </div>
        </motion.aside>
      </div>
    </div>
  );
}
