"use client";

import RevealWords from "@/components/motion/RevealWords";
import { StickyStorySection, StickyStep } from "@/components/motion/StickyStory";

export default function ScrollStoryProcess() {
  return (
    <StickyStorySection className="bg-stone-50 py-24">
      <div className="container mx-auto max-w-6xl px-8 mb-8">
        <p className="text-amber-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-af3aad">
          From the farm to your cup
        </p>
        <h2 className="text-stone-900 text-5xl md:text-6xl font-bold leading-tight max-w-2xl" data-pebble-id="pb-a3f2f2">
          <RevealWords>How we go from a green bean to the bag in your hands.</RevealWords>
        </h2>
      </div>

      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/29798812/pexels-photo-29798812.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="We source direct from the farm"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-f19f2f">
          Step 1
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-41c14c">
          We source direct from the farm
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-b01495">
          We work with importers and cooperatives we trust to find single-origin lots from small farms in Ethiopia, Colombia, and Guatemala — traceable to the specific harvest.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/7175961/pexels-photo-7175961.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="We roast in small batches"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-7bda72">
          Step 2
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-ae385b">
          We roast in small batches
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-2adb52">
          A few mornings a week, we load the drum and roast to order. Small batches mean we can stay attentive — adjusting time and temperature for each origin's personality.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/37539911/pexels-photo-37539911.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="We write the date by hand"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-88c8b3">
          Step 3
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-415e29">
          We write the date by hand
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-73f698">
          Every single bag gets a handwritten roast date and a note about the farm — origin, altitude, processing method. It takes a minute. We think it's worth it.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/10540813/pexels-photo-10540813.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="We ship it or you stop by"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-amber-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-502a9e">
          Step 4
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-d87cfd">
          We ship it or you stop by
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-d3cab3">
          Bags ship within 48 hours of roasting. Or come to the café — smell the fresh roast, pick up your order, stay for a pour-over. We're usually here.
        </p>
      </StickyStep>
      
    </StickyStorySection>
  );
}
