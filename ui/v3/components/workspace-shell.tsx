"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
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
import { usePhase, phaseToStage, type Phase } from "@/components/phases/use-phase";
import { STANDARD_S, EASE_CINEMATIC, phaseEnter, phaseExit } from "@/lib/motion";
import { WelcomePhase } from "@/components/phases/welcome-phase";
import { IdeaPhase } from "@/components/phases/idea-phase";
import { PlanPhase } from "@/components/phases/plan-phase";
import { DraftPhase } from "@/components/phases/draft-phase";
import { EditPhase, type EditPhaseHandle } from "@/components/phases/edit-phase";
import { PublishPhase } from "@/components/phases/publish-phase";

/**
 * Unified workspace shell. Single component, rendered by both ``/`` (the
 * welcome route) and ``/workspace`` (the build / design route). The two
 * pages exist so that bookmarks and external links resolve naturally, but
 * the visible chrome is identical between them — switching from welcome
 * into the questionnaire is a phase transition inside this same shell,
 * with one router.push at the commit moment so the URL accurately
 * reflects "you're now building a project."
 *
 * Phase model:
 * - welcome  → full-bleed prompt + starter cards (no left rail, no project name)
 * - idea     → chip questions (left rail visible, "Idea" highlighted)
 * - plan     → Pebble Plan review
 * - draft    → build animation
 * - design   → preview + refine + visual editor + history drawer + block gallery
 * - publish  → publish flow (used to live at /publish)
 */

type RailStep = { id: Phase | "features" | "setup"; label: string; Icon: LucideIcon };

const BUILD_PLAN: RailStep[] = [
  { id: "idea",     label: "Idea",     Icon: Lightbulb },
  { id: "plan",     label: "Plan",     Icon: Map },
  { id: "draft",    label: "Draft",    Icon: Edit3 },
  { id: "design",   label: "Design",   Icon: Palette },
  { id: "features", label: "Features", Icon: Puzzle },
  { id: "setup",    label: "Setup",    Icon: Settings },
  { id: "publish",  label: "Publish",  Icon: Rocket },
];


export function WorkspaceShell() {
  const router = useRouter();
  const pathname = usePathname();
  // The route is the source of truth for the *initial* phase, but the URL
  // hash overrides it on mount (handled inside usePhase). After mount,
  // setPhase is what drives the URL.
  const initialPhase: Phase = pathname === "/" ? "welcome" : "design";
  const [phase, setPhase] = usePhase(initialPhase);
  const [brief, setBrief] = useState<Brief>({});
  const [build, setBuild] = useState<{ slug: string; preview_url: string; [k: string]: unknown } | null>(null);
  const [plan, setPlan] = useState<PebblePlan | null>(null);
  const [generateDone, setGenerateDone] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);
  const editPhaseRef = useRef<EditPhaseHandle>(null);

  // Initial hydrate. Snap to a sensible phase based on what state actually
  // exists: no build + asking for design/draft/publish → step back to the
  // earliest phase the user can reasonably resume from.
  useEffect(() => {
    const currentBrief = getBrief();
    const currentBuild = getLastBuild();
    const currentPlan = getPlan();
    setBrief(currentBrief);
    setBuild(currentBuild);
    setPlan(currentPlan);
    if (!currentBuild && (phase === "design" || phase === "draft" || phase === "publish")) {
      const hasBriefContent = !!(currentBrief.business_name || currentBrief.extra_context);
      setPhase(hasBriefContent ? "idea" : "welcome");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleAdvanceFromWelcome() {
    // On the welcome / home route, this is the one meaningful "commit to
    // building" transition — the URL flips from / to /workspace so the
    // browser bar reflects the new context. From any other route, we're
    // already inside the workspace shell; just update the phase.
    if (pathname === "/") {
      router.push("/workspace#phase=idea");
    } else {
      setPhase("idea");
    }
  }

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

  function handleJumpPhase(target: RailStep["id"]) {
    if (target === "publish") {
      // Publish is only meaningful once we've generated something.
      if (build) setPhase("publish");
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

  const projectName = phase === "welcome"
    ? undefined
    : (brief.business_name as string) || "Untitled Project";

  const showLeftRail = phase !== "welcome";
  const railStage = phaseToStage(phase);

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
          onClick={() => setPhase("publish")}
          className="bg-primary text-primary-foreground px-4 h-10 rounded-full font-semibold text-sm flex items-center gap-2 hover:opacity-90 transition-opacity"
        >
          <Rocket className="w-4 h-4" /> Publish
        </button>
      </div>
    ) : null;

  return (
    <div className="min-h-screen flex flex-col">
      {/* TopNav persists across all phase changes. */}
      <TopNav projectName={projectName} rightSlot={topNavRightSlot} />

      <div className="flex flex-1 overflow-hidden">
        {/* Rail is persistent — visible state animates instead of mounting/unmounting.
            On welcome the rail's width and opacity collapse to 0 so it visually
            disappears but stays in the DOM, preserving its layoutId children for
            cross-phase morphs. */}
        <motion.aside
          aria-hidden={!showLeftRail}
          inert={!showLeftRail}
          animate={{
            width:   showLeftRail ? 240 : 0,
            opacity: showLeftRail ? 1   : 0,
          }}
          transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
          className="flex flex-col gap-1 p-4 bg-card border-r border-border overflow-hidden shrink-0"
        >
          <div className="mb-6 px-1">
            <h2 className="font-display text-xl font-semibold text-primary leading-tight">Your Build Plan</h2>
            <p className="text-xs text-muted-foreground opacity-70">AI-Guided Strategy</p>
          </div>
          <nav className="flex flex-col gap-1">
            {BUILD_PLAN.map((s) => {
              const isActive = s.id === railStage;
              return (
                <button
                  key={s.id}
                  onClick={() => handleJumpPhase(s.id)}
                  className={`relative flex items-center gap-2 p-2.5 rounded-lg text-sm font-semibold transition-colors text-left ${
                    isActive ? "text-primary" : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  }`}
                >
                  {isActive && (
                    <motion.div
                      layoutId="rail-active"
                      className="absolute inset-0 bg-primary/15 rounded-lg"
                      transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
                    />
                  )}
                  <s.Icon className="w-5 h-5 shrink-0" />
                  <span>{s.label}</span>
                </button>
              );
            })}
          </nav>
        </motion.aside>

        {/* Center column — only this swaps between phases. AnimatePresence with
            mode="wait" ensures the outgoing phase finishes its exit before the
            incoming one mounts. */}
        <AnimatePresence mode="wait">
          <motion.div
            key={phase}
            variants={phaseEnter}
            initial="hidden"
            animate="visible"
            exit={phaseExit.exit}
            className="flex-1 flex flex-col overflow-hidden"
          >
            {phase === "welcome" && <WelcomePhase onAdvance={handleAdvanceFromWelcome} />}
            {phase === "design"  && (
              <EditPhase
                ref={editPhaseRef}
                build={build}
                plan={plan}
                onPublish={() => setPhase("publish")}
              />
            )}
            {phase === "publish" && <PublishPhase build={build} onBack={() => setPhase("design")} />}
            {phase === "idea"    && <IdeaPhase  onAdvance={handleAdvanceFromIdea} />}
            {phase === "plan"    && <PlanPhase  onBack={handleBackToIdea} onGenerate={handleGenerate} />}
            {phase === "draft"   && <DraftPhase done={generateDone} error={generateError} />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
