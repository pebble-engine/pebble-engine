"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServiceAreaTrade() {
  return (
    <section className="bg-slate-50 py-20 px-8">
      <div className="max-w-5xl mx-auto text-center">

        <h2 className="text-slate-900 text-3xl md:text-4xl font-semibold leading-tight tracking-tight" data-pebble-id="pb-134cff">
          <RevealWords>Proudly Serving Austin & All of Travis County</RevealWords>
        </h2>

        <Stagger className="mt-10 flex flex-wrap justify-center gap-3">
          
          <StaggerItem className="inline-block border border-amber-600/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Austin
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-600/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Round Rock
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-600/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Cedar Park
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-600/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Pflugerville
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-600/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Bee Cave
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-600/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Lakeway
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-600/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Manor
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-600/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Rollingwood
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-600/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            West Lake Hills
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-amber-600/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Del Valle
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
