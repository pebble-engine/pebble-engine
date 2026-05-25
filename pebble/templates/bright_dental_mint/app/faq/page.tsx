import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { FaqAccordion } from "@/components/sections/FaqAccordion";
import { InsuranceGrid } from "@/components/sections/InsuranceGrid";

export default function FaqPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1 min-h-screen pt-28 px-6 bg-white">
        <div className="max-w-3xl mx-auto mb-12">
          <h1 className="font-[family-name:var(--font-display)] text-5xl font-bold text-navy mb-4">
            Questions? Answers.
          </h1>
          <p className="text-slate-600 text-lg leading-relaxed">
            Plain language. No jargon. If we don&apos;t cover your situation, call us.
          </p>
        </div>
        <FaqAccordion />
        <InsuranceGrid />
      </main>
      <Footer />
    </>
  );
}
