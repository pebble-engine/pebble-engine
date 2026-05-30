import Image from "next/image";

export default function AboutEthos() {
  return (
    <section className="bg-stone-50 py-32 px-8 overflow-hidden">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-20 items-start">

          {/* Left — prose, floated top */}
          <div className="md:pt-8">
            <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-8 font-light">
              {{eyebrow}}
            </p>
            <h2 className="text-stone-700 text-5xl md:text-6xl font-light leading-[1.1] tracking-tight mb-10 max-w-lg">
              {{headline}}
            </h2>

            {/* {{story_paragraphs_list_start}} */}
            <p className="text-stone-500 text-lg font-light leading-relaxed mb-6">
              {{story_paragraphs[]}}
            </p>
            {/* {{story_paragraphs_list_end}} */}

            {/* Signature — thin rule above */}
            <div className="mt-12 pt-8 border-t border-stone-200">
              <p className="text-stone-600 text-base font-light italic tracking-wide">
                — {{signature}}
              </p>
            </div>
          </div>

          {/* Right — portrait, accent accent block behind it */}
          <div className="relative">
            <div className="relative aspect-[3/4] rounded-2xl overflow-hidden">
              <Image
                src="{{portrait_image}}"
                alt="{{headline}}"
                fill
                priority
                className="object-cover"
              />
              {/* Soft cream gradient at base — doesn't crush the image */}
              <div className="absolute inset-0 bg-gradient-to-t from-stone-50/20 to-transparent" />
            </div>
            {/* Decorative accent square — floated behind */}
            <div className="absolute -bottom-8 -left-8 w-40 h-40 rounded-2xl bg-amber-600/8 -z-10" />
            <div className="absolute -top-4 -right-4 w-24 h-24 rounded-full bg-rose-200/30 -z-10" />
          </div>

        </div>
      </div>
    </section>
  );
}
