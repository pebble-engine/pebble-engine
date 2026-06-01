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
          <p className="text-neutral-900 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-911e94">
            Selected work
          </p>
          <h2 className="text-neutral-900 text-5xl md:text-6xl font-bold leading-tight" data-pebble-id="pb-f3a6b5">
            <RevealWords>Finished homes. Every line placed on purpose.</RevealWords>
          </h2>
        </div>

        {/* Masonry gallery */}
        <Masonry>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/29248853/pexels-photo-29248853.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Catskill Ridge House, 2023"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/11408618/pexels-photo-11408618.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="River Bend Residence, 2022"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/36777558/pexels-photo-36777558.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Millbrook Farmhouse, 2023"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/33217595/pexels-photo-33217595.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Stone Road House, 2021"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/10069252/pexels-photo-10069252.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Tivoli Cabin, 2022"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/36241382/pexels-photo-36241382.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Accord House, 2023"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/8134806/pexels-photo-8134806.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Millbrook Farmhouse, 2023"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="https://images.pexels.com/photos/18399926/pexels-photo-18399926.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Catskill Ridge House, 2023"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          
        </Masonry>
      </div>
    </section>
  );
}
