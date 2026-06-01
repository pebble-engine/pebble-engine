"use client";

import RevealWords from "@/components/motion/RevealWords";
import { StickyStorySection, StickyStep } from "@/components/motion/StickyStory";

export default function ScrollStoryProcess() {
  return (
    <StickyStorySection className="bg-slate-50 py-24">
      <div className="container mx-auto max-w-6xl px-8 mb-8">
        <p className="text-teal-600 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-36b5c9">
          How a visit works
        </p>
        <h2 className="text-slate-900 text-5xl md:text-6xl font-bold leading-tight max-w-2xl" data-pebble-id="pb-26cdfd">
          <RevealWords>What to expect when you walk through our door</RevealWords>
        </h2>
      </div>

      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/4562895/pexels-photo-4562895.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="You arrive — no waiting room chaos"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-teal-600 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-6d3949">
          Step 1
        </span>
        <h3 className="text-slate-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-ad4c8d">
          You arrive — no waiting room chaos
        </h3>
        <p className="text-slate-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-503d3a">
          We never double-book, so your appointment starts on time. A calm, unhurried space is waiting for you when you arrive.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/3884103/pexels-photo-3884103.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="We listen before we look"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-teal-600 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-3792e9">
          Step 2
        </span>
        <h3 className="text-slate-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-4bb12b">
          We listen before we look
        </h3>
        <p className="text-slate-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-24d290">
          Before anything else, we ask about your concerns, your history, and how you're feeling. Anxious? That's normal here. We take our time.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/5622259/pexels-photo-5622259.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="We explain everything first"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-teal-600 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-96049c">
          Step 3
        </span>
        <h3 className="text-slate-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-de9d74">
          We explain everything first
        </h3>
        <p className="text-slate-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-f7fbc2">
          Nothing happens without your full understanding. We show you what we see, describe what we're going to do, and answer every question.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/3845842/pexels-photo-3845842.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Treatment, at your pace"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-teal-600 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-b97834">
          Step 4
        </span>
        <h3 className="text-slate-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-f16ffd">
          Treatment, at your pace
        </h3>
        <p className="text-slate-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-f4ce1c">
          You stay in control. We check in throughout. If you need a break, just say so. Unhurried care isn't a policy — it's how we work.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/5622275/pexels-photo-5622275.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="You leave knowing exactly what's next"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-teal-600 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-c5719f">
          Step 5
        </span>
        <h3 className="text-slate-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-2d8916">
          You leave knowing exactly what's next
        </h3>
        <p className="text-slate-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-edb3e8">
          Before you go, we review findings and any follow-up in plain language — no jargon, no surprises on the bill.
        </p>
      </StickyStep>
      
    </StickyStorySection>
  );
}
