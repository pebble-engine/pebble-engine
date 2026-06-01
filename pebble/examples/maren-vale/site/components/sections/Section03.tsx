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
          <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-5 font-light" data-pebble-id="pb-5874a2">
            What we offer.
          </p>
          <h2 className="text-stone-700 text-5xl md:text-6xl font-light leading-tight max-w-xl mx-auto tracking-tight" data-pebble-id="pb-b170d1">
            <RevealWords>Each piece made to order, with time and attention it deserves.</RevealWords>
          </h2>
        </div>

        {/* Services — stacked menu rows with image thumbnails */}
        <Stagger className="divide-y divide-stone-200">
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/8281508/pexels-photo-8281508.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Engagement Rings"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-55250c">
                Engagement Rings
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-5fe701">
                Designed around your story. Every ring begins with a hand sketch and is built from metal at the bench — no casting catalogues, no stock settings.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-05ad28">
                From $2,800
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/17368721/pexels-photo-17368721.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Heirloom Necklaces"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-79f638">
                Heirloom Necklaces
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-b9554f">
                Pendants and chains made to be passed down. We work with your inherited stones, your metal preferences, your sense of what should endure.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-7a5fca">
                From $1,200
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/4802274/pexels-photo-4802274.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Anniversary Bands"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-3af187">
                Anniversary Bands
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-2981a9">
                Quiet, considered bands for marking time together. Etched, textured, set or plain — always made by hand, always singular.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-0a5cb4">
                From $900
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/34330821/pexels-photo-34330821.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Memorial Pieces"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-89cd78">
                Memorial Pieces
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-47d8f1">
                Jewelry made to hold something — a lock of hair, a stone from a beloved ring, an impression. Handled with discretion and real care.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-949f36">
                From $850
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/7167020/pexels-photo-7167020.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="One-of-a-Kind Commissions"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-2bed3d">
                One-of-a-Kind Commissions
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-9ae88f">
                Something entirely your own. Bring a feeling, a reference, a photograph — I'll translate it into metal. No two are ever the same.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-f7db2f">
                From $1,500
              </span>
            </div>
          </StaggerItem>
          
        </Stagger>
      </div>
    </section>
  );
}
