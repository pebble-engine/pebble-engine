"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger } from "@/components/motion/Stagger";
import TiltCard from "@/components/motion/TiltCard";

export default function ServicesCardsPlayful() {
  return (
    <section className="bg-purple-100 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="text-center mb-16">
          <p className="inline-flex items-center gap-2 bg-pink-500 text-white text-sm font-bold px-5 py-2 rounded-full mb-5 tracking-wide" data-pebble-id="pb-93bebe">
            What we make together 🖌️
          </p>
          <h2 className="text-purple-900 text-5xl md:text-6xl font-extrabold leading-tight max-w-2xl mx-auto" data-pebble-id="pb-28af86">
            <RevealWords>Classes for every kind of creative kid</RevealWords>
          </h2>
        </div>

        {/* Services grid */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          <TiltCard className="group bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-100">
            {/* Image */}
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/4172988/pexels-photo-4172988.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Paint Explorers"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
              {/* Colorful top-corner badge */}
              <div className="absolute top-3 right-3 bg-amber-300 text-purple-900 text-xs font-extrabold px-3 py-1 rounded-full shadow">
                $28/class
              </div>
            </div>
            {/* Card body */}
            <div className="p-7">
              <h3 className="text-purple-900 text-xl font-extrabold mb-2 leading-snug" data-pebble-id="pb-98e062">
                Paint Explorers
              </h3>
              <p className="text-purple-900/65 text-base leading-relaxed" data-pebble-id="pb-4de92b">
                Acrylics, watercolors, finger paints — kids experiment with color, layering, and their own wild instincts. No stencils. No wrong strokes.
              </p>
            </div>
          </TiltCard>
          
          <TiltCard className="group bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-100">
            {/* Image */}
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/8301833/pexels-photo-8301833.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Clay & Sculpture"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
              {/* Colorful top-corner badge */}
              <div className="absolute top-3 right-3 bg-amber-300 text-purple-900 text-xs font-extrabold px-3 py-1 rounded-full shadow">
                $32/class
              </div>
            </div>
            {/* Card body */}
            <div className="p-7">
              <h3 className="text-purple-900 text-xl font-extrabold mb-2 leading-snug" data-pebble-id="pb-6a5dd2">
                Clay & Sculpture
              </h3>
              <p className="text-purple-900/65 text-base leading-relaxed" data-pebble-id="pb-097b86">
                Hands-on clay building, pinch pots, animals, and abstract shapes. Kiln-fired pieces go home as real keepsakes.
              </p>
            </div>
          </TiltCard>
          
          <TiltCard className="group bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-100">
            {/* Image */}
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/7869798/pexels-photo-7869798.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Collage Studio"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
              {/* Colorful top-corner badge */}
              <div className="absolute top-3 right-3 bg-amber-300 text-purple-900 text-xs font-extrabold px-3 py-1 rounded-full shadow">
                $26/class
              </div>
            </div>
            {/* Card body */}
            <div className="p-7">
              <h3 className="text-purple-900 text-xl font-extrabold mb-2 leading-snug" data-pebble-id="pb-6f1616">
                Collage Studio
              </h3>
              <p className="text-purple-900/65 text-base leading-relaxed" data-pebble-id="pb-325c2b">
                Torn paper, fabric scraps, magazine cutouts, and glitter galore. Big layered works that look like they belong in a gallery.
              </p>
            </div>
          </TiltCard>
          
          <TiltCard className="group bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-100">
            {/* Image */}
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/8014220/pexels-photo-8014220.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Mixed Media Mess"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
              {/* Colorful top-corner badge */}
              <div className="absolute top-3 right-3 bg-amber-300 text-purple-900 text-xs font-extrabold px-3 py-1 rounded-full shadow">
                $30/class
              </div>
            </div>
            {/* Card body */}
            <div className="p-7">
              <h3 className="text-purple-900 text-xl font-extrabold mb-2 leading-snug" data-pebble-id="pb-0e43e0">
                Mixed Media Mess
              </h3>
              <p className="text-purple-900/65 text-base leading-relaxed" data-pebble-id="pb-e0a019">
                Our most popular class: paint + clay + collage + whatever else we can find. Expect glitter in hair and smiles all the way home.
              </p>
            </div>
          </TiltCard>
          
          <TiltCard className="group bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-100">
            {/* Image */}
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/13418660/pexels-photo-13418660.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Weekend Workshops"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
              {/* Colorful top-corner badge */}
              <div className="absolute top-3 right-3 bg-amber-300 text-purple-900 text-xs font-extrabold px-3 py-1 rounded-full shadow">
                $35/session
              </div>
            </div>
            {/* Card body */}
            <div className="p-7">
              <h3 className="text-purple-900 text-xl font-extrabold mb-2 leading-snug" data-pebble-id="pb-69d314">
                Weekend Workshops
              </h3>
              <p className="text-purple-900/65 text-base leading-relaxed" data-pebble-id="pb-1b97ad">
                Saturday and Sunday drop-in sessions themed around seasons, holidays, and pure imagination. Perfect for a fun morning out.
              </p>
            </div>
          </TiltCard>
          
        </Stagger>
      </div>
    </section>
  );
}
