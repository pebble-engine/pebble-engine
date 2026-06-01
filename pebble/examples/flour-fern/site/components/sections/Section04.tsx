"use client";

import Image from "next/image";
import FadeUp from "@/components/motion/FadeUp";

export default function TestimonialsReview() {
  return (
    <section className="bg-stone-50 py-28 px-8">
      <div className="container mx-auto max-w-4xl">

        {/* Warm decorative rule */}
        <div className="flex items-center gap-4 mb-14 justify-center">
          <span className="h-px w-16 bg-amber-700/30" aria-hidden="true" data-pebble-id="pb-ecc7f9"/>
          <span className="text-amber-700/50 text-xs uppercase tracking-[0.25em] font-sans" data-pebble-id="pb-7001d2">
            What people say
          </span>
          <span className="h-px w-16 bg-amber-700/30" aria-hidden="true" data-pebble-id="pb-179174"/>
        </div>

        {/* Oversized opening quote glyph */}
        <div
          aria-hidden="true"
          className="text-amber-700/15 font-serif text-9xl leading-none select-none text-center -mb-6"
        >
          &ldquo;
        </div>

        {/* Pull-quote */}
        <FadeUp>
        <blockquote className="text-center" data-pebble-id="pb-4e7c69">
          <p className="text-stone-900 font-serif text-2xl md:text-4xl leading-snug tracking-tight max-w-3xl mx-auto italic" data-pebble-id="pb-4a498c">
            I set an alarm on Saturdays specifically for the rye-and-fig loaf. I've missed it twice and both times were genuinely bad mornings. It's the kind of bread that makes you slow down and eat at the table.
          </p>

          {/* Attribution */}
          <footer className="mt-12 flex flex-col items-center gap-4">
            <div className="relative w-14 h-14 rounded-full overflow-hidden ring-2 ring-amber-700/25">
              <Image
                src="https://images.pexels.com/photos/10881441/pexels-photo-10881441.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Marta L."
                fill
                priority
                className="object-cover"
              />
            </div>
            <div>
              <cite className="text-stone-900 font-sans text-sm font-semibold not-italic block">
                Marta L.
              </cite>
              <span className="text-stone-900/50 font-sans text-xs tracking-wide mt-1 block" data-pebble-id="pb-721b51">
                Regular every weekend since last spring
              </span>
            </div>
          </footer>
        </blockquote>
        </FadeUp>

      </div>
    </section>
  );
}
