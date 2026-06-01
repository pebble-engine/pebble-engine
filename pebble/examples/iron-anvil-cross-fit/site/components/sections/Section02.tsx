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
                  src="https://images.pexels.com/photos/4761380/pexels-photo-4761380.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="BUILT FOR EVERYDAY PEOPLE"
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
            <p className="text-lime-400 text-xs font-black uppercase tracking-[0.3em] mb-6" data-pebble-id="pb-7862b7">
              OUR STORY
            </p>
            <h2 className="text-zinc-50 text-5xl md:text-7xl font-black uppercase leading-none mb-10 max-w-lg" data-pebble-id="pb-b15354">
              <RevealWords>BUILT FOR EVERYDAY PEOPLE</RevealWords>
            </h2>

            
            <p className="text-zinc-50/70 text-base md:text-lg leading-relaxed mb-5" data-pebble-id="pb-83f6bf">
              We opened Iron Anvil CrossFit on the east side because this neighborhood needed a box that didn't care how you looked in a tank top. We care about how you move, how hard you work, and whether you show up for your crew.
            </p>
            
            <p className="text-zinc-50/70 text-base md:text-lg leading-relaxed mb-5" data-pebble-id="pb-3178c9">
              Every coach here was once a nervous beginner staring down a barbell. We coach real humans — teachers, nurses, parents, first-timers — through tough WODs because we know what it feels like to need someone in your corner.
            </p>
            
            <p className="text-zinc-50/70 text-base md:text-lg leading-relaxed mb-5" data-pebble-id="pb-fbb9db">
              The 6am First Light crew set the tone from day one. They finish every session ringing the PR bell and grabbing coffee from the trailer out front. That ritual is who we are. Come find out for yourself.
            </p>
            

            {/* Signature — hard rule above */}
            <div className="mt-10 pt-6 border-t-2 border-lime-400/40">
              <p className="text-zinc-50 text-sm font-black uppercase tracking-widest" data-pebble-id="pb-ba4853">
                — COACH DEREK — FOUNDER & HEAD TRAINER
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
