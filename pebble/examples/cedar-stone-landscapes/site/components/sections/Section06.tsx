"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServiceAreaTrade() {
  return (
    <section className="bg-stone-50 py-20 px-8">
      <div className="max-w-5xl mx-auto text-center">

        <h2 className="text-stone-900 text-3xl md:text-4xl font-semibold leading-tight tracking-tight" data-pebble-id="pb-71f6fb">
          <RevealWords>Proudly Serving Raleigh & the Triangle Area</RevealWords>
        </h2>

        <Stagger className="mt-10 flex flex-wrap justify-center gap-3">
          
          <StaggerItem className="inline-block border border-green-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Raleigh
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-green-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Cary
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-green-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Durham
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-green-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Chapel Hill
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-green-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Morrisville
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-green-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Apex
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-green-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Wake Forest
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-green-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Garner
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-green-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Holly Springs
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-green-700/40 text-stone-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Fuquay-Varina
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
