"use client";

import RevealWords from "@/components/motion/RevealWords";
import { StickyStorySection, StickyStep } from "@/components/motion/StickyStory";

export default function ScrollStoryProcess() {
  return (
    <StickyStorySection className="bg-neutral-50 py-24">
      <div className="container mx-auto max-w-6xl px-8 mb-8">
        <p className="text-neutral-900 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-1e74f3">
          Our process
        </p>
        <h2 className="text-neutral-900 text-5xl md:text-6xl font-bold leading-tight max-w-2xl" data-pebble-id="pb-fea721">
          <RevealWords>From the first site walk to the finished house.</RevealWords>
        </h2>
      </div>

      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/9993874/pexels-photo-9993874.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="We walk the site"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-neutral-900 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-83a375">
          First
        </span>
        <h3 className="text-neutral-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-6b0b51">
          We walk the site
        </h3>
        <p className="text-neutral-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-626b0d">
          Before any drawing starts, we visit the land at sunrise and sunset. We document the light, the views, the slope, the trees. The house has to earn its place.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/6614748/pexels-photo-6614748.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Schematic design"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-neutral-900 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-7ecfdf">
          Second
        </span>
        <h3 className="text-neutral-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-952430">
          Schematic design
        </h3>
        <p className="text-neutral-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-a8ca13">
          We develop a scheme that responds to what we found on site — orientation, massing, where the windows open and why. We present two or three directions before we commit to one.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/5089125/pexels-photo-5089125.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Design development"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-neutral-900 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-bad44c">
          Third
        </span>
        <h3 className="text-neutral-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-7ddfb0">
          Design development
        </h3>
        <p className="text-neutral-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-582009">
          Materials, details, structure. We work through every decision carefully — not to add layers, but to strip them away until only what's necessary remains.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/6614786/pexels-photo-6614786.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Construction documents"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-neutral-900 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-ce94c3">
          Fourth
        </span>
        <h3 className="text-neutral-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-4d007d">
          Construction documents
        </h3>
        <p className="text-neutral-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-6a4422">
          We produce a thorough set of drawings and specifications. Fewer questions in the field means fewer surprises in the budget and a better-built house at the end.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/7937756/pexels-photo-7937756.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Construction administration"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-neutral-900 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-e0294a">
          Fifth
        </span>
        <h3 className="text-neutral-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-ab2f37">
          Construction administration
        </h3>
        <p className="text-neutral-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-ce534f">
          We stay involved through the build — site visits, contractor coordination, responding to RFIs. We don't hand off a drawing set and disappear.
        </p>
      </StickyStep>
      
    </StickyStorySection>
  );
}
