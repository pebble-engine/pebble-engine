"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import { HERO_IMAGE, HERO_HEADLINE, HERO_CTA, HERO_CTA_HREF } from "@/content/site";

export function Hero() {
  return (
    <section className="relative h-screen overflow-hidden flex flex-col items-center justify-center px-6">
      <div className="absolute inset-0 hero-zoom">
        <Image
          src={HERO_IMAGE}
          alt="Black-and-white wedding portrait"
          fill
          priority
          sizes="100vw"
          className="object-cover brightness-50 grayscale"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#0a2820]/30 via-transparent to-[#0a2820]/80" />
      </div>
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
        className="relative z-10 text-center max-w-4xl"
      >
        <h1 className="font-[family-name:var(--font-display)] text-5xl md:text-7xl lg:text-8xl italic font-semibold text-[#f5f0dc] leading-[1.1] mb-8">
          {HERO_HEADLINE}
        </h1>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.8 }}
        >
          <a href={HERO_CTA_HREF} className="btn-brass">
            {HERO_CTA}
          </a>
        </motion.div>
      </motion.div>
    </section>
  );
}
