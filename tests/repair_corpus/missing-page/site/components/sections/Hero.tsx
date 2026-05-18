import { AnimatedHeading } from "@/components/ui/AnimatedHeading";
import { FadeIn } from "@/components/ui/FadeIn";

export function Hero() {
  return (
    <section className="relative min-h-[100dvh] md:min-h-screen lg:min-h-[100dvh] overflow-hidden"
      style={{ background: "var(--color-bg)" }}>
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full blur-3xl opacity-20"
          style={{ background: "var(--color-accent-glow)" }} />
      </div>
      <AnimatedHeading text="Heron Plumbing" className="text-7xl text-white" />
      <FadeIn delay={800}><p>Expert plumbing services.</p></FadeIn>
      <a href="/contact" className="bg-white text-black px-6 py-3 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white">Get Started</a>
    </section>
  );
}
