import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Hero } from "@/components/sections/Hero";
import { FeaturedStory } from "@/components/sections/FeaturedStory";
import { GalleryGrid } from "@/components/sections/GalleryGrid";
import { About } from "@/components/sections/About";
import { Packages } from "@/components/sections/Packages";
import { Process } from "@/components/sections/Process";
import { Testimonials } from "@/components/sections/Testimonials";
import { Inquiry } from "@/components/sections/Inquiry";

export default function HomePage() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        <Hero />
        <FeaturedStory />
        <GalleryGrid />
        <About />
        <Packages />
        <Process />
        <Testimonials />
        <Inquiry />
      </main>
      <Footer />
    </>
  );
}
