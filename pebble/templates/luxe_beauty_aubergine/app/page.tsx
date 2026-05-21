import { Hero } from "@/components/sections/Hero";
import { ValuePillars } from "@/components/sections/ValuePillars";
import { CategoryGrid } from "@/components/sections/CategoryGrid";
import { FeaturedCollection } from "@/components/sections/FeaturedCollection";
import { Editorial } from "@/components/sections/Editorial";
import { Testimonials } from "@/components/sections/Testimonials";
import { Contact } from "@/components/sections/Contact";

export default function HomePage() {
  return (
    <>
      <Hero />
      <ValuePillars />
      <CategoryGrid />
      <FeaturedCollection />
      <Editorial />
      <Testimonials />
      <Contact />
    </>
  );
}
