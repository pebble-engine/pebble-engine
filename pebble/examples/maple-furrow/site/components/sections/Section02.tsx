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
                  src="https://images.pexels.com/photos/8900094/pexels-photo-8900094.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="We cook the way we want to eat — slow, honest, from people we know by name."
                  fill
                  priority
                  className="object-cover"
                />
              </Parallax>
              <div className="absolute inset-0 bg-gradient-to-t from-stone-50/40 to-transparent" />
            </div>
            {/* Warm amber accent block */}
            <div className="absolute -bottom-6 -right-6 w-40 h-40 rounded-3xl bg-amber-800/10 -z-10" />
          </div>

          {/* Story prose — right */}
          <div>
            <p className="text-amber-800 text-sm uppercase tracking-widest font-sans mb-4" data-pebble-id="pb-cf7af1">
              Behind the pass
            </p>
            <h2 className="text-stone-900 font-serif text-4xl md:text-5xl leading-tight mb-8 max-w-md" data-pebble-id="pb-ea97a0">
              <RevealWords>We cook the way we want to eat — slow, honest, from people we know by name.</RevealWords>
            </h2>

            
            <p className="text-stone-900/70 font-sans text-lg leading-relaxed mb-6" data-pebble-id="pb-2f5faf">
              My wife Dana and I opened Maple & Furrow because we were tired of restaurants that felt like performances. We wanted something that felt like a long dinner at a friend's house — warm, unhurried, genuinely good.
            </p>
            
            <p className="text-stone-900/70 font-sans text-lg leading-relaxed mb-6" data-pebble-id="pb-5a7234">
              Every dish on the menu carries the name of the farm it came from. That's not a marketing choice — it's a promise. When you order the lamb, you should know it came from Kinderhook Farm, eight miles up the road. The beets from Holler Creek. The eggs from our neighbor's yard.
            </p>
            
            <p className="text-stone-900/70 font-sans text-lg leading-relaxed mb-6" data-pebble-id="pb-c38826">
              The menu changes every few weeks, driven entirely by what our growers bring in. Some nights that means improvising at 4pm. That's the part we love most. It keeps the cooking honest and the plates tasting like the season they're in.
            </p>
            

            {/* Signature */}
            <div className="mt-10 pt-8 border-t border-stone-900/10">
              <p className="text-stone-900 font-serif text-base italic" data-pebble-id="pb-5d5d23">
                — Dana & the kitchen crew · Founders, Maple & Furrow
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
