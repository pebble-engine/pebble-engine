"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";
import MagneticButton from "@/components/motion/MagneticButton";

export default function HeroBrightPlayful() {
  return (
    <section className="relative min-h-screen bg-pink-50 flex flex-col items-center justify-center overflow-hidden px-8 py-24">
      {/* Decorative blob shapes — pure CSS, no images */}
      <div aria-hidden="true" className="pointer-events-none absolute -top-24 -left-24 w-96 h-96 rounded-full bg-amber-300/30 blur-3xl" />
      <div aria-hidden="true" className="pointer-events-none absolute -bottom-32 -right-16 w-80 h-80 rounded-full bg-pink-400/20 blur-3xl" />

      <div className="relative z-10 container mx-auto max-w-5xl text-center">
        {/* Eyebrow */}
        <p className="inline-flex items-center gap-2 bg-pink-100 text-pink-600 text-sm font-semibold px-5 py-2 rounded-full mb-8 tracking-wide" data-pebble-id="pb-26669a">
          🌲 A little shop full of big surprises
        </p>

        {/* Headline */}
        <h1 className="text-purple-900 text-6xl md:text-8xl font-extrabold leading-none tracking-tight max-w-4xl mx-auto" data-pebble-id="pb-5c8258">
          <RevealWords>Toys worth keeping, play worth remembering</RevealWords>
        </h1>

        {/* Subheadline */}
        <p className="text-purple-900/70 text-xl md:text-2xl mt-8 max-w-2xl mx-auto leading-relaxed" data-pebble-id="pb-2c95bc">
          We hand-pick every wooden toy, building set, and wind-up wonder ourselves — no big-box stuff, no mountains of plastic. Just the good kind of play, tucked into our cozy corner storefront.
        </p>

        {/* CTAs */}
        <div className="mt-12 flex flex-wrap gap-4 justify-center">
          <MagneticButton
            href="#join"
            className="inline-block bg-pink-500 text-white px-10 py-5 rounded-full font-bold text-lg shadow-lg hover:scale-110 hover:rotate-2 hover:shadow-pink-300 transition-all duration-200"
          >
            Visit the shop
          </MagneticButton>
          <a
            href="#learn"
            className="bg-white text-purple-900 border-2 border-purple-200 px-10 py-5 rounded-full font-bold text-lg hover:scale-105 hover:border-pink-400 transition-all duration-200" data-pebble-id="pb-ee09ad">
            Meet our mystery cubby
          </a>
        </div>
      </div>

      {/* Hero image — floaty card with drop shadow */}
      <div className="relative z-10 mt-16 w-full max-w-3xl mx-auto">
        <div className="relative aspect-[16/9] rounded-3xl overflow-hidden shadow-2xl ring-4 ring-pink-200">
          <Parallax className="absolute inset-0" distance={40}>
            <Image
              src="https://images.pexels.com/photos/36303741/pexels-photo-36303741.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
              alt="Toys worth keeping, play worth remembering"
              fill
              priority
              className="object-cover"
            />
          </Parallax>
        </div>
        {/* Decorative offset badge */}
        <div aria-hidden="true" className="absolute -bottom-4 -right-4 w-24 h-24 bg-amber-300 rounded-3xl -z-10" />
        <div aria-hidden="true" className="absolute -top-4 -left-4 w-16 h-16 bg-pink-300 rounded-2xl -z-10" />
      </div>
    </section>
  );
}
