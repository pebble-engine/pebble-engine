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
          <p className="text-amber-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-b255c8">
            Recent work
          </p>
          <h2 className="text-stone-900 text-5xl md:text-6xl font-bold leading-tight" data-pebble-id="pb-733cd4">
            <RevealWords>Hair we've loved working on lately.</RevealWords>
          </h2>
        </div>

        {/* Masonry gallery */}
        <Masonry>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/7752412/pexels-photo-7752412.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Warm balayage, east side light"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/15659494/pexels-photo-15659494.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="A strong, clean cut"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/7755215/pexels-photo-7755215.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Embracing the curl"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/1049687/pexels-photo-1049687.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Soft highlights, long layers"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/8834079/pexels-photo-8834079.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Letting it go silver"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/13138585/pexels-photo-13138585.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="The perfect bob"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/28994390/pexels-photo-28994390.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Post-gloss shine"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/22696517/pexels-photo-22696517.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="The house on Marigold Lane"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
        </Masonry>
      </div>
    </section>
  );
}
