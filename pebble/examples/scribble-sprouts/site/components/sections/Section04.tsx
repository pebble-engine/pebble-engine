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
        <blockquote className="relative" data-pebble-id="pb-934a73">
          <p className="text-white text-3xl md:text-5xl font-extrabold leading-tight tracking-tight max-w-3xl mx-auto" data-pebble-id="pb-f3dfbd">
            My son has never called himself an artist — until he walked past the Wall of Fame and pointed at his painting. He literally gasped. He asks every week when his next class is. Scribble Sprouts gave him something I couldn't have bought him anywhere else.
          </p>

          {/* Attribution */}
          <footer className="mt-14 flex flex-col items-center gap-5">
            {/* Headshot with colorful ring */}
            <div className="relative w-20 h-20 rounded-full overflow-hidden ring-4 ring-pink-500 shadow-lg shadow-pink-500/40">
              <Image
                src="https://images.pexels.com/photos/8208251/pexels-photo-8208251.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Rachel — mom of two"
                fill
                priority
                className="object-cover"
              />
            </div>

            <div>
              <cite className="text-white text-lg font-extrabold not-italic block">
                Rachel — mom of two
              </cite>
              <span className="text-pink-300 text-sm tracking-wide mt-1 block" data-pebble-id="pb-a6814e">
                Parent of a 7-year-old, attending since September
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
