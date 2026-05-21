import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Hero } from "@/components/sections/Hero";
import { Stats } from "@/components/sections/Stats";
import { Courses } from "@/components/sections/Courses";
import { Instructor } from "@/components/sections/Instructor";
import { Mission } from "@/components/sections/Mission";
import { Offer } from "@/components/sections/Offer";
import { Testimonials } from "@/components/sections/Testimonials";
import { Contact } from "@/components/sections/Contact";

export default function HomePage() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Stats />
        <Instructor />
        <Mission />
        <Offer />
        <Courses />
        <Testimonials />
        <Contact />
      </main>
      <Footer />
    </>
  );
}
