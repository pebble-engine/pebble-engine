"use client";
import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";

export default function AboutStory() {
  return (
    <section className="bg-{{bg}} py-24 px-8 overflow-hidden">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">

          {/* Portrait image — left column */}
          <div className="relative">
            <div className="relative aspect-[3/4] rounded-3xl overflow-hidden">
              <Parallax className="absolute inset-0" distance={30}>
                <Image
                  src="{{portrait_image}}"
                  alt="{{headline}}"
                  fill
                  priority
                  className="object-cover"
                />
              </Parallax>
              {/* Warm gradient wash at the bottom of the portrait */}
              <div className="absolute inset-0 bg-gradient-to-t from-{{bg}}/30 to-transparent" />
            </div>
            {/* Decorative accent block — visual warmth */}
            <div className="absolute -bottom-6 -right-6 w-48 h-48 rounded-3xl bg-{{accent}}/10 -z-10" />
          </div>

          {/* Prose — right column */}
          <div>
            <p className="text-{{accent}} text-sm uppercase tracking-widest mb-4">
              {{eyebrow}}
            </p>
            <h2 className="text-{{fg}} text-5xl md:text-6xl font-bold leading-tight mb-8 max-w-lg">
              <RevealWords>{{headline}}</RevealWords>
            </h2>

            {/* {{story_paragraphs_list_start}} */}
            <p className="text-{{fg}}/70 text-xl leading-relaxed mb-6">
              {{story_paragraphs[]}}
            </p>
            {/* {{story_paragraphs_list_end}} */}

            {/* Signature line */}
            <div className="mt-10 pt-8 border-t border-{{fg}}/10">
              <p className="text-{{fg}} text-base font-semibold italic">
                — {{signature}}
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
