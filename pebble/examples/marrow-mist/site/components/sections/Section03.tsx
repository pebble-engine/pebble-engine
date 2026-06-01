"use client";

import RevealWords from "@/components/motion/RevealWords";
import { StickyStorySection, StickyStep } from "@/components/motion/StickyStory";

export default function ScrollStoryProcess() {
  return (
    <StickyStorySection className="bg-stone-50 py-24">
      <div className="container mx-auto max-w-6xl px-8 mb-8">
        <p className="text-stone-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-f25137">
          How a visit unfolds.
        </p>
        <h2 className="text-stone-900 text-5xl md:text-6xl font-bold leading-tight max-w-2xl" data-pebble-id="pb-b640e7">
          <RevealWords>From threshold to table — your visit, step by step.</RevealWords>
        </h2>
      </div>

      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/17640381/pexels-photo-17640381.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Leave the noise outside."
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-stone-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-1aad48">
          Arrival
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-a111c1">
          Leave the noise outside.
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-bffced">
          You're greeted by name, shown to a quiet anteroom, and offered a moment to set down whatever you carried in. No forms on a clipboard. No waiting-room screens.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/19695967/pexels-photo-19695967.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Warm water and cedar tea."
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-stone-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-3779dc">
          The Ritual
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-3e8e14">
          Warm water and cedar tea.
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-d8dd4c">
          Your foot soak is drawn — warm water with mineral salts and eucalyptus. A cup of cedar-and-chamomile tea arrives. This is yours before anything else begins.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/6628601/pexels-photo-6628601.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Unhurried, thorough, yours."
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-stone-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-760c1f">
          The Treatment
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-144bcb">
          Unhurried, thorough, yours.
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-22d9c6">
          Your therapist checks in — not with a questionnaire, but a conversation. Then the treatment begins at your pace, for the full duration you booked.
        </p>
      </StickyStep>
      
      <StickyStep
        media={
          <img
            src="https://images.pexels.com/photos/3921397/pexels-photo-3921397.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Slow your return to the day."
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-stone-700 text-sm font-semibold uppercase tracking-widest" data-pebble-id="pb-733b70">
          Coming Back
        </span>
        <h3 className="text-stone-900 text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5" data-pebble-id="pb-aa889a">
          Slow your return to the day.
        </h3>
        <p className="text-stone-900/70 text-xl leading-relaxed max-w-md" data-pebble-id="pb-4bbb78">
          After your treatment, rest in the recovery lounge as long as you need. There's no rush to the door. Hot water, a robe, a few minutes of just being still.
        </p>
      </StickyStep>
      
    </StickyStorySection>
  );
}
