import { EstimateForm } from "@/components/forms/EstimateForm";

export function EstimateSection() {
  return (
    <section id="estimate" className="py-20 px-6 bg-[#1e293b]">
      <div className="max-w-3xl mx-auto bg-[#e7e5e4]/10 p-8 md:p-12 border-2 border-[#facc15]/30 rounded-sm">
        <h2 className="font-[family-name:var(--font-display)] text-3xl md:text-4xl text-[#fafaf9] uppercase text-center mb-8">
          [Get An Honest Estimate]
        </h2>
        <EstimateForm />
      </div>
    </section>
  );
}
