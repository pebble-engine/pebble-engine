"use client";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServiceAreaTrade() {
  return (
    <section className="bg-{{bg}} py-20 px-8">
      <div className="max-w-5xl mx-auto text-center">

        <h2 className="text-{{fg}} text-3xl md:text-4xl font-semibold leading-tight tracking-tight">
          <RevealWords>{{headline}}</RevealWords>
        </h2>

        <Stagger className="mt-10 flex flex-wrap justify-center gap-3">
          {/* {{areas_list_start}} */}
          <StaggerItem className="inline-block border border-{{accent}}/40 text-{{fg}} px-4 py-2 rounded-full text-sm tracking-wide">
            {{areas[]}}
          </StaggerItem>
          {/* {{areas_list_end}} */}
        </Stagger>

      </div>
    </section>
  );
}
