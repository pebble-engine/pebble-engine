"use client";

import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function TrustStripTrade() {
  return (
    <section className="bg-slate-50 py-16 md:py-20 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Credentials stat band — 2 cols mobile, 4 cols desktop */}
        <Stagger className="grid grid-cols-2 md:grid-cols-4 gap-px bg-slate-200/30">
          
          <StaggerItem className="bg-slate-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-amber-600 leading-none" data-pebble-id="pb-5e7c71">
              Licensed
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-1c84bd">
              Master Electrician
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-amber-600 leading-none" data-pebble-id="pb-437a57">
              Same-Day
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-9ef46b">
              Diagnostic Visits
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-amber-600 leading-none" data-pebble-id="pb-160706">
              Upfront
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-afdc47">
              Written Estimates
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-amber-600 leading-none" data-pebble-id="pb-d606cb">
              Permit-Ready
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-495618">
              All Travis County Jurisdictions
            </p>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
