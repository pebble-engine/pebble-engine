import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { HomeHero } from "@/components/sections/HomeHero";
import { TrustStrip } from "@/components/sections/TrustStrip";
import { Services } from "@/components/sections/Services";
import { Process } from "@/components/sections/Process";
import { Testimonial } from "@/components/sections/Testimonial";

export default function HomePage() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        <HomeHero />
        <TrustStrip />
        <Services />
        <Process />
        <Testimonial />
      </main>
      <Footer />
    </>
  );
}
