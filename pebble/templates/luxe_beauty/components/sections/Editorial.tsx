"use client";

import * as React from "react";
import Image from "next/image";
import { motion, useReducedMotion } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { ScriptText } from "@/components/ui/ScriptText";
import {
  EDITORIAL_EYEBROW,
  EDITORIAL_HEADLINE,
  EDITORIAL_SCRIPT_ACCENT,
  EDITORIAL_BODY,
  EDITORIAL_BODY_2,
  EDITORIAL_IMAGE_URL,
  EDITORIAL_CTA,
  EDITORIAL_CTA_HREF,
} from "@/content/site";

/**
 * Editorial — magazine-style block. Full-width image with text panel
 * offset on top-left at desktop. Italic Bodoni headline.
 */
export function Editorial() {
  const reduce = useReducedMotion();

  return (
    <section
      aria-labelledby="editorial-heading"
      className="bg-surface-container-low"
    >
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="relative">
          {/* Image */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 1, ease: "easeOut" }}
            className="relative aspect-[16/10] md:aspect-[16/7] w-full overflow-hidden rounded-3xl shadow-vapor"
          >
            <Image
              src={EDITORIAL_IMAGE_URL}
              alt="The Maison Lume atelier in SoHo"
              fill
              sizes="(min-width: 1024px) 1280px, 100vw"
              className="object-cover"
            />
          </motion.div>

          {/* Offset text panel — sits at desktop bottom-right, stacked on mobile */}
          <motion.div
            initial={{ opacity: 0, y: reduce ? 0 : 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="relative mt-6 md:mt-0 md:absolute md:bottom-10 md:right-10 max-w-md glass-card-strong rounded-3xl p-8 md:p-10"
          >
            <p className="text-label mb-3">{EDITORIAL_EYEBROW}</p>
            <h2 id="editorial-heading" className="font-display italic text-3xl md:text-4xl text-on-surface leading-tight mb-1">
              {EDITORIAL_HEADLINE}
            </h2>
            <ScriptText className="text-2xl md:text-3xl block mb-5">
              {EDITORIAL_SCRIPT_ACCENT}
            </ScriptText>
            <p className="text-body-lg mb-3">{EDITORIAL_BODY}</p>
            <p className="text-body-lg mb-6">{EDITORIAL_BODY_2}</p>
            <Button href={EDITORIAL_CTA_HREF} variant="primary">
              {EDITORIAL_CTA}
            </Button>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
