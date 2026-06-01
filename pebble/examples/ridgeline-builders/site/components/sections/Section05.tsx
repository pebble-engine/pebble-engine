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
          className="text-amber-700/20 text-9xl font-serif leading-none select-none -mb-8"
        >
          &ldquo;
        </div>

        {/* The pull-quote itself */}
        <FadeUp>
        <blockquote className="relative" data-pebble-id="pb-781c47">
          <p className="text-stone-900 text-3xl md:text-5xl font-semibold leading-tight tracking-tight max-w-3xl mx-auto" data-pebble-id="pb-5b6d7b">
            Ridgeline gave us a number on day one and stuck to it. Our kitchen went from a cramped 1990s layout to something we actually want to spend time in. The crew was on-site when they said they'd be, and the finish work is exactly what we asked for.
          </p>

          {/* Attribution block */}
          <footer className="mt-12 flex flex-col items-center gap-4">
            {/* Headshot circle */}
            <div className="relative w-16 h-16 rounded-full overflow-hidden ring-2 ring-amber-700/30">
              <Image
                src="https://images.pexels.com/photos/23224973/pexels-photo-23224973.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Sarah & Tom M."
                fill
                priority
                className="object-cover"
              />
            </div>

            <div>
              <cite className="text-stone-900 text-base font-semibold not-italic block">
                Sarah & Tom M.
              </cite>
              <span className="text-stone-900/50 text-sm tracking-wide mt-1 block" data-pebble-id="pb-943aa0">
                Homeowners, Boise, ID
              </span>
            </div>
          </footer>
        </blockquote>
        </FadeUp>

      </div>
    </section>
  );
}
