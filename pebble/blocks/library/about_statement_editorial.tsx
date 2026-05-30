import Image from "next/image";

export default function AboutStatementEditorial() {
  return (
    <section className="bg-{{bg}} py-28 px-8">
      <div className="container mx-auto max-w-5xl">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-16 items-start">

          {/* Portrait — spans 5 of 12 cols, no decorative flourishes */}
          <div className="md:col-span-5">
            <div className="relative aspect-[2/3] overflow-hidden">
              <Image
                src="{{portrait_image}}"
                alt="{{headline}}"
                fill
                priority
                className="object-cover grayscale"
              />
            </div>
          </div>

          {/* Statement — spans 7 of 12 cols */}
          <div className="md:col-span-7 md:pt-12">
            <p className="text-{{muted}} text-xs uppercase tracking-widest mb-6 font-sans">
              {{eyebrow}}
            </p>
            <h2 className="font-serif text-{{fg}} text-4xl md:text-5xl leading-tight mb-10 max-w-lg">
              {{headline}}
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
          </div>

        </div>
      </div>
    </section>
  );
}
