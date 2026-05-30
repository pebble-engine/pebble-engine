export default function PricingPrixFixe() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Section header */}
        <div className="text-center mb-16">
          <p className="text-{{accent}} text-sm uppercase tracking-widest font-sans mb-3">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} font-serif text-4xl md:text-5xl leading-tight max-w-xl mx-auto">
            {{headline}}
          </h2>
        </div>

        {/* Prix-fixe tier cards — warm parchment styling */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">

          {/* {{tiers_list_start}} */}
          <div className="relative bg-{{muted}}/30 rounded-3xl p-8 flex flex-col gap-6 border border-{{fg}}/10 hover:border-{{accent}}/40 transition-colors duration-200">
            {/* Tier name */}
            <div>
              <span className="text-{{accent}} font-sans text-xs font-semibold uppercase tracking-widest">
                {{tiers[].name}}
              </span>
              {/* Price */}
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-{{fg}} font-serif text-5xl leading-none">
                  {{tiers[].price}}
                </span>
                <span className="text-{{fg}}/50 font-sans text-sm">
                  {{tiers[].period}}
                </span>
              </div>
            </div>

            {/* Course / feature list */}
            <ul className="flex-1 space-y-3">
              {/* {{tiers[].features_list_start}} */}
              <li className="flex items-start gap-3 text-{{fg}}/75 font-sans text-sm leading-snug">
                <span className="mt-0.5 text-{{accent}} text-base leading-none" aria-hidden="true">✦</span>
                <span>{{tiers[].features[]}}</span>
              </li>
              {/* {{tiers[].features_list_end}} */}
            </ul>

            {/* CTA */}
            <a
              href="#reserve"
              className="mt-2 bg-{{accent}} text-stone-50 px-8 py-4 rounded-full font-sans font-semibold text-center hover:scale-105 hover:opacity-95 transition-transform duration-200"
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
