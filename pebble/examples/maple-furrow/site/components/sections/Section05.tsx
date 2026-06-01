"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function PricingPrixFixe() {
  return (
    <section className="bg-stone-50 py-24 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Section header */}
        <div className="text-center mb-16">
          <p className="text-amber-800 text-sm uppercase tracking-widest font-sans mb-3" data-pebble-id="pb-fc6414">
            The offering
          </p>
          <h2 className="text-stone-900 font-serif text-4xl md:text-5xl leading-tight max-w-xl mx-auto" data-pebble-id="pb-7706af">
            <RevealWords>A meal worth planning for.</RevealWords>
          </h2>
        </div>

        {/* Prix-fixe tier cards — warm parchment styling */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">

          
          <StaggerItem className="relative bg-stone-100/30 rounded-3xl p-8 flex flex-col gap-6 border border-stone-900/10 hover:border-amber-800/40 transition-colors duration-200">
            {/* Tier name */}
            <div>
              <span className="text-amber-800 font-sans text-xs font-semibold uppercase tracking-widest" data-pebble-id="pb-8667ff">
                À la carte
              </span>
              {/* Price */}
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-stone-900 font-serif text-5xl leading-none" data-pebble-id="pb-0c421b">
                  From $13
                </span>
                <span className="text-stone-900/50 font-sans text-sm" data-pebble-id="pb-8287b0">
                  per dish
                </span>
              </div>
            </div>

            {/* Course / feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-stone-900/75 font-sans text-sm leading-snug" data-pebble-id="pb-e14e2a">
                <span className="mt-0.5 text-amber-800 text-base leading-none" aria-hidden="true" data-pebble-id="pb-db4eb8">✦</span>
                <span data-pebble-id="pb-990b2e">Full menu, order at your own pace</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 font-sans text-sm leading-snug" data-pebble-id="pb-4e1ff9">
                <span className="mt-0.5 text-amber-800 text-base leading-none" aria-hidden="true" data-pebble-id="pb-c94d28">✦</span>
                <span data-pebble-id="pb-f8c990">Dishes sourced from named local farms</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 font-sans text-sm leading-snug" data-pebble-id="pb-aacf73">
                <span className="mt-0.5 text-amber-800 text-base leading-none" aria-hidden="true" data-pebble-id="pb-ab6a1a">✦</span>
                <span data-pebble-id="pb-bd8437">Menu rotates every few weeks</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 font-sans text-sm leading-snug" data-pebble-id="pb-dfa680">
                <span className="mt-0.5 text-amber-800 text-base leading-none" aria-hidden="true" data-pebble-id="pb-448fd6">✦</span>
                <span data-pebble-id="pb-d1586a">Vegetarian options always available</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 font-sans text-sm leading-snug" data-pebble-id="pb-3b3edd">
                <span className="mt-0.5 text-amber-800 text-base leading-none" aria-hidden="true" data-pebble-id="pb-29e559">✦</span>
                <span data-pebble-id="pb-d456d9">Wine & local cider pairings available</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#reserve"
              className="mt-2 bg-amber-800 text-stone-50 px-8 py-4 rounded-full font-sans font-semibold text-center hover:scale-105 hover:opacity-95 transition-transform duration-200" data-pebble-id="pb-cdf7e7">
              Reserve a table
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-stone-100/30 rounded-3xl p-8 flex flex-col gap-6 border border-stone-900/10 hover:border-amber-800/40 transition-colors duration-200">
            {/* Tier name */}
            <div>
              <span className="text-amber-800 font-sans text-xs font-semibold uppercase tracking-widest" data-pebble-id="pb-d7357d">
                Chef's tasting
              </span>
              {/* Price */}
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-stone-900 font-serif text-5xl leading-none" data-pebble-id="pb-191783">
                  $72
                </span>
                <span className="text-stone-900/50 font-sans text-sm" data-pebble-id="pb-bd2d4a">
                  per person
                </span>
              </div>
            </div>

            {/* Course / feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-stone-900/75 font-sans text-sm leading-snug" data-pebble-id="pb-0ab6fa">
                <span className="mt-0.5 text-amber-800 text-base leading-none" aria-hidden="true" data-pebble-id="pb-9ffca2">✦</span>
                <span data-pebble-id="pb-46193a">Five courses chosen by the kitchen</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 font-sans text-sm leading-snug" data-pebble-id="pb-c816f5">
                <span className="mt-0.5 text-amber-800 text-base leading-none" aria-hidden="true" data-pebble-id="pb-290f3b">✦</span>
                <span data-pebble-id="pb-8c51aa">Reflects whatever arrived from the farms this week</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 font-sans text-sm leading-snug" data-pebble-id="pb-e1d38b">
                <span className="mt-0.5 text-amber-800 text-base leading-none" aria-hidden="true" data-pebble-id="pb-8b1872">✦</span>
                <span data-pebble-id="pb-5d65c9">Paired with seasonal wine or cider (add $38)</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 font-sans text-sm leading-snug" data-pebble-id="pb-8bed72">
                <span className="mt-0.5 text-amber-800 text-base leading-none" aria-hidden="true" data-pebble-id="pb-fd906c">✦</span>
                <span data-pebble-id="pb-dcbcc2">Available Thursday – Sunday, full table only</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 font-sans text-sm leading-snug" data-pebble-id="pb-a3ed72">
                <span className="mt-0.5 text-amber-800 text-base leading-none" aria-hidden="true" data-pebble-id="pb-ce6904">✦</span>
                <span data-pebble-id="pb-0bf0e9">48-hour advance reservation required</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#reserve"
              className="mt-2 bg-amber-800 text-stone-50 px-8 py-4 rounded-full font-sans font-semibold text-center hover:scale-105 hover:opacity-95 transition-transform duration-200" data-pebble-id="pb-b0e59a">
              Book the tasting
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-stone-100/30 rounded-3xl p-8 flex flex-col gap-6 border border-stone-900/10 hover:border-amber-800/40 transition-colors duration-200">
            {/* Tier name */}
            <div>
              <span className="text-amber-800 font-sans text-xs font-semibold uppercase tracking-widest" data-pebble-id="pb-72eb6c">
                Private dining
              </span>
              {/* Price */}
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-stone-900 font-serif text-5xl leading-none" data-pebble-id="pb-87e278">
                  From $800
                </span>
                <span className="text-stone-900/50 font-sans text-sm" data-pebble-id="pb-2575b2">
                  per evening
                </span>
              </div>
            </div>

            {/* Course / feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-stone-900/75 font-sans text-sm leading-snug" data-pebble-id="pb-8c29eb">
                <span className="mt-0.5 text-amber-800 text-base leading-none" aria-hidden="true" data-pebble-id="pb-ac6beb">✦</span>
                <span data-pebble-id="pb-fbd99e">Exclusive use of our back room, seats up to 14</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 font-sans text-sm leading-snug" data-pebble-id="pb-43b236">
                <span className="mt-0.5 text-amber-800 text-base leading-none" aria-hidden="true" data-pebble-id="pb-a5daa3">✦</span>
                <span data-pebble-id="pb-06e2a9">Custom menu built around your guests</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 font-sans text-sm leading-snug" data-pebble-id="pb-12452e">
                <span className="mt-0.5 text-amber-800 text-base leading-none" aria-hidden="true" data-pebble-id="pb-592bf5">✦</span>
                <span data-pebble-id="pb-1fa5ae">Full farm sourcing list provided</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 font-sans text-sm leading-snug" data-pebble-id="pb-49329a">
                <span className="mt-0.5 text-amber-800 text-base leading-none" aria-hidden="true" data-pebble-id="pb-c2f4a2">✦</span>
                <span data-pebble-id="pb-4e40d0">Wine pairing available on request</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#reserve"
              className="mt-2 bg-amber-800 text-stone-50 px-8 py-4 rounded-full font-sans font-semibold text-center hover:scale-105 hover:opacity-95 transition-transform duration-200" data-pebble-id="pb-5e5039">
              Inquire now
            </a>
          </StaggerItem>
          

        </Stagger>
      </div>
    </section>
  );
}
