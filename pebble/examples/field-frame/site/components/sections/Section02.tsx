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
                  src="https://images.pexels.com/photos/9522818/pexels-photo-9522818.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="Light-first architecture from a small studio in the Hudson Valley."
                  fill
                  priority
                  className="object-cover grayscale"
                />
              </Parallax>
            </div>
          </div>

          {/* Statement — spans 7 of 12 cols */}
          <FadeUp className="md:col-span-7 md:pt-12">
            <p className="text-neutral-100 text-xs uppercase tracking-widest mb-6 font-sans" data-pebble-id="pb-66d8cc">
              Studio
            </p>
            <h2 className="font-serif text-neutral-900 text-4xl md:text-5xl leading-tight mb-10 max-w-lg" data-pebble-id="pb-4836e2">
              <RevealWords>Light-first architecture from a small studio in the Hudson Valley.</RevealWords>
            </h2>

            
            <p className="text-neutral-900/65 text-base leading-relaxed mb-6 font-sans" data-pebble-id="pb-07a59e">
              Field & Frame is Nora and two other architects. We design modern single-family homes and occasional renovations — mostly for people who want something quiet and considered, not a statement.
            </p>
            
            <p className="text-neutral-900/65 text-base leading-relaxed mb-6 font-sans" data-pebble-id="pb-549b84">
              Before we draw a single wall, we walk the site at sunrise and at sunset. We track where the light falls in January and where it pools in July. The house gets oriented around that. Not the other way around.
            </p>
            
            <p className="text-neutral-900/65 text-base leading-relaxed mb-6 font-sans" data-pebble-id="pb-d4abbf">
              We keep the studio small because the work requires it. Each project gets our full attention from the first site visit to the last punch list item. That's the only way we know how to do it.
            </p>
            

            {/* Signature — ruled above, no decoration */}
            <div className="mt-12 pt-8 border-t border-neutral-900/10">
              <p className="text-neutral-900/50 text-sm font-sans tracking-wide italic" data-pebble-id="pb-661fa9">
                — Nora Ellsworth, Principal Architect
              </p>
            </div>
          </FadeUp>

        </div>
      </div>
    </section>
  );
}
