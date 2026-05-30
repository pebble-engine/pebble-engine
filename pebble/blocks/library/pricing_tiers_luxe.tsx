export default function PricingLuxe() {
  return (
    <section className="bg-stone-50 py-32 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Section header */}
        <div className="text-center mb-20">
          <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-5 font-light">
            {{eyebrow}}
          </p>
          <h2 className="text-stone-700 text-5xl md:text-6xl font-light leading-tight max-w-xl mx-auto tracking-tight">
            {{headline}}
          </h2>
        </div>

        {/* Tier cards — clean outlines, no heavy fills */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">

          {/* {{tiers_list_start}} */}
          <div className="relative flex flex-col gap-8 rounded-2xl border border-stone-200 bg-white/60 p-8 hover:border-amber-600/40 transition-colors duration-300">
            {/* Tier name */}
            <div>
              <span className="text-amber-600 text-xs font-light uppercase tracking-[0.2em]">
                {{tiers[].name}}
              </span>
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-stone-700 text-4xl font-light leading-none tracking-tight">
                  {{tiers[].price}}
                </span>
                <span className="text-stone-400 text-sm font-light ml-1">
                  {{tiers[].period}}
                </span>
              </div>
            </div>

            {/* Thin rule */}
            <div className="w-full h-px bg-stone-200" aria-hidden="true" />

            {/* Feature list */}
            <ul className="flex-1 space-y-4">
              {/* {{tiers[].features_list_start}} */}
              <li className="flex items-start gap-3 text-stone-500 text-sm font-light leading-relaxed">
                <span className="mt-0.5 text-amber-600 text-xs leading-none" aria-hidden="true">—</span>
                <span>{{tiers[].features[]}}</span>
              </li>
              {/* {{tiers[].features_list_end}} */}
            </ul>

            {/* CTA — thin border, wide tracking */}
            <a
              href="#book"
              className="mt-auto inline-block text-center border border-stone-700 text-stone-700 px-8 py-3.5 rounded-full text-xs uppercase tracking-[0.2em] font-light hover:border-amber-600 hover:text-amber-600 transition-colors duration-300"
            >
              {{tiers[].cta}}
            </a>
          </div>
          {/* {{tiers_list_end}} */}

        </div>
      </div>
    </section>
  );
}
