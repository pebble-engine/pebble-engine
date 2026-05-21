"use client";

import * as React from "react";
import Image from "next/image";
import { motion, useReducedMotion } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { EyebrowChip } from "@/components/ui/EyebrowChip";
import {
  ABOUT_EYEBROW,
  ABOUT_HEADLINE,
  ABOUT_BODY,
  ABOUT_IMAGE_URL,
  ABOUT_CTA,
  ABOUT_CTA_HREF,
} from "@/content/site";

/**
 * About — DNA's two_column_square_photo_left_story_right.
 * Square 1:1 photo with rounded-4xl mask paired with chip + Fraunces
 * headline + multi-paragraph story copy + secondary CTA.
 */
export function About() {
  const reduce = useReducedMotion();

  return (
    <section
      aria-labelledby="about-heading"
      className="bg-cream"
    >
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 md:gap-16 items-center">
          {/* Square photo */}
          <motion.div
            initial={{ opacity: 0, scale: reduce ? 1 : 0.96 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
            className="lg:col-span-6"
          >
            <div className="relative aspect-square w-full overflow-hidden rounded-4xl warm-shadow-strong">
              <Image
                src={ABOUT_IMAGE_URL}
                alt="Inside the trattoria"
                fill
                sizes="(min-width: 1024px) 600px, 100vw"
                className="object-cover"
              />
            </div>
          </motion.div>

          {/* Story */}
          <motion.div
            initial={{ opacity: 0, y: reduce ? 0 : 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="lg:col-span-6"
          >
            <EyebrowChip className="mb-4">{ABOUT_EYEBROW}</EyebrowChip>
            <h2
              id="about-heading"
              className="font-display text-3xl md:text-4xl lg:text-5xl text-ink leading-tight mb-6"
            >
              {ABOUT_HEADLINE}
            </h2>
            <div className="space-y-5 mb-8">
              {ABOUT_BODY.map((p, i) => (
                <p key={i} className="text-body-lg">
                  {p}
                </p>
              ))}
            </div>
            <Button href={ABOUT_CTA_HREF} variant="secondary">
              {ABOUT_CTA}
            </Button>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
