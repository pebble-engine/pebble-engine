"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServiceAreaTrade() {
  return (
    <section className="bg-slate-50 py-20 px-8">
      <div className="max-w-5xl mx-auto text-center">

        <h2 className="text-slate-900 text-3xl md:text-4xl font-semibold leading-tight tracking-tight" data-pebble-id="pb-3ed235">
          <RevealWords>Proudly Serving Portland & Surrounding Areas</RevealWords>
        </h2>

        <Stagger className="mt-10 flex flex-wrap justify-center gap-3">
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            SE Portland
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            NE Portland
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            North Portland
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            SW Portland
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Beaverton
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Hillsboro
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Lake Oswego
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Milwaukie
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Gresham
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Tigard
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Tualatin
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            St. Johns
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
