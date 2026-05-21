import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Instructor } from "@/components/sections/Instructor";
import { Mission } from "@/components/sections/Mission";
import { Stats } from "@/components/sections/Stats";
import { Contact } from "@/components/sections/Contact";

export default function AboutPage() {
  return (
    <>
      <Navbar />
      <main className="pt-20">
        <Instructor />
        <Mission />
        <Stats />
        <Contact />
      </main>
      <Footer />
    </>
  );
}
