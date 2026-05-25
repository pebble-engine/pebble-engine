import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Gallery } from "@/components/sections/Gallery";
import { Contact } from "@/components/sections/Contact";

export default function GalleryPage() {
  return (
    <>
      <Navbar />
      <main className="pt-20">
        <Gallery />
        <Contact />
      </main>
      <Footer />
    </>
  );
}
