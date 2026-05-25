import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { FAQList } from "@/components/sections/FAQList";
import { CTABand } from "@/components/sections/CTABand";

export default function FAQPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        <FAQList />
        <CTABand />
      </main>
      <Footer />
    </>
  );
}
