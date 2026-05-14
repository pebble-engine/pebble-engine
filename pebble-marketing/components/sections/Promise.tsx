import { FadeIn } from "@/components/ui/FadeIn";

const PROMISES = [
  {
    label: "Different every time",
    title: "Your site won't look like anyone else's.",
    body:
      "Pebble has 10 design personalities — and growing. Two business owners can answer the same questions and get sites that look like they came from two different design studios. No templates. No clones.",
  },
  {
    label: "You own everything",
    title: "Every line of code is yours from day one.",
    body:
      "Pebble doesn't hold your site hostage. If you ever want to leave, you walk out with the whole project — code, content, even the domain. We build the site for you; we don't lock you in to keep it.",
  },
  {
    label: "No credit games",
    title: "No \"you've used your 5 messages today.\"",
    body:
      "Other AI tools throttle you to 25 generations a month or 5 a day. Pebble doesn't play that game. You sign up, you build, you publish. The price is the price.",
  },
];

export function Promise() {
  return (
    <section className="px-6 lg:px-12 py-section-mobile lg:py-section bg-sand">
      <div className="max-w-5xl mx-auto">
        <FadeIn duration={800}>
          <p className="brand-mono mb-6">The promise</p>
        </FadeIn>

        <FadeIn delay={200} duration={1000}>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-normal text-stone mb-16 max-w-3xl leading-tight">
            Three things make Pebble different.
          </h2>
        </FadeIn>

        <div className="space-y-16">
          {PROMISES.map((p, i) => (
            <FadeIn key={p.label} delay={400 + i * 200} duration={1000}>
              <article className="grid md:grid-cols-[180px_1fr] gap-6 md:gap-12">
                <div>
                  <p className="brand-mono">{p.label}</p>
                </div>
                <div>
                  <h3 className="text-2xl md:text-3xl font-normal text-stone mb-3 leading-tight">
                    {p.title}
                  </h3>
                  <p className="text-stone/70 leading-relaxed text-lg max-w-2xl">
                    {p.body}
                  </p>
                </div>
              </article>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
