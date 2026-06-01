"use client";

import FadeUp from "@/components/motion/FadeUp";

export default function TestimonialsPressEditorial() {
  return (
    <section className="bg-neutral-50 py-28 px-8">
      <div className="container mx-auto max-w-3xl">

        {/* Rule above — editorial breath */}
        <div className="border-t border-neutral-900/15 pt-16">

          {/* Oversized opening mark — hairline weight only */}
          <div
            aria-hidden="true"
            className="font-serif text-neutral-900/10 text-8xl leading-none select-none -mb-4"
          >
            &ldquo;
          </div>

          <FadeUp>
          <blockquote data-pebble-id="pb-144161">
            <p className="font-serif text-neutral-900 text-2xl md:text-4xl leading-snug tracking-tight" data-pebble-id="pb-23bdca">
              The Catskill Ridge House is the kind of work that makes you reconsider what a house is for. Every room feels like it was placed there by someone paying close attention to the land beneath it.
            </p>

            <footer className="mt-12 flex items-center gap-6">
              {/* Minimal horizontal rule in lieu of headshot */}
              <div className="w-8 h-px bg-neutral-900/25 flex-shrink-0" aria-hidden="true" />
              <div>
                <cite className="text-neutral-900 text-sm font-sans tracking-wide not-italic block">
                  Architectural Record
                </cite>
                <span className="text-neutral-900/40 text-xs font-sans tracking-widest uppercase mt-1 block" data-pebble-id="pb-c4fed8">
                  Regional Design Review, 2023
                </span>
              </div>
            </footer>
          </blockquote>
          </FadeUp>

        </div>
      </div>
    </section>
  );
}
