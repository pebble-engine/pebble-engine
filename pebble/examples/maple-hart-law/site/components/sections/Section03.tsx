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
                  src="https://images.pexels.com/photos/7841855/pexels-photo-7841855.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="A lawyer who gives it to you straight — no fine print, no runaround"
                  fill
                  priority
                  className="object-cover"
                />
              </Parallax>
              {/* Warm gradient wash at the bottom of the portrait */}
              <div className="absolute inset-0 bg-gradient-to-t from-slate-50/30 to-transparent" />
            </div>
            {/* Decorative accent block — visual warmth */}
            <div className="absolute -bottom-6 -right-6 w-48 h-48 rounded-3xl bg-teal-700/10 -z-10" />
          </div>

          {/* Prose — right column */}
          <div>
            <p className="text-teal-700 text-sm uppercase tracking-widest mb-4" data-pebble-id="pb-dc5c4b">
              About Dana Hart
            </p>
            <h2 className="text-slate-900 text-5xl md:text-6xl font-bold leading-tight mb-8 max-w-lg" data-pebble-id="pb-704f1f">
              <RevealWords>A lawyer who gives it to you straight — no fine print, no runaround</RevealWords>
            </h2>

            
            <p className="text-slate-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-b9887f">
              I started Maple & Hart because I kept seeing people walk into legal situations completely in the dark. They were scared, they didn't know what the words meant, and nobody was slowing down to explain it to them. I decided that was going to be different here.
            </p>
            
            <p className="text-slate-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-b0519d">
              I've practiced family law in Burlington for over a decade. Divorce, custody, adoption — I've handled all of it, and I've learned that what people need most isn't legal jargon, it's clarity. Knowing what's actually going to happen makes everything feel more manageable.
            </p>
            
            <p className="text-slate-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-d5a593">
              My job is to be the person across the table who tells you the truth, walks you through every step, and makes sure you feel like a participant in your own case — not a bystander. That's what I'd want for my own family.
            </p>
            

            {/* Signature line */}
            <div className="mt-10 pt-8 border-t border-slate-900/10">
              <p className="text-slate-900 text-base font-semibold italic" data-pebble-id="pb-82471e">
                — Dana Hart — Founder & Family Law Attorney
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
