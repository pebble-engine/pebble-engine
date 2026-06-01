"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGrid() {
  return (
    <section className="bg-stone-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">
        {/* Section header */}
        <div className="text-center mb-16">
          <p className="text-amber-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-f7ad2a">
            What we're pouring
          </p>
          <h2 className="text-stone-900 text-5xl md:text-6xl font-bold leading-tight max-w-2xl mx-auto" data-pebble-id="pb-aba965">
            <RevealWords>Single-origin coffee, roasted to order and ready to ship.</RevealWords>
          </h2>
        </div>

        {/* Services grid */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          <StaggerItem className="group bg-stone-50 rounded-3xl overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300">
            <div className="relative aspect-[4/3] overflow-hidden rounded-t-3xl">
              <Image
                src="https://images.pexels.com/photos/9329115/pexels-photo-9329115.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Whole Bean Bags"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            <div className="p-7">
              <h3 className="text-stone-900 text-xl font-semibold mb-2 leading-snug" data-pebble-id="pb-699443">
                Whole Bean Bags
              </h3>
              <p className="text-stone-900/70 text-base leading-relaxed mb-4" data-pebble-id="pb-4565bc">
                250g and 500g bags of freshly roasted single-origin coffee. Each bag is hand-dated and comes with a farm note. We ship nationwide, usually within 48 hours of roasting.
              </p>
              <span className="text-amber-700 text-sm font-semibold tracking-wide" data-pebble-id="pb-d73f10">
                From $18
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group bg-stone-50 rounded-3xl overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300">
            <div className="relative aspect-[4/3] overflow-hidden rounded-t-3xl">
              <Image
                src="https://images.pexels.com/photos/31777077/pexels-photo-31777077.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Espresso Blends"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            <div className="p-7">
              <h3 className="text-stone-900 text-xl font-semibold mb-2 leading-snug" data-pebble-id="pb-8dc19b">
                Espresso Blends
              </h3>
              <p className="text-stone-900/70 text-base leading-relaxed mb-4" data-pebble-id="pb-e19508">
                Our house espresso blend is built for balance — sweet caramel up front, a clean finish. Roasted twice a week and designed to pull well on home machines and commercial gear alike.
              </p>
              <span className="text-amber-700 text-sm font-semibold tracking-wide" data-pebble-id="pb-04e27d">
                From $19
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group bg-stone-50 rounded-3xl overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300">
            <div className="relative aspect-[4/3] overflow-hidden rounded-t-3xl">
              <Image
                src="https://images.pexels.com/photos/2036776/pexels-photo-2036776.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Café Drinks"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            <div className="p-7">
              <h3 className="text-stone-900 text-xl font-semibold mb-2 leading-snug" data-pebble-id="pb-44c364">
                Café Drinks
              </h3>
              <p className="text-stone-900/70 text-base leading-relaxed mb-4" data-pebble-id="pb-7ef569">
                Come in and we'll brew you a cup. Pour-overs, lattes, cortados — whatever fits the morning. We use the same beans we sell, nothing held back for the bar.
              </p>
              <span className="text-amber-700 text-sm font-semibold tracking-wide" data-pebble-id="pb-b759a6">
                From $4.50
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group bg-stone-50 rounded-3xl overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300">
            <div className="relative aspect-[4/3] overflow-hidden rounded-t-3xl">
              <Image
                src="https://images.pexels.com/photos/7310206/pexels-photo-7310206.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Coffee Subscriptions"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            <div className="p-7">
              <h3 className="text-stone-900 text-xl font-semibold mb-2 leading-snug" data-pebble-id="pb-758ed7">
                Coffee Subscriptions
              </h3>
              <p className="text-stone-900/70 text-base leading-relaxed mb-4" data-pebble-id="pb-750305">
                Get a fresh bag every 2 or 4 weeks. Choose your roast level, we'll rotate the origin to keep things interesting. Pause or cancel any time — no awkward emails needed.
              </p>
              <span className="text-amber-700 text-sm font-semibold tracking-wide" data-pebble-id="pb-b52661">
                From $17/bag
              </span>
            </div>
          </StaggerItem>
          
        </Stagger>
      </div>
    </section>
  );
}
