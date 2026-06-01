"use client";

import Image from "next/image";
import FadeUp from "@/components/motion/FadeUp";

export default function TestimonialsQuote() {
  return (
    <section className="bg-stone-50 py-28 px-8">
      <div className="container mx-auto max-w-4xl text-center">

        {/* Opening quote mark — oversized decorative glyph */}
        <div
          aria-hidden="true"
          className="text-green-700/20 text-9xl font-serif leading-none select-none -mb-8"
        >
          &ldquo;
        </div>

        {/* The pull-quote itself */}
        <FadeUp>
        <blockquote className="relative" data-pebble-id="pb-d6a5b2">
          <p className="text-stone-900 text-3xl md:text-5xl font-semibold leading-tight tracking-tight max-w-3xl mx-auto" data-pebble-id="pb-3edb17">
            They transformed our overgrown backyard into something we actually use. The patio design was thoughtful, the installation was clean, and they explained every decision along the way. We get compliments from neighbors every week.
          </p>

          {/* Attribution block */}
          <footer className="mt-12 flex flex-col items-center gap-4">
            {/* Headshot circle */}
            <div className="relative w-16 h-16 rounded-full overflow-hidden ring-2 ring-green-700/30">
              <Image
                src="https://images.pexels.com/photos/7579146/pexels-photo-7579146.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Meredith & Tom F."
                fill
                priority
                className="object-cover"
              />
            </div>

            <div>
              <cite className="text-stone-900 text-base font-semibold not-italic block">
                Meredith & Tom F.
              </cite>
              <span className="text-stone-900/50 text-sm tracking-wide mt-1 block" data-pebble-id="pb-cd75af">
                Homeowners in Cary, NC
              </span>
            </div>
          </footer>
        </blockquote>
        </FadeUp>

      </div>
    </section>
  );
}
