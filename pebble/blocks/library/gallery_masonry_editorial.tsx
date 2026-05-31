"use client";
import RevealWords from "@/components/motion/RevealWords";
import Masonry from "@/components/motion/Masonry";
import FadeUp from "@/components/motion/FadeUp";

export default function GalleryMasonry() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-6xl">
        {/* Section header */}
        <div className="mb-14 max-w-2xl">
          <p className="text-{{accent}} text-sm uppercase tracking-widest mb-3">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-5xl md:text-6xl font-bold leading-tight">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        {/* Masonry gallery */}
        <Masonry>
          {/* {{images_list_start}} */}
          <FadeUp className="overflow-hidden rounded-2xl">
            <img
              src="{{images[].image}}"
              alt="{{images[].caption}}"
              className="w-full rounded-2xl object-cover"
            />
          </FadeUp>
          {/* {{images_list_end}} */}
        </Masonry>
      </div>
    </section>
  );
}
