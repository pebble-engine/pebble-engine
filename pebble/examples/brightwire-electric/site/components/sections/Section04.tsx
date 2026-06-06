"use client";

import Image from "next/image";
import FadeUp from "@/components/motion/FadeUp";

export default function TestimonialsQuote() {
  return (
    <section className="bg-slate-50 py-28 px-8">
      <div className="container mx-auto max-w-4xl text-center">

        {/* Opening quote mark — oversized decorative glyph */}
        <div
          aria-hidden="true"
          className="text-amber-600/20 text-9xl font-serif leading-none select-none -mb-8"
        >
          &ldquo;
        </div>

        {/* The pull-quote itself */}
        <FadeUp>
        <blockquote className="relative" data-pebble-id="pb-4469fd">
          <p className="text-slate-900 text-3xl md:text-5xl font-semibold leading-tight tracking-tight max-w-3xl mx-auto" data-pebble-id="pb-a8acd2">
            Brightwire upgraded our panel and ran a dedicated circuit for our new EV charger in one visit. The estimate they gave us the day before matched the final invoice exactly — not a penny over. That kind of transparency is rare.
          </p>

          {/* Attribution block */}
          <footer className="mt-12 flex flex-col items-center gap-4">
            {/* Headshot circle */}
            <div className="relative w-16 h-16 rounded-full overflow-hidden ring-2 ring-amber-600/30">
              <Image
                src="https://images.pexels.com/photos/33435724/pexels-photo-33435724.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Marcus T."
                fill
                priority
                className="object-cover"
              />
            </div>

            <div>
              <cite className="text-slate-900 text-base font-semibold not-italic block">
                Marcus T.
              </cite>
              <span className="text-slate-900/50 text-sm tracking-wide mt-1 block" data-pebble-id="pb-d49ccd">
                Austin homeowner, South Congress neighborhood
              </span>
            </div>
          </footer>
        </blockquote>
        </FadeUp>

      </div>
    </section>
  );
}
