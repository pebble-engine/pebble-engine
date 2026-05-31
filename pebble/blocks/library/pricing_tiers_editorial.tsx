"use client";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function PricingTiersEditorial() {
  return (
    <section className="bg-{{bg}} py-28 px-8">
      <div className="container mx-auto max-w-4xl">

        {/* Header — left-aligned, ruled */}
        <div className="mb-16 border-b border-{{fg}}/10 pb-10">
          <p className="text-{{muted}} text-xs uppercase tracking-widest mb-4 font-sans">
            {{eyebrow}}
          </p>
          <h2 className="font-serif text-{{fg}} text-4xl md:text-5xl leading-tight max-w-lg">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        {/* Tiers — stacked table rows, no cards, no color fill */}
        <Stagger className="divide-y divide-{{fg}}/8">
          {/* {{tiers_list_start}} */}
          <StaggerItem className="py-10 grid grid-cols-1 md:grid-cols-12 gap-6 md:gap-10 items-start">

            {/* Tier name + price — left 4 cols */}
            <div className="md:col-span-4">
              <span className="text-{{muted}} text-xs uppercase tracking-widest font-sans block mb-3">
                {{tiers[].name}}
              </span>
              <div className="flex items-baseline gap-1">
                <span className="font-serif text-{{fg}} text-4xl leading-none">
                  {{tiers[].price}}
                </span>
                <span className="text-{{fg}}/35 text-sm font-sans">
                  {{tiers[].period}}
                </span>
              </div>
            </div>

            {/* Feature list — right 8 cols */}
            <div className="md:col-span-5">
              <ul className="space-y-2">
                {/* {{tiers[].features_list_start}} */}
                <li className="text-{{fg}}/60 text-sm leading-relaxed font-sans flex items-start gap-2">
                  <span className="text-{{fg}}/25 text-xs mt-px" aria-hidden="true">—</span>
                  <span>{{tiers[].features[]}}</span>
                </li>
                {/* {{tiers[].features_list_end}} */}
              </ul>
            </div>

            {/* CTA — right 3 cols */}
            <div className="md:col-span-3 md:text-right">
              <a
                href="#contact"
                className="inline-block text-{{fg}} text-sm font-sans tracking-wide border-b border-{{fg}}/40 pb-px hover:border-{{fg}} transition-colors"
              >
                {{tiers[].cta}}
              </a>
            </div>

          </StaggerItem>
          {/* {{tiers_list_end}} */}
        </Stagger>

      </div>
    </section>
  );
}
