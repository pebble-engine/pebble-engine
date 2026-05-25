import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { ServiceArea } from "@/components/sections/ServiceArea";
import { Contact } from "@/components/sections/Contact";

export default function ServiceAreaPage() {
  return (
    <>
      <Navbar />
      <main className="pt-20">
        <ServiceArea />
        <Contact />
      </main>
      <Footer />
    </>
  );
}
