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
          <blockquote data-pebble-id="pb-f1bc48">
            <p className="font-serif text-neutral-900 text-2xl md:text-4xl leading-snug tracking-tight" data-pebble-id="pb-e34622">
              We framed three of Nora's photographs within a week of receiving them. They look like they've always been on the wall — the light, the grain, the way she caught a moment we didn't even notice happening. Nothing posed, nothing obvious.
            </p>

            <footer className="mt-12 flex items-center gap-6">
              {/* Minimal horizontal rule in lieu of headshot */}
              <div className="w-8 h-px bg-neutral-900/25 flex-shrink-0" aria-hidden="true" />
              <div>
                <cite className="text-neutral-900 text-sm font-sans tracking-wide not-italic block">
                  Claire & Tom R.
                </cite>
                <span className="text-neutral-900/40 text-xs font-sans tracking-widest uppercase mt-1 block" data-pebble-id="pb-52f859">
                  Married in the Willamette Valley, 2023
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
