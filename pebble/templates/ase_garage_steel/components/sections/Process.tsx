import { Reveal } from "@/components/ui/Reveal";
import { PROCESS_STEPS } from "@/content/site";

export function Process() {
  return (
    <section id="process" className="py-20 px-6 bg-[#fafaf9] border-y border-[#e7e5e4]">
      <div className="max-w-4xl mx-auto">
        <Reveal>
          <h2 className="font-[family-name:var(--font-display)] text-3xl text-center mb-16 uppercase tracking-tight">
            Drop &amp; Go Process
          </h2>
        </Reveal>
        <div className="grid md:grid-cols-3 gap-8 relative">
          <div className="absolute top-0 left-1/2 w-0.5 h-full bg-[#e7e5e4] hidden md:block" />
          {PROCESS_STEPS.map((step, i) => (
            <Reveal key={step.number} delay={0.1 * i}>
              <div className="relative text-center">
                <div className="w-12 h-12 bg-[#3b82f6] text-[#1e3a5f] font-[family-name:var(--font-display)] text-xl rounded-full flex items-center justify-center mx-auto mb-4">
                  {step.number}
                </div>
                <h3 className="font-bold text-xl mb-2 uppercase">{step.title}</h3>
                <p className="text-sm text-[#1e3a5f]/70 px-4">{step.body}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
