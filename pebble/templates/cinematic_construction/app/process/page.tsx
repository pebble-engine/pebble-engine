import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { ProcessSteps } from "@/components/sections/ProcessSteps";
import { CTABand } from "@/components/sections/CTABand";

export default function ProcessPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        <ProcessSteps />
        <CTABand />
      </main>
      <Footer />
    </>
  );
}
