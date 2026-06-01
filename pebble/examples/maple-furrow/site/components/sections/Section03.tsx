"use client";

import RevealWords from "@/components/motion/RevealWords";
import Masonry from "@/components/motion/Masonry";
import FadeUp from "@/components/motion/FadeUp";

export default function GalleryMasonry() {
  return (
    <section className="bg-stone-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">
        {/* Section header */}
        <div className="mb-14 max-w-2xl">
          <p className="text-amber-800 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-2e8826">
            From the kitchen & the fields
          </p>
          <h2 className="text-stone-900 text-5xl md:text-6xl font-bold leading-tight" data-pebble-id="pb-0fbc33">
            <RevealWords>A record of the seasons we've cooked through.</RevealWords>
          </h2>
        </div>

        {/* Masonry gallery */}
        <Masonry>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/19986452/pexels-photo-19986452.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Friday night, full house"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/5425794/pexels-photo-5425794.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Holler Creek Farm delivery"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/6287313/pexels-photo-6287313.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Wednesday pasta prep"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/12771066/pexels-photo-12771066.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Beets & chèvre, late summer"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/37164095/pexels-photo-37164095.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="The wood fire, every night"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/2889314/pexels-photo-2889314.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Barton Orchards, August"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/1850600/pexels-photo-1850600.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="The dining room at dusk"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/15671409/pexels-photo-15671409.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Hands on every plate"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
        </Masonry>
      </div>
    </section>
  );
}
