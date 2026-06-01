"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function PricingTiersBold() {
  return (
    <section className="bg-zinc-900 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-lime-400 text-xs font-black uppercase tracking-[0.3em] mb-4" data-pebble-id="pb-80bc65">
            CHOOSE YOUR TIER
          </p>
          <h2 className="text-zinc-50 text-6xl md:text-8xl font-black uppercase leading-none max-w-3xl" data-pebble-id="pb-a06cfb">
            <RevealWords>INVEST IN YOURSELF. COMMIT.</RevealWords>
          </h2>
        </div>

        {/* Tier cards — horizontal stacked, dark */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-4">

          
          <StaggerItem className="relative bg-zinc-700 rounded-md p-8 flex flex-col gap-6 ring-2 ring-lime-400">
            {/* Tier name */}
            <div>
              <span className="text-lime-400 text-xs font-black uppercase tracking-[0.3em]" data-pebble-id="pb-74f8cc">
                DROP-IN
              </span>
              {/* Price */}
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-zinc-50 text-5xl font-black leading-none" data-pebble-id="pb-01f342">
                  $25
                </span>
                <span className="text-zinc-50/40 text-sm uppercase tracking-wide" data-pebble-id="pb-0fdbcf">
                  per class
                </span>
              </div>
            </div>

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-148503">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-f2e143">+</span>
                <span data-pebble-id="pb-4ee9a8">Single coached group WOD</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-f117ae">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-9865ce">+</span>
                <span data-pebble-id="pb-777d2a">Access to all equipment</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-204cfb">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-f016a1">+</span>
                <span data-pebble-id="pb-472f31">Coach-led warm-up and cool-down</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-0dc240">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-180919">+</span>
                <span data-pebble-id="pb-73a94b">Full scaling options provided</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#signup"
              className="mt-2 bg-lime-400 text-zinc-900 px-8 py-4 rounded-md font-black uppercase tracking-widest text-sm text-center hover:scale-105 hover:bg-zinc-50 transition-all duration-150" data-pebble-id="pb-11d1ec">
              BOOK A CLASS
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-zinc-700 rounded-md p-8 flex flex-col gap-6 ring-2 ring-lime-400">
            {/* Tier name */}
            <div>
              <span className="text-lime-400 text-xs font-black uppercase tracking-[0.3em]" data-pebble-id="pb-d9c02a">
                UNLIMITED
              </span>
              {/* Price */}
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-zinc-50 text-5xl font-black leading-none" data-pebble-id="pb-4994fa">
                  $149
                </span>
                <span className="text-zinc-50/40 text-sm uppercase tracking-wide" data-pebble-id="pb-2aa5b9">
                  /month
                </span>
              </div>
            </div>

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-91575a">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-be5ec4">+</span>
                <span data-pebble-id="pb-1346d5">Unlimited group WOD classes</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-f9a3f8">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-227b74">+</span>
                <span data-pebble-id="pb-277017">First Light 6am access included</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-599dc1">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-160e74">+</span>
                <span data-pebble-id="pb-84f108">Open gym floor time</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-8b20a4">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-30cb05">+</span>
                <span data-pebble-id="pb-54d6b9">Monthly progress check-in with a coach</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-ef23b9">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-d92b38">+</span>
                <span data-pebble-id="pb-3ededb">Members-only community events</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#signup"
              className="mt-2 bg-lime-400 text-zinc-900 px-8 py-4 rounded-md font-black uppercase tracking-widest text-sm text-center hover:scale-105 hover:bg-zinc-50 transition-all duration-150" data-pebble-id="pb-5daf39">
              JOIN NOW
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-zinc-700 rounded-md p-8 flex flex-col gap-6 ring-2 ring-lime-400">
            {/* Tier name */}
            <div>
              <span className="text-lime-400 text-xs font-black uppercase tracking-[0.3em]" data-pebble-id="pb-100a7e">
                ELITE
              </span>
              {/* Price */}
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-zinc-50 text-5xl font-black leading-none" data-pebble-id="pb-449eb4">
                  $249
                </span>
                <span className="text-zinc-50/40 text-sm uppercase tracking-wide" data-pebble-id="pb-15582c">
                  /month
                </span>
              </div>
            </div>

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-d259d1">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-4dc12a">+</span>
                <span data-pebble-id="pb-31c7b0">Everything in Unlimited</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-3367c4">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-2b5173">+</span>
                <span data-pebble-id="pb-e59dd1">2x personal coaching sessions/month</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-14ddba">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-018c72">+</span>
                <span data-pebble-id="pb-554cdb">Custom programming and goal tracking</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-bb5555">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-ddb459">+</span>
                <span data-pebble-id="pb-46f845">Priority scheduling for all classes</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-6d6e88">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-3eacb0">+</span>
                <span data-pebble-id="pb-20cd73">Nutrition guidance add-on available</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#signup"
              className="mt-2 bg-lime-400 text-zinc-900 px-8 py-4 rounded-md font-black uppercase tracking-widest text-sm text-center hover:scale-105 hover:bg-zinc-50 transition-all duration-150" data-pebble-id="pb-d49fbf">
              GO ELITE
            </a>
          </StaggerItem>
          

        </Stagger>
      </div>
    </section>
  );
}
