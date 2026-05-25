import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { FAQList } from "@/components/sections/FAQList";
import { Contact } from "@/components/sections/Contact";

export default function FAQPage() {
  return (
    <>
      <Navbar />
      <main className="pt-20">
        <FAQList />
        <Contact />
      </main>
      <Footer />
    </>
  );
}
