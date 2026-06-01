"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";

export default function AboutStory() {
  return (
    <section className="bg-slate-50 py-24 px-8 overflow-hidden">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">

          {/* Portrait image — left column */}
          <div className="relative">
            <div className="relative aspect-[3/4] rounded-3xl overflow-hidden">
              <Parallax className="absolute inset-0" distance={30}>
                <Image
                  src="https://images.pexels.com/photos/12917343/pexels-photo-12917343.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="Built for the patients who've always dreaded the dentist"
                  fill
                  priority
                  className="object-cover"
                />
              </Parallax>
              {/* Warm gradient wash at the bottom of the portrait */}
              <div className="absolute inset-0 bg-gradient-to-t from-slate-50/30 to-transparent" />
            </div>
            {/* Decorative accent block — visual warmth */}
            <div className="absolute -bottom-6 -right-6 w-48 h-48 rounded-3xl bg-teal-600/10 -z-10" />
          </div>

          {/* Prose — right column */}
          <div>
            <p className="text-teal-600 text-sm uppercase tracking-widest mb-4" data-pebble-id="pb-18b64d">
              Our story
            </p>
            <h2 className="text-slate-900 text-5xl md:text-6xl font-bold leading-tight mb-8 max-w-lg" data-pebble-id="pb-c4a906">
              <RevealWords>Built for the patients who've always dreaded the dentist</RevealWords>
            </h2>

            
            <p className="text-slate-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-a348aa">
              Willow Creek Dental started with a simple observation: most people don't dislike dentistry — they dislike feeling rushed, uninformed, or powerless in the chair. We built our practice around fixing that.
            </p>
            
            <p className="text-slate-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-e86f19">
              We see everyone from toddlers getting their very first cleaning to grandparents who've been putting off a visit for years. Each appointment is blocked generously — one patient at a time, no overlap, no hurrying you out the door.
            </p>
            
            <p className="text-slate-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-ce09fd">
              Before we do anything, we explain it. Before you feel anything, you know why. That's not a script — it's just how we think dental care should feel. Calm, clear, and genuinely yours.
            </p>
            

            {/* Signature line */}
            <div className="mt-10 pt-8 border-t border-slate-900/10">
              <p className="text-slate-900 text-base font-semibold italic" data-pebble-id="pb-80a2e0">
                — Dr. Sarah Wren, DDS · Founder & Lead Dentist
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
