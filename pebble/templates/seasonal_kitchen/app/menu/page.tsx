import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { MenuList } from "@/components/sections/MenuList";

export default function MenuPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1 min-h-screen pt-24 px-6 bg-bone">
        <div className="max-w-4xl mx-auto mb-12">
          <h1 className="font-[family-name:var(--font-display)] text-5xl md:text-7xl italic mb-6">
            The Menu
          </h1>
          <p className="text-charcoal/70 max-w-2xl leading-relaxed">
            Seasonal produce, ethically sourced proteins, and a restrained hand. Filter by dietary preference.
          </p>
        </div>
        <MenuList />
      </main>
      <Footer />
    </>
  );
}
