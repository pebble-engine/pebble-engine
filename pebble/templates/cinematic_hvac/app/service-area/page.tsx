import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { ServiceArea } from "@/components/sections/ServiceArea";
import { CTABand } from "@/components/sections/CTABand";

export default function ServiceAreaPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        <ServiceArea />
        <CTABand />
      </main>
      <Footer />
    </>
  );
}
