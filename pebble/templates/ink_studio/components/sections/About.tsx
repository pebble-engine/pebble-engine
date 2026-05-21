"use client";

import * as React from "react";
import Image from "next/image";
import { motion, useReducedMotion } from "framer-motion";
import {
  ABOUT_EYEBROW,
  ABOUT_HEADLINE,
  ABOUT_BODY,
  ABOUT_PORTRAIT_URL,
  ABOUT_PORTRAIT_ALT,
} from "@/content/site";

/**
 * About — two-column portrait + text block. Portrait sits inside the
 * `corner-brackets` + `gold-border-glow` treatment per DNA. All-caps
 * Bebas eyebrow + blackletter h2 + Source Sans body.
 */
export function About() {
  const reduce = useReducedMotion();

  return (
    <section aria-labelledby="about-heading" className="bg-ink-bg">
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-10 md:gap-16 items-center">
          {/* Portrait */}
          <motion.div
            initial={{ opacity: 0, x: reduce ? 0 : -24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
            className="md:col-span-5"
          >
            <div className="corner-brackets gold-border-glow relative aspect-[4/5] overflow-hidden bg-ink-card">
              <Image
                src={ABOUT_PORTRAIT_URL}
                alt={ABOUT_PORTRAIT_ALT}
                fill
                sizes="(min-width: 1024px) 500px, 100vw"
                className="object-cover"
              />
            </div>
          </motion.div>

          {/* Copy */}
          <motion.div
            initial={{ opacity: 0, x: reduce ? 0 : 24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.9, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="md:col-span-7"
          >
            <p className="text-eyebrow mb-4">{ABOUT_EYEBROW}</p>
            <h2 id="about-heading" className="text-headline mb-8">
              {ABOUT_HEADLINE}
            </h2>
            <div className="space-y-5">
              {ABOUT_BODY.map((p, i) => (
                <p key={i} className="text-body-lg">
                  {p}
                </p>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
