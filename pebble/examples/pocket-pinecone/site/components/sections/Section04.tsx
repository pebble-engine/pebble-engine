"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function PricingTiersPlayful() {
  return (
    <section className="bg-pink-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="text-center mb-16">
          <p className="inline-flex items-center gap-2 bg-pink-500 text-white text-sm font-bold px-5 py-2 rounded-full mb-5 tracking-wide" data-pebble-id="pb-eb9257">
            Pick your play
          </p>
          <h2 className="text-purple-900 text-5xl md:text-6xl font-extrabold leading-tight max-w-2xl mx-auto" data-pebble-id="pb-6feee7">
            <RevealWords>Great gifts for every budget, no guesswork needed</RevealWords>
          </h2>
        </div>

        {/* Tier cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">

          
          <StaggerItem className="relative bg-white rounded-[2rem] p-8 flex flex-col gap-6 shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-200">
            {/* Name + price */}
            <div>
              <span className="text-pink-500 text-xs font-extrabold uppercase tracking-widest" data-pebble-id="pb-b75d77">
                Stocking Stuffers
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-purple-900 text-5xl font-extrabold leading-none" data-pebble-id="pb-83a9b3">
                  $5 – $15
                </span>
                <span className="text-purple-900/50 text-base" data-pebble-id="pb-7046ba">
                  per item
                </span>
              </div>
            </div>

            {/* Features */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-119566">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-fa5b27">&#10003;</span>
                <span data-pebble-id="pb-1b392e">Mystery cubby surprise toys ($5 each)</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-d9b6d6">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-cb067e">&#10003;</span>
                <span data-pebble-id="pb-33ffe0">Wind-up critters and novelties</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-ef6da0">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-26e533">&#10003;</span>
                <span data-pebble-id="pb-925494">Small wooden figures and animals</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-f35722">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-cfb94a">&#10003;</span>
                <span data-pebble-id="pb-8dc886">Great for party favors or add-ons</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#book"
              className="mt-2 bg-pink-500 text-white px-10 py-5 rounded-full font-extrabold text-center shadow hover:scale-105 hover:rotate-1 hover:shadow-pink-300 transition-all duration-200" data-pebble-id="pb-385529">
              Browse the shop
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-white rounded-[2rem] p-8 flex flex-col gap-6 shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-200">
            {/* Name + price */}
            <div>
              <span className="text-pink-500 text-xs font-extrabold uppercase tracking-widest" data-pebble-id="pb-d6639a">
                Sweet Spot Gifts
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-purple-900 text-5xl font-extrabold leading-none" data-pebble-id="pb-f9a5b1">
                  $16 – $45
                </span>
                <span className="text-purple-900/50 text-base" data-pebble-id="pb-c4b737">
                  per item
                </span>
              </div>
            </div>

            {/* Features */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-962c6f">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-9a1d76">&#10003;</span>
                <span data-pebble-id="pb-64789b">Open-ended building and stacking sets</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-125381">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-874f94">&#10003;</span>
                <span data-pebble-id="pb-a03acd">Indie card and strategy games</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-c3237e">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-b727b3">&#10003;</span>
                <span data-pebble-id="pb-370941">Wooden play kitchens and small-world sets</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-073872">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-d2024e">&#10003;</span>
                <span data-pebble-id="pb-fd4ac5">Hand-picked for ages 2–10</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#book"
              className="mt-2 bg-pink-500 text-white px-10 py-5 rounded-full font-extrabold text-center shadow hover:scale-105 hover:rotate-1 hover:shadow-pink-300 transition-all duration-200" data-pebble-id="pb-685b9d">
              Come explore
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-white rounded-[2rem] p-8 flex flex-col gap-6 shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-200">
            {/* Name + price */}
            <div>
              <span className="text-pink-500 text-xs font-extrabold uppercase tracking-widest" data-pebble-id="pb-33b0de">
                Heirloom Picks
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-purple-900 text-5xl font-extrabold leading-none" data-pebble-id="pb-d92c01">
                  $50 – $120
                </span>
                <span className="text-purple-900/50 text-base" data-pebble-id="pb-1ba469">
                  per item
                </span>
              </div>
            </div>

            {/* Features */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-917716">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-9f6f35">&#10003;</span>
                <span data-pebble-id="pb-0ee0a0">Large wooden playsets and dollhouses</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-8a62e2">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-cf3aee">&#10003;</span>
                <span data-pebble-id="pb-d81312">Premium building and marble run sets</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-ffe10e">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-18bb98">&#10003;</span>
                <span data-pebble-id="pb-c42cc2">Curated gift bundles we put together for you</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-f7161f">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-108324">&#10003;</span>
                <span data-pebble-id="pb-ee21ae">Toys built to survive years of love</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#book"
              className="mt-2 bg-pink-500 text-white px-10 py-5 rounded-full font-extrabold text-center shadow hover:scale-105 hover:rotate-1 hover:shadow-pink-300 transition-all duration-200" data-pebble-id="pb-81f39c">
              Ask us for help
            </a>
          </StaggerItem>
          

        </Stagger>
      </div>
    </section>
  );
}
