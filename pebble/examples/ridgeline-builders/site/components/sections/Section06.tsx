"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServiceAreaTrade() {
  return (
    <section className="bg-stone-50 py-20 px-8">
      <div className="max-w-5xl mx-auto text-center">

        <h2 className="text-stone-900 text-3xl md:text-4xl font-semibold leading-tight tracking-tight" data-pebble-id="pb-07b206">
          <RevealWords>Proudly Serving Boise & the Treasure Valley</RevealWords>
        </h2>

        <Stagger className="mt-10 flex flex-wrap justify-center gap-3">
          
          <StaggerItem className="inline-block border border-amber-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Boise
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Meridian
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Nampa
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Eagle
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Caldwell
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Kuna
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Star
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Garden City
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Hidden Springs
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            South Boise
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
