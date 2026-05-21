import { Hero } from "@/components/sections/Hero";
import { GalleryStrip } from "@/components/sections/GalleryStrip";
import { Services } from "@/components/sections/Services";
import { About } from "@/components/sections/About";
import { Testimonials } from "@/components/sections/Testimonials";
import { BookingCta } from "@/components/sections/BookingCta";
import { GoldWavyDivider } from "@/components/ui/GoldWavyDivider";

export default function HomePage() {
  return (
    <>
      <Hero />
      <GoldWavyDivider />
      <GalleryStrip />
      <Services />
      <GoldWavyDivider />
      <About />
      <Testimonials />
      <BookingCta />
    </>
  );
}
