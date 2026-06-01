"use client";

import RevealWords from "@/components/motion/RevealWords";
import Masonry from "@/components/motion/Masonry";
import FadeUp from "@/components/motion/FadeUp";

export default function GalleryMasonry() {
  return (
    <section className="bg-neutral-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">
        {/* Section header */}
        <div className="mb-14 max-w-2xl">
          <p className="text-neutral-900 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-e9963a">
            Selected work
          </p>
          <h2 className="text-neutral-900 text-5xl md:text-6xl font-bold leading-tight" data-pebble-id="pb-48aa20">
            <RevealWords>photographs from barns, vineyards, and backyards.</RevealWords>
          </h2>
        </div>

        {/* Masonry gallery */}
        <Masonry>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/29205725/pexels-photo-29205725.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Willamette Valley, October"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/33458157/pexels-photo-33458157.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Farmhouse, Sebastopol"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/35870527/pexels-photo-35870527.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Old barn, Dundee Hills"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/36305352/pexels-photo-36305352.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Backyard, Portland"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/7358821/pexels-photo-7358821.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="35mm, hand-developed"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/18263210/pexels-photo-18263210.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Napa Valley, June"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/12409635/pexels-photo-12409635.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Sonoma County, September"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/9951107/pexels-photo-9951107.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Medium format, Oregon"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
        </Masonry>
      </div>
    </section>
  );
}
