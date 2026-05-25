"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import {
  HERO_IMAGE,
  HERO_HEADLINE,
  HERO_PRIMARY_CTA,
  HERO_PRIMARY_HREF,
  HERO_SECONDARY_CTA,
  HERO_SECONDARY_HREF,
} from "@/content/site";

export function HomeHero() {
  return (
    <section className="relative min-h-[100svh] min-h-[640px] overflow-hidden flex items-end pb-24 px-6">
      <div className="absolute inset-0 -z-10">
        <Image
          src={HERO_IMAGE}
          alt="Plated dish"
          fill
          priority
          sizes="100vw"
          className="object-cover opacity-80"
        />
        <div className="absolute inset-0 bg-charcoal/40" />
      </div>
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
        className="max-w-7xl mx-auto w-full relative z-10"
      >
        <h1 className="font-[family-name:var(--font-display)] text-5xl md:text-7xl lg:text-8xl italic text-bone mb-8 max-w-4xl leading-tight">
          {HERO_HEADLINE}
        </h1>
        <div className="flex flex-col sm:flex-row gap-4">
          <a
            href={HERO_PRIMARY_HREF}
            className="bg-burgundy text-bone px-8 py-4 text-center rounded-full font-medium tracking-wide hover:bg-charcoal transition-colors"
          >
            {HERO_PRIMARY_CTA}
          </a>
          <a
            href={HERO_SECONDARY_HREF}
            className="border-2 border-bone text-bone px-8 py-4 text-center rounded-full font-medium tracking-wide hover:bg-bone hover:text-charcoal transition-colors"
          >
            {HERO_SECONDARY_CTA}
          </a>
        </div>
      </motion.div>
    </section>
  );
}
