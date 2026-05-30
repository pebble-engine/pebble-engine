export default function PricingTiersPlayful() {
  return (
    <section className="bg-pink-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="text-center mb-16">
          <p className="inline-flex items-center gap-2 bg-pink-500 text-white text-sm font-bold px-5 py-2 rounded-full mb-5 tracking-wide">
            {{eyebrow}}
          </p>
          <h2 className="text-purple-900 text-5xl md:text-6xl font-extrabold leading-tight max-w-2xl mx-auto">
            {{headline}}
          </h2>
        </div>

        {/* Tier cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">

          {/* {{tiers_list_start}} */}
          <div className="relative bg-white rounded-[2rem] p-8 flex flex-col gap-6 shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-200">
            {/* Name + price */}
            <div>
              <span className="text-pink-500 text-xs font-extrabold uppercase tracking-widest">
                {{tiers[].name}}
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-purple-900 text-5xl font-extrabold leading-none">
                  {{tiers[].price}}
                </span>
                <span className="text-purple-900/50 text-base">
                  {{tiers[].period}}
                </span>
              </div>
            </div>

            {/* Features */}
            <ul className="flex-1 space-y-3">
              {/* {{tiers[].features_list_start}} */}
              <li className="flex items-start gap-3 text-purple-900/75 text-base leading-snug">
                <span className="mt-0.5 text-amber-400 text-lg leading-none" aria-hidden="true">&#10003;</span>
                <span>{{tiers[].features[]}}</span>
              </li>
              {/* {{tiers[].features_list_end}} */}
            </ul>

            {/* CTA */}
            <a
              href="#book"
              className="mt-2 bg-pink-500 text-white px-10 py-5 rounded-full font-extrabold text-center shadow hover:scale-105 hover:rotate-1 hover:shadow-pink-300 transition-all duration-200"
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
