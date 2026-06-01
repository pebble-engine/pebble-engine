"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import FadeUp from "@/components/motion/FadeUp";
import Parallax from "@/components/motion/Parallax";

export default function AboutEthos() {
  return (
    <section className="bg-stone-50 py-32 px-8 overflow-hidden">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-20 items-start">

          {/* Left — prose, floated top */}
          <div className="md:pt-8">
            <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-8 font-light" data-pebble-id="pb-819ad6">
              Our ethos.
            </p>
            <h2 className="text-stone-700 text-5xl md:text-6xl font-light leading-[1.1] tracking-tight mb-10 max-w-lg" data-pebble-id="pb-84a021">
              <RevealWords>We built this place around one idea: you should arrive slowly.</RevealWords>
            </h2>

            <FadeUp>
            
            <p className="text-stone-500 text-lg font-light leading-relaxed mb-6" data-pebble-id="pb-d21016">
              Most spas rush you in. We built Marrow & Mist to do the opposite. Before any treatment, every guest sits with a warm foot ritual and a cup of cedar-and-chamomile tea. You don't get on the table until the day has left your body.
            </p>
            
            <p className="text-stone-500 text-lg font-light leading-relaxed mb-6" data-pebble-id="pb-8825e4">
              We mostly see women in their 30s and 40s who are holding a lot. Career, family, the thousand small decisions that add up to exhaustion. We don't talk about wellness goals here. We talk about an hour of actual quiet — and we protect it.
            </p>
            
            <p className="text-stone-500 text-lg font-light leading-relaxed mb-6" data-pebble-id="pb-a6807b">
              Tucked just off the main road, we stay small on purpose. Our therapists know your name, your pressure preferences, and which blend helps you sleep. That's not a feature. That's just how we think care should work.
            </p>
            
            </FadeUp>

            {/* Signature — thin rule above */}
            <div className="mt-12 pt-8 border-t border-stone-200">
              <p className="text-stone-600 text-base font-light italic tracking-wide" data-pebble-id="pb-ce060b">
                — Nadia Voss, Founder & Lead Therapist
              </p>
            </div>
          </div>

          {/* Right — portrait, accent accent block behind it */}
          <div className="relative">
            <div className="relative aspect-[3/4] rounded-2xl overflow-hidden">
              <Parallax className="absolute inset-0" distance={30}>
                <Image
                  src="https://images.pexels.com/photos/7019718/pexels-photo-7019718.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="We built this place around one idea: you should arrive slowly."
                  fill
                  priority
                  className="object-cover"
                />
              </Parallax>
              {/* Soft cream gradient at base — doesn't crush the image */}
              <div className="absolute inset-0 bg-gradient-to-t from-stone-50/20 to-transparent" />
            </div>
            {/* Decorative accent square — floated behind */}
            <div className="absolute -bottom-8 -left-8 w-40 h-40 rounded-2xl bg-amber-600/8 -z-10" />
            <div className="absolute -top-4 -right-4 w-24 h-24 rounded-full bg-rose-200/30 -z-10" />
          </div>

        </div>
      </div>
    </section>
  );
}
