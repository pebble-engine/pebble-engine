import { Navbar } from "@/components/layout/Navbar";
import { Hero } from "@/components/sections/Hero";
import { Problem } from "@/components/sections/Problem";
import { Promise as PromiseSection } from "@/components/sections/Promise";
import { HowItWorks } from "@/components/sections/HowItWorks";
import { Pricing } from "@/components/sections/Pricing";
import { Footer } from "@/components/sections/Footer";

export default function HomePage() {
  return (
    <main className="bg-sand text-stone">
      <Navbar />
      <Hero />
      <Problem />
      <PromiseSection />
      <HowItWorks />
      <Pricing />
      <Footer />
    </main>
  );
}
