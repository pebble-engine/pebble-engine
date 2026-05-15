"use client";

import { useCallback, useEffect, useState } from "react";

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

export type Phase = "idea" | "plan" | "draft" | "design" | "publish";

export const PHASE_ORDER: Phase[] = ["idea", "plan", "draft", "design", "publish"];

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

  // Hydrate from the hash on mount. SSR-safe because we only run this
  // in useEffect, after the first paint. The initial value matches what
  // the server would render so there's no hydration mismatch.
  useEffect(() => {
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
