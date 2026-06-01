"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import FadeUp from "@/components/motion/FadeUp";
import Parallax from "@/components/motion/Parallax";

export default function AboutStatementEditorial() {
  return (
    <section className="bg-neutral-50 py-28 px-8">
      <div className="container mx-auto max-w-5xl">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-16 items-start">

          {/* Portrait — spans 5 of 12 cols, no decorative flourishes */}
          <div className="md:col-span-5">
            <div className="relative aspect-[2/3] overflow-hidden">
              <Parallax className="absolute inset-0" distance={30}>
                <Image
                  src="https://images.pexels.com/photos/20362296/pexels-photo-20362296.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="film photography from a small practice in Oregon."
                  fill
                  priority
                  className="object-cover grayscale"
                />
              </Parallax>
            </div>
          </div>

          {/* Statement — spans 7 of 12 cols */}
          <FadeUp className="md:col-span-7 md:pt-12">
            <p className="text-neutral-200 text-xs uppercase tracking-widest mb-6 font-sans" data-pebble-id="pb-d43dc8">
              About
            </p>
            <h2 className="font-serif text-neutral-900 text-4xl md:text-5xl leading-tight mb-10 max-w-lg" data-pebble-id="pb-5f23e5">
              <RevealWords>film photography from a small practice in Oregon.</RevealWords>
            </h2>

            
            <p className="text-neutral-900/65 text-base leading-relaxed mb-6 font-sans" data-pebble-id="pb-07e69e">
              I'm Nora. I shoot every wedding on 35mm and medium-format film — no digital backup, no presets. The grain, the tones, the slight softness at the edges: those are real, not applied after the fact.
            </p>
            
            <p className="text-neutral-900/65 text-base leading-relaxed mb-6 font-sans" data-pebble-id="pb-7eea05">
              Most of my couples are getting married somewhere quiet — a vineyard, an old barn, a backyard they've known for years. They want photos that feel like the day actually felt, not a performance of it.
            </p>
            
            <p className="text-neutral-900/65 text-base leading-relaxed mb-6 font-sans" data-pebble-id="pb-bb1df3">
              I hand-develop all the black-and-white film myself. It takes longer. The results belong entirely to the moment. I work mostly in Oregon and Northern California, and I book a limited number of weddings each year.
            </p>
            

            {/* Signature — ruled above, no decoration */}
            <div className="mt-12 pt-8 border-t border-neutral-900/10">
              <p className="text-neutral-900/50 text-sm font-sans tracking-wide italic" data-pebble-id="pb-e3d6c9">
                — Nora, Founder & Film Photographer
              </p>
            </div>
          </FadeUp>

        </div>
      </div>
    </section>
  );
}
