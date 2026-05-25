import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { GalleryGrid } from "@/components/sections/GalleryGrid";
import { CTABand } from "@/components/sections/CTABand";

export default function GalleryPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        <GalleryGrid />
        <CTABand />
      </main>
      <Footer />
    </>
  );
}
