"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";

export default function AboutKitchen() {
  return (
    <section className="bg-stone-50 py-24 px-8 overflow-hidden">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">

          {/* Kitchen / chef photograph — left */}
          <div className="relative">
            <div className="relative aspect-[3/4] rounded-3xl overflow-hidden">
              <Parallax className="absolute inset-0" distance={30}>
                <Image
                  src="https://images.pexels.com/photos/6996209/pexels-photo-6996209.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="A thirty-year starter and two early-morning bakers."
                  fill
                  priority
                  className="object-cover"
                />
              </Parallax>
              <div className="absolute inset-0 bg-gradient-to-t from-stone-50/40 to-transparent" />
            </div>
            {/* Warm amber accent block */}
            <div className="absolute -bottom-6 -right-6 w-40 h-40 rounded-3xl bg-amber-700/10 -z-10" />
          </div>

          {/* Story prose — right */}
          <div>
            <p className="text-amber-700 text-sm uppercase tracking-widest font-sans mb-4" data-pebble-id="pb-05753f">
              How it began
            </p>
            <h2 className="text-stone-900 font-serif text-4xl md:text-5xl leading-tight mb-8 max-w-md" data-pebble-id="pb-8935f4">
              <RevealWords>A thirty-year starter and two early-morning bakers.</RevealWords>
            </h2>

            
            <p className="text-stone-900/70 font-sans text-lg leading-relaxed mb-6" data-pebble-id="pb-b3345a">
              Flour & Fern is three people and a tiny corner space in Riverside. We open the ovens before sunrise, mix everything by hand, and try to have a good loaf on the shelf by the time the neighborhood starts moving.
            </p>
            
            <p className="text-stone-900/70 font-sans text-lg leading-relaxed mb-6" data-pebble-id="pb-c183c6">
              Our sourdough ferments for 48 hours minimum — no shortcuts, no commercial yeast. The flavor comes from time and a house starter we've kept alive and fed every single day since we opened our doors.
            </p>
            
            <p className="text-stone-900/70 font-sans text-lg leading-relaxed mb-6" data-pebble-id="pb-11e41f">
              The Saturday rye-and-fig loaf is the one people drive across town for. It's baked from a starter our baker's grandmother kept for thirty years in her kitchen in Portugal. We think of it as borrowed — we're just its current keepers.
            </p>
            

            {/* Signature */}
            <div className="mt-10 pt-8 border-t border-stone-900/10">
              <p className="text-stone-900 font-serif text-base italic" data-pebble-id="pb-e3431a">
                — Founders & bakers, Flour & Fern
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
