"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import {
  HERO_BG_IMAGE,
  HERO_PILL,
  HERO_HEADLINE,
  HERO_SUBLINE,
  HERO_CTA_PRIMARY,
  HERO_CTA_SECONDARY,
  HERO_CTA_PRIMARY_HREF,
  HERO_CTA_SECONDARY_HREF,
} from "@/content/site";

export function Hero() {
  return (
    <section className="relative h-[100svh] min-h-[640px] w-full overflow-hidden bg-slate-900">
      <Image
        src={HERO_BG_IMAGE}
        alt=""
        fill
        priority
        sizes="100vw"
        className="object-cover object-center"
      />
      <div
        aria-hidden
        className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/60 to-transparent"
      />
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        className="absolute bottom-0 left-0 p-8 md:p-16 max-w-[640px] text-white"
      >
        <span className="inline-block mb-4 px-3 py-1 rounded-full bg-[var(--color-accent)]/25 border border-[var(--color-accent)]/40 text-[10px] uppercase tracking-[0.18em] font-bold">
          {HERO_PILL}
        </span>
        <h1 className="font-[family-name:var(--font-display)] text-[40px] md:text-[64px] leading-[0.95] uppercase tracking-tight">
          {HERO_HEADLINE}
        </h1>
        <p className="mt-4 text-[15px] md:text-[18px] leading-relaxed text-white/85 max-w-md">
          {HERO_SUBLINE}
        </p>
        <div className="mt-7 flex flex-wrap gap-3">
          <a
            href={HERO_CTA_PRIMARY_HREF}
            className="inline-flex items-center justify-center h-14 px-6 rounded-full bg-[var(--color-accent)] hover:bg-[var(--color-accent-dark)] text-white font-semibold text-base transition-colors"
          >
            {HERO_CTA_PRIMARY}
          </a>
          <a
            href={HERO_CTA_SECONDARY_HREF}
            className="inline-flex items-center justify-center h-14 px-6 rounded-full bg-transparent border border-white/70 hover:bg-white/10 text-white font-semibold text-base transition-colors"
          >
            {HERO_CTA_SECONDARY}
          </a>
        </div>
      </motion.div>
    </section>
  );
}
