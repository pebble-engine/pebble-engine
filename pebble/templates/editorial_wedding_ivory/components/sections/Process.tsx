import { Reveal } from "@/components/ui/Reveal";
import { PROCESS_STEPS } from "@/content/site";

export function Process() {
  return (
    <section className="py-24 px-6 bg-[#1f1a14]/5">
      <div className="max-w-5xl mx-auto">
        <Reveal>
          <h2 className="font-[family-name:var(--font-display)] italic text-4xl mb-12 text-center text-[#1f1a14]">
            How we begin
          </h2>
        </Reveal>
        <div className="grid md:grid-cols-4 gap-8 relative">
          <div className="absolute top-0 left-1/2 w-px h-full bg-[#a47236]/20 hidden md:block" />
          {PROCESS_STEPS.map((step, i) => (
            <Reveal key={step.number} delay={i * 0.1}>
              <div className="relative text-center md:text-left">
                <span className="text-[#a47236] font-[family-name:var(--font-display)] italic text-5xl mb-2 block">
                  {step.number}
                </span>
                <h3 className="font-medium text-[#1f1a14] text-lg mb-2">{step.title}</h3>
                <p className="text-[#1f1a14]/60 text-sm leading-relaxed">{step.body}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
