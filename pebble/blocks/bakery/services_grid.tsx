import Image from "next/image";

export default function ServicesGrid() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-6xl">
        {/* Section header */}
        <div className="text-center mb-16">
          <p className="text-{{accent}} text-sm uppercase tracking-widest mb-3">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-5xl md:text-6xl font-bold leading-tight max-w-2xl mx-auto">
            {{headline}}
          </h2>
        </div>

        {/* Services grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* {{services_list_start}} */}
          <div className="group bg-{{bg}} rounded-3xl overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300">
            <div className="relative aspect-[4/3] overflow-hidden rounded-t-3xl">
              <Image
                src="{{services[].image}}"
                alt="{{services[].title}}"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            <div className="p-7">
              <h3 className="text-{{fg}} text-xl font-semibold mb-2 leading-snug">
                {{services[].title}}
              </h3>
              <p className="text-{{fg}}/70 text-base leading-relaxed mb-4">
                {{services[].body}}
              </p>
              <span className="text-{{accent}} text-sm font-semibold tracking-wide">
                {{services[].price}}
              </span>
            </div>
          </div>
          {/* {{services_list_end}} */}
        </div>
      </div>
    </section>
  );
}
