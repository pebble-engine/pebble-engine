"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";

export default function AboutOriginBold() {
  return (
    <section className="bg-zinc-900 py-24 px-8 overflow-hidden">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">

          {/* Left — raw portrait with hard-edge lime accent block */}
          <div className="relative">
            <div className="relative aspect-[3/4] overflow-hidden rounded-md">
              <Parallax className="absolute inset-0" distance={30}>
                <Image
                  src="https://images.pexels.com/photos/9072298/pexels-photo-9072298.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="BUILT FROM STATIC. NOT FROM SILENCE."
                  fill
                  priority
                  className="object-cover brightness-90"
                />
              </Parallax>
              {/* Hard lime corner accent — bottom-left */}
              <div className="absolute bottom-0 left-0 w-1 h-24 bg-lime-400" />
              <div className="absolute bottom-0 left-0 h-1 w-24 bg-lime-400" />
            </div>
            {/* Oversized bg number / decorative element */}
            <div
              aria-hidden="true"
              className="absolute -bottom-8 -right-4 text-zinc-50/5 text-[12rem] font-black leading-none select-none pointer-events-none"
            >
              01
            </div>
          </div>

          {/* Right — story prose */}
          <div>
            <p className="text-lime-400 text-xs font-black uppercase tracking-[0.3em] mb-6" data-pebble-id="pb-67b586">
              THE ORIGIN
            </p>
            <h2 className="text-zinc-50 text-5xl md:text-7xl font-black uppercase leading-none mb-10 max-w-lg" data-pebble-id="pb-60e177">
              <RevealWords>BUILT FROM STATIC. NOT FROM SILENCE.</RevealWords>
            </h2>

            
            <p className="text-zinc-50/70 text-base md:text-lg leading-relaxed mb-5" data-pebble-id="pb-bbb500">
              Static Vanguard started in a Discord server with six players who were tired of grinding alone. No org. No backing. Just raw talent and a refusal to disappear into the ranked queue.
            </p>
            
            <p className="text-zinc-50/70 text-base md:text-lg leading-relaxed mb-5" data-pebble-id="pb-344388">
              Then came the glitch intro. What started as a streamer overlay became the thing fans screenshot, remix, and tattoo on their gear. The static became our signal — chaos with a purpose.
            </p>
            
            <p className="text-zinc-50/70 text-base md:text-lg leading-relaxed mb-5" data-pebble-id="pb-3727a4">
              Now we're taking it further. Two rosters. A growing fanbase. And a pitch to every brand that wants in before the crowd gets too loud to ignore. The static was always there. We just turned up the volume.
            </p>
            

            {/* Signature — hard rule above */}
            <div className="mt-10 pt-6 border-t-2 border-lime-400/40">
              <p className="text-zinc-50 text-sm font-black uppercase tracking-widest" data-pebble-id="pb-f047cb">
                — VANCE 'STATIC' OKAFOR, FOUNDER & IGL
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
