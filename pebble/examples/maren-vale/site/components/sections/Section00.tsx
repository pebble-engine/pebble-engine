"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";
import MagneticButton from "@/components/motion/MagneticButton";

export default function HeroSerene() {
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden bg-stone-50">
      {/* Full-bleed image — soft natural light, no dark overlay */}
      <div className="absolute inset-0">
        <Parallax className="absolute inset-0" distance={30}>
          <Image
            src="https://images.pexels.com/photos/5009521/pexels-photo-5009521.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Made slowly, by hand, for the moment that changes everything."
            fill
            priority
            className="object-cover"
          />
        </Parallax>
        {/* Very gentle cream wash so text reads without crushing the image */}
        <div className="absolute inset-0 bg-gradient-to-r from-stone-50/90 via-stone-50/50 to-transparent" />
      </div>

      {/* Content — left-aligned, generous breathing room */}
      <div className="relative z-10 container mx-auto px-8 md:px-16 py-32 max-w-6xl">
        {/* Eyebrow — tiny caps, gold accent */}
        <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-6 font-light" data-pebble-id="pb-abf723">
          Hand-fabricated fine jewelry.
        </p>

        {/* Headline — light weight, never aggressive */}
        <h1 className="text-stone-700 text-5xl md:text-7xl font-light leading-[1.1] tracking-tight max-w-2xl" data-pebble-id="pb-f046b9">
          <RevealWords>Made slowly, by hand, for the moment that changes everything.</RevealWords>
        </h1>

        <p className="text-stone-500 text-xl font-light leading-relaxed mt-8 max-w-xl" data-pebble-id="pb-efe8e4">
          Every piece begins at the bench — formed from metal, shaped by hand, finished with care. For engagements, heirlooms, and the milestones worth remembering.
        </p>

        {/* CTAs — rounded-full, thin border, wide tracking */}
        <div className="mt-12 flex flex-wrap gap-4">
          <MagneticButton
            href="#book"
            className="inline-block border border-stone-700 text-stone-700 px-10 py-4 rounded-full text-xs uppercase tracking-[0.2em] font-light hover:border-amber-600 hover:text-amber-600 transition-colors duration-300"
          >
            BEGIN A COMMISSION
          </MagneticButton>
          <a
            href="#services"
            className="inline-block border border-stone-300 text-stone-500 px-10 py-4 rounded-full text-xs uppercase tracking-[0.2em] font-light hover:border-stone-500 transition-colors duration-300" data-pebble-id="pb-6c72d8">
            OUR OFFERINGS
          </a>
        </div>
      </div>
    </section>
  );
}
