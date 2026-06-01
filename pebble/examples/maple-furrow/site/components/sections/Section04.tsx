"use client";

import Image from "next/image";
import FadeUp from "@/components/motion/FadeUp";

export default function TestimonialsReview() {
  return (
    <section className="bg-stone-50 py-28 px-8">
      <div className="container mx-auto max-w-4xl">

        {/* Warm decorative rule */}
        <div className="flex items-center gap-4 mb-14 justify-center">
          <span className="h-px w-16 bg-amber-800/30" aria-hidden="true" data-pebble-id="pb-e5bed5"/>
          <span className="text-amber-800/50 text-xs uppercase tracking-[0.25em] font-sans" data-pebble-id="pb-76ea07">
            What people say
          </span>
          <span className="h-px w-16 bg-amber-800/30" aria-hidden="true" data-pebble-id="pb-2a07b7"/>
        </div>

        {/* Oversized opening quote glyph */}
        <div
          aria-hidden="true"
          className="text-amber-800/15 font-serif text-9xl leading-none select-none text-center -mb-6"
        >
          &ldquo;
        </div>

        {/* Pull-quote */}
        <FadeUp>
        <blockquote className="text-center" data-pebble-id="pb-c2649a">
          <p className="text-stone-900 font-serif text-2xl md:text-4xl leading-snug tracking-tight max-w-3xl mx-auto italic" data-pebble-id="pb-082073">
            We had the duck confit from Herondale and I still think about it a month later. The room felt like eating inside someone's home — candlelight, no rush, a server who could tell you exactly where every ingredient came from. We'll be back every season.
          </p>

          {/* Attribution */}
          <footer className="mt-12 flex flex-col items-center gap-4">
            <div className="relative w-14 h-14 rounded-full overflow-hidden ring-2 ring-amber-800/25">
              <Image
                src="https://images.pexels.com/photos/3938951/pexels-photo-3938951.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Margot H."
                fill
                priority
                className="object-cover"
              />
            </div>
            <div>
              <cite className="text-stone-900 font-sans text-sm font-semibold not-italic block">
                Margot H.
              </cite>
              <span className="text-stone-900/50 font-sans text-xs tracking-wide mt-1 block" data-pebble-id="pb-82c403">
                Table of two, been coming since last fall
              </span>
            </div>
          </footer>
        </blockquote>
        </FadeUp>

      </div>
    </section>
  );
}
