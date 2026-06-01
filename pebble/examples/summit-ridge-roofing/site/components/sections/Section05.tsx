"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServiceAreaTrade() {
  return (
    <section className="bg-slate-50 py-20 px-8">
      <div className="max-w-5xl mx-auto text-center">

        <h2 className="text-slate-900 text-3xl md:text-4xl font-semibold leading-tight tracking-tight" data-pebble-id="pb-06db60">
          <RevealWords>Proudly Serving Kansas City & Surrounding Areas</RevealWords>
        </h2>

        <Stagger className="mt-10 flex flex-wrap justify-center gap-3">
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Kansas City, MO
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Lee's Summit
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Overland Park, KS
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Lenexa
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Olathe
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Independence
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Blue Springs
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Shawnee
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Raytown
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Liberty
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Gladstone
          </StaggerItem>
          
          <StaggerItem className="inline-block border border-sky-700/40 text-slate-900 px-4 py-2 rounded-full text-sm tracking-wide">
            Belton
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
