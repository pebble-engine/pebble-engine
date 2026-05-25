import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Hero } from "@/components/sections/Hero";
import { Services } from "@/components/sections/Services";
import { WhyUs } from "@/components/sections/WhyUs";
import { BeforeAfter } from "@/components/sections/BeforeAfter";
import { Process } from "@/components/sections/Process";
import { Reviews } from "@/components/sections/Reviews";
import { EstimateSection } from "@/components/sections/EstimateSection";
import { Location } from "@/components/sections/Location";

export default function HomePage() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        <Hero />
        <Services />
        <WhyUs />
        <BeforeAfter />
        <Process />
        <Reviews />
        <EstimateSection />
        <Location />
      </main>
      <Footer />
    </>
  );
}
