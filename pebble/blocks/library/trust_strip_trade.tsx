"use client";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function TrustStripTrade() {
  return (
    <section className="bg-{{bg}} py-16 md:py-20 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Credentials stat band — 2 cols mobile, 4 cols desktop */}
        <Stagger className="grid grid-cols-2 md:grid-cols-4 gap-px bg-slate-200/30">
          {/* {{stats_list_start}} */}
          <StaggerItem className="bg-{{bg}} flex flex-col items-center justify-center gap-2 px-6 py-10 text-center md:border-l md:border-slate-200/30 md:first:border-l-0">
            <p className="text-3xl md:text-5xl font-semibold tabular-nums text-{{accent}} leading-none">
              {{stats[].value}}
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-{{muted}} leading-snug mt-1">
              {{stats[].label}}
            </p>
          </StaggerItem>
          {/* {{stats_list_end}} */}
        </Stagger>

      </div>
    </section>
  );
}
