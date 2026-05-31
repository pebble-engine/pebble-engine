"use client";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function PricingTiersBold() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-{{accent}} text-xs font-black uppercase tracking-[0.3em] mb-4">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-6xl md:text-8xl font-black uppercase leading-none max-w-3xl">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        {/* Tier cards — horizontal stacked, dark */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-4">

          {/* {{tiers_list_start}} */}
          <StaggerItem className="relative bg-{{muted}} rounded-md p-8 flex flex-col gap-6 ring-2 ring-{{accent}}">
            {/* Tier name */}
            <div>
              <span className="text-{{accent}} text-xs font-black uppercase tracking-[0.3em]">
                {{tiers[].name}}
              </span>
              {/* Price */}
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-{{fg}} text-5xl font-black leading-none">
                  {{tiers[].price}}
                </span>
                <span className="text-{{fg}}/40 text-sm uppercase tracking-wide">
                  {{tiers[].period}}
                </span>
              </div>
            </div>

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              {/* {{tiers[].features_list_start}} */}
              <li className="flex items-start gap-3 text-{{fg}}/70 text-sm leading-snug">
                <span className="mt-0.5 text-{{accent}} font-black text-base leading-none" aria-hidden="true">+</span>
                <span>{{tiers[].features[]}}</span>
              </li>
              {/* {{tiers[].features_list_end}} */}
            </ul>

            {/* CTA */}
            <a
              href="#signup"
              className="mt-2 bg-{{accent}} text-{{bg}} px-8 py-4 rounded-md font-black uppercase tracking-widest text-sm text-center hover:scale-105 hover:bg-{{fg}} transition-all duration-150"
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
