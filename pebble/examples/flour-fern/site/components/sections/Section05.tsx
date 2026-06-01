"use client";

import RevealWords from "@/components/motion/RevealWords";
import { StickyStorySection, StickyStep } from "@/components/motion/StickyStory";

export default function ScrollStoryProcess() {
  return (
    <StickyStorySection className="bg-stone-50 py-24">
      <div className="container mx-auto max-w-6xl px-8 mb-8">
        <p className="text-amber-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-4d112f">
          How it's made
        </p>
        <h2 className="text-stone-900 text-5xl md:text-6xl font-bold leading-tight max-w-2xl" data-pebble-id="pb-5fc0b1">
          <RevealWords>Forty-eight hours from flour to your hands.</RevealWords>
        </h2>
      </div>

      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/18929284/pexels-photo-18929284.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="The mix"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-fd0578">
          Day one
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-14f427">
          The mix
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-f89654">
          We combine stone-milled flour, water, and our live starter by hand each afternoon. No machines, no shortcuts. The dough starts its long, slow rise in covered tubs overnight.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/6594903/pexels-photo-6594903.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Cold ferment"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-68fe96">
          Day two
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-bc490e">
          Cold ferment
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-d55b93">
          Shaped loaves go into the walk-in for a full night cold proof. The cold slows everything down and builds the sour, complex flavor that sets our bread apart.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/10481790/pexels-photo-10481790.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Into the oven"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-c10e1c">
          Early morning
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-3916cf">
          Into the oven
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-bbb93f">
          We score each loaf by hand before loading the deck oven. Steam injection gives the crust its shine and crackle. The whole bakery smells like nothing else.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/30350350/pexels-photo-30350350.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="On the shelf"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-822849">
          By 7am
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-b83bc1">
          On the shelf
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-53609a">
          Loaves cool on the rack, then go up for sale. Most days we're sold out before noon. Saturdays we always recommend arriving early for the rye-and-fig.
        </p>
      </StickyStep>
      
    </StickyStorySection>
  );
}
