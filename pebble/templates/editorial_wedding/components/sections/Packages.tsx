import { Reveal } from "@/components/ui/Reveal";
import { PACKAGES } from "@/content/site";

export function Packages() {
  return (
    <section id="packages" className="py-24 px-6 bg-[#0a0a0a] border-t border-[#f5f1e8]/10">
      <div className="max-w-7xl mx-auto">
        <Reveal>
          <h2 className="font-[family-name:var(--font-display)] italic text-4xl md:text-5xl mb-16 text-center text-[#f5f1e8]">
            Collections
          </h2>
        </Reveal>
        <div className="grid md:grid-cols-3 gap-8">
          {PACKAGES.map((pkg, i) => (
            <Reveal key={pkg.title} delay={i * 0.08}>
              <div
                className={`p-8 rounded-sm transition-colors h-full flex flex-col ${
                  pkg.popular
                    ? "border border-[#b08d57] bg-[#b08d57]/10 shadow-[0_8px_30px_-8px_rgba(176,141,87,0.35)]"
                    : "border border-[#f5f1e8]/20 hover:border-[#b08d57] bg-[#0a0a0a]/50"
                }`}
              >
                {pkg.popular && (
                  <div className="text-center mb-4">
                    <span className="bg-[#b08d57] text-[#0a0a0a] text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide">
                      Most Popular
                    </span>
                  </div>
                )}
                <p className={`font-[family-name:var(--font-display)] italic text-2xl mb-2 ${pkg.popular ? "text-[#f5f1e8]" : "text-[#b08d57]"}`}>
                  {pkg.title}
                </p>
                <p className="text-4xl font-bold text-[#f5f1e8] mb-4 tracking-tight">{pkg.price}</p>
                <p className="text-[#f5f1e8]/60 text-sm mb-6">{pkg.duration}</p>
                <ul className="space-y-3 text-[#f5f1e8]/80 text-sm mb-8 flex-1">
                  {pkg.features.map((f) => (
                    <li key={f} className="flex items-start gap-2">
                      <span className={`${pkg.popular ? "text-[#f5f1e8]" : "text-[#b08d57]"} mt-1`}>✦</span>
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
