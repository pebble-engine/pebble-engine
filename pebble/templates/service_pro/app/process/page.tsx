import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Process } from "@/components/sections/Process";
import { Contact } from "@/components/sections/Contact";

export default function ProcessPage() {
  return (
    <>
      <Navbar />
      <main className="pt-20">
        <Process />
        <Contact />
      </main>
      <Footer />
    </>
  );
}
