import { Reveal } from "@/components/ui/Reveal";
import { SERVICES } from "@/content/site";

export function Services() {
  return (
    <section id="services" className="bg-[#fafaf9] border-b border-[#e7e5e4] py-12 overflow-x-auto">
      <div className="max-w-7xl mx-auto px-6 min-w-[768px]">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {SERVICES.map((svc, i) => (
            <Reveal key={svc.name} delay={0.03 * i}>
              <div className="group p-4 bg-[#e7e5e4]/50 hover:bg-[#d97444] hover:text-[#2a1810] transition-colors cursor-default border-2 border-transparent hover:border-[#2a1810] rounded-sm relative h-full">
                <p className="font-[family-name:var(--font-display)] text-lg uppercase leading-tight mb-1">
                  {svc.name}
                </p>
                <p className="text-xs uppercase tracking-wider opacity-0 group-hover:opacity-100 h-0 group-hover:h-auto transition-all font-bold">
                  {svc.price}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
