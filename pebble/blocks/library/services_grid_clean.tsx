export default function ServicesGridClean() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-4">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-4xl md:text-5xl font-semibold leading-tight max-w-xl tracking-tight">
            {{headline}}
          </h2>
        </div>

        {/* Services grid — 3 columns, text-only cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-slate-200">
          {/* {{services_list_start}} */}
          <div className="bg-{{bg}} p-8 flex flex-col gap-4">
            <h3 className="text-{{fg}} text-lg font-semibold leading-snug">
              {{services[].title}}
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1">
              {{services[].body}}
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2"
            >
              Learn more &rarr;
            </a>
          </div>
          {/* {{services_list_end}} */}
        </div>

      </div>
    </section>
  );
}
