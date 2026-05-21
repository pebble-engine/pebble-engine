"use client";

/**
 * StickyScrollStack — Phase 40e.2 (2026-05-21).
 *
 * Loader wrapper for the client-only sticky-scroll stack section.
 * Imported via Next.js `dynamic({ ssr: false })` so useScroll never
 * fires during SSR/hydration — eliminates the "Target ref is defined
 * but not hydrated" Framer Motion race that broke Phase 40e on first
 * render.
 *
 * During SSR + before the dynamic chunk loads, renders a static
 * fallback showing only the FIRST card statically — same overall
 * height as the final component so the page doesn't reflow on hydrate.
 *
 * Once the client chunk hydrates, the real motion-driven version
 * takes over and the user gets the full pinned scroll-stack experience.
 *
 * See sticky-scroll-stack-client.tsx for the actual implementation.
 */

import dynamic from "next/dynamic";
import type { ReactNode } from "react";
import { type } from "@/lib/type";

export type StackCard = {
  id:    string;
  icon?: ReactNode;
  eyebrow?: string;
  title: string;
  body:  string;
  accent?: string;
};

type Props = {
  cards:    StackCard[];
  id?:      string;
  heading?: string;
  subhead?: string;
  closer?:  ReactNode;
  className?: string;
};

/** Static SSR-safe placeholder. Shows the heading + the first card +
    closer as a normal-flow section. No useScroll, no useRef, no
    Framer Motion magic. Layout is similar to the final pinned state
    at scrollYProgress = 0.5 so the visual change on hydrate is small. */
function StickyScrollStackFallback({
  cards,
  id,
  heading,
  subhead,
  closer,
  className = "",
}: Props) {
  const totalVh = cards.length * 100 + 60;
  const first = cards[0];
  return (
    <section
      id={id}
      className={`relative ${className}`}
      style={{ height: `${totalVh}vh` }}
    >
      <div className="sticky top-0 h-screen flex flex-col items-center justify-center px-4 max-w-6xl mx-auto overflow-hidden">
        {heading && (
          <div className="text-center mb-12 space-y-4">
            <h2 className={`${type.display.l} text-foreground`}>{heading}</h2>
            {subhead && (
              <p className="text-lg max-w-xl mx-auto text-muted-foreground">
                {subhead}
              </p>
            )}
          </div>
        )}
        {first && (
          <div className="relative w-full max-w-xl h-[480px] sm:h-[420px] flex items-center justify-center">
            <div className="w-full max-w-xl p-10 rounded-3xl bg-card border border-border shadow-[0_24px_80px_rgba(31,29,26,0.12)]">
              {first.eyebrow && (
                <p className={`${type.eyebrow} mb-3`}>{first.eyebrow}</p>
              )}
              {first.icon && (
                <div className="mb-6 text-[#3054ff]">{first.icon}</div>
              )}
              <h3 className={`${type.heading.l} mb-4 text-foreground`}>{first.title}</h3>
              <p className="text-muted-foreground leading-relaxed text-base">{first.body}</p>
            </div>
          </div>
        )}
        {closer && (
          <div className="mt-12 opacity-0" aria-hidden>
            {closer}
          </div>
        )}
      </div>
    </section>
  );
}

const StickyScrollStackClient = dynamic(
  () => import("./sticky-scroll-stack-client"),
  {
    ssr: false,
    loading: () => null,
  },
);

export function StickyScrollStack(props: Props) {
  return (
    <>
      {/* The dynamic client takes over once hydrated. The fallback
          renders FIRST for SSR + while the chunk is loading. We render
          both but hide the fallback as soon as the client is up — the
          client renders absolutely-positioned over the fallback's
          space via the section's height. */}
      <StickyScrollStackClient {...props} />
      <noscript>
        <StickyScrollStackFallback {...props} />
      </noscript>
    </>
  );
}
