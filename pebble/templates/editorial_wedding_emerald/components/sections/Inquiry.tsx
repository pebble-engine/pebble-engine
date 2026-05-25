import { Reveal } from "@/components/ui/Reveal";
import { InquiryForm } from "@/components/forms/InquiryForm";

export function Inquiry() {
  return (
    <section id="inquiry" className="py-24 px-6 bg-[#f5f0dc]/5">
      <div className="max-w-3xl mx-auto">
        <Reveal>
          <h2 className="font-[family-name:var(--font-display)] italic text-4xl md:text-5xl mb-12 text-center text-[#f5f0dc]">
            Begin your story
          </h2>
        </Reveal>
        <Reveal delay={0.1}>
          <InquiryForm />
        </Reveal>
      </div>
    </section>
  );
}
