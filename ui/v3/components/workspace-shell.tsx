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
// PhaseTracker removed — internal workflow steps not exposed to users.
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
import { streamGenerateSite, enrichContent, type GenerateResponse, type SSEEvent } from "@/lib/api";
import { type CollectedAnswer } from "@/components/phases/build-chat";
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
  const generatingRef = useRef(false); // concurrency guard — prevents double-build on fast double-click / autostart
  const editPhaseRef = useRef<EditPhaseHandle>(null);
  // Phase 58a — chat answers collected by BuildChatPanel during the build.
  // Updated via the onEnrich callback on DraftPhase; read in handleGenerate's
  // .then() to fire enrichContent in the background after the build lands.
  const chatAnswersRef = useRef<CollectedAnswer[]>([]);

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

    // Phase 58a: if the user just submitted a prompt on / and we're now
    // mounting on /workspace, the autostart flag is set and we have a brief.
    // Jump STRAIGHT to "draft" in this layoutEffect so the user never sees
    // the welcome page flash on /workspace. Without this, the sequence is
    // design → welcome (this layoutEffect) → draft (useEffect autostart),
    // which paints the welcome page for one frame and reads as "bounced
    // back to landing."
    const hasBriefContent = !!(currentBrief.business_name || currentBrief.extra_context);
    const autostartPending =
      typeof window !== "undefined" &&
      sessionStorage.getItem("pebble.autostart") === "1" &&
      hasBriefContent &&
      !currentBuild;

    if (autostartPending) {
      setPhase("draft");
      return;
    }

    // Welcome-bounce: ONLY when user has nothing in progress.
    // - hasBriefContent=true means a build is queued or in flight (don't bounce).
    // - generatingRef.current=true means a build just kicked off (don't bounce).
    // - resolvedPhase==="draft" means we're actively building (don't bounce).
    // Without these guards, this layoutEffect's second run (StrictMode dev OR
    // post-handleGenerate re-render) sees a stale autostartFlag and clobbers
    // the active draft state back to welcome.
    const isActivelyBuilding = hasBriefContent || generatingRef.current || resolvedPhase === "draft";
    if (!currentBuild && !isActivelyBuilding && (resolvedPhase === "design" || resolvedPhase === "publish")) {
      setPhase("welcome");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Phase 56a + 58b: auto-start generation when the user clicked Build from
  // the landing page. STRICT: only the explicit pebble.autostart flag triggers
  // a build. Previously had a self-healing "fire on /workspace mount if brief
  // exists" branch — but that auto-built stale briefs every time the user
  // navigated to /workspace from the dashboard, even when they wanted a
  // FRESH idea capture. Bad UX (and bad for the user's wallet — every fire
  // is a billed build).
  //
  // The planFirst escape hatch: if the user explicitly chose plan-first
  // mode, don't autostart — they want to see the plan preview first.
  useEffect(() => {
    const flagSet = sessionStorage.getItem("pebble.autostart") === "1";
    if (!flagSet) return;
    sessionStorage.removeItem("pebble.autostart");

    const currentBrief = getBrief();
    const currentBuild = getLastBuild();
    const hasBrief = !!(currentBrief.business_name || currentBrief.extra_context);
    const wantsPlan = currentBrief.planFirst === true;

    if (wantsPlan) return;
    if (!hasBrief) return;
    if (currentBuild) return;

    handleGenerate(() => Promise.resolve({} as GenerateResponse));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleAdvanceFromWelcome() {
    const currentBrief = getBrief();

    // Phase 58a / Phase 54c — signup gate. Unauthenticated visitors must
    // sign up before they can land on /workspace (proxy.ts middleware
    // would otherwise bounce them to /login, which feels broken — they
    // submitted a Build prompt, not a Sign In). Route to /signup with
    // ?redirect=/workspace so the brief is preserved in localStorage and
    // they autostart on return. Wait for auth to resolve so we don't
    // accidentally signup-route a logged-in user whose session is still
    // hydrating.
    if (!authLoading && !authUser && pathname === "/") {
      // Ensure the autostart flag is set so /workspace kicks off the
      // build automatically after signup completes.
      sessionStorage.setItem("pebble.autostart", "1");
      router.push(`/signup?redirect=${encodeURIComponent("/workspace")}`);
      return;
    }

    if (currentBrief.planFirst === true) {
      // Plan mode: show the plan preview before building.
      if (pathname === "/") {
        // Bypass view-transition (same reason as the standard-mode branch).
        router.push("/workspace#phase=plan");
      } else {
        setPhase("plan");
      }
    } else {
      // Standard mode: skip the questionnaire — go straight to build.
      if (pathname === "/") {
        // Flag for the auto-start useEffect above, then navigate to workspace.
        sessionStorage.setItem("pebble.autostart", "1");
        // Phase 58a — bypass safeStartViewTransition for this navigation.
        // The View Transitions wrap was swallowing the router.push silently
        // in some browser/Next combos (URL stayed at / after submit). Direct
        // router.push always works; the visual transition is non-essential
        // for this specific hop (welcome → workspace mount swap).
        router.push("/workspace");
      } else {
        // Already inside workspace — kick off generation immediately.
        handleGenerate(() => Promise.resolve({} as GenerateResponse));
      }
    }
  }

  function handleAdvanceFromIdea() {
    setBrief(getBrief());
    setPhase("plan");
  }

  function handleBackFromPlan() {
    // Back from plan always returns to welcome — "idea" questionnaire is no
    // longer in the standard flow (Phase 56a removed it). Clear planFirst so
    // the next Build click from welcome doesn't re-enter plan mode.
    patchBrief({ planFirst: false });
    setBrief(getBrief());
    setPhase("welcome");
  }

  // Plan phase → Draft phase → Design phase. Streams build progress via
  // /api/generate-stream (SSE), feeding real events into DraftPhase.
  // The kickOff param is accepted for API compatibility with PlanPhase
  // but is not used — we call streamGenerateSite directly so we can
  // feed live events into the draft animation.
  function handleGenerate(_kickOff: () => Promise<GenerateResponse>) {
    // Concurrency guard: one build at a time. Protects against double-click
    // from the landing page autostart and fast double-tap on mobile.
    if (generatingRef.current) return;
    generatingRef.current = true;

    // Phase 40i: clear planFirst so returning to welcome after a build
    // doesn't re-trigger the plan-first shortcut.
    patchBrief({ planFirst: false });
    setSseEvents([]);
    setGenerateDone(false);
    setGenerateError(null);
    setBuild(null);  // clear stale build so design phase doesn't show old site on error
    setBuildElapsedSec(null);
    generateStartedAtRef.current = Date.now();
    setPhase("draft");
    const brief = getBrief();

    // 12-minute hard timeout — Qwen 3.6 Plus multi-page builds typically
    // run 60-300s but the eval+repair loop (PEBBLE_AUTO_REPAIR=true) can
    // push past the prior 5-min ceiling. Bumped to 12 min so a normal
    // build completes cleanly; real engine hangs still surface inside the
    // window. Matches the engine-side _TIMEOUT_S=900s SSE generator
    // timeout so neither side gives up before the other.
    const timeoutMs = 12 * 60 * 1000;
    const timeoutP = new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error("Build timed out — please try again.")), timeoutMs),
    );

    Promise.race([
      streamGenerateSite(brief, (event) => {
        setSseEvents((prev) => [...prev, event]);
      }),
      timeoutP,
    ])
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
        // Phase 58a — fire enrichment in background if the user answered
        // chat questions during the build. React effects run before the
        // 600ms macrotask fires, so chatAnswersRef is populated by then.
        // Fire-and-forget: the user transitions to "ready" regardless.
        const buildSlug = response.slug;
        setTimeout(() => {
          const answers = chatAnswersRef.current;
          if (answers.length > 0) {
            const facts = answers.map((a) => ({ key: a.questionId, value: a.answer }));
            enrichContent(buildSlug, facts).catch(() => {
              /* best-effort — enrichment failure doesn't block the user */
            });
          }
          // Phase 49 — draft → ready → (user clicks) → design.
          setPhase("ready");
        }, 600);
      })
      .catch((e: Error) => {
        setGenerateError(e.message || "Build failed");
      })
      .finally(() => {
        generatingRef.current = false;
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
      if (build) setPhase("integrations");
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

        {/* Center column — phase-specific content.
            Phase 58e (2026-05-22): removed the AnimatePresence + motion.div
            wrap. With React 19 + framer-motion in this project, the wrap
            mounted the new key in `hidden` initial state (opacity 0,
            translateY 24px) and never animated to `visible` — leaving the
            workspace permanently invisible whenever you navigated between
            phases. Plain conditional rendering works. If we want the
            cinematic transition back later, wrap individual phase
            components with their own motion.div with explicit transitions
            rather than relying on AnimatePresence at the shell level. */}
        <div className={`flex-1 flex flex-col ${isWelcome ? "" : "overflow-hidden"}`}>
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
          {phase === "draft"   && (
            <DraftPhase
              done={generateDone}
              error={generateError}
              sseEvents={sseEvents}
              onRetry={() => handleGenerate(() => Promise.resolve({} as GenerateResponse))}
              onEnrich={(answers) => { chatAnswersRef.current = answers; }}
            />
          )}
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
