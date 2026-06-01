"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function PricingTiersEditorial() {
  return (
    <section className="bg-neutral-50 py-28 px-8">
      <div className="container mx-auto max-w-4xl">

        {/* Header — left-aligned, ruled */}
        <div className="mb-16 border-b border-neutral-900/10 pb-10">
          <p className="text-neutral-200 text-xs uppercase tracking-widest mb-4 font-sans" data-pebble-id="pb-2cd736">
            Rates
          </p>
          <h2 className="font-serif text-neutral-900 text-4xl md:text-5xl leading-tight max-w-lg" data-pebble-id="pb-f6ef66">
            <RevealWords>Honest rates for considered work.</RevealWords>
          </h2>
        </div>

        {/* Tiers — stacked table rows, no cards, no color fill */}
        <Stagger className="divide-y divide-neutral-900/8">
          
          <StaggerItem className="py-10 grid grid-cols-1 md:grid-cols-12 gap-6 md:gap-10 items-start">

            {/* Tier name + price — left 4 cols */}
            <div className="md:col-span-4">
              <span className="text-neutral-200 text-xs uppercase tracking-widest font-sans block mb-3" data-pebble-id="pb-5ac2ad">
                Elopement
              </span>
              <div className="flex items-baseline gap-1">
                <span className="font-serif text-neutral-900 text-4xl leading-none" data-pebble-id="pb-95fa96">
                  $1,400
                </span>
                <span className="text-neutral-900/35 text-sm font-sans" data-pebble-id="pb-7a5324">
                  /day
                </span>
              </div>
            </div>

            {/* Feature list — right 8 cols */}
            <div className="md:col-span-5">
              <ul className="space-y-2">
                
                <li className="text-neutral-900/60 text-sm leading-relaxed font-sans flex items-start gap-2" data-pebble-id="pb-b980d8">
                  <span className="text-neutral-900/25 text-xs mt-px" aria-hidden="true" data-pebble-id="pb-bc20a5">—</span>
                  <span data-pebble-id="pb-d64ca2">Up to 5 hours of coverage</span>
                </li>
                
                <li className="text-neutral-900/60 text-sm leading-relaxed font-sans flex items-start gap-2" data-pebble-id="pb-8be86b">
                  <span className="text-neutral-900/25 text-xs mt-px" aria-hidden="true" data-pebble-id="pb-6ada66">—</span>
                  <span data-pebble-id="pb-b67c71">35mm or medium-format film throughout</span>
                </li>
                
                <li className="text-neutral-900/60 text-sm leading-relaxed font-sans flex items-start gap-2" data-pebble-id="pb-a1d6e7">
                  <span className="text-neutral-900/25 text-xs mt-px" aria-hidden="true" data-pebble-id="pb-cc2d75">—</span>
                  <span data-pebble-id="pb-7cb342">Hand-developed black-and-white rolls</span>
                </li>
                
                <li className="text-neutral-900/60 text-sm leading-relaxed font-sans flex items-start gap-2" data-pebble-id="pb-cdeb0a">
                  <span className="text-neutral-900/25 text-xs mt-px" aria-hidden="true" data-pebble-id="pb-4c311a">—</span>
                  <span data-pebble-id="pb-4711cd">60–90 scanned images delivered</span>
                </li>
                
              </ul>
            </div>

            {/* CTA — right 3 cols */}
            <div className="md:col-span-3 md:text-right">
              <a
                href="#contact"
                className="inline-block text-neutral-900 text-sm font-sans tracking-wide border-b border-neutral-900/40 pb-px hover:border-neutral-900 transition-colors" data-pebble-id="pb-218770">
                Inquire
              </a>
            </div>

          </StaggerItem>
          
          <StaggerItem className="py-10 grid grid-cols-1 md:grid-cols-12 gap-6 md:gap-10 items-start">

            {/* Tier name + price — left 4 cols */}
            <div className="md:col-span-4">
              <span className="text-neutral-200 text-xs uppercase tracking-widest font-sans block mb-3" data-pebble-id="pb-59220f">
                Ceremony & Portraits
              </span>
              <div className="flex items-baseline gap-1">
                <span className="font-serif text-neutral-900 text-4xl leading-none" data-pebble-id="pb-7bc697">
                  $2,200
                </span>
                <span className="text-neutral-900/35 text-sm font-sans" data-pebble-id="pb-e5e037">
                  /day
                </span>
              </div>
            </div>

            {/* Feature list — right 8 cols */}
            <div className="md:col-span-5">
              <ul className="space-y-2">
                
                <li className="text-neutral-900/60 text-sm leading-relaxed font-sans flex items-start gap-2" data-pebble-id="pb-af9256">
                  <span className="text-neutral-900/25 text-xs mt-px" aria-hidden="true" data-pebble-id="pb-0dcaff">—</span>
                  <span data-pebble-id="pb-8f0c0b">4–5 hours of coverage</span>
                </li>
                
                <li className="text-neutral-900/60 text-sm leading-relaxed font-sans flex items-start gap-2" data-pebble-id="pb-82398a">
                  <span className="text-neutral-900/25 text-xs mt-px" aria-hidden="true" data-pebble-id="pb-abacd9">—</span>
                  <span data-pebble-id="pb-699e47">Ceremony, quiet hour, and portraits</span>
                </li>
                
                <li className="text-neutral-900/60 text-sm leading-relaxed font-sans flex items-start gap-2" data-pebble-id="pb-3e5f6f">
                  <span className="text-neutral-900/25 text-xs mt-px" aria-hidden="true" data-pebble-id="pb-fbac4c">—</span>
                  <span data-pebble-id="pb-50ff22">Both 35mm and medium-format</span>
                </li>
                
                <li className="text-neutral-900/60 text-sm leading-relaxed font-sans flex items-start gap-2" data-pebble-id="pb-1091d1">
                  <span className="text-neutral-900/25 text-xs mt-px" aria-hidden="true" data-pebble-id="pb-c954ff">—</span>
                  <span data-pebble-id="pb-002259">Hand-developed black-and-whites</span>
                </li>
                
                <li className="text-neutral-900/60 text-sm leading-relaxed font-sans flex items-start gap-2" data-pebble-id="pb-c36cdf">
                  <span className="text-neutral-900/25 text-xs mt-px" aria-hidden="true" data-pebble-id="pb-b9a6c2">—</span>
                  <span data-pebble-id="pb-99fa0c">100–130 scanned images delivered</span>
                </li>
                
              </ul>
            </div>

            {/* CTA — right 3 cols */}
            <div className="md:col-span-3 md:text-right">
              <a
                href="#contact"
                className="inline-block text-neutral-900 text-sm font-sans tracking-wide border-b border-neutral-900/40 pb-px hover:border-neutral-900 transition-colors" data-pebble-id="pb-68c8c8">
                Inquire
              </a>
            </div>

          </StaggerItem>
          
          <StaggerItem className="py-10 grid grid-cols-1 md:grid-cols-12 gap-6 md:gap-10 items-start">

            {/* Tier name + price — left 4 cols */}
            <div className="md:col-span-4">
              <span className="text-neutral-200 text-xs uppercase tracking-widest font-sans block mb-3" data-pebble-id="pb-7e27b6">
                Full Day
              </span>
              <div className="flex items-baseline gap-1">
                <span className="font-serif text-neutral-900 text-4xl leading-none" data-pebble-id="pb-24b276">
                  $3,800
                </span>
                <span className="text-neutral-900/35 text-sm font-sans" data-pebble-id="pb-51e4a0">
                  /day
                </span>
              </div>
            </div>

            {/* Feature list — right 8 cols */}
            <div className="md:col-span-5">
              <ul className="space-y-2">
                
                <li className="text-neutral-900/60 text-sm leading-relaxed font-sans flex items-start gap-2" data-pebble-id="pb-89da3a">
                  <span className="text-neutral-900/25 text-xs mt-px" aria-hidden="true" data-pebble-id="pb-8a0c01">—</span>
                  <span data-pebble-id="pb-6e880c">8–10 hours of coverage</span>
                </li>
                
                <li className="text-neutral-900/60 text-sm leading-relaxed font-sans flex items-start gap-2" data-pebble-id="pb-518aec">
                  <span className="text-neutral-900/25 text-xs mt-px" aria-hidden="true" data-pebble-id="pb-615d74">—</span>
                  <span data-pebble-id="pb-47f152">Getting ready through last dance</span>
                </li>
                
                <li className="text-neutral-900/60 text-sm leading-relaxed font-sans flex items-start gap-2" data-pebble-id="pb-ff4e4f">
                  <span className="text-neutral-900/25 text-xs mt-px" aria-hidden="true" data-pebble-id="pb-d5fb60">—</span>
                  <span data-pebble-id="pb-dd68b1">All film developed and scanned by hand</span>
                </li>
                
                <li className="text-neutral-900/60 text-sm leading-relaxed font-sans flex items-start gap-2" data-pebble-id="pb-da76ab">
                  <span className="text-neutral-900/25 text-xs mt-px" aria-hidden="true" data-pebble-id="pb-67da8c">—</span>
                  <span data-pebble-id="pb-53130c">180–220 scanned images delivered</span>
                </li>
                
              </ul>
            </div>

            {/* CTA — right 3 cols */}
            <div className="md:col-span-3 md:text-right">
              <a
                href="#contact"
                className="inline-block text-neutral-900 text-sm font-sans tracking-wide border-b border-neutral-900/40 pb-px hover:border-neutral-900 transition-colors" data-pebble-id="pb-f04037">
                Inquire
              </a>
            </div>

          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
