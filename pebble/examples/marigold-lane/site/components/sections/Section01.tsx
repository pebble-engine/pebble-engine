"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";

export default function AboutStory() {
  return (
    <section className="bg-stone-50 py-24 px-8 overflow-hidden">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">

          {/* Portrait image — left column */}
          <div className="relative">
            <div className="relative aspect-[3/4] rounded-3xl overflow-hidden">
              <Parallax className="absolute inset-0" distance={30}>
                <Image
                  src="https://images.pexels.com/photos/6599027/pexels-photo-6599027.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="Three stylists, one old house, years of good haircuts."
                  fill
                  priority
                  className="object-cover"
                />
              </Parallax>
              {/* Warm gradient wash at the bottom of the portrait */}
              <div className="absolute inset-0 bg-gradient-to-t from-stone-50/30 to-transparent" />
            </div>
            {/* Decorative accent block — visual warmth */}
            <div className="absolute -bottom-6 -right-6 w-48 h-48 rounded-3xl bg-amber-700/10 -z-10" />
          </div>

          {/* Prose — right column */}
          <div>
            <p className="text-amber-700 text-sm uppercase tracking-widest mb-4" data-pebble-id="pb-f4e847">
              How it began
            </p>
            <h2 className="text-stone-900 text-5xl md:text-6xl font-bold leading-tight mb-8 max-w-lg" data-pebble-id="pb-8c4259">
              <RevealWords>Three stylists, one old house, years of good haircuts.</RevealWords>
            </h2>

            
            <p className="text-stone-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-44cb56">
              Marigold Lane started when three of us decided we'd rather work somewhere that felt like home. We found an old house on the east side, painted the trim, put in good chairs, and opened the door.
            </p>
            
            <p className="text-stone-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-97b2bc">
              Most of our clients have been coming for years — some since the very beginning. We know which side your hair falls on, what you tried that one time that didn't work, and how you take your tea.
            </p>
            
            <p className="text-stone-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-8b987e">
              Every first appointment starts with a proper sit-down. Kettle on, no scissors yet. We want to understand your hair before we touch it, and we want you to feel unhurried from the moment you walk in.
            </p>
            

            {/* Signature line */}
            <div className="mt-10 pt-8 border-t border-stone-900/10">
              <p className="text-stone-900 text-base font-semibold italic" data-pebble-id="pb-62f6a2">
                — — The team at Marigold Lane
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
