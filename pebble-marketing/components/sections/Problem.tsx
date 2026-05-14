import { FadeIn } from "@/components/ui/FadeIn";

export function Problem() {
  return (
    <section className="px-6 lg:px-12 py-section-mobile lg:py-section bg-sand">
      <div className="max-w-5xl mx-auto">
        <FadeIn duration={800}>
          <p className="brand-mono mb-6">The problem</p>
        </FadeIn>

        <FadeIn delay={200} duration={1000}>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-normal text-stone mb-10 max-w-3xl leading-tight">
            You&apos;ve been told you should have a website —
            and that you shouldn&apos;t try to make it yourself.
          </h2>
        </FadeIn>

        <FadeIn delay={400} duration={1000}>
          <div className="grid md:grid-cols-3 gap-8 mt-12">
            <div>
              <p className="brand-mono mb-3 text-stone/40">Squarespace · Wix</p>
              <p className="text-stone/80 leading-relaxed">
                Look generic. Everyone else also picks template 7. Your
                competitor across town has the same site you do.
              </p>
            </div>
            <div>
              <p className="brand-mono mb-3 text-stone/40">Lovable · Base44</p>
              <p className="text-stone/80 leading-relaxed">
                Made for coders. You&apos;re asked to write &quot;prompts&quot; and
                debug components. You bounce. The free tier runs out
                before you ship.
              </p>
            </div>
            <div>
              <p className="brand-mono mb-3 text-stone/40">Hiring a designer</p>
              <p className="text-stone/80 leading-relaxed">
                $5,000–$20,000 and three months. You don&apos;t have either.
                You also can&apos;t change a word without paying again.
              </p>
            </div>
          </div>
        </FadeIn>

        <FadeIn delay={600} duration={1000}>
          <p className="mt-16 text-xl md:text-2xl text-stone leading-relaxed max-w-2xl">
            <span className="editorial-accent">There&apos;s a quieter way.</span>
            {" "}One built for the rest of us.
          </p>
        </FadeIn>
      </div>
    </section>
  );
}
