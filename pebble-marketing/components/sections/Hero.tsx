import { AnimatedHeading } from "@/components/ui/AnimatedHeading";
import { FadeIn } from "@/components/ui/FadeIn";
import { WaitlistForm } from "@/components/forms/WaitlistForm";

export function Hero() {
  return (
    <section
      id="waitlist"
      className="
        relative
        min-h-[100dvh]
        flex flex-col justify-center
        px-6 lg:px-12
        pt-32 pb-20
        bg-sand
      "
    >
      <div className="max-w-5xl mx-auto w-full">
        {/* POWERED BY — small brand mono tag */}
        <FadeIn delay={0} duration={600}>
          <p className="brand-mono mb-6">
            Pebble · Early Access · 2026
          </p>
        </FadeIn>

        {/* Headline */}
        <AnimatedHeading
          text={"Beautiful websites,\nmade easy."}
          className="
            text-5xl md:text-6xl lg:text-7xl xl:text-8xl
            font-normal text-stone
            mb-6
          "
        />

        {/* Subhead */}
        <FadeIn delay={900} duration={1000}>
          <p
            className="
              text-lg md:text-xl lg:text-2xl
              text-stone/70
              max-w-2xl
              mb-10
              font-normal
              leading-relaxed
            "
          >
            Pebble makes building a beautiful website feel easy
            — so anyone can turn an idea into a real, working site.
          </p>
        </FadeIn>

        {/* Waitlist form */}
        <FadeIn delay={1300} duration={1000}>
          <WaitlistForm />
        </FadeIn>

        {/* Editorial accent line */}
        <FadeIn delay={1700} duration={1000}>
          <p className="
            mt-12 max-w-xl text-stone/60 text-base leading-relaxed
          ">
            <span className="editorial-accent text-xl">No coding.</span>
            {" "}
            No templates. No subscription you can&apos;t get out of.
            Answer 8 questions, and we hand you a beautiful site
            you fully own.
          </p>
        </FadeIn>

        {/* Brand soul-line — from the brand book.
            "If you can dream it, you can hold it." */}
        <FadeIn delay={2100} duration={1200}>
          <p className="mt-16 max-w-xl">
            <span className="editorial-accent text-2xl md:text-3xl">
              If you can dream it, you can hold it.
            </span>
          </p>
        </FadeIn>
      </div>
    </section>
  );
}
