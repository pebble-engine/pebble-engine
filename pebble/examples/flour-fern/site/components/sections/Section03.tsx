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
          <p className="text-amber-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-fa737e">
            From the oven
          </p>
          <h2 className="text-stone-900 text-5xl md:text-6xl font-bold leading-tight" data-pebble-id="pb-0ba208">
            <RevealWords>A look inside a Flour & Fern morning.</RevealWords>
          </h2>
        </div>

        {/* Masonry gallery */}
        <Masonry>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/30666751/pexels-photo-30666751.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Scoring before the oven"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/30918892/pexels-photo-30918892.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Hand-shaped, every time"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/30767873/pexels-photo-30767873.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="The Saturday rye"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/20002837/pexels-photo-20002837.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Off the rack by 7am"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/30632198/pexels-photo-30632198.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Our 30-year starter"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/30274512/pexels-photo-30274512.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Ready to go"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/30667452/pexels-photo-30667452.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="The corner on Riverside"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/8964253/pexels-photo-8964253.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Rye, fig, and patience"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
        </Masonry>
      </div>
    </section>
  );
}
