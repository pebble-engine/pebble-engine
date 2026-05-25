import { Reveal } from "@/components/ui/Reveal";
import { PROCESS_STEPS } from "@/content/site";

export function Process() {
  return (
    <section id="process" className="py-20 lg:py-28 px-6 bg-white">
      <div className="max-w-7xl mx-auto">
        <Reveal>
          <div className="text-center mb-16">
            <h2 className="font-[family-name:var(--font-display)] text-3xl md:text-4xl font-bold text-navy mb-3">
              How it works
            </h2>
            <p className="text-slate-600">Three simple steps. No surprises. No pressure.</p>
          </div>
        </Reveal>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 relative">
          {PROCESS_STEPS.map((step, i) => (
            <Reveal key={step.step} delay={i * 0.08}>
              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 bg-ice rounded-full flex items-center justify-center mb-6 text-navy font-[family-name:var(--font-display)] text-2xl font-bold">
                  {step.step}
                </div>
                <h3 className="font-[family-name:var(--font-display)] text-xl font-bold mb-2">{step.title}</h3>
                <p className="text-slate-600 max-w-xs">{step.body}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
