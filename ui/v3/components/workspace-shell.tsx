"use client";

import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { motion, AnimatePresence, MotionConfig } from "framer-motion";
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
import { streamGenerateSite, type GenerateResponse, type SSEEvent } from "@/lib/api";
import { usePhase, phaseToStage, type Phase } from "@/components/phases/use-phase";
import { STANDARD_S, EASE_CINEMATIC, phaseVariants, chipDeck, fadeUp, withReducedMotion } from "@/lib/motion";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";
import { safeStartViewTransition } from "@/lib/view-transitions";
import { WelcomePhase } from "@/components/phases/welcome-phase";
import { IdeaPhase } from "@/components/phases/idea-phase";
import { PlanPhase } from "@/components/phases/plan-phase";
import { DraftPhase } from "@/components/phases/draft-phase";
import { EditPhase, type EditPhaseHandle } from "@/components/phases/edit-phase";
import { PublishPhase } from "@/components/phases/publish-phase";

// Fires synchronously before paint on the client; falls back to useEffect
// on the server (where there is no DOM) to suppress the SSR warning.
const useIsomorphicLayoutEffect =
  typeof window !== "undefined" ? useLayoutEffect : useEffect;

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
  const [sseEvents, setSseEvents] = useState<SSEEvent[]>([]);
  const editPhaseRef = useRef<EditPhaseHandle>(null);

  const safePhaseVariants = useMemo(() => withReducedMotion(phaseVariants), []);
  const safeChipDeck = useMemo(() => withReducedMotion(chipDeck), []);
  const safeFadeUp = useMemo(() => withReducedMotion(fadeUp), []);

  // Hydrate from localStorage before the first paint so the user never sees
  // an "empty" brief or the wrong phase. useLayoutEffect fires synchronously
  // after the commit but before the browser paints; useEffect would show the
  // wrong state for one frame (causes the logo / project-name flicker).
  // Phase resolution reads the hash directly so it doesn't race with
  // usePhase's own layoutEffect that also reads the hash.
  useIsomorphicLayoutEffect(() => {
    const currentBrief = getBrief();
    const currentBuild = getLastBuild();
    const currentPlan = getPlan();
    setBrief(currentBrief);
    setBuild(currentBuild);
    setPlan(currentPlan);
    // Resolve the actual phase: prefer the URL hash (usePhase also reads this,
    // but we check it here so we don't race with its layoutEffect).
    const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ""));
    const hashPhase = hashParams.get("phase");
    const resolvedPhase: Phase = (
      hashPhase && ["welcome","idea","plan","draft","design","publish"].includes(hashPhase)
        ? hashPhase as Phase
        : phase
    );
    if (!currentBuild && (resolvedPhase === "design" || resolvedPhase === "draft" || resolvedPhase === "publish")) {
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
      // Wrap the router.push in a View Transition so Chrome/Edge/Safari
      // morph the layout natively instead of cutting between routes.
      // Firefox + older browsers fall through to a plain router.push and
      // get the AnimatePresence-based fade.
      safeStartViewTransition(() => {
        router.push("/workspace#phase=idea");
      });
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

  // Plan phase → Draft phase → Design phase. Streams build progress via
  // /api/generate-stream (SSE), feeding real events into DraftPhase.
  // The kickOff param is accepted for API compatibility with PlanPhase
  // but is not used — we call streamGenerateSite directly so we can
  // feed live events into the draft animation.
  function handleGenerate(_kickOff: () => Promise<GenerateResponse>) {
    setSseEvents([]);
    setGenerateDone(false);
    setGenerateError(null);
    setPhase("draft");
    const brief = getBrief();
    streamGenerateSite(brief, (event) => {
      setSseEvents((prev) => [...prev, event]);
    })
      .then((response) => {
        const built = {
          slug: response.slug,
          preview_url: response.preview_url,
          industry_intel_key: response.industry_intel_key,
          // Surface the live `next dev` URL so the iframe can load the
          // running app directly. preview_url 404s for Next.js sites
          // (no static index.html on disk). dev_server.url is the live
          // process URL — only valid while the engine is running.
          dev_server: response.dev_server ?? null,
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
      <motion.div
        variants={safeChipDeck}
        initial="hidden"
        animate="visible"
        className="flex items-center gap-2"
      >
        <motion.button
          variants={safeFadeUp}
          onClick={() => editPhaseRef.current?.openGallery()}
          className={`${interactions.chip} flex items-center gap-2 ${type.label} text-foreground bg-card border border-border px-3 h-10 rounded-full`}
          title="Add a DNA-themed section"
        >
          <Plus className="w-4 h-4" /> Add section
        </motion.button>
        <motion.button
          variants={safeFadeUp}
          onClick={() => { editPhaseRef.current?.openHistory(); }}
          title="Version history"
          className={`${interactions.iconButton} w-10 h-10 rounded-full flex items-center justify-center text-graphite hover:text-charcoal dark:text-pebble dark:hover:bg-stone/40 dark:hover:text-sand`}
          aria-label="Open version history"
        >
          <History className="w-5 h-5" />
        </motion.button>
        <motion.button
          variants={safeFadeUp}
          onClick={() => setPhase("publish")}
          className={`${interactions.button} bg-primary text-primary-foreground px-4 h-10 rounded-full flex items-center gap-2 ${type.label}`}
        >
          <Rocket className="w-4 h-4" /> Publish
        </motion.button>
      </motion.div>
    ) : null;

  const isWelcome = phase === "welcome";

  return (
    // reducedMotion="user" makes framer-motion respect the OS prefers-reduced-motion
    // preference for animations that bypass the Variants path — most importantly,
    // the layoutId/shared-element morphs that withReducedMotion() can't reach.
    <MotionConfig reducedMotion="user">
    <div className={`min-h-screen flex flex-col ${isWelcome ? "bg-black" : ""}`}>
      {/* TopNav persists across all phase changes — but the welcome phase
          owns its own full-bleed dark canvas (and renders the Pebble logo
          itself, fading in after Start Building Free is clicked). */}
      {!isWelcome && <TopNav projectName={projectName} rightSlot={topNavRightSlot} />}

      <div className={`flex flex-1 ${isWelcome ? "bg-black" : "overflow-hidden"}`}>
        {/* Rail is persistent — visible state animates instead of mounting/unmounting.
            On welcome the rail's width and opacity collapse to 0 so it visually
            disappears but stays in the DOM, preserving its layoutId children for
            cross-phase morphs. */}
        <motion.aside
          aria-hidden={!showLeftRail}
          inert={!showLeftRail}
          style={{ viewTransitionName: "rail" }}
          animate={{
            width:   showLeftRail ? 240 : 0,
            opacity: showLeftRail ? 1   : 0,
          }}
          transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
          className={`flex flex-col gap-1 p-4 overflow-hidden shrink-0 ${
            showLeftRail ? "bg-card border-r border-border" : ""
          }`}
        >
          <div className="mb-6 px-1">
            <h2 className={`${type.heading.m} text-primary`}>Your Build Plan</h2>
            <p className={`${type.caption} opacity-70`}>AI-Guided Strategy</p>
          </div>
          <nav className="flex flex-col gap-1">
            {BUILD_PLAN.map((s) => {
              const isActive = s.id === railStage;
              return (
                <button
                  key={s.id}
                  onClick={() => handleJumpPhase(s.id)}
                  className={`${interactions.chip} relative flex items-center gap-2 p-3 rounded-lg text-left ${type.label} ${
                    isActive ? "text-primary" : "text-muted-foreground hover:text-foreground"
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
            variants={safePhaseVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            className={`flex-1 flex flex-col ${isWelcome ? "" : "overflow-hidden"}`}
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
            {phase === "draft"   && <DraftPhase done={generateDone} error={generateError} sseEvents={sseEvents} />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
    </MotionConfig>
  );
}
