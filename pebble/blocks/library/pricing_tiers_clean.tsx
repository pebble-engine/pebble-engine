"use client";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function PricingTiersClean() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-4">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-4xl md:text-5xl font-semibold leading-tight tracking-tight max-w-lg">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        {/* Tier cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">

          {/* {{tiers_list_start}} */}
          <StaggerItem className="relative bg-{{bg}} border border-slate-200 rounded-md p-8 flex flex-col gap-6 ring-1 ring-sky-600">
            {/* Tier name + price */}
            <div>
              <span className="text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em]">
                {{tiers[].name}}
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-{{fg}} text-4xl font-semibold leading-none tracking-tight">
                  {{tiers[].price}}
                </span>
                <span className="text-slate-400 text-sm">
                  {{tiers[].period}}
                </span>
              </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-slate-200" aria-hidden="true" />

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              {/* {{tiers[].features_list_start}} */}
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true">&#10003;</span>
                <span>{{tiers[].features[]}}</span>
              </li>
              {/* {{tiers[].features_list_end}} */}
            </ul>

            {/* CTA */}
            <a
              href="#contact"
              className="mt-2 bg-sky-600 text-white px-6 py-3 rounded-md font-medium text-sm text-center hover:bg-sky-700 transition tracking-wide"
            >
              {{tiers[].cta}}
            </a>
          </StaggerItem>
          {/* {{tiers_list_end}} */}

        </Stagger>
      </div>
    </section>
  );
}
