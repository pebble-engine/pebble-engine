"use client";

import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { motion, AnimatePresence, MotionConfig } from "framer-motion";
import {
  Rocket,
  History,
  Plus,
} from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { DashboardSidebar } from "@/components/workspace/dashboard-sidebar";
import { PhaseTracker } from "@/components/workspace/phase-tracker";
import {
  getBrief,
  getLastBuild,
  getPlan,
  setLastBuild,
  patchBrief,
  clearBriefForNewProject,
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
import { ReadyPhase } from "@/components/phases/ready-phase";
import { EditPhase, type EditPhaseHandle } from "@/components/phases/edit-phase";
import { PublishPhase } from "@/components/phases/publish-phase";
import { IntegrationsPhase } from "@/components/phases/integrations-phase";
import { PlanPickerModal } from "@/components/plan-picker-modal";
import { fetchSubscription } from "@/lib/api";
import { useAuth } from "@/components/auth-provider";
import { getUserProfile } from "@/lib/state";

// Fires synchronously before paint on the client; falls back to useEffect
// on the server (where there is no DOM) to suppress the SSR warning.
const useIsomorphicLayoutEffect =
  typeof window !== "undefined" ? useLayoutEffect : useEffect;

/**
 * Phase 40i — plan-first flow; reads brief.planFirst (set by DetectiveInput)
 * and inserts a /api/plan preview step before /api/generate. When
 * brief.planFirst === true, handleAdvanceFromWelcome routes welcome → plan
 * instead of welcome → idea, the PlanPhase back-button returns to welcome
 * (not idea), and the flag is cleared before /api/generate fires so that
 * subsequent welcome → advance flows behave normally if the user comes back.
 */

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

/* Phase 46 (2026-05-22) — the old vertical "Your Build Plan" rail
   (Idea/Plan/Draft/Design/Features/Setup/Publish) lived here. Marc
   reviewed the workspace and called it "too wizard-y, not workspace-y"
   compared to Base44's left-nav (Home/All/Templates/Integrations/
   Community). We now share that nav with /dashboard via DashboardSidebar.
   The per-project phase progress moves to a horizontal PhaseTracker at
   the top of the main content area (hidden on welcome + design). */


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
  // Phase 49 — elapsed seconds for the build. Captured at the moment we
  // kick off /api/generate-stream so the Ready-phase summary can show
  // "Built in 47s". Cleared on new generation.
  const [buildElapsedSec, setBuildElapsedSec] = useState<number | null>(null);
  const generateStartedAtRef = useRef<number | null>(null);
  const editPhaseRef = useRef<EditPhaseHandle>(null);

  // Phase 54c — plan-picker overlay state. Marc's "offer wall during
  // build" UX: show the picker while the build is in flight so the
  // user reads tiers as a perceived-speed boost instead of staring at
  // a progress bar. Triggered by the needs_plan_selection flag set
  // during signup (Phase 54b) — surfaced in /api/billing/subscription.
  // We only fetch the flag once per shell mount; clearing happens via
  // the picker's own select-plan call.
  const { user: authUser, loading: authLoading } = useAuth();
  const [needsPlanPick, setNeedsPlanPick] = useState(false);
  const [planPickFetched, setPlanPickFetched] = useState(false);

  useEffect(() => {
    // Wait for auth to resolve so we don't fire a Bearer request before
    // there's a session token. Anonymous visitors get no picker.
    if (authLoading || !authUser) {
      setPlanPickFetched(true);
      return;
    }
    let cancelled = false;
    fetchSubscription()
      .then((sub) => {
        if (cancelled) return;
        setNeedsPlanPick(Boolean((sub as { needs_plan_selection?: boolean }).needs_plan_selection));
      })
      .catch(() => {
        // Network / auth glitch — don't block the user on the picker.
        if (!cancelled) setNeedsPlanPick(false);
      })
      .finally(() => {
        if (!cancelled) setPlanPickFetched(true);
      });
    return () => {
      cancelled = true;
    };
  }, [authUser, authLoading]);

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
    // Phase 40i: if the user toggled "Plan first" in DetectiveInput, skip
    // the idea questionnaire and go straight to the plan preview.
    const currentBrief = getBrief();
    const targetPhase: Phase = currentBrief.planFirst === true ? "plan" : "idea";

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
        router.push(`/workspace#phase=${targetPhase}`);
      });
    } else {
      setPhase(targetPhase);
    }
  }

  function handleAdvanceFromIdea() {
    setBrief(getBrief());
    setPhase("plan");
  }

  function handleBackFromPlan() {
    // Phase 40i: if the user arrived via plan-first, back goes to welcome.
    // Clear the planFirst flag so the normal flow is restored.
    const currentBrief = getBrief();
    if (currentBrief.planFirst === true) {
      patchBrief({ planFirst: false });
      setBrief(getBrief());
      setPhase("welcome");
    } else {
      setPhase("idea");
    }
  }

  // Plan phase → Draft phase → Design phase. Streams build progress via
  // /api/generate-stream (SSE), feeding real events into DraftPhase.
  // The kickOff param is accepted for API compatibility with PlanPhase
  // but is not used — we call streamGenerateSite directly so we can
  // feed live events into the draft animation.
  function handleGenerate(_kickOff: () => Promise<GenerateResponse>) {
    // Phase 40i: clear planFirst so returning to welcome after a build
    // doesn't re-trigger the plan-first shortcut.
    patchBrief({ planFirst: false });
    setSseEvents([]);
    setGenerateDone(false);
    setGenerateError(null);
    setBuildElapsedSec(null);
    generateStartedAtRef.current = Date.now();
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
        // Capture elapsed for ReadyPhase summary.
        if (generateStartedAtRef.current) {
          setBuildElapsedSec(Math.round((Date.now() - generateStartedAtRef.current) / 1000));
        }
        // Phase 49 — draft → ready → (user clicks) → design. Gives the
        // user a real "site is live" moment with a summary card instead
        // of snapping silently into the editor. Tiny pause lets the
        // draft "Ready" pulse paint once before the switch.
        setTimeout(() => setPhase("ready"), 600);
      })
      .catch((e: Error) => {
        setGenerateError(e.message || "Build failed");
      });
  }

  function handleJumpPhase(target: Phase | "features" | "setup") {
    if (target === "publish") {
      // Publish is only meaningful once we've generated something.
      if (build) setPhase("publish");
      return;
    }
    if (target === "features") {
      // Phase 56a: Integrations panel — available once a site is built.
      if (build) setPhase("integrations" as Phase);
      return;
    }
    if (target === "setup") {
      // Setup has no dedicated phase yet — surface inside design.
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
    <div
      data-workspace-theme={isWelcome ? undefined : "mono"}
      className={`min-h-screen-safe flex flex-col ${isWelcome ? "bg-black" : ""}`}
    >
      {/* TopNav persists across all phase changes — but the welcome phase
          owns its own full-bleed dark canvas (and renders the Pebble logo
          itself, fading in after Start Building Free is clicked). */}
      {!isWelcome && (
        <TopNav
          projectName={projectName}
          rightSlot={topNavRightSlot}
          onProjectNameChange={(next) => {
            patchBrief({ business_name: next });
            // Force re-read so the next render picks up the new name
            // without waiting for the next phase change.
            setBrief(getBrief());
          }}
          onNewProject={() => {
            // 2026-05-20 Phase 15a: wipe brief + plan + last build so the
            // questionnaire opens blank. Navigates to welcome to start
            // fresh. Doesn't touch user profile or auth.
            clearBriefForNewProject();
            setBrief({});
            setPlan(null);
            setBuild(null);
            router.push("/workspace#phase=welcome");
            setPhase("welcome");
          }}
        />
      )}

      <div className={`flex flex-1 ${isWelcome ? "bg-black" : "overflow-hidden"}`}>
        {/* Phase 46 — shared dashboard sidebar (same one used on /dashboard,
            /integrations, /community/*) replaces the per-project rail. The
            workspace now feels like a coherent product surface across all
            logged-in routes, not a wizard. Hidden on welcome (the marketing
            canvas is full-bleed). */}
        {showLeftRail && <DashboardSidebar />}

        {/* Center column — phase-specific content. AnimatePresence mode="wait"
            ensures the outgoing phase finishes its exit before the incoming
            one mounts. The horizontal PhaseTracker sits above it as a subtle
            breadcrumb (renders nothing on welcome / design). */}
        <div className={`flex-1 flex flex-col ${isWelcome ? "" : "overflow-hidden"}`}>
          {!isWelcome && (
            <PhaseTracker
              current={phase}
              onJump={handleJumpPhase}
              buildExists={!!build}
            />
          )}
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
              {phase === "plan"    && <PlanPhase  onBack={handleBackFromPlan} planFirst={brief.planFirst === true} onGenerate={handleGenerate} />}
              {phase === "draft"   && <DraftPhase done={generateDone} error={generateError} sseEvents={sseEvents} />}
              {phase === "ready"   && (
                <ReadyPhase
                  build={build}
                  elapsedSeconds={buildElapsedSec ?? undefined}
                  onOpenEditor={() => setPhase("design")}
                  onPublish={() => setPhase("publish")}
                />
              )}
              {(phase as string) === "integrations" && (
                <IntegrationsPhase onBack={() => setPhase("design")} />
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {/* Phase 54c — plan-picker overlay. Marc's "offer wall during
          build" UX: mounts on top of the workspace shell whenever the
          authenticated user still has needs_plan_selection=true. The
          build (if any) streams underneath; the picker is the time-
          filler that doubles as upgrade prompt. Skip on welcome — the
          marketing canvas owns the visitor and shouldn't be obscured.
          The fetched gate is the one signal — we don't manually open
          this from any phase transition. */}
      {planPickFetched && needsPlanPick && !isWelcome && (
        <PlanPickerModal
          firstName={getUserProfile().firstName || null}
          onPlanSelected={() => setNeedsPlanPick(false)}
        />
      )}
    </div>
    </MotionConfig>
  );
}
