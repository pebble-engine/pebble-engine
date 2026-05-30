import Image from "next/image";

export default function AboutTeamClean() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-start">

          {/* Left — portrait */}
          <div className="relative">
            <div className="relative aspect-[4/5] overflow-hidden rounded-sm">
              <Image
                src="{{portrait_image}}"
                alt="{{headline}}"
                fill
                priority
                className="object-cover grayscale-[15%]"
              />
            </div>
            {/* Accent rule below portrait */}
            <div className="mt-5 h-px w-16 bg-sky-600" aria-hidden="true" />
          </div>

          {/* Right — credentials + prose */}
          <div className="md:pt-8">
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5">
              {{eyebrow}}
            </p>
            <h2 className="text-{{fg}} text-4xl md:text-5xl font-semibold leading-tight tracking-tight mb-8 max-w-sm">
              {{headline}}
            </h2>

            {/* {{story_paragraphs_list_start}} */}
            <p className="text-slate-600 text-base leading-relaxed mb-5">
              {{story_paragraphs[]}}
            </p>
            {/* {{story_paragraphs_list_end}} */}

            {/* Signature / credentials line */}
            <div className="mt-8 pt-6 border-t border-slate-200">
              <p className="text-{{fg}} text-sm font-semibold tracking-wide">
                {{signature}}
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
