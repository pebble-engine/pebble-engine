import Image from "next/image";

export default function AboutOriginBold() {
  return (
    <section className="bg-{{bg}} py-24 px-8 overflow-hidden">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">

          {/* Left — raw portrait with hard-edge lime accent block */}
          <div className="relative">
            <div className="relative aspect-[3/4] overflow-hidden rounded-md">
              <Image
                src="{{portrait_image}}"
                alt="{{headline}}"
                fill
                priority
                className="object-cover brightness-90"
              />
              {/* Hard lime corner accent — bottom-left */}
              <div className="absolute bottom-0 left-0 w-1 h-24 bg-{{accent}}" />
              <div className="absolute bottom-0 left-0 h-1 w-24 bg-{{accent}}" />
            </div>
            {/* Oversized bg number / decorative element */}
            <div
              aria-hidden="true"
              className="absolute -bottom-8 -right-4 text-{{fg}}/5 text-[12rem] font-black leading-none select-none pointer-events-none"
            >
              01
            </div>
          </div>

          {/* Right — story prose */}
          <div>
            <p className="text-{{accent}} text-xs font-black uppercase tracking-[0.3em] mb-6">
              {{eyebrow}}
            </p>
            <h2 className="text-{{fg}} text-5xl md:text-7xl font-black uppercase leading-none mb-10 max-w-lg">
              {{headline}}
            </h2>

            {/* {{story_paragraphs_list_start}} */}
            <p className="text-{{fg}}/70 text-base md:text-lg leading-relaxed mb-5">
              {{story_paragraphs[]}}
            </p>
            {/* {{story_paragraphs_list_end}} */}

            {/* Signature — hard rule above */}
            <div className="mt-10 pt-6 border-t-2 border-{{accent}}/40">
              <p className="text-{{fg}} text-sm font-black uppercase tracking-widest">
                — {{signature}}
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
