"use client";

import RevealWords from "@/components/motion/RevealWords";
import { StickyStorySection, StickyStep } from "@/components/motion/StickyStory";

export default function ScrollStoryProcess() {
  return (
    <StickyStorySection className="bg-slate-50 py-24">
      <div className="container mx-auto max-w-6xl px-8 mb-8">
        <p className="text-teal-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-da47ab">
          How it works
        </p>
        <h2 className="text-slate-900 text-5xl md:text-6xl font-bold leading-tight max-w-2xl" data-pebble-id="pb-92a7b6">
          <RevealWords>From first question to final resolution — we're with you every step</RevealWords>
        </h2>
      </div>

      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/33648576/pexels-photo-33648576.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Your free plain English call"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-teal-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-31afa7">
          Step 1
        </span>
        <h3 className="text-slate-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-e52bdc">
          Your free plain English call
        </h3>
        <p className="text-slate-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-169835">
          We spend 30 minutes on the phone — no charge, no obligation. You tell us what's going on. We explain your options in plain language and answer every question you have.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/8112153/pexels-photo-8112153.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="We build your case plan together"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-teal-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-9cf3ae">
          Step 2
        </span>
        <h3 className="text-slate-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-81d90d">
          We build your case plan together
        </h3>
        <p className="text-slate-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-1029b5">
          If you decide to work with us, we map out the full process — timeline, documents, likely outcomes — so there are no surprises. You always know where things stand.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/8112111/pexels-photo-8112111.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="We handle the legal work"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-teal-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-805390">
          Step 3
        </span>
        <h3 className="text-slate-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-6d6795">
          We handle the legal work
        </h3>
        <p className="text-slate-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-cb5909">
          Filings, negotiations, court appearances — we take care of it. We check in at every milestone and translate any legal language into plain English before you act.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/7880784/pexels-photo-7880784.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="You move forward"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-teal-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-52e152">
          Step 4
        </span>
        <h3 className="text-slate-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-743b21">
          You move forward
        </h3>
        <p className="text-slate-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-5db07f">
          When your case closes, you understand every outcome and know exactly what it means for you and your family. We're still available if questions come up down the road.
        </p>
      </StickyStep>
      
    </StickyStorySection>
  );
}
