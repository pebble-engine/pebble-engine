"use client";

import RevealWords from "@/components/motion/RevealWords";
import { StickyStorySection, StickyStep } from "@/components/motion/StickyStory";

export default function ScrollStoryProcess() {
  return (
    <StickyStorySection className="bg-stone-50 py-24">
      <div className="container mx-auto max-w-6xl px-8 mb-8">
        <p className="text-amber-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-a36a07">
          Your first visit
        </p>
        <h2 className="text-stone-900 text-5xl md:text-6xl font-bold leading-tight max-w-2xl" data-pebble-id="pb-2df76e">
          <RevealWords>What to expect when you come in for the first time.</RevealWords>
        </h2>
      </div>

      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/6653888/pexels-photo-6653888.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="The kettle goes on"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-93c24e">
          First
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-3b115b">
          The kettle goes on
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-8ed411">
          Before anything else, you'll sit down with one of us for a cup of tea. We'll ask about your hair, your life, your last cut — whatever helps us understand what you're after.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/20309789/pexels-photo-20309789.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="A slow consultation"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-248420">
          Then
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-d5c421">
          A slow consultation
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-e5aa56">
          We look at your hair properly — texture, growth patterns, what's been done before. We talk through options without pushing, and nothing happens until you're ready.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/10593034/pexels-photo-10593034.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="The cut, colour, or treatment"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-eb00b4">
          Next
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-170c95">
          The cut, colour, or treatment
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-4608b2">
          Your stylist is the same person every visit. They remember what you asked for last time and they build on it. No handoffs, no confusion.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/8834016/pexels-photo-8834016.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="You leave feeling like yourself"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-303ba6">
          Finally
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-4da8d9">
          You leave feeling like yourself
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-032af7">
          We finish with a style that fits how you actually wear your hair. We'll note what we did so your next visit picks right up from here.
        </p>
      </StickyStep>
      
    </StickyStorySection>
  );
}
