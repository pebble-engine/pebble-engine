"use client";

import Link from "next/link";
import type { ReactNode } from "react";

/**
 * Shared chrome for marketing-surface pages — auth, billing, legal, etc.
 *
 * Dark canvas + decorative gradient blobs + glass Pebble. wordmark in the
 * top-left. The children render centered inside the main area; pages
 * supply their own form/content card (typically white-on-dark for legible
 * forms).
 *
 * Uses Instrument Sans (matches the landing) and ignores the user's
 * theme toggle on purpose — these surfaces are dark by design so the
 * whole pre-auth + post-checkout flow feels of-a-piece with the landing.
 */
export function MarketingShell({ children }: { children: ReactNode }) {
  return (
    <div className="relative min-h-screen flex flex-col bg-black text-white overflow-hidden font-[family-name:var(--font-plus-jakarta-sans)]">
      {/* Decorative blobs. */}
      <div
        aria-hidden
        className="pointer-events-none absolute -top-[10%] left-[20%] w-[600px] h-[600px] bg-blue-900/20 blur-[120px] mix-blend-screen"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -bottom-[10%] right-[15%] w-[500px] h-[500px] bg-indigo-900/20 blur-[120px] mix-blend-screen"
      />

      {/* Pebble wordmark — glass pill, links to landing root. */}
      <header className="relative z-10 px-6 py-5">
        <Link
          href="/"
          className="inline-flex items-center px-4 py-2 rounded-full bg-stone-900/40 backdrop-blur-xl border border-white/15 text-lg font-semibold"
        >
          <span className="bg-gradient-to-b from-white via-white to-[#b4c0ff] bg-clip-text text-transparent">
            Pebble.
          </span>
        </Link>
      </header>

      <main className="relative z-10 flex-1 flex items-center justify-center px-6 py-10">
        {children}
      </main>
    </div>
  );
}

/**
 * White card container for forms/content inside MarketingShell. Pages
 * compose their own form fields inside, but the card chrome (rounded,
 * white, soft shadow) is shared.
 */
export function MarketingCard({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={`w-full max-w-md p-8 rounded-2xl bg-white text-[#1a1a1a] shadow-[0_24px_80px_rgba(0,0,0,0.4)] space-y-6 ${className}`}
    >
      {children}
    </div>
  );
}

/**
 * Wider variant of MarketingCard for prose-heavy pages — privacy, terms,
 * help, etc. Same dark-on-white card chrome, max-w-3xl, generous padding.
 */
export function MarketingProse({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={`w-full max-w-3xl p-8 sm:p-12 rounded-2xl bg-white text-[#1a1a1a] shadow-[0_24px_80px_rgba(0,0,0,0.4)] ${className}`}
    >
      {children}
    </div>
  );
}
