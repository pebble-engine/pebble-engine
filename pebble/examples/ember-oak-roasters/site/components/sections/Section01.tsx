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
                  src="https://images.pexels.com/photos/7175963/pexels-photo-7175963.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="Every roast starts with a handful of beans and a story worth knowing."
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
            <p className="text-amber-700 text-sm uppercase tracking-widest font-sans mb-4" data-pebble-id="pb-2c300c">
              How it began
            </p>
            <h2 className="text-stone-900 font-serif text-4xl md:text-5xl leading-tight mb-8 max-w-md" data-pebble-id="pb-5521e1">
              <RevealWords>Every roast starts with a handful of beans and a story worth knowing.</RevealWords>
            </h2>

            
            <p className="text-stone-900/70 font-sans text-lg leading-relaxed mb-6" data-pebble-id="pb-97daf9">
              We built Ember & Oak around one idea: that coffee is better when you know where it came from. We source single-origin beans direct from small farms — Ethiopia, Colombia, Guatemala — and roast them in small batches right here, a few mornings a week.
            </p>
            
            <p className="text-stone-900/70 font-sans text-lg leading-relaxed mb-6" data-pebble-id="pb-fbf68b">
              You'll smell the roast before you see it. That's the point. We wanted a place that felt like someone's kitchen on a slow Sunday — warm, a little unhurried, nothing slick or corporate. Pull up a stool. We'll pour you something worth tasting.
            </p>
            
            <p className="text-stone-900/70 font-sans text-lg leading-relaxed mb-6" data-pebble-id="pb-0ac82a">
              Every bag that leaves here has a handwritten roast date and a short note about the farm — the altitude, the variety, the people who grew it. It matters to us, and we think it'll matter to you too.
            </p>
            

            {/* Signature */}
            <div className="mt-10 pt-8 border-t border-stone-900/10">
              <p className="text-stone-900 font-serif text-base italic" data-pebble-id="pb-82285b">
                — — The Ember & Oak team, Roasters & Neighbors
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
