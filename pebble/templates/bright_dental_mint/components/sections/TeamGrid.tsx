import Image from "next/image";
import { Reveal } from "@/components/ui/Reveal";
import { TEAM } from "@/content/site";

export function TeamGrid() {
  return (
    <section className="py-20 lg:py-28 px-6 bg-slate-50">
      <div className="max-w-7xl mx-auto">
        <Reveal>
          <div className="text-center mb-16">
            <h2 className="font-[family-name:var(--font-display)] text-3xl md:text-4xl font-bold text-navy mb-3">
              Meet the team
            </h2>
            <p className="text-slate-600 max-w-xl mx-auto leading-relaxed">
              Licensed, experienced, and genuinely good listeners. No hard sell, just honest care.
            </p>
          </div>
        </Reveal>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {TEAM.map((m, i) => (
            <Reveal key={m.name} delay={i * 0.08}>
              <div className="hover-lift bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden h-full">
                <div className="relative aspect-square w-full">
                  <Image
                    src={m.image}
                    alt={m.alt}
                    fill
                    sizes="(max-width: 768px) 100vw, 400px"
                    className="object-cover"
                  />
                </div>
                <div className="p-6">
                  <h3 className="font-[family-name:var(--font-display)] text-xl font-bold mb-1">{m.name}</h3>
                  <p className="text-slate-500 text-sm mb-2">{m.role}</p>
                  <p className="text-slate-600 text-sm">{m.bio}</p>
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
