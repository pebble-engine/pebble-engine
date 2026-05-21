"use client";

import * as React from "react";
import Image from "next/image";
import { motion, useReducedMotion } from "framer-motion";
import { StatCard } from "@/components/ui/StatCard";
import { SectionDivider } from "@/components/ui/SectionDivider";
import {
  PRINCIPAL_EYEBROW,
  PRINCIPAL_NAME_LINE_1,
  PRINCIPAL_NAME_LINE_2,
  PRINCIPAL_BODY,
  PRINCIPAL_IMAGE_URL,
  PRINCIPAL_STATS,
} from "@/content/site";

/**
 * Principal — split-screen with a deliberately sticky right-side panel.
 * Left: portrait image with a soft bg-fade gradient. Right: pinned dark
 * content panel with eyebrow + 2-line headline + paragraph + Stats pair.
 *
 * Sticky behavior degrades gracefully on shorter viewports — the image
 * simply sits above the text panel rather than pinning.
 *
 * When PRINCIPAL_IMAGE_URL is empty (anti-slop default), the image side
 * collapses into a vermilion accent slab so the section still composes
 * visually without inventing a headshot.
 */
export function Principal() {
  const reduce = useReducedMotion();
  const hasImage = PRINCIPAL_IMAGE_URL.length > 0;
  const hasStats = PRINCIPAL_STATS.length > 0;

  return (
    <section
      aria-labelledby="principal-heading"
      className="bg-bg"
    >
      <div className="page-container">
        <SectionDivider index="03" label="Principal" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 min-h-[60vh] lg:min-h-screen">
        {/* Left — portrait or accent slab */}
        <div className="relative bg-surface overflow-hidden">
          {hasImage ? (
            <Image
              src={PRINCIPAL_IMAGE_URL}
              alt={`${PRINCIPAL_NAME_LINE_1} ${PRINCIPAL_NAME_LINE_2}`}
              fill
              sizes="(min-width: 1024px) 50vw, 100vw"
              className="object-cover cinematic-img"
            />
          ) : (
            <div className="relative w-full h-full min-h-[420px] flex items-end justify-start p-10">
              <div className="w-32 h-32 bg-accent cinematic-radius" aria-hidden="true" />
            </div>
          )}
          {/* Bottom fade for legibility */}
          <div
            className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-bg to-transparent pointer-events-none"
            aria-hidden="true"
          />
        </div>

        {/* Right — pinned content */}
        <div className="relative bg-bg">
          <div className="lg:sticky lg:top-0 lg:h-screen flex items-center">
            <motion.div
              initial={{ opacity: 0, y: reduce ? 0 : 32 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-120px" }}
              transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
              className="page-container py-section-mobile md:py-section-desktop max-w-xl"
            >
              <p className="text-label mb-6">{PRINCIPAL_EYEBROW}</p>
              <h2 id="principal-heading" className="text-display mb-8">
                {PRINCIPAL_NAME_LINE_1}
                <br />
                <span className="text-accent">{PRINCIPAL_NAME_LINE_2}</span>
              </h2>
              <p className="text-body-lg mb-10">{PRINCIPAL_BODY}</p>

              {hasStats && (
                <div className="grid grid-cols-2 gap-3 md:gap-4">
                  {PRINCIPAL_STATS.map((stat, i) => (
                    <StatCard key={i} value={stat.value} label={stat.label} />
                  ))}
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
