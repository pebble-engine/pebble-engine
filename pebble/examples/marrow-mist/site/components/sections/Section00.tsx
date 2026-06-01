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
            src="https://images.pexels.com/photos/35884499/pexels-photo-35884499.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Leave the noise at the door. Arrive slowly."
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
        <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-6 font-light" data-pebble-id="pb-e540d9">
          A quiet beginning.
        </p>

        {/* Headline — light weight, never aggressive */}
        <h1 className="text-stone-700 text-5xl md:text-7xl font-light leading-[1.1] tracking-tight max-w-2xl" data-pebble-id="pb-c1983d">
          <RevealWords>Leave the noise at the door. Arrive slowly.</RevealWords>
        </h1>

        <p className="text-stone-500 text-xl font-light leading-relaxed mt-8 max-w-xl" data-pebble-id="pb-05ac2b">
          Every visit begins with warm water, cedar-and-chamomile tea, and a foot ritual that asks nothing of you — before a single treatment begins. This is where you exhale.
        </p>

        {/* CTAs — rounded-full, thin border, wide tracking */}
        <div className="mt-12 flex flex-wrap gap-4">
          <MagneticButton
            href="#book"
            className="inline-block border border-stone-700 text-stone-700 px-10 py-4 rounded-full text-xs uppercase tracking-[0.2em] font-light hover:border-amber-600 hover:text-amber-600 transition-colors duration-300"
          >
            BOOK A VISIT
          </MagneticButton>
          <a
            href="#services"
            className="inline-block border border-stone-300 text-stone-500 px-10 py-4 rounded-full text-xs uppercase tracking-[0.2em] font-light hover:border-stone-500 transition-colors duration-300" data-pebble-id="pb-9a7336">
            OUR OFFERINGS
          </a>
        </div>
      </div>
    </section>
  );
}
