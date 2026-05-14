import { FadeIn } from "@/components/ui/FadeIn";

const TIERS = [
  {
    name: "Free trial",
    price: "$0",
    cadence: "for 7 days",
    bullets: [
      "1 site",
      "Pebble subdomain",
      "No credit card needed",
      "All design personalities",
    ],
    accent: false,
  },
  {
    name: "Starter",
    price: "$29",
    cadence: "per month",
    bullets: [
      "1 site, always live",
      "Pebble subdomain",
      "Contact form delivery",
      "Edit anytime",
      "Email support",
    ],
    accent: false,
  },
  {
    name: "Pro",
    price: "$59",
    cadence: "per month",
    bullets: [
      "Up to 3 sites",
      "Custom domain",
      "Priority support",
      "Advanced design controls",
      "Visual editor (when it ships)",
    ],
    accent: true,
  },
];

export function Pricing() {
  return (
    <section
      id="pricing"
      className="px-6 lg:px-12 py-section-mobile lg:py-section bg-sand"
    >
      <div className="max-w-5xl mx-auto">
        <FadeIn duration={800}>
          <p className="brand-mono mb-6">Pricing</p>
        </FadeIn>

        <FadeIn delay={200} duration={1000}>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-normal text-stone mb-4 max-w-3xl leading-tight">
            Simple, honest pricing.
          </h2>
          <p className="text-stone/70 max-w-2xl mb-16 leading-relaxed text-lg">
            Start free. Pay only when you publish. Cancel any time —
            and your code stays yours forever.
          </p>
        </FadeIn>

        <div className="grid md:grid-cols-3 gap-6">
          {TIERS.map((tier, i) => (
            <FadeIn key={tier.name} delay={400 + i * 150} duration={1000}>
              <article
                className={
                  tier.accent
                    ? "rounded-card border-2 border-river p-8 bg-sand"
                    : "rounded-card border border-mist p-8 bg-sand"
                }
              >
                <p className="brand-mono mb-3">{tier.name}</p>
                <p className="mb-1">
                  <span className="text-4xl font-normal text-stone">{tier.price}</span>
                  <span className="text-stone/50 ml-2 text-sm">{tier.cadence}</span>
                </p>
                <ul className="mt-6 space-y-2.5">
                  {tier.bullets.map((b) => (
                    <li key={b} className="text-stone/75 text-sm leading-relaxed">
                      — {b}
                    </li>
                  ))}
                </ul>
              </article>
            </FadeIn>
          ))}
        </div>

        <FadeIn delay={900} duration={1000}>
          <div className="mt-10 rounded-card border border-mist p-6 max-w-2xl mx-auto text-center bg-sand">
            <p className="brand-mono mb-2 text-spark">Optional add-on</p>
            <p className="text-stone leading-relaxed">
              <span className="font-medium">$99 one-time</span> for a 30-minute
              setup call. We walk you through your first site, answer questions,
              get you live before we hang up.
            </p>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
