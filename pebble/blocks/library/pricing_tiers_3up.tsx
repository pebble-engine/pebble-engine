"use client";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function PricingSimple() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="text-center mb-16">
          <p className="text-{{accent}} text-sm uppercase tracking-widest mb-3">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-5xl md:text-6xl font-bold leading-tight max-w-2xl mx-auto">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        {/* Tier cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">

          {/* {{tiers_list_start}} */}
          <StaggerItem className="relative bg-{{muted}}/40 rounded-3xl p-8 flex flex-col gap-6 ring-2 ring-{{accent}}">
            {/* Tier name */}
            <div>
              <span className="text-{{accent}} text-xs font-semibold uppercase tracking-widest">
                {{tiers[].name}}
              </span>
              {/* Price */}
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-{{fg}} text-5xl font-bold leading-none">
                  {{tiers[].price}}
                </span>
                <span className="text-{{fg}}/50 text-base">
                  {{tiers[].period}}
                </span>
              </div>
            </div>

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              {/* {{tiers[].features_list_start}} */}
              <li className="flex items-start gap-3 text-{{fg}}/75 text-base leading-snug">
                <span className="mt-1 text-{{accent}} text-lg leading-none" aria-hidden="true">✓</span>
                <span>{{tiers[].features[]}}</span>
              </li>
              {/* {{tiers[].features_list_end}} */}
            </ul>

            {/* CTA */}
            <a
              href="#order"
              className="mt-2 bg-{{accent}} text-{{bg}} px-8 py-4 rounded-full font-semibold text-center hover:opacity-90 transition"
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
