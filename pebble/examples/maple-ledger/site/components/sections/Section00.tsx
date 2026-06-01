"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";
import MagneticButton from "@/components/motion/MagneticButton";

export default function HeroFocused() {
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden bg-slate-50">
      {/* Background image — right half only, desktop */}
      <div className="absolute inset-y-0 right-0 w-full md:w-1/2">
        <Parallax className="absolute inset-0" distance={40}>
          <Image
            src="https://images.pexels.com/photos/8297044/pexels-photo-8297044.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Finally, an accountant who picks up the phone."
            fill
            priority
            className="object-cover"
          />
        </Parallax>
        <div className="absolute inset-0 bg-gradient-to-r from-slate-50 via-slate-50/60 to-transparent" />
      </div>

      {/* Content — left column */}
      <div className="relative z-10 container mx-auto max-w-6xl px-8 py-28">
        <div className="max-w-xl">
          <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-6" data-pebble-id="pb-1aa242">
            CPA & bookkeeping for local small businesses
          </p>
          <h1 className="text-slate-900 text-5xl md:text-7xl font-semibold leading-tight tracking-tight" data-pebble-id="pb-f474da">
            <RevealWords>Finally, an accountant who picks up the phone.</RevealWords>
          </h1>
          <p className="text-slate-600 text-lg mt-6 leading-relaxed max-w-md" data-pebble-id="pb-73cd66">
            We handle the day-to-day books and yearly taxes for restaurants, contractors, salons, and individuals who want their returns done right — no vanishing acts, no surprises.
          </p>
          <div className="mt-10 flex flex-wrap gap-4">
            <MagneticButton
              href="#contact"
              className="inline-block bg-sky-600 text-white px-7 py-3.5 rounded-md font-medium hover:bg-sky-700 transition text-sm tracking-wide"
            >
              Book your free review
            </MagneticButton>
            <a
              href="#services"
              className="text-slate-700 px-7 py-3.5 rounded-md border border-slate-300 hover:border-slate-400 hover:bg-slate-100 transition text-sm tracking-wide" data-pebble-id="pb-e0e1c7">
              See our services
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
