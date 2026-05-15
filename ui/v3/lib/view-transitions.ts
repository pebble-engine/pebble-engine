/**
 * Thin wrapper over the browser's View Transitions API.
 *
 * Chrome / Edge / Safari (and other Chromium browsers) implement
 * document.startViewTransition; Firefox does not (as of 2026-05).
 * Calling code wraps a state-changing callback in
 * safeStartViewTransition() and gets the native cross-route morph
 * where supported, falling back to a synchronous callback elsewhere
 * — at which point our existing framer-motion AnimatePresence
 * handles the inter-phase transitions.
 *
 * Elements whose layout / size / position should morph across the
 * transition need a CSS `view-transition-name` set, usually via
 * inline style on the persistent shell elements (TopNav, Rail).
 */

// Augment the global Document type so TypeScript doesn't complain
// about the still-experimental method. We only call it inside the
// capability check so the cast is safe.
type DocumentWithViewTransition = Document & {
  startViewTransition?: (cb: () => void) => unknown;
};

/** Capability check. Safe to call on the server (returns false). */
export function supportsViewTransitions(): boolean {
  if (typeof document === "undefined") return false;
  return typeof (document as DocumentWithViewTransition).startViewTransition === "function";
}

/** Run `callback` inside a native View Transition when the browser
 *  supports it; otherwise call it synchronously. The synchronous
 *  fallback is the same code path that runs in unsupported browsers,
 *  so any framer-motion AnimatePresence wrapping the changed UI still
 *  animates the transition. */
export function safeStartViewTransition(callback: () => void): void {
  if (supportsViewTransitions()) {
    (document as DocumentWithViewTransition).startViewTransition!(callback);
  } else {
    callback();
  }
}
