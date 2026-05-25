import { Reveal } from "@/components/ui/Reveal";
import { TRUST_POINTS } from "@/content/site";

export function WhyUs() {
  return (
    <section id="why-us" className="py-20 px-6 bg-[#e7e5e4]/30">
      <div className="max-w-7xl mx-auto">
        <Reveal>
          <h2 className="font-[family-name:var(--font-display)] text-3xl text-center mb-12 uppercase tracking-tight">
            Why Locals Drop Here
          </h2>
        </Reveal>
        <div className="grid md:grid-cols-4 gap-6">
          {TRUST_POINTS.map((tp, i) => (
            <Reveal key={tp.title} delay={0.05 * i}>
              <div className="p-6 bg-[#fafaf9] border-b-4 border-[#1e3a5f] shadow-sm h-full">
                <p className="text-[#3b82f6] font-[family-name:var(--font-display)] text-4xl mb-2">
                  {tp.number}
                </p>
                <h3 className="font-bold text-lg mb-2">{tp.title}</h3>
                <p className="text-sm text-[#1e3a5f]/70 leading-relaxed">{tp.body}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
