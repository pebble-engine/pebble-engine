"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";
import MagneticButton from "@/components/motion/MagneticButton";

export default function HeroPlate() {
  return (
    <section className="relative min-h-screen flex items-end overflow-hidden bg-stone-900">
      {/* Full-bleed food photograph */}
      <div className="absolute inset-0">
        <Parallax className="absolute inset-0" distance={40}>
          <Image
            src="https://images.pexels.com/photos/18823960/pexels-photo-18823960.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Rooted in season. Cooked for the table."
            fill
            priority
            className="object-cover"
          />
        </Parallax>
        {/* Rich warm gradient — bottom-heavy so type is readable */}
        <div className="absolute inset-0 bg-gradient-to-t from-stone-900 via-stone-900/70 to-transparent" />
      </div>

      {/* Copy block — sits beneath the photo like a menu caption */}
      <div className="relative z-10 container mx-auto px-8 pb-20 md:pb-28 max-w-6xl">
        <p className="text-amber-800 text-sm uppercase tracking-widest font-sans mb-4 [text-shadow:0_1px_8px_rgba(0,0,0,0.5)]" data-pebble-id="pb-5aa2d3">
          Now seating · Hudson Valley, NY
        </p>
        <h1 className="text-stone-50 font-serif text-5xl md:text-7xl leading-tight max-w-3xl mb-6 [text-shadow:0_2px_16px_rgba(0,0,0,0.55)]" data-pebble-id="pb-e0d8c2">
          <RevealWords>Rooted in season. Cooked for the table.</RevealWords>
        </h1>
        <p className="text-stone-200/80 text-lg md:text-xl font-sans leading-relaxed max-w-2xl mb-10 [text-shadow:0_1px_10px_rgba(0,0,0,0.5)]" data-pebble-id="pb-9b31b3">
          Every plate names the farm it came from — most within 30 miles. The menu shifts with the harvest, so what you eat tonight won't be here next month. Pull up a chair.
        </p>
        <div className="flex flex-wrap gap-4">
          <MagneticButton
            href="#reserve"
            className="inline-block bg-amber-800 text-stone-50 px-8 py-4 rounded-full font-sans font-semibold hover:scale-105 hover:opacity-95 transition-transform duration-200"
          >
            Reserve a table
          </MagneticButton>
          <a
            href="#menu"
            className="text-stone-100 px-8 py-4 rounded-full border border-stone-400/40 font-sans hover:bg-stone-50/10 transition" data-pebble-id="pb-3f91f4">
            See the menu
          </a>
        </div>
      </div>
    </section>
  );
}
