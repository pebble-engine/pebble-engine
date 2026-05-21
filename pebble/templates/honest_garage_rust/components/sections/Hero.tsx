"use client";
import { motion } from "framer-motion";
import Link from "next/link";
import { GlowBlob } from "@/components/ui/GlowBlob";
import { RefCode } from "@/components/ui/RefCode";
import {
  HERO_REF_CODE,
  HERO_HEADLINE_TOP,
  HERO_HEADLINE_ACCENT,
  HERO_SUBLINE,
  HERO_CTA_PRIMARY,
  HERO_CTA_SECONDARY,
  HERO_SERVICE_CHIP,
  PHONE,
  PHONE_DISPLAY,
} from "@/content/site";

/**
 * The hero is the load-bearing tell of the auto_honest_diag DNA:
 *   - 1A1714 warm-dark bg with two huge blurred rust blobs (top-right + bottom-left)
 *   - JetBrains Mono REF-XXXX code stenciled in the top-right corner
 *   - H1 in INTER bold (NOT the display stencil) — reads like a work order
 *   - Dual CTAs: filled-rust + ghost-outline
 *   - Right-column glass chip listing service categories in mono
 */
export function Hero() {
  return (
    <section className="relative isolate overflow-hidden pt-32 pb-20 sm:pt-40 sm:pb-28 min-h-[88vh] flex items-end">
      {/* Two blurred rust glow blobs */}
      <GlowBlob className="-top-32 -right-48 h-[700px] w-[700px]" />
      <GlowBlob className="-bottom-24 -left-48 h-[500px] w-[500px]" />

      {/* Top-right REF code, stenciled like a job ticket */}
      <div className="absolute top-6 right-6 z-10 sm:top-10 sm:right-10">
        <RefCode>{HERO_REF_CODE}</RefCode>
      </div>

      <div className="relative z-10 mx-auto grid w-full max-w-6xl gap-12 px-6 lg:grid-cols-12 lg:items-end">
        {/* Left — content */}
        <div className="lg:col-span-8">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            <RefCode accent>// PRIMARY WORK ORDER</RefCode>
          </motion.div>

          {/* H1 — Inter bold, NOT stencil. Work-order, not brochure. */}
          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: "easeOut", delay: 0.05 }}
            className="mt-4 font-sans text-5xl font-bold leading-[1.02] tracking-tight text-fg sm:text-7xl"
          >
            <span className="block">{HERO_HEADLINE_TOP}</span>
            <span className="block text-primary">{HERO_HEADLINE_ACCENT}</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut", delay: 0.18 }}
            className="mt-6 max-w-xl text-base text-body sm:text-lg"
          >
            {HERO_SUBLINE}
          </motion.p>

          {/* Dual CTAs — filled rust + ghost outline */}
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut", delay: 0.28 }}
            className="mt-8 flex flex-wrap items-center gap-3"
          >
            <a href={`tel:${PHONE.replace(/[^+\d]/g, "")}`} className="btn-primary">
              <PhoneIcon />
              CALL {PHONE_DISPLAY}
            </a>
            <Link href="/services" className="btn-ghost">
              {HERO_CTA_SECONDARY}
            </Link>
            <Link href="/contact" className="btn-ghost">
              {HERO_CTA_PRIMARY}
            </Link>
          </motion.div>
        </div>

        {/* Right — glass-card pill listing service categories in mono */}
        <motion.div
          initial={{ opacity: 0, x: 16 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, ease: "easeOut", delay: 0.35 }}
          className="lg:col-span-4 lg:justify-self-end"
        >
          <div className="glass-card inline-flex max-w-xs flex-col gap-2 px-5 py-4">
            <RefCode accent>// SERVICE CATEGORIES</RefCode>
            <p className="font-mono text-xs font-bold uppercase tracking-[0.12em] text-fg/90">
              {HERO_SERVICE_CHIP}
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function PhoneIcon() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
    </svg>
  );
}
