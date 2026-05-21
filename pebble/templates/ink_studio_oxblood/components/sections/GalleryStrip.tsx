"use client";

import * as React from "react";
import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import { GalleryCard } from "@/components/ui/GalleryCard";
import {
  GALLERY_EYEBROW,
  GALLERY_HEADLINE,
  GALLERY_INTRO,
  GALLERY_ITEMS,
} from "@/content/site";

/**
 * GalleryStrip — homepage three-column portfolio strip. Center card gets the
 * gold-border + corner-bracket treatment (DNA: carousel center-image styling).
 * "View full portfolio" link sits below; the dedicated /gallery page renders
 * the complete grid.
 *
 * We deliberately ship a static three-up rather than an auto-advancing
 * carousel — easier to maintain, no JS dependency for the headline section,
 * and the dedicated /gallery page handles the full body of work.
 */
export function GalleryStrip() {
  const reduce = useReducedMotion();

  if (GALLERY_ITEMS.length === 0) {
    return null;
  }

  // Show the first three; center one is highlighted.
  const visible = GALLERY_ITEMS.slice(0, 3);

  return (
    <section
      aria-labelledby="gallery-heading"
      className="relative bg-ink-bg"
    >
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="mb-12 md:mb-16 text-center max-w-2xl mx-auto">
          <p className="text-eyebrow mb-4">{GALLERY_EYEBROW}</p>
          <h2 id="gallery-heading" className="text-headline mb-5">
            {GALLERY_HEADLINE}
          </h2>
          <p className="text-body-lg">{GALLERY_INTRO}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
          {visible.map((item, i) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: reduce ? 0 : 32 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.8, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
            >
              <GalleryCard
                title={item.title}
                style={item.style}
                imageUrl={item.image_url}
                alt={item.alt}
                highlighted={i === 1}
              />
            </motion.div>
          ))}
        </div>

        <div className="mt-12 md:mt-16 text-center">
          <Link
            href="/gallery"
            className="inline-flex items-center gap-3 text-button text-ink-primary hover:gap-5 transition-all duration-300"
          >
            View full portfolio
            <span aria-hidden="true">&rarr;</span>
          </Link>
        </div>
      </div>
    </section>
  );
}
