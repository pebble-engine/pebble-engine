"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";

export default function AboutOriginPlayful() {
  return (
    <section className="bg-pink-50 py-24 px-8 overflow-hidden">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">

          {/* Portrait — left column with playful frame */}
          <div className="relative">
            <div className="relative aspect-[3/4] rounded-[2.5rem] overflow-hidden shadow-xl ring-4 ring-pink-300">
              <Parallax className="absolute inset-0" distance={30}>
                <Image
                  src="https://images.pexels.com/photos/36303741/pexels-photo-36303741.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="We opened a tiny shop and filled it with the toys we actually wanted for our own kids"
                  fill
                  priority
                  className="object-cover"
                />
              </Parallax>
            </div>
            {/* Floating accent blocks */}
            <div aria-hidden="true" className="absolute -bottom-6 -right-6 w-36 h-36 rounded-3xl bg-amber-300 -z-10" />
            <div aria-hidden="true" className="absolute -top-5 -left-5 w-20 h-20 rounded-2xl bg-pink-400 -z-10 rotate-6" />
          </div>

          {/* Prose — right column */}
          <div>
            <p className="inline-flex items-center gap-2 bg-pink-100 text-pink-600 text-sm font-bold px-5 py-2 rounded-full mb-6" data-pebble-id="pb-37155e">
              🌿 How it all started
            </p>
            <h2 className="text-purple-900 text-5xl md:text-6xl font-extrabold leading-tight mb-8 max-w-lg" data-pebble-id="pb-b2c11c">
              <RevealWords>We opened a tiny shop and filled it with the toys we actually wanted for our own kids</RevealWords>
            </h2>

            
            <p className="text-purple-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-4d56e4">
              We got tired of driving to big-box stores and leaving with bags full of plastic stuff that broke in a week. We knew there were better toys out there — we just had to go find them. So we did, one maker and one market at a time.
            </p>
            
            <p className="text-purple-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-6a8d3e">
              Pocket & Pinecone started in a corner storefront with a handful of wooden toys, some hand-lettered signs, and a real belief that play should feel magical. We hand-pick every single thing on our shelves — if we wouldn't give it to a kid we love, it doesn't make the cut.
            </p>
            
            <p className="text-purple-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-5ecc15">
              The mystery cubby wall was our first big idea and it's still the heart of the shop. Five dollars, one numbered wooden box, infinite delight. We restock the cubbies every week, and we've never once seen a kid walk away disappointed.
            </p>
            

            {/* Signature */}
            <div className="mt-10 pt-8 border-t-2 border-dashed border-pink-200">
              <p className="text-purple-900 text-base font-bold italic" data-pebble-id="pb-70508d">
                — Maren & Joel, Founders & Chief Toy Scouts
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
