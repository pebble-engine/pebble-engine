import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { HomeHero } from "@/components/sections/HomeHero";
import { Story } from "@/components/sections/Story";
import { Gallery } from "@/components/sections/Gallery";
import { Location } from "@/components/sections/Location";

export default function HomePage() {
  return (
    <>
      <Navbar transparent />
      <main className="flex-1">
        <HomeHero />
        <Story />
        <Gallery />
        <Location />
      </main>
      <Footer />
    </>
  );
}
