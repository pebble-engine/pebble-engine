"use client";

import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function TrustStripTrade() {
  return (
    <section className="bg-slate-50 py-16 md:py-20 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Credentials stat band — 2 cols mobile, 4 cols desktop */}
        <Stagger className="grid grid-cols-2 md:grid-cols-4 gap-px bg-slate-200/30">
          
          <StaggerItem className="bg-slate-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-sky-700 leading-none" data-pebble-id="pb-18cc7d">
              NATE-Certified
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-0e2c7b">
              Licensed Technicians
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-sky-700 leading-none" data-pebble-id="pb-a11fe5">
              24/7
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-d32eca">
              Emergency Service
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-sky-700 leading-none" data-pebble-id="pb-4ec658">
              Flat-Rate
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-f9173c">
              Upfront Pricing
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-sky-700 leading-none" data-pebble-id="pb-d0c091">
              Licensed & Insured
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-85ab90">
              Fully Credentialed
            </p>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
