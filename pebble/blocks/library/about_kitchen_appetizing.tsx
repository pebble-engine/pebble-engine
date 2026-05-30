import Image from "next/image";

export default function AboutKitchen() {
  return (
    <section className="bg-{{bg}} py-24 px-8 overflow-hidden">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">

          {/* Kitchen / chef photograph — left */}
          <div className="relative">
            <div className="relative aspect-[3/4] rounded-3xl overflow-hidden">
              <Image
                src="{{portrait_image}}"
                alt="{{headline}}"
                fill
                priority
                className="object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-{{bg}}/40 to-transparent" />
            </div>
            {/* Warm amber accent block */}
            <div className="absolute -bottom-6 -right-6 w-40 h-40 rounded-3xl bg-{{accent}}/10 -z-10" />
          </div>

          {/* Story prose — right */}
          <div>
            <p className="text-{{accent}} text-sm uppercase tracking-widest font-sans mb-4">
              {{eyebrow}}
            </p>
            <h2 className="text-{{fg}} font-serif text-4xl md:text-5xl leading-tight mb-8 max-w-md">
              {{headline}}
            </h2>

            {/* {{story_paragraphs_list_start}} */}
            <p className="text-{{fg}}/70 font-sans text-lg leading-relaxed mb-6">
              {{story_paragraphs[]}}
            </p>
            {/* {{story_paragraphs_list_end}} */}

            {/* Signature */}
            <div className="mt-10 pt-8 border-t border-{{fg}}/10">
              <p className="text-{{fg}} font-serif text-base italic">
                — {{signature}}
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
