"use client";

import { useCallback, useEffect, useLayoutEffect, useState } from "react";

// Hash hydration must happen before paint, otherwise users navigating
// from / to /workspace#phase=idea see a one-frame flash of the default
// "design" phase before the hash override snaps in. useLayoutEffect
// fires synchronously after DOM mutations but before paint. It's a no-op
// on the server (SSR has no DOM), so swap to useEffect there to silence
// React's "useLayoutEffect during SSR" warning.
const useIsomorphicLayoutEffect = typeof window !== "undefined" ? useLayoutEffect : useEffect;

/**
 * Phase routing inside the unified workspace shell.
 *
 * The previous flow hopped between four post-welcome pages (/intake,
 * /thinking, /plan-review, /workspace) — each a router.push, each its
 * own scroll-to-top, each a full layout swap. The unified workspace
 * keeps one URL (``/workspace``) and tracks the current step in the URL
 * hash so back/forward + reload still work and links remain shareable.
 *
 * The hash form is ``#phase=plan`` (not just ``#plan``) so we can grow
 * other hash-bound state later without colliding.
 */

export type Phase = "welcome" | "idea" | "plan" | "draft" | "design" | "publish";

export const PHASE_ORDER: Phase[] = ["welcome", "idea", "plan", "draft", "design", "publish"];

/**
 * Phase → Build-Plan-rail "stage" mapping. The rail has seven steps
 * (Idea, Plan, Draft, Design, Features, Setup, Publish) but our phase
 * machinery is finer-grained: "welcome" and "idea" both belong to the
 * Idea stage, just with different chrome (welcome hides the rail, idea
 * shows the chip questionnaire).
 */
export function phaseToStage(p: Phase): string {
  if (p === "welcome") return "idea";
  return p;
}

const HASH_KEY = "phase";


function readPhaseFromHash(): Phase | null {
  if (typeof window === "undefined") return null;
  const hash = window.location.hash.replace(/^#/, "");
  if (!hash) return null;
  const params = new URLSearchParams(hash);
  const candidate = params.get(HASH_KEY);
  if (!candidate) return null;
  if ((PHASE_ORDER as string[]).includes(candidate)) return candidate as Phase;
  return null;
}


function writePhaseToHash(phase: Phase): void {
  if (typeof window === "undefined") return;
  const url = new URL(window.location.href);
  const hash = new URLSearchParams(url.hash.replace(/^#/, ""));
  hash.set(HASH_KEY, phase);
  const newHash = `#${hash.toString()}`;
  if (newHash !== url.hash) {
    url.hash = newHash;
    window.history.replaceState(null, "", url.toString());
  }
}


export function usePhase(initial: Phase = "design"): [Phase, (next: Phase) => void] {
  const [phase, setPhaseState] = useState<Phase>(initial);

  // Hydrate from the hash before the first paint, so client navigation
  // (router.push from / to /workspace#phase=idea) doesn't flash the
  // default "design" view before the hash override snaps in. The initial
  // useState value matches what the server would render, so hydration
  // still reconciles cleanly — this just runs immediately after.
  useIsomorphicLayoutEffect(() => {
    const fromHash = readPhaseFromHash();
    if (fromHash && fromHash !== phase) {
      setPhaseState(fromHash);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Reflect browser back/forward into our state. The hashchange event
  // fires AFTER the URL has updated, so reading the hash now gives the
  // new value.
  useEffect(() => {
    function onHashChange() {
      const fromHash = readPhaseFromHash();
      if (fromHash) setPhaseState(fromHash);
    }
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const setPhase = useCallback((next: Phase) => {
    setPhaseState(next);
    writePhaseToHash(next);
    // Phase changes that scroll back to the top read more naturally in
    // a wizard — the user expects a "new screen" feel even though it's
    // the same URL.
    if (typeof window !== "undefined") {
      window.scrollTo({ top: 0, behavior: "instant" as ScrollBehavior });
    }
  }, []);

  return [phase, setPhase];
}
