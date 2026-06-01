"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function PricingSimple() {
  return (
    <section className="bg-stone-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="text-center mb-16">
          <p className="text-amber-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-3ead13">
            Options
          </p>
          <h2 className="text-stone-900 text-5xl md:text-6xl font-bold leading-tight max-w-2xl mx-auto" data-pebble-id="pb-7a6208">
            <RevealWords>Fresh coffee your way — one bag or a standing order.</RevealWords>
          </h2>
        </div>

        {/* Tier cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">

          
          <StaggerItem className="relative bg-stone-100/40 rounded-3xl p-8 flex flex-col gap-6 ring-2 ring-amber-700">
            {/* Tier name */}
            <div>
              <span className="text-amber-700 text-xs font-semibold uppercase tracking-widest" data-pebble-id="pb-2f432e">
                Single Bag
              </span>
              {/* Price */}
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-stone-900 text-5xl font-bold leading-none" data-pebble-id="pb-934d6f">
                  From $18
                </span>
                <span className="text-stone-900/50 text-base" data-pebble-id="pb-d0be19">
                  per bag
                </span>
              </div>
            </div>

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-stone-900/75 text-base leading-snug" data-pebble-id="pb-275e83">
                <span className="mt-1 text-amber-700 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-36ff24">✓</span>
                <span data-pebble-id="pb-45b766">250g or 500g whole bean bags</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 text-base leading-snug" data-pebble-id="pb-6f04b8">
                <span className="mt-1 text-amber-700 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-ecd249">✓</span>
                <span data-pebble-id="pb-e80b39">Handwritten roast date on every bag</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 text-base leading-snug" data-pebble-id="pb-30864a">
                <span className="mt-1 text-amber-700 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-6952fd">✓</span>
                <span data-pebble-id="pb-62ac46">Farm notes included</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 text-base leading-snug" data-pebble-id="pb-59803d">
                <span className="mt-1 text-amber-700 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-897a5a">✓</span>
                <span data-pebble-id="pb-58d49b">Ships within 48 hrs of roasting</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#order"
              className="mt-2 bg-amber-700 text-stone-50 px-8 py-4 rounded-full font-semibold text-center hover:opacity-90 transition" data-pebble-id="pb-aedd79">
              Shop now
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-stone-100/40 rounded-3xl p-8 flex flex-col gap-6 ring-2 ring-amber-700">
            {/* Tier name */}
            <div>
              <span className="text-amber-700 text-xs font-semibold uppercase tracking-widest" data-pebble-id="pb-8d71f0">
                Subscription
              </span>
              {/* Price */}
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-stone-900 text-5xl font-bold leading-none" data-pebble-id="pb-7e2f2f">
                  From $17
                </span>
                <span className="text-stone-900/50 text-base" data-pebble-id="pb-210906">
                  per bag
                </span>
              </div>
            </div>

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-stone-900/75 text-base leading-snug" data-pebble-id="pb-e4f23d">
                <span className="mt-1 text-amber-700 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-6ee953">✓</span>
                <span data-pebble-id="pb-bf6649">Delivery every 2 or 4 weeks</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 text-base leading-snug" data-pebble-id="pb-bf15c2">
                <span className="mt-1 text-amber-700 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-f0a425">✓</span>
                <span data-pebble-id="pb-ec27cc">We rotate the origin each cycle</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 text-base leading-snug" data-pebble-id="pb-ce180f">
                <span className="mt-1 text-amber-700 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-e352af">✓</span>
                <span data-pebble-id="pb-c91bb6">Handwritten roast date & farm note</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 text-base leading-snug" data-pebble-id="pb-32eec5">
                <span className="mt-1 text-amber-700 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-b89cf8">✓</span>
                <span data-pebble-id="pb-5bd473">Free shipping on every order</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 text-base leading-snug" data-pebble-id="pb-b5425f">
                <span className="mt-1 text-amber-700 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-804790">✓</span>
                <span data-pebble-id="pb-f31374">Pause or cancel any time</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#order"
              className="mt-2 bg-amber-700 text-stone-50 px-8 py-4 rounded-full font-semibold text-center hover:opacity-90 transition" data-pebble-id="pb-a42c44">
              Start a subscription
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-stone-100/40 rounded-3xl p-8 flex flex-col gap-6 ring-2 ring-amber-700">
            {/* Tier name */}
            <div>
              <span className="text-amber-700 text-xs font-semibold uppercase tracking-widest" data-pebble-id="pb-90da94">
                Café Visit
              </span>
              {/* Price */}
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-stone-900 text-5xl font-bold leading-none" data-pebble-id="pb-9c68de">
                  From $4.50
                </span>
                <span className="text-stone-900/50 text-base" data-pebble-id="pb-f90e21">
                  per drink
                </span>
              </div>
            </div>

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-stone-900/75 text-base leading-snug" data-pebble-id="pb-84f3bb">
                <span className="mt-1 text-amber-700 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-be63a5">✓</span>
                <span data-pebble-id="pb-dda01d">Pour-overs, lattes, cortados</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 text-base leading-snug" data-pebble-id="pb-832e10">
                <span className="mt-1 text-amber-700 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-562137">✓</span>
                <span data-pebble-id="pb-115c4d">Beans pulled fresh from in-house roasts</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 text-base leading-snug" data-pebble-id="pb-9fa128">
                <span className="mt-1 text-amber-700 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-d1f3cc">✓</span>
                <span data-pebble-id="pb-158c2b">Take a bag home on your way out</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-900/75 text-base leading-snug" data-pebble-id="pb-ade047">
                <span className="mt-1 text-amber-700 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-2db929">✓</span>
                <span data-pebble-id="pb-17b975">Regulars always welcome</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#order"
              className="mt-2 bg-amber-700 text-stone-50 px-8 py-4 rounded-full font-semibold text-center hover:opacity-90 transition" data-pebble-id="pb-253482">
              Find us
            </a>
          </StaggerItem>
          

        </Stagger>
      </div>
    </section>
  );
}
