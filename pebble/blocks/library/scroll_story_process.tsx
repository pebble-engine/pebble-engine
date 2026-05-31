"use client";
import RevealWords from "@/components/motion/RevealWords";
import { StickyStorySection, StickyStep } from "@/components/motion/StickyStory";

export default function ScrollStoryProcess() {
  return (
    <StickyStorySection className="bg-{{bg}} py-24">
      <div className="container mx-auto max-w-6xl px-8 mb-8">
        <p className="text-{{accent}} text-sm uppercase tracking-widest mb-3">
          {{eyebrow}}
        </p>
        <h2 className="text-{{fg}} text-5xl md:text-6xl font-bold leading-tight max-w-2xl">
          <RevealWords>{{headline}}</RevealWords>
        </h2>
      </div>

      {/* {{steps_list_start}} */}
      <StickyStep
        media={
          <img
            src="{{steps[].image}}"
            alt="{{steps[].title}}"
            className="h-full w-full object-cover"
          />
        }
      >
        <span className="text-{{accent}} text-sm font-semibold uppercase tracking-widest">
          {{steps[].step_label}}
        </span>
        <h3 className="text-{{fg}} text-4xl md:text-5xl font-bold leading-tight mt-3 mb-5">
          {{steps[].title}}
        </h3>
        <p className="text-{{fg}}/70 text-xl leading-relaxed max-w-md">
          {{steps[].body}}
        </p>
      </StickyStep>
      {/* {{steps_list_end}} */}
    </StickyStorySection>
  );
}
