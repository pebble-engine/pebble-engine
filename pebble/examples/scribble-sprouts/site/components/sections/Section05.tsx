"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function PricingTiersPlayful() {
  return (
    <section className="bg-pink-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="text-center mb-16">
          <p className="inline-flex items-center gap-2 bg-pink-500 text-white text-sm font-bold px-5 py-2 rounded-full mb-5 tracking-wide" data-pebble-id="pb-11f5e7">
            Pick your plan
          </p>
          <h2 className="text-purple-900 text-5xl md:text-6xl font-extrabold leading-tight max-w-2xl mx-auto" data-pebble-id="pb-c912b1">
            <RevealWords>Flexible options so every kid can join in</RevealWords>
          </h2>
        </div>

        {/* Tier cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">

          
          <StaggerItem className="relative bg-white rounded-[2rem] p-8 flex flex-col gap-6 shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-200">
            {/* Name + price */}
            <div>
              <span className="text-pink-500 text-xs font-extrabold uppercase tracking-widest" data-pebble-id="pb-29c5a5">
                Drop-In
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-purple-900 text-5xl font-extrabold leading-none" data-pebble-id="pb-53c479">
                  From $26
                </span>
                <span className="text-purple-900/50 text-base" data-pebble-id="pb-ad2a52">
                  per class
                </span>
              </div>
            </div>

            {/* Features */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-466029">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-af740a">&#10003;</span>
                <span data-pebble-id="pb-70c1f3">Any single class or weekend workshop</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-ff1414">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-475bd8">&#10003;</span>
                <span data-pebble-id="pb-af626a">All materials included</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-4f4b7e">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-033420">&#10003;</span>
                <span data-pebble-id="pb-757931">Your artwork goes on the Wall of Fame</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-b0eb95">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-f6977f">&#10003;</span>
                <span data-pebble-id="pb-7b971c">No commitment needed</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#book"
              className="mt-2 bg-pink-500 text-white px-10 py-5 rounded-full font-extrabold text-center shadow hover:scale-105 hover:rotate-1 hover:shadow-pink-300 transition-all duration-200" data-pebble-id="pb-911c2c">
              Book a class
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-white rounded-[2rem] p-8 flex flex-col gap-6 shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-200">
            {/* Name + price */}
            <div>
              <span className="text-pink-500 text-xs font-extrabold uppercase tracking-widest" data-pebble-id="pb-bc8f86">
                Monthly Bundle
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-purple-900 text-5xl font-extrabold leading-none" data-pebble-id="pb-5e7a36">
                  $99
                </span>
                <span className="text-purple-900/50 text-base" data-pebble-id="pb-172972">
                  per month
                </span>
              </div>
            </div>

            {/* Features */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-e555e7">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-6ea21f">&#10003;</span>
                <span data-pebble-id="pb-5605f3">4 classes per month (any mix)</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-e553e6">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-93360d">&#10003;</span>
                <span data-pebble-id="pb-806527">All materials included</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-dab776">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-702818">&#10003;</span>
                <span data-pebble-id="pb-9eab13">Reserved spot in your chosen sessions</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-5314d3">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-5829d0">&#10003;</span>
                <span data-pebble-id="pb-21a6c5">Wall of Fame for every piece</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-16b868">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-f8a88b">&#10003;</span>
                <span data-pebble-id="pb-63a17d">10% off weekend workshops</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#book"
              className="mt-2 bg-pink-500 text-white px-10 py-5 rounded-full font-extrabold text-center shadow hover:scale-105 hover:rotate-1 hover:shadow-pink-300 transition-all duration-200" data-pebble-id="pb-19ff25">
              Join monthly
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-white rounded-[2rem] p-8 flex flex-col gap-6 shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-200">
            {/* Name + price */}
            <div>
              <span className="text-pink-500 text-xs font-extrabold uppercase tracking-widest" data-pebble-id="pb-8e888d">
                Birthday Party
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-purple-900 text-5xl font-extrabold leading-none" data-pebble-id="pb-3c7864">
                  $220
                </span>
                <span className="text-purple-900/50 text-base" data-pebble-id="pb-fcd542">
                  per party
                </span>
              </div>
            </div>

            {/* Features */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-d0d79d">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-da11ef">&#10003;</span>
                <span data-pebble-id="pb-0d202a">2-hour private studio session</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-9a58ac">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-761ac6">&#10003;</span>
                <span data-pebble-id="pb-7cea79">Up to 12 kids</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-7e341b">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-d06111">&#10003;</span>
                <span data-pebble-id="pb-eb2a95">Guided project + free paint time</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-453852">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-d24860">&#10003;</span>
                <span data-pebble-id="pb-ff7f7d">Every kid takes their art home</span>
              </li>
              
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug" data-pebble-id="pb-7c30ec">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true" data-pebble-id="pb-9facc8">&#10003;</span>
                <span data-pebble-id="pb-a9a0f0">We handle all the mess!</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#book"
              className="mt-2 bg-pink-500 text-white px-10 py-5 rounded-full font-extrabold text-center shadow hover:scale-105 hover:rotate-1 hover:shadow-pink-300 transition-all duration-200" data-pebble-id="pb-abdb6d">
              Book a party
            </a>
          </StaggerItem>
          

        </Stagger>
      </div>
    </section>
  );
}
