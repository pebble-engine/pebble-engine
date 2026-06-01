"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function PricingLuxe() {
  return (
    <section className="bg-stone-50 py-32 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Section header */}
        <div className="text-center mb-20">
          <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-5 font-light" data-pebble-id="pb-1326f0">
            What's included.
          </p>
          <h2 className="text-stone-700 text-5xl md:text-6xl font-light leading-tight max-w-xl mx-auto tracking-tight" data-pebble-id="pb-b78c91">
            <RevealWords>Every visit, however long, begins the same way.</RevealWords>
          </h2>
        </div>

        {/* Tier cards — clean outlines, no heavy fills */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">

          
          <StaggerItem className="relative flex flex-col gap-8 rounded-2xl border border-stone-200 bg-white/60 p-8 hover:border-amber-600/40 transition-colors duration-300">
            {/* Tier name */}
            <div>
              <span className="text-amber-600 text-xs font-light uppercase tracking-[0.2em]" data-pebble-id="pb-e4e07d">
                The Hour
              </span>
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-stone-700 text-4xl font-light leading-none tracking-tight" data-pebble-id="pb-8cae97">
                  From $120
                </span>
                <span className="text-stone-400 text-sm font-light ml-1" data-pebble-id="pb-b419ed">
                  per visit
                </span>
              </div>
            </div>

            {/* Thin rule */}
            <div className="w-full h-px bg-stone-200" aria-hidden="true" />

            {/* Feature list */}
            <ul className="flex-1 space-y-4">
              
              <li className="flex items-start gap-3 text-stone-500 text-sm font-light leading-relaxed" data-pebble-id="pb-1c6130">
                <span className="mt-0.5 text-amber-600 text-xs leading-none" aria-hidden="true" data-pebble-id="pb-b216f3">—</span>
                <span data-pebble-id="pb-4cddae">Warm foot ritual & cedar-chamomile tea</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-500 text-sm font-light leading-relaxed" data-pebble-id="pb-a6b0e4">
                <span className="mt-0.5 text-amber-600 text-xs leading-none" aria-hidden="true" data-pebble-id="pb-42e71c">—</span>
                <span data-pebble-id="pb-88aba1">60-minute massage or facial</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-500 text-sm font-light leading-relaxed" data-pebble-id="pb-4da272">
                <span className="mt-0.5 text-amber-600 text-xs leading-none" aria-hidden="true" data-pebble-id="pb-596f51">—</span>
                <span data-pebble-id="pb-f77910">Recovery lounge access</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-500 text-sm font-light leading-relaxed" data-pebble-id="pb-144129">
                <span className="mt-0.5 text-amber-600 text-xs leading-none" aria-hidden="true" data-pebble-id="pb-579820">—</span>
                <span data-pebble-id="pb-923a43">Personalised pressure & scent consult</span>
              </li>
              
            </ul>

            {/* CTA — thin border, wide tracking */}
            <a
              href="#book"
              className="mt-auto inline-block text-center border border-stone-700 text-stone-700 px-8 py-3.5 rounded-full text-xs uppercase tracking-[0.2em] font-light hover:border-amber-600 hover:text-amber-600 transition-colors duration-300" data-pebble-id="pb-edf990">
              BOOK NOW
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative flex flex-col gap-8 rounded-2xl border border-stone-200 bg-white/60 p-8 hover:border-amber-600/40 transition-colors duration-300">
            {/* Tier name */}
            <div>
              <span className="text-amber-600 text-xs font-light uppercase tracking-[0.2em]" data-pebble-id="pb-0d4a07">
                The Deep Rest
              </span>
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-stone-700 text-4xl font-light leading-none tracking-tight" data-pebble-id="pb-e0ef1a">
                  From $195
                </span>
                <span className="text-stone-400 text-sm font-light ml-1" data-pebble-id="pb-4d982a">
                  per visit
                </span>
              </div>
            </div>

            {/* Thin rule */}
            <div className="w-full h-px bg-stone-200" aria-hidden="true" />

            {/* Feature list */}
            <ul className="flex-1 space-y-4">
              
              <li className="flex items-start gap-3 text-stone-500 text-sm font-light leading-relaxed" data-pebble-id="pb-cd3c97">
                <span className="mt-0.5 text-amber-600 text-xs leading-none" aria-hidden="true" data-pebble-id="pb-3dfd78">—</span>
                <span data-pebble-id="pb-746b81">Warm foot ritual & cedar-chamomile tea</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-500 text-sm font-light leading-relaxed" data-pebble-id="pb-667560">
                <span className="mt-0.5 text-amber-600 text-xs leading-none" aria-hidden="true" data-pebble-id="pb-d7f08c">—</span>
                <span data-pebble-id="pb-9ae3bc">90-minute massage or body wrap</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-500 text-sm font-light leading-relaxed" data-pebble-id="pb-2f6200">
                <span className="mt-0.5 text-amber-600 text-xs leading-none" aria-hidden="true" data-pebble-id="pb-d65052">—</span>
                <span data-pebble-id="pb-25606d">Scalp massage included</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-500 text-sm font-light leading-relaxed" data-pebble-id="pb-f0d60c">
                <span className="mt-0.5 text-amber-600 text-xs leading-none" aria-hidden="true" data-pebble-id="pb-95674f">—</span>
                <span data-pebble-id="pb-a73c96">Recovery lounge — take your time</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-500 text-sm font-light leading-relaxed" data-pebble-id="pb-2b7a08">
                <span className="mt-0.5 text-amber-600 text-xs leading-none" aria-hidden="true" data-pebble-id="pb-5e7fac">—</span>
                <span data-pebble-id="pb-1b3412">Complimentary botanical mist</span>
              </li>
              
            </ul>

            {/* CTA — thin border, wide tracking */}
            <a
              href="#book"
              className="mt-auto inline-block text-center border border-stone-700 text-stone-700 px-8 py-3.5 rounded-full text-xs uppercase tracking-[0.2em] font-light hover:border-amber-600 hover:text-amber-600 transition-colors duration-300" data-pebble-id="pb-8caae6">
              BOOK NOW
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative flex flex-col gap-8 rounded-2xl border border-stone-200 bg-white/60 p-8 hover:border-amber-600/40 transition-colors duration-300">
            {/* Tier name */}
            <div>
              <span className="text-amber-600 text-xs font-light uppercase tracking-[0.2em]" data-pebble-id="pb-0cf9fa">
                The Couples' Suite
              </span>
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-stone-700 text-4xl font-light leading-none tracking-tight" data-pebble-id="pb-3bdaf7">
                  From $260
                </span>
                <span className="text-stone-400 text-sm font-light ml-1" data-pebble-id="pb-589440">
                  per couple
                </span>
              </div>
            </div>

            {/* Thin rule */}
            <div className="w-full h-px bg-stone-200" aria-hidden="true" />

            {/* Feature list */}
            <ul className="flex-1 space-y-4">
              
              <li className="flex items-start gap-3 text-stone-500 text-sm font-light leading-relaxed" data-pebble-id="pb-3226b7">
                <span className="mt-0.5 text-amber-600 text-xs leading-none" aria-hidden="true" data-pebble-id="pb-d277ce">—</span>
                <span data-pebble-id="pb-732d30">Private suite, two foot rituals</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-500 text-sm font-light leading-relaxed" data-pebble-id="pb-810b24">
                <span className="mt-0.5 text-amber-600 text-xs leading-none" aria-hidden="true" data-pebble-id="pb-e4ade9">—</span>
                <span data-pebble-id="pb-f1a329">Two cups of cedar-chamomile tea</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-500 text-sm font-light leading-relaxed" data-pebble-id="pb-2b8dbe">
                <span className="mt-0.5 text-amber-600 text-xs leading-none" aria-hidden="true" data-pebble-id="pb-fee382">—</span>
                <span data-pebble-id="pb-896f9e">Synchronized 60-minute massages</span>
              </li>
              
              <li className="flex items-start gap-3 text-stone-500 text-sm font-light leading-relaxed" data-pebble-id="pb-c83f4d">
                <span className="mt-0.5 text-amber-600 text-xs leading-none" aria-hidden="true" data-pebble-id="pb-8ea38a">—</span>
                <span data-pebble-id="pb-e1a8b7">Ideal for anniversaries & gifts</span>
              </li>
              
            </ul>

            {/* CTA — thin border, wide tracking */}
            <a
              href="#book"
              className="mt-auto inline-block text-center border border-stone-700 text-stone-700 px-8 py-3.5 rounded-full text-xs uppercase tracking-[0.2em] font-light hover:border-amber-600 hover:text-amber-600 transition-colors duration-300" data-pebble-id="pb-cdd070">
              BOOK NOW
            </a>
          </StaggerItem>
          

        </Stagger>
      </div>
    </section>
  );
}
