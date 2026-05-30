import Image from "next/image";

export default function MenuGrid() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-{{accent}} text-sm uppercase tracking-widest font-sans mb-3">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} font-serif text-4xl md:text-6xl leading-tight max-w-xl">
            {{headline}}
          </h2>
        </div>

        {/* Menu items grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
          {/* {{services_list_start}} */}
          <article className="group flex flex-col">
            {/* Food photograph */}
            <div className="relative aspect-[4/3] rounded-2xl overflow-hidden mb-5">
              <Image
                src="{{services[].image}}"
                alt="{{services[].title}}"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            {/* Menu caption */}
            <div className="flex items-baseline justify-between mb-2">
              <h3 className="text-{{fg}} font-serif text-xl leading-snug italic">
                {{services[].title}}
              </h3>
              <span className="text-{{accent}} font-sans text-sm font-semibold ml-4 flex-shrink-0">
                {{services[].price}}
              </span>
            </div>
            <p className="text-{{fg}}/65 font-sans text-base leading-relaxed">
              {{services[].body}}
            </p>
          </article>
          {/* {{services_list_end}} */}
        </div>

      </div>
    </section>
  );
}
