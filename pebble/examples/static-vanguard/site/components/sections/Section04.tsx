"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function PricingTiersBold() {
  return (
    <section className="bg-zinc-900 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-lime-400 text-xs font-black uppercase tracking-[0.3em] mb-4" data-pebble-id="pb-2d76dd">
            PARTNERSHIP TIERS
          </p>
          <h2 className="text-zinc-50 text-6xl md:text-8xl font-black uppercase leading-none max-w-3xl" data-pebble-id="pb-184ecc">
            <RevealWords>GET IN BEFORE THE ARENA FILLS UP.</RevealWords>
          </h2>
        </div>

        {/* Tier cards — horizontal stacked, dark */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-4">

          
          <StaggerItem className="relative bg-zinc-700 rounded-md p-8 flex flex-col gap-6 ring-2 ring-lime-400">
            {/* Tier name */}
            <div>
              <span className="text-lime-400 text-xs font-black uppercase tracking-[0.3em]" data-pebble-id="pb-a553ae">
                ALLY
              </span>
              {/* Price */}
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-zinc-50 text-5xl font-black leading-none" data-pebble-id="pb-abc66a">
                  $500
                </span>
                <span className="text-zinc-50/40 text-sm uppercase tracking-wide" data-pebble-id="pb-d28399">
                  /month
                </span>
              </div>
            </div>

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-036f76">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-30a71b">+</span>
                <span data-pebble-id="pb-341b8a">Logo on team social graphics</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-936ef9">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-cc5c25">+</span>
                <span data-pebble-id="pb-a44cff">Shoutout in match-day stream</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-682965">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-eda94c">+</span>
                <span data-pebble-id="pb-1d222c">Discord sponsor channel post</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-842a92">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-87510d">+</span>
                <span data-pebble-id="pb-8c2eea">Monthly performance report</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#signup"
              className="mt-2 bg-lime-400 text-zinc-900 px-8 py-4 rounded-md font-black uppercase tracking-widest text-sm text-center hover:scale-105 hover:bg-zinc-50 transition-all duration-150" data-pebble-id="pb-9b1383">
              START HERE
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-zinc-700 rounded-md p-8 flex flex-col gap-6 ring-2 ring-lime-400">
            {/* Tier name */}
            <div>
              <span className="text-lime-400 text-xs font-black uppercase tracking-[0.3em]" data-pebble-id="pb-1bc524">
                SIGNAL
              </span>
              {/* Price */}
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-zinc-50 text-5xl font-black leading-none" data-pebble-id="pb-f2e8d1">
                  $1,500
                </span>
                <span className="text-zinc-50/40 text-sm uppercase tracking-wide" data-pebble-id="pb-ea897f">
                  /month
                </span>
              </div>
            </div>

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-637a1f">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-6004fd">+</span>
                <span data-pebble-id="pb-de9d59">Jersey sleeve logo placement</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-15c8d4">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-8e3450">+</span>
                <span data-pebble-id="pb-9bdf99">Static glitch intro brand drop</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-00ec33">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-79323f">+</span>
                <span data-pebble-id="pb-a41b93">Dedicated Twitch segment weekly</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-dc73f1">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-c0a647">+</span>
                <span data-pebble-id="pb-a2cb95">Co-branded clip series monthly</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-91bf75">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-ea489e">+</span>
                <span data-pebble-id="pb-3540ee">Priority in sponsor announcements</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#signup"
              className="mt-2 bg-lime-400 text-zinc-900 px-8 py-4 rounded-md font-black uppercase tracking-widest text-sm text-center hover:scale-105 hover:bg-zinc-50 transition-all duration-150" data-pebble-id="pb-41455c">
              GO SIGNAL
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-zinc-700 rounded-md p-8 flex flex-col gap-6 ring-2 ring-lime-400">
            {/* Tier name */}
            <div>
              <span className="text-lime-400 text-xs font-black uppercase tracking-[0.3em]" data-pebble-id="pb-b3f2da">
                VANGUARD
              </span>
              {/* Price */}
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-zinc-50 text-5xl font-black leading-none" data-pebble-id="pb-d14ffa">
                  $4,000
                </span>
                <span className="text-zinc-50/40 text-sm uppercase tracking-wide" data-pebble-id="pb-07b9d7">
                  /month
                </span>
              </div>
            </div>

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-02f636">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-7a90e7">+</span>
                <span data-pebble-id="pb-e388e0">Chest logo — both division jerseys</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-00de7d">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-f28cda">+</span>
                <span data-pebble-id="pb-6a2b43">Named segment on all broadcasts</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-1d8049">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-de9eb9">+</span>
                <span data-pebble-id="pb-e3fe79">Full static glitch branded variant</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-12347c">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-56bbbb">+</span>
                <span data-pebble-id="pb-c3c354">Quarterly campaign collaboration</span>
              </li>
              
              <li className="flex items-start gap-3 text-zinc-50/70 text-sm leading-snug" data-pebble-id="pb-2f2077">
                <span className="mt-0.5 text-lime-400 font-black text-base leading-none" aria-hidden="true" data-pebble-id="pb-af82e0">+</span>
                <span data-pebble-id="pb-736f55">Exclusive fan activation rights</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#signup"
              className="mt-2 bg-lime-400 text-zinc-900 px-8 py-4 rounded-md font-black uppercase tracking-widest text-sm text-center hover:scale-105 hover:bg-zinc-50 transition-all duration-150" data-pebble-id="pb-062365">
              OWN THE STATIC
            </a>
          </StaggerItem>
          

        </Stagger>
      </div>
    </section>
  );
}
