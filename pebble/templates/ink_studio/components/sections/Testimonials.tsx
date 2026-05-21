"use client";

import * as React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { TESTIMONIALS } from "@/content/site";

/**
 * Testimonials — three-column quote cards on the dark card surface.
 * Returns null when TESTIMONIALS is empty — anti-slop default. The customer
 * fills the array in after launch.
 */
export function Testimonials() {
  const reduce = useReducedMotion();

  if (TESTIMONIALS.length === 0) {
    return null;
  }

  return (
    <section
      aria-labelledby="testimonials-heading"
      className="bg-ink-secondary border-y border-ink-border"
    >
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="mb-12 md:mb-16 max-w-2xl mx-auto text-center">
          <p className="text-eyebrow mb-4">Said about us</p>
          <h2 id="testimonials-heading" className="text-headline">
            From the People Who Wore It Home
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
          {TESTIMONIALS.map((t, i) => (
            <motion.figure
              key={`${t.name}-${i}`}
              initial={{ opacity: 0, y: reduce ? 0 : 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.6, delay: i * 0.08, ease: "easeOut" }}
              className="flex flex-col gap-4 border border-ink-border bg-ink-card p-7 md:p-8"
            >
              <span aria-hidden="true" className="text-ink-primary text-3xl leading-none">
                &ldquo;
              </span>
              <blockquote className="font-display text-2xl md:text-3xl text-ink-fg leading-snug">
                {t.quote}
              </blockquote>
              <figcaption className="mt-auto pt-4 border-t border-ink-border">
                <p className="text-sm text-ink-fg font-medium">{t.name}</p>
                <p className="text-xs uppercase tracking-[0.22em] text-ink-muted mt-1">
                  {t.piece}
                </p>
              </figcaption>
            </motion.figure>
          ))}
        </div>
      </div>
    </section>
  );
}
