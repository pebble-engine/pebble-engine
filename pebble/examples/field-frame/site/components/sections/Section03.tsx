"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridEditorial() {
  return (
    <section className="bg-neutral-50 py-28 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Sparse header — left-aligned, no centering */}
        <div className="mb-16 border-b border-neutral-900/10 pb-10">
          <p className="text-neutral-100 text-xs uppercase tracking-widest mb-4 font-sans" data-pebble-id="pb-f50a4d">
            Work
          </p>
          <h2 className="font-serif text-neutral-900 text-4xl md:text-5xl leading-tight max-w-xl" data-pebble-id="pb-618729">
            <RevealWords>Work designed for the long view.</RevealWords>
          </h2>
        </div>

        {/* Services — two-column editorial grid */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 gap-px bg-neutral-900/8">
          
          <StaggerItem className="bg-neutral-50 p-10 group">
            <div className="relative aspect-[4/3] overflow-hidden mb-8">
              <Image
                src="https://images.pexels.com/photos/37627682/pexels-photo-37627682.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="New Construction"
                fill
                priority
                className="object-cover grayscale group-hover:grayscale-0 transition-all duration-700"
              />
            </div>
            <h3 className="font-serif text-neutral-900 text-2xl leading-snug mb-3" data-pebble-id="pb-717570">
              New Construction
            </h3>
            <p className="text-neutral-900/60 text-sm leading-relaxed mb-5 font-sans" data-pebble-id="pb-43133e">
              Modern single-family homes designed from the site outward — sited for light, built for longevity. We work through all phases, from schematic to construction administration.
            </p>
            <span className="text-neutral-900/40 text-xs tracking-widest uppercase font-sans" data-pebble-id="pb-97c840">
              
            </span>
          </StaggerItem>
          
          <StaggerItem className="bg-neutral-50 p-10 group">
            <div className="relative aspect-[4/3] overflow-hidden mb-8">
              <Image
                src="https://images.pexels.com/photos/8146336/pexels-photo-8146336.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Thoughtful Renovation"
                fill
                priority
                className="object-cover grayscale group-hover:grayscale-0 transition-all duration-700"
              />
            </div>
            <h3 className="font-serif text-neutral-900 text-2xl leading-snug mb-3" data-pebble-id="pb-4dc88e">
              Thoughtful Renovation
            </h3>
            <p className="text-neutral-900/60 text-sm leading-relaxed mb-5 font-sans" data-pebble-id="pb-13e1dc">
              Additions and renovations that respect what's already there. We find the logic of the existing house and extend it — more light, better flow, nothing gratuitous.
            </p>
            <span className="text-neutral-900/40 text-xs tracking-widest uppercase font-sans" data-pebble-id="pb-aa4cea">
              
            </span>
          </StaggerItem>
          
          <StaggerItem className="bg-neutral-50 p-10 group">
            <div className="relative aspect-[4/3] overflow-hidden mb-8">
              <Image
                src="https://images.pexels.com/photos/36930873/pexels-photo-36930873.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Site Analysis"
                fill
                priority
                className="object-cover grayscale group-hover:grayscale-0 transition-all duration-700"
              />
            </div>
            <h3 className="font-serif text-neutral-900 text-2xl leading-snug mb-3" data-pebble-id="pb-2b1aa9">
              Site Analysis
            </h3>
            <p className="text-neutral-900/60 text-sm leading-relaxed mb-5 font-sans" data-pebble-id="pb-5c92d6">
              Every engagement begins with the land. We document solar angles, seasonal shadow patterns, views, and prevailing winds before a floor plan exists.
            </p>
            <span className="text-neutral-900/40 text-xs tracking-widest uppercase font-sans" data-pebble-id="pb-65dfbd">
              
            </span>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
