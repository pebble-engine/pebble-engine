import { Reveal } from "@/components/ui/Reveal";
import { PROCESS_HEADLINE, PROCESS_SUBLINE, PROCESS_STEPS } from "@/content/site";

export function ProcessSteps() {
  return (
    <section className="py-20 md:py-28 max-w-4xl mx-auto px-6">
      <Reveal>
        <header className="mb-16">
          <h1 className="font-[family-name:var(--font-display)] text-3xl md:text-5xl uppercase tracking-tight">
            {PROCESS_HEADLINE}
          </h1>
          <p className="mt-4 text-base md:text-lg text-[var(--color-text-secondary)] leading-relaxed max-w-2xl">
            {PROCESS_SUBLINE}
          </p>
        </header>
      </Reveal>

      <ol className="space-y-12 relative">
        {PROCESS_STEPS.map((step, i) => (
          <Reveal key={step.number} delay={i * 0.1}>
            <li className="grid grid-cols-[80px_1fr] md:grid-cols-[120px_1fr] gap-6 md:gap-10 items-start">
              <div className="font-[family-name:var(--font-display)] text-5xl md:text-7xl text-[var(--color-accent)] leading-none">
                {step.number}
              </div>
              <div>
                <h2 className="font-[family-name:var(--font-display)] text-xl md:text-2xl uppercase tracking-tight">
                  {step.title}
                </h2>
                <p className="mt-3 text-base text-[var(--color-text-secondary)] leading-relaxed max-w-prose">
                  {step.description}
                </p>
              </div>
            </li>
          </Reveal>
        ))}
      </ol>
    </section>
  );
}
