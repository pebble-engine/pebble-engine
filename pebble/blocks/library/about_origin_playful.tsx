import Image from "next/image";

export default function AboutOriginPlayful() {
  return (
    <section className="bg-pink-50 py-24 px-8 overflow-hidden">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">

          {/* Portrait — left column with playful frame */}
          <div className="relative">
            <div className="relative aspect-[3/4] rounded-[2.5rem] overflow-hidden shadow-xl ring-4 ring-pink-300">
              <Image
                src="{{portrait_image}}"
                alt="{{headline}}"
                fill
                priority
                className="object-cover"
              />
            </div>
            {/* Floating accent blocks */}
            <div aria-hidden="true" className="absolute -bottom-6 -right-6 w-36 h-36 rounded-3xl bg-amber-300 -z-10" />
            <div aria-hidden="true" className="absolute -top-5 -left-5 w-20 h-20 rounded-2xl bg-pink-400 -z-10 rotate-6" />
          </div>

          {/* Prose — right column */}
          <div>
            <p className="inline-flex items-center gap-2 bg-pink-100 text-pink-600 text-sm font-bold px-5 py-2 rounded-full mb-6">
              {{eyebrow}}
            </p>
            <h2 className="text-purple-900 text-5xl md:text-6xl font-extrabold leading-tight mb-8 max-w-lg">
              {{headline}}
            </h2>

            {/* {{story_paragraphs_list_start}} */}
            <p className="text-purple-900/70 text-xl leading-relaxed mb-6">
              {{story_paragraphs[]}}
            </p>
            {/* {{story_paragraphs_list_end}} */}

            {/* Signature */}
            <div className="mt-10 pt-8 border-t-2 border-dashed border-pink-200">
              <p className="text-purple-900 text-base font-bold italic">
                — {{signature}}
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
