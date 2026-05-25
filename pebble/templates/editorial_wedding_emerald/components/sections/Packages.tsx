import { Reveal } from "@/components/ui/Reveal";
import { PACKAGES } from "@/content/site";

export function Packages() {
  return (
    <section id="packages" className="py-24 px-6 bg-[#0a2820] border-t border-[#f5f0dc]/10">
      <div className="max-w-7xl mx-auto">
        <Reveal>
          <h2 className="font-[family-name:var(--font-display)] italic text-4xl md:text-5xl mb-16 text-center text-[#f5f0dc]">
            Collections
          </h2>
        </Reveal>
        <div className="grid md:grid-cols-3 gap-8">
          {PACKAGES.map((pkg, i) => (
            <Reveal key={pkg.title} delay={i * 0.08}>
              <div
                className={`p-8 rounded-sm transition-colors h-full flex flex-col ${
                  pkg.popular
                    ? "border border-[#c9a96e] bg-[#c9a96e]/10 shadow-[0_8px_30px_-8px_rgba(201,169,110,0.35)]"
                    : "border border-[#f5f0dc]/20 hover:border-[#c9a96e] bg-[#0a2820]/50"
                }`}
              >
                {pkg.popular && (
                  <div className="text-center mb-4">
                    <span className="bg-[#c9a96e] text-[#0a2820] text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide">
                      Most Popular
                    </span>
                  </div>
                )}
                <p className={`font-[family-name:var(--font-display)] italic text-2xl mb-2 ${pkg.popular ? "text-[#f5f0dc]" : "text-[#c9a96e]"}`}>
                  {pkg.title}
                </p>
                <p className="text-4xl font-bold text-[#f5f0dc] mb-4 tracking-tight">{pkg.price}</p>
                <p className="text-[#f5f0dc]/60 text-sm mb-6">{pkg.duration}</p>
                <ul className="space-y-3 text-[#f5f0dc]/80 text-sm mb-8 flex-1">
                  {pkg.features.map((f) => (
                    <li key={f} className="flex items-start gap-2">
                      <span className={`${pkg.popular ? "text-[#f5f0dc]" : "text-[#c9a96e]"} mt-1`}>✦</span>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
                <a href="#inquiry" className="btn-brass w-full text-center text-sm">
                  Reserve this date
                </a>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
