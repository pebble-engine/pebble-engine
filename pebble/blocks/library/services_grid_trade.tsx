"use client";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridTrade() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="max-w-6xl mx-auto">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-{{accent}} text-xs font-semibold uppercase tracking-[0.2em] mb-4">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-4xl md:text-5xl font-semibold leading-tight max-w-xl tracking-tight">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        {/* Services grid — photo-top cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-slate-200">
          {/* {{services_list_start}} */}
          <StaggerItem className="bg-{{bg}} flex flex-col overflow-hidden">
            <div className="aspect-[4/3] overflow-hidden bg-slate-100">
              <img
                src="{{services[].image}}"
                alt="{{services[].title}}"
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-{{fg}} text-lg font-semibold leading-snug">
                {{services[].title}}
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1">
                {{services[].body}}
              </p>
              <span className="inline-block self-start bg-{{accent}}/10 text-{{accent}} text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded">
                {{services[].from_price}}
              </span>
              <a
                href="#contact"
                className="text-{{accent}} text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-{{accent}}/50 rounded"
              >
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          {/* {{services_list_end}} */}
        </Stagger>

      </div>
    </section>
  );
}
