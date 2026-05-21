import * as React from "react";
import { GlassCard } from "@/components/ui/GlassCard";
import { TESTIMONIALS } from "@/content/site";

/**
 * Testimonials — 3-column glass review cards.
 * Returns null when TESTIMONIALS is empty (anti-slop: no invented reviews).
 */
export function Testimonials() {
  if (TESTIMONIALS.length === 0) {
    return null;
  }

  return (
    <section
      aria-labelledby="testimonials-heading"
      className="bg-surface"
    >
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="mb-12 md:mb-16 max-w-2xl">
          <p className="text-label mb-3">Said about us</p>
          <h2 id="testimonials-heading" className="text-headline italic">
            From the people who wear it
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {TESTIMONIALS.map((t, i) => (
            <GlassCard key={i} className="flex flex-col gap-4">
              <div aria-hidden="true" className="flex gap-1 text-tertiary">
                {Array.from({ length: 5 }).map((_, idx) => (
                  <span key={idx}>&#9733;</span>
                ))}
              </div>
              <blockquote className="font-display italic text-xl md:text-2xl text-on-surface leading-snug">
                &ldquo;{t.quote}&rdquo;
              </blockquote>
              <div className="mt-auto flex items-center gap-3 pt-2 border-t border-outline-variant/40">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-container text-primary font-display text-lg">
                  {t.name.charAt(0)}
                </div>
                <div>
                  <p className="text-sm font-medium text-on-surface">{t.name}</p>
                  <p className="text-xs uppercase tracking-[0.12em] text-on-surface-variant">
                    {t.location}
                  </p>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>
      </div>
    </section>
  );
}
