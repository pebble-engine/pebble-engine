"use client";
import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import FadeUp from "@/components/motion/FadeUp";
import Parallax from "@/components/motion/Parallax";

export default function AboutStatementEditorial() {
  return (
    <section className="bg-{{bg}} py-28 px-8">
      <div className="container mx-auto max-w-5xl">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-16 items-start">

          {/* Portrait — spans 5 of 12 cols, no decorative flourishes */}
          <div className="md:col-span-5">
            <div className="relative aspect-[2/3] overflow-hidden">
              <Parallax className="absolute inset-0" distance={30}>
                <Image
                  src="{{portrait_image}}"
                  alt="{{headline}}"
                  fill
                  priority
                  className="object-cover grayscale"
                />
              </Parallax>
            </div>
          </div>

          {/* Statement — spans 7 of 12 cols */}
          <FadeUp className="md:col-span-7 md:pt-12">
            <p className="text-{{muted}} text-xs uppercase tracking-widest mb-6 font-sans">
              {{eyebrow}}
            </p>
            <h2 className="font-serif text-{{fg}} text-4xl md:text-5xl leading-tight mb-10 max-w-lg">
              <RevealWords>{{headline}}</RevealWords>
            </h2>

            {/* {{story_paragraphs_list_start}} */}
            <p className="text-{{fg}}/65 text-base leading-relaxed mb-6 font-sans">
              {{story_paragraphs[]}}
            </p>
            {/* {{story_paragraphs_list_end}} */}

            {/* Signature — ruled above, no decoration */}
            <div className="mt-12 pt-8 border-t border-{{fg}}/10">
              <p className="text-{{fg}}/50 text-sm font-sans tracking-wide italic">
                — {{signature}}
              </p>
            </div>
          </FadeUp>

        </div>
      </div>
    </section>
  );
}
