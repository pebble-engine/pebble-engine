"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServiceAreaTrade() {
  return (
    <section className="bg-slate-50 py-20 px-8">
      <div className="max-w-5xl mx-auto text-center">

        <h2 className="text-slate-900 text-3xl md:text-4xl font-semibold leading-tight tracking-tight" data-pebble-id="pb-ed3fe5">
          <RevealWords>Proudly Serving Denver & the Front Range</RevealWords>
        </h2>

        <Stagger className="mt-10 flex flex-wrap justify-center gap-3">
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Denver
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Aurora
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Lakewood
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Englewood
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Littleton
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Centennial
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Highlands Ranch
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Westminster
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Arvada
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Thornton
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Parker
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Castle Rock
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
