"use client";

import RevealWords from "@/components/motion/RevealWords";
import Masonry from "@/components/motion/Masonry";
import FadeUp from "@/components/motion/FadeUp";

export default function GalleryMasonry() {
  return (
    <section className="bg-yellow-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">
        {/* Section header */}
        <div className="mb-14 max-w-2xl">
          <p className="text-pink-500 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-98b386">
            The Wall of Fame
          </p>
          <h2 className="text-stone-900 text-5xl md:text-6xl font-bold leading-tight" data-pebble-id="pb-794fac">
            <RevealWords>Every piece. Every kid. Every time.</RevealWords>
          </h2>
        </div>

        {/* Masonry gallery */}
        <Masonry>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/6658167/pexels-photo-6658167.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Lily, age 6 — Watercolor Galaxy"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/4547467/pexels-photo-4547467.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Marcus, age 9 — Clay Dragon"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/36591281/pexels-photo-36591281.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Sofia, age 7 — City Collage"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/1174932/pexels-photo-1174932.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Theo, age 4 — First Painting"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/7450561/pexels-photo-7450561.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Aisha, age 11 — Mixed Media Garden"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/37195334/pexels-photo-37195334.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Ben, age 8 — Jungle Storm"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/5789769/pexels-photo-5789769.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Saturday crew — Group Mural"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/32532497/pexels-photo-32532497.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Nadia, age 10 — Self Portrait"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
        </Masonry>
      </div>
    </section>
  );
}
