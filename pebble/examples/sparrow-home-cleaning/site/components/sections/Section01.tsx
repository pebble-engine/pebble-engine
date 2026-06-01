"use client";

import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function TrustStripTrade() {
  return (
    <section className="bg-sky-50 py-16 md:py-20 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Credentials stat band — 2 cols mobile, 4 cols desktop */}
        <Stagger className="grid grid-cols-2 md:grid-cols-4 gap-px bg-slate-200/30">
          
          <StaggerItem className="bg-sky-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-sky-600 leading-none" data-pebble-id="pb-01b38e">
              Fully Insured
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-418dec">
              & Bonded
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-sky-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-sky-600 leading-none" data-pebble-id="pb-52872b">
              Background-
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-b4f9b8">
              Checked Staff
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-sky-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-sky-600 leading-none" data-pebble-id="pb-7ef98c">
              Satisfaction
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-6f7140">
              Guarantee, Every Visit
            </p>
          </StaggerItem>
          
          <StaggerItem className="bg-sky-50 flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-sky-600 leading-none" data-pebble-id="pb-f8cc46">
              Eco-Friendly
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600 leading-snug mt-1" data-pebble-id="pb-a5228e">
              Products Available
            </p>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
