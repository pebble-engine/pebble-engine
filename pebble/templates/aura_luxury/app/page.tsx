import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Hero } from "@/components/sections/Hero";
import { TransformationSlider } from "@/components/sections/TransformationSlider";
import { ServiceBento } from "@/components/sections/ServiceBento";
import { Philosophy } from "@/components/sections/Philosophy";
import { ContactForm } from "@/components/forms/ContactForm";

export default function HomePage() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        <Hero />
        <TransformationSlider />
        <ServiceBento />
        <Philosophy />

        {/* Inquiry section */}
        <section id="contact" className="py-24 px-6 sm:px-12 md:px-20 bg-[#0F1115] border-t border-white/5">
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-12">
              <div className="text-[10px] tracking-[0.25em] text-slate-400 uppercase font-sans mb-4">
                Direct Inquiry
              </div>
              <h2 className="text-3xl sm:text-4xl font-serif text-white">
                Request a Private Consultation
              </h2>
              <p className="text-sm text-slate-400 font-light leading-relaxed mt-3">
                Tell us about your space. Our concierge responds in under 15 minutes during business hours.
              </p>
            </div>
            <ContactForm />
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
