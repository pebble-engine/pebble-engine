"use client";

import { useEffect, useRef, useState } from "react";
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
  History,
  Plus,
  type LucideIcon,
} from "lucide-react";
import { TopNav } from "@/components/top-nav";
import {
  getBrief,
  getLastBuild,
  getPlan,
  setLastBuild,
  type Brief,
  type PebblePlan,
} from "@/lib/state";
import { generateSite, type GenerateResponse } from "@/lib/api";
import { usePhase, type Phase } from "@/components/phases/use-phase";
import { IdeaPhase } from "@/components/phases/idea-phase";
import { PlanPhase } from "@/components/phases/plan-phase";
import { DraftPhase } from "@/components/phases/draft-phase";
import { EditPhase, type EditPhaseHandle } from "@/components/phases/edit-phase";

/**
 * Unified workspace shell. Holds the persistent chrome (top nav + Build
 * Plan rail), the current ``phase`` from the URL hash, and the few cross-
 * phase coordinations the old four-page flow had to manage by routing:
 *
 * - clicking Generate on the plan kicks off ``/api/generate`` and flips
 *   the phase from plan → draft → design without leaving the URL.
 * - clicking a Build Plan rail item jumps to that phase (with light
 *   eligibility gating — can't jump to "design" without a build).
 *
 * Each phase component is responsible for its own center content; the
 * design phase additionally claims the right rail. Other phases occupy
 * the full center area between rails.
 */

type Step = { id: Phase | "features" | "setup"; label: string; Icon: LucideIcon };

const BUILD_PLAN: Step[] = [
  { id: "idea",     label: "Idea",     Icon: Lightbulb },
  { id: "plan",     label: "Plan",     Icon: Map },
  { id: "draft",    label: "Draft",    Icon: Edit3 },
  { id: "design",   label: "Design",   Icon: Palette },
  { id: "features", label: "Features", Icon: Puzzle },
  { id: "setup",    label: "Setup",    Icon: Settings },
  { id: "publish",  label: "Publish",  Icon: Rocket },
];


export default function WorkspacePage() {
  const router = useRouter();
  const [phase, setPhase] = usePhase("design");
  const [brief, setBrief] = useState<Brief>({});
  const [build, setBuild] = useState<{ slug: string; preview_url: string; [k: string]: unknown } | null>(null);
  const [plan, setPlan] = useState<PebblePlan | null>(null);
  const [generateDone, setGenerateDone] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);
  const editPhaseRef = useRef<EditPhaseHandle>(null);

  // Initial hydrate. If the user lands at #phase=design without a build
  // yet, snap them back to idea so they aren't staring at "about:blank".
  useEffect(() => {
    const currentBrief = getBrief();
    const currentBuild = getLastBuild();
    const currentPlan = getPlan();
    setBrief(currentBrief);
    setBuild(currentBuild);
    setPlan(currentPlan);
    if (!currentBuild && (phase === "design" || phase === "draft")) {
      setPhase("idea");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleAdvanceFromIdea() {
    setBrief(getBrief());
    setPhase("plan");
  }

  function handleBackToIdea() {
    setPhase("idea");
  }

  // Plan phase → Draft phase → Design phase. The plan phase hands us a
  // closure that posts to /api/generate when invoked. We kick it off,
  // flip into draft for the animation, and on resolution flip to design.
  function handleGenerate(kickOff: () => Promise<GenerateResponse>) {
    setGenerateDone(false);
    setGenerateError(null);
    setPhase("draft");
    kickOff()
      .then((response) => {
        const built = {
          slug: response.slug,
          preview_url: response.preview_url,
          industry_intel_key: response.industry_intel_key,
        };
        setLastBuild(built);
        setBuild(built);
        setPlan(getPlan());
        setGenerateDone(true);
        // Tiny pause lets the draft phase paint its "Ready" state once
        // before we swap views; eliminates the visual hiccup of jumping
        // straight from "Drafting…" to a full preview.
        setTimeout(() => setPhase("design"), 600);
      })
      .catch((e: Error) => {
        setGenerateError(e.message || "Build failed");
      });
  }

  function handleJumpPhase(target: Step["id"]) {
    if (target === "publish") {
      router.push("/publish");
      return;
    }
    if (target === "features" || target === "setup") {
      // No dedicated phase yet — both surface as views inside design.
      if (build) setPhase("design");
      return;
    }
    if (target === "draft") {
      // Draft is only meaningful while a build is in-flight; ignore stale
      // clicks. Once the build resolves the shell snaps to design.
      return;
    }
    if (target === "design" && !build) return;
    setPhase(target as Phase);
  }

  const projectName = (brief.business_name as string) || "Untitled Project";

  const topNavRightSlot =
    phase === "design" ? (
      <div className="flex items-center gap-2">
        <button
          onClick={() => editPhaseRef.current?.openGallery()}
          className="flex items-center gap-1.5 text-sm font-semibold text-foreground bg-card border border-border px-3 h-10 rounded-full hover:bg-accent transition-colors"
          title="Add a DNA-themed section"
        >
          <Plus className="w-4 h-4" /> Add section
        </button>
        <button
          onClick={() => { editPhaseRef.current?.openHistory(); }}
          title="Version history"
          className="w-10 h-10 rounded-full flex items-center justify-center text-graphite hover:bg-mist hover:text-charcoal dark:text-pebble dark:hover:bg-stone/40 dark:hover:text-sand transition-colors"
          aria-label="Open version history"
        >
          <History className="w-5 h-5" />
        </button>
        <button
          onClick={() => router.push("/publish")}
          className="bg-primary text-primary-foreground px-4 h-10 rounded-full font-semibold text-sm flex items-center gap-2 hover:opacity-90 transition-opacity"
        >
          <Rocket className="w-4 h-4" /> Publish
        </button>
      </div>
    ) : null;

  return (
    <div className="min-h-screen flex flex-col">
      <TopNav projectName={projectName} rightSlot={topNavRightSlot} />

      <div className="flex flex-1 overflow-hidden">
        {/* Left rail — Build Plan */}
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
              const isActive = s.id === phase;
              return (
                <motion.button
                  key={s.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.06 * i, duration: 0.3 }}
                  onClick={() => handleJumpPhase(s.id)}
                  className={`flex items-center gap-2 p-2.5 rounded-lg text-sm font-semibold transition-colors text-left ${
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

        {/* Center + right — phase-specific */}
        {phase === "design" ? (
          <EditPhase
            ref={editPhaseRef}
            build={build}
            plan={plan}
            onPublish={() => router.push("/publish")}
          />
        ) : (
          <div className="flex-1 flex flex-col overflow-y-auto">
            {phase === "idea"  && <IdeaPhase  onAdvance={handleAdvanceFromIdea} />}
            {phase === "plan"  && <PlanPhase  onBack={handleBackToIdea} onGenerate={handleGenerate} />}
            {phase === "draft" && <DraftPhase done={generateDone} error={generateError} />}
          </div>
        )}
      </div>
    </div>
  );
}
