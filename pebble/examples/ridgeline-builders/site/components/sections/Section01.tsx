"use client";

import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function TrustStripTrade() {
  return (
    <section className="bg-stone-50 py-16 md:py-20 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Credentials stat band — 2 cols mobile, 4 cols desktop */}
        <Stagger className="grid grid-cols-2 md:grid-cols-4 gap-px bg-slate-200/30">
          
          <StaggerItem className="bg-stone-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-amber-700 leading-none" data-pebble-id="pb-af0b35">
              Licensed
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-6e8f0d">
              Idaho General Contractor
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-stone-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-amber-700 leading-none" data-pebble-id="pb-bbdd4e">
              Fully Insured
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-84a3a5">
              Every Project, Every Trade
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-stone-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-amber-700 leading-none" data-pebble-id="pb-d91ec2">
              Fixed Price
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-cefd39">
              No Hidden Change Orders
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-stone-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-amber-700 leading-none" data-pebble-id="pb-52be4d">
              Free Estimates
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-307d43">
              In-Home Consultations
            </p>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
