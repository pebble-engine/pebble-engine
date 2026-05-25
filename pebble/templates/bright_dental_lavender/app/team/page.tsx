import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { TeamGrid } from "@/components/sections/TeamGrid";

export default function TeamPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1 min-h-screen pt-28 bg-white">
        <div className="max-w-3xl mx-auto px-6 mb-4">
          <h1 className="font-[family-name:var(--font-display)] text-5xl font-bold text-navy mb-4">
            Meet the team
          </h1>
          <p className="text-slate-600 text-lg leading-relaxed">
            Licensed, experienced, and genuinely good listeners. No hard sell, just honest care for every age.
          </p>
        </div>
        <TeamGrid />
      </main>
      <Footer />
    </>
  );
}
