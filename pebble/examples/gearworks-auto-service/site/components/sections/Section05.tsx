"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServiceAreaTrade() {
  return (
    <section className="bg-slate-50 py-20 px-8">
      <div className="max-w-5xl mx-auto text-center">

        <h2 className="text-slate-900 text-3xl md:text-4xl font-semibold leading-tight tracking-tight" data-pebble-id="pb-00782d">
          <RevealWords>Serving Columbus & the Surrounding Communities</RevealWords>
        </h2>

        <Stagger className="mt-10 flex flex-wrap justify-center gap-3">
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Columbus
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Dublin
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Westerville
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Gahanna
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Hilliard
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Grove City
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Pickerington
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Upper Arlington
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Worthington
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            New Albany
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
