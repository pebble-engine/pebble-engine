"use client";

import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function TrustStripTrade() {
  return (
    <section className="bg-stone-50 py-16 md:py-20 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Credentials stat band — 2 cols mobile, 4 cols desktop */}
        <Stagger className="grid grid-cols-2 md:grid-cols-4 gap-px bg-slate-200/30">
          
          <StaggerItem className="bg-stone-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-green-700 leading-none" data-pebble-id="pb-46c842">
              Licensed & Insured
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-94ee7d">
              Fully credentialed in NC
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-stone-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-green-700 leading-none" data-pebble-id="pb-1ec380">
              Free Consultations
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-1ac39e">
              No-obligation design meeting
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-stone-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-green-700 leading-none" data-pebble-id="pb-2654ab">
              Warranty Backed
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-7c125d">
              Workmanship guarantee on all projects
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-stone-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-green-700 leading-none" data-pebble-id="pb-3bb700">
              Local Roots
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-08f3a7">
              Proudly serving the Triangle area
            </p>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
