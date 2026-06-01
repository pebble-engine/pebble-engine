"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesMenu() {
  return (
    <section className="bg-stone-50 py-32 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Section header — centered, airy */}
        <div className="text-center mb-20">
          <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-5 font-light" data-pebble-id="pb-561bcb">
            What we offer.
          </p>
          <h2 className="text-stone-700 text-5xl md:text-6xl font-light leading-tight max-w-xl mx-auto tracking-tight" data-pebble-id="pb-5f6659">
            <RevealWords>Unhurried cuts, colour, and care for every kind of hair.</RevealWords>
          </h2>
        </div>

        {/* Services — stacked menu rows with image thumbnails */}
        <Stagger className="divide-y divide-stone-200">
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/3992861/pexels-photo-3992861.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="New Client Consultation"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-711755">
                New Client Consultation
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-5a365b">
                Every first visit begins with tea and a slow conversation. No scissors until we both know the plan.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-a296ad">
                Complimentary
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/15659458/pexels-photo-15659458.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Cut & Style"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-a04661">
                Cut & Style
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-53b77e">
                A considered cut shaped for how you live in your hair day to day — finished however you like it.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-bbdde4">
                From $75
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/29555469/pexels-photo-29555469.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Colour & Highlights"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-4ea41d">
                Colour & Highlights
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-33a6b9">
                Lived-in colour, bold statements, or a gentle refresh. Mixed by hand and applied with care.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-4fa68c">
                From $110
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/28994390/pexels-photo-28994390.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Gloss & Treatment"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-6442aa">
                Gloss & Treatment
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-2a8f53">
                Restorative treatments that bring back softness and shine without stripping what makes your hair yours.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-a9bf1b">
                From $55
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/7755521/pexels-photo-7755521.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Blowout & Finish"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-73147e">
                Blowout & Finish
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-50ca47">
                A proper blowout that lasts — smooth, full, or natural. Done with a brush and no rush.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-64d76c">
                From $45
              </span>
            </div>
          </StaggerItem>
          
        </Stagger>
      </div>
    </section>
  );
}
