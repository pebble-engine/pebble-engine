"use client";

import RevealWords from "@/components/motion/RevealWords";
import { StickyStorySection, StickyStep } from "@/components/motion/StickyStory";

export default function ScrollStoryProcess() {
  return (
    <StickyStorySection className="bg-stone-50 py-24">
      <div className="container mx-auto max-w-6xl px-8 mb-8">
        <p className="text-amber-800 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-25dc8e">
          How it works.
        </p>
        <h2 className="text-stone-900 text-5xl md:text-6xl font-bold leading-tight max-w-2xl" data-pebble-id="pb-c2535a">
          <RevealWords>From your first words to a piece you'll wear for a lifetime.</RevealWords>
        </h2>
      </div>

      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/8056990/pexels-photo-8056990.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="A conversation"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-800 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-00e61c">
          First
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-44d1a8">
          A conversation
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-ffd542">
          We begin with a quiet conversation — in the studio or over email — about the moment you're marking, the metals you're drawn to, and the story you want the piece to carry.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/1050312/pexels-photo-1050312.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="The sketch"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-800 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-6b9100">
          Second
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-4dabde">
          The sketch
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-cd7b09">
          I draw your piece by hand on cotton paper. You'll receive the original — not a scan, the actual sketch — before any work at the bench begins. Changes are welcome at this stage.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/15955333/pexels-photo-15955333.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="The making"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-800 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-6b32a2">
          Third
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-bde4dd">
          The making
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-503815">
          Once the design is approved, I fabricate your piece at my bench. Sawing, forming, soldering, stone-setting — each step done by hand, in my studio.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/11351004/pexels-photo-11351004.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Yours to keep"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-800 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-942705">
          Finally
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-c7eed4">
          Yours to keep
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-3b11f3">
          Your finished piece arrives with its original design sketch, wrapped simply and without fuss. The sketch and the jewelry together — a record of how something beautiful was made for you.
        </p>
      </StickyStep>
      
    </StickyStorySection>
  );
}
