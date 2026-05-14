import { FadeIn } from "@/components/ui/FadeIn";

const STEPS = [
  {
    n: "01",
    title: "Answer 8 questions",
    body:
      "What's your business? Who do you serve? What do you want visitors to do? It's a five-minute conversation, in plain English, no jargon. We never ask anything you don't know the answer to.",
  },
  {
    n: "02",
    title: "Preview your site",
    body:
      "Pebble generates a complete website — hero, services, contact form, the works. We pick the design personality. You see it on screen in about two minutes. If it doesn't feel right, you can regenerate or tweak it.",
  },
  {
    n: "03",
    title: "Click publish",
    body:
      "We host it for you at a Pebble subdomain (or your own custom domain, on Pro). The contact form actually sends you email. The whole thing is live and working in under ten minutes from start to finish.",
  },
];

export function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="px-6 lg:px-12 py-section-mobile lg:py-section bg-sand"
    >
      <div className="max-w-5xl mx-auto">
        <FadeIn duration={800}>
          <p className="brand-mono mb-6">How it works</p>
        </FadeIn>

        <FadeIn delay={200} duration={1000}>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-normal text-stone mb-16 max-w-3xl leading-tight">
            Three steps. About ten minutes.
          </h2>
        </FadeIn>

        <div className="grid md:grid-cols-3 gap-8 md:gap-12">
          {STEPS.map((step, i) => (
            <FadeIn key={step.n} delay={400 + i * 200} duration={1000}>
              <article>
                <p className="brand-mono text-river mb-4 text-base">{step.n}</p>
                <h3 className="text-xl md:text-2xl font-normal text-stone mb-3 leading-tight">
                  {step.title}
                </h3>
                <p className="text-stone/70 leading-relaxed">
                  {step.body}
                </p>
              </article>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
