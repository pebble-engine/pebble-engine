"use client";

import RevealWords from "@/components/motion/RevealWords";
import { StickyStorySection, StickyStep } from "@/components/motion/StickyStory";

export default function ScrollStoryProcess() {
  return (
    <StickyStorySection className="bg-slate-50 py-24">
      <div className="container mx-auto max-w-6xl px-8 mb-8">
        <p className="text-teal-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-52db3a">
          How it works
        </p>
        <h2 className="text-slate-900 text-5xl md:text-6xl font-bold leading-tight max-w-2xl" data-pebble-id="pb-f0c2f4">
          <RevealWords>From shoebox chaos to clear books — here's what working with us looks like.</RevealWords>
        </h2>
      </div>

      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/8296977/pexels-photo-8296977.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Start with the Shoebox Review"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-teal-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-c9a057">
          Step 1
        </span>
        <h3 className="text-slate-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-02d5f8">
          Start with the Shoebox Review
        </h3>
        <p className="text-slate-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-8c0f30">
          Bring whatever you've got — receipts, bank statements, a shoebox, or nothing at all. We'll spend 20 minutes together and tell you exactly what you're dealing with, free of charge.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/8439695/pexels-photo-8439695.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="We agree on a clear scope"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-teal-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-2fdbf0">
          Step 2
        </span>
        <h3 className="text-slate-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-5f75d8">
          We agree on a clear scope
        </h3>
        <p className="text-slate-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-d05832">
          No vague packages. We tell you what needs to be done, what it costs, and what the timeline looks like. You decide what works for you before anything starts.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/8296971/pexels-photo-8296971.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="We take it off your plate"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-teal-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-2254e1">
          Step 3
        </span>
        <h3 className="text-slate-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-730538">
          We take it off your plate
        </h3>
        <p className="text-slate-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-c09e6f">
          Once we're aligned, you hand over access and we get to work. Books get organized, returns get filed, and you get regular updates — not silence.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/5917857/pexels-photo-5917857.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="You stay informed, always"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-teal-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-a4521a">
          Step 4
        </span>
        <h3 className="text-slate-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-69c298">
          You stay informed, always
        </h3>
        <p className="text-slate-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-75d609">
          We send clear summaries, answer your questions the same day, and flag anything that needs your attention before it becomes a problem. You're never left guessing.
        </p>
      </StickyStep>
      
    </StickyStorySection>
  );
}
