"use client";

import Image from "next/image";
import FadeUp from "@/components/motion/FadeUp";

export default function TestimonialsKidsPlayful() {
  return (
    <section className="bg-purple-900 py-28 px-8">
      <div className="container mx-auto max-w-4xl text-center">

        {/* Big cheerful quote mark */}
        <div
          aria-hidden="true"
          className="text-pink-400/30 text-9xl font-extrabold leading-none select-none -mb-6"
        >
          &ldquo;
        </div>

        {/* Pull-quote */}
        <FadeUp>
        <blockquote className="relative" data-pebble-id="pb-6ee5d8">
          <p className="text-white text-3xl md:text-5xl font-extrabold leading-tight tracking-tight max-w-3xl mx-auto" data-pebble-id="pb-d8133b">
            My son has dragged us back every Saturday for three months just to pick a mystery cubby. We've started budgeting for it. The toys inside are always so thoughtful — nothing cheap, nothing junky. This shop is the real deal.
          </p>

          {/* Attribution */}
          <footer className="mt-14 flex flex-col items-center gap-5">
            {/* Headshot with colorful ring */}
            <div className="relative w-20 h-20 rounded-full overflow-hidden ring-4 ring-pink-500 shadow-lg shadow-pink-500/40">
              <Image
                src="https://images.pexels.com/photos/962337/pexels-photo-962337.png?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Claudia — mom of two"
                fill
                priority
                className="object-cover"
              />
            </div>

            <div>
              <cite className="text-white text-lg font-extrabold not-italic block">
                Claudia — mom of two
              </cite>
              <span className="text-pink-300 text-sm tracking-wide mt-1 block" data-pebble-id="pb-0efe7a">
                Regular customer since the shop opened
              </span>
            </div>

            {/* Star rating — decorative */}
            <div aria-hidden="true" className="flex gap-1 text-amber-300 text-2xl mt-1">
              &#9733;&#9733;&#9733;&#9733;&#9733;
            </div>
          </footer>
        </blockquote>
        </FadeUp>

      </div>
    </section>
  );
}
