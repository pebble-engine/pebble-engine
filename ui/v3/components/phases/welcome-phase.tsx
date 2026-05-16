"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { InfiniteGrid } from "@/components/ui/the-infinite-grid";
import { PromptInputBox } from "@/components/ui/ai-prompt-box";
import {
  patchBrief,
  getUserProfile,
  getLastBuild,
  getBrief,
} from "@/lib/state";
import { fadeUp, STANDARD_S, SHORT_S, EASE_CINEMATIC, withReducedMotion } from "@/lib/motion";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

/**
 * Welcome phase — the "first encounter" screen.
 *
 * Renders the InfiniteGrid background + a centered prompt box + starter
 * chips + the migrate entry link. Lives at ``/`` (no hash) and inside
 * ``/workspace#phase=welcome`` for direct hits. Submitting the prompt
 * patches the brief with the freeform idea and calls ``onAdvance()``,
 * which is wired in the shell to push to ``/workspace#phase=idea``.
 *
 * Visually distinctive — full-bleed grid, big headline, no project chrome.
 * The shell hides the Build Plan rail during this phase so the user
 * isn't staring at navigation for a project that doesn't exist yet.
 */

const STARTER_CHIPS = [
  { label: "Business website", prompt: "A business website that introduces what I do and lets people reach out." },
  { label: "Online store",     prompt: "An online store where customers can browse products and check out." },
  { label: "Portfolio",        prompt: "A portfolio site that showcases my work and bio." },
  { label: "Booking site",     prompt: "A booking site where clients can schedule appointments with me." },
  { label: "Restaurant menu",  prompt: "A restaurant site with my menu, hours, and a reservation option." },
  { label: "Real estate",      prompt: "A real-estate page that showcases listings and lets buyers contact me." },
];

type Props = {
  onAdvance: () => void;
};

export function WelcomePhase({ onAdvance }: Props) {
  const router = useRouter();
  const [prefill, setPrefill] = useState<string | null>(null);
  const [firstName, setFirstName] = useState<string | null>(null);
  const [resumeName, setResumeName] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  const safeFadeUp = useMemo(() => withReducedMotion(fadeUp), []);

  useEffect(() => {
    const profile = getUserProfile();
    setFirstName(profile.firstName || null);
    // Returning user detection: if there's an existing build in
    // sessionStorage, surface a one-click resume tile so they don't have
    // to manually navigate to /workspace or /dashboard. Read after mount
    // to keep the SSR output deterministic (no storage access on server).
    const build = getLastBuild();
    if (build?.slug) {
      const brief = getBrief();
      const name = (brief.business_name as string) || "your last project";
      setResumeName(name);
    }
    setMounted(true);
  }, []);

  const handleResume = () => {
    router.push("/workspace#phase=design");
  };

  const handleSend = (message: string, files?: File[]) => {
    if (typeof window === "undefined") return;
    patchBrief({
      extra_context: message,
      business_name: "Untitled Project",
      user_first_name: firstName || undefined,
    });
    if (files && files.length > 0) {
      sessionStorage.setItem(
        "pebble.pendingFiles",
        JSON.stringify(files.map((f) => ({ name: f.name, type: f.type, size: f.size }))),
      );
    }
    onAdvance();
  };

  const headline = firstName
    ? `What's on your mind, ${firstName}?`
    : "What would you like to build today?";

  return (
    <InfiniteGrid className="flex-1 min-h-0">
      <main className="relative z-10 flex flex-col items-center text-center px-4 max-w-3xl mx-auto space-y-8 pointer-events-none py-24">
        <div className="space-y-3 pointer-events-auto min-h-[170px]">
          <AnimatePresence mode="wait">
            <motion.h1
              key={firstName ?? "anon"}
              variants={safeFadeUp}
              initial="hidden"
              animate="visible"
              exit={{ opacity: 0, y: -8, transition: { duration: STANDARD_S, ease: EASE_CINEMATIC } }}
              className={`${type.display.xl} text-foreground drop-shadow-sm`}
            >
              {headline}
            </motion.h1>
          </AnimatePresence>
          <p className={`${type.body.l} text-muted-foreground max-w-xl mx-auto`}>
            Tell me in your own words. I&apos;ll handle the technical parts.
          </p>
        </div>

        <div className="w-full max-w-2xl pointer-events-auto">
          <PromptInputBox
            onSend={handleSend}
            placeholder={
              prefill ??
              "Example: I run a bakery in Brooklyn and I want a website where customers can see my menu and order online."
            }
          />
        </div>

        <div className="flex flex-wrap justify-center gap-2 pointer-events-auto">
          {STARTER_CHIPS.map((chip) => (
            <button
              key={chip.label}
              onClick={() => setPrefill(chip.prompt)}
              className={`${interactions.chip} px-4 py-2 bg-card border border-border rounded-full text-foreground ${type.label}`}
            >
              {chip.label}
            </button>
          ))}
        </div>

        {/* Returning user resume — only when there's an existing build in
            sessionStorage. Sits between the starter chips and the migrate
            link so it's findable but doesn't compete with the primary
            "type your idea" CTA for first-visitor attention. */}
        {mounted && resumeName && (
          <motion.button
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0, transition: { delay: 0.3, duration: SHORT_S, ease: EASE_CINEMATIC } }}
            onClick={handleResume}
            className={`${interactions.focusRing} pointer-events-auto group flex items-center gap-2 px-5 py-3 bg-secondary/10 hover:bg-secondary/20 border border-secondary/30 rounded-full text-secondary transition-colors duration-100 ease-out active:bg-secondary/30 motion-reduce:active:bg-secondary/20 ${type.label}`}
          >
            <span>Continue working on</span>
            <span className="text-foreground">{resumeName}</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </motion.button>
        )}

        {/* Migration entry — alternative to typing a fresh idea. */}
        <Link
          href="/migrate"
          className={`${interactions.link} pointer-events-auto text-sm text-muted-foreground flex items-center gap-2 mt-2`}
        >
          <span className="opacity-80">Already have a site?</span>
          <span className="font-semibold underline underline-offset-2">Bring it over →</span>
        </Link>

        <p className="pointer-events-auto text-sm text-muted-foreground max-w-lg mx-auto pt-8">
          You&apos;ll see exactly what I&apos;m doing every step of the way. Nothing is final until you say it is.
        </p>
      </main>
    </InfiniteGrid>
  );
}
