import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Courses } from "@/components/sections/Courses";
import { Offer } from "@/components/sections/Offer";
import { Contact } from "@/components/sections/Contact";

export default function CoursesPage() {
  return (
    <>
      <Navbar />
      <main className="pt-20">
        <Courses />
        <Offer />
        <Contact />
      </main>
      <Footer />
    </>
  );
}
