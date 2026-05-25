import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { ContactForm } from "@/components/forms/ContactForm";
import {
  CONTACT_HEADLINE,
  CONTACT_BODY,
  CONTACT_HOURS,
  PHONE,
  EMAIL,
  ADDRESS,
} from "@/content/site";

export default function ContactPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        <section className="py-24">
          <div className="max-w-5xl mx-auto px-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-16">
              {/* Left: form */}
              <div>
                <h1 className="font-bold text-[36px] text-[var(--color-text-primary)] mb-3">
                  {CONTACT_HEADLINE}
                </h1>
                <p className="text-[16px] text-[var(--color-text-secondary)] leading-relaxed mb-8">
                  {CONTACT_BODY}
                </p>
                <ContactForm />
              </div>

              {/* Right: contact info */}
              <div>
                <div className="bg-[var(--color-surface-2)] rounded-2xl p-8 border border-[var(--color-border)]">
                  <h2 className="font-bold text-[20px] text-[var(--color-text-primary)] mb-6">
                    Contact info
                  </h2>
                  <ul className="space-y-5">
                    <li>
                      <p className="text-[11px] font-bold uppercase tracking-widest text-[var(--color-text-secondary)] mb-1">
                        Phone
                      </p>
                      <p className="text-[15px] text-[var(--color-text-primary)]">{PHONE}</p>
                    </li>
                    <li>
                      <p className="text-[11px] font-bold uppercase tracking-widest text-[var(--color-text-secondary)] mb-1">
                        Email
                      </p>
                      <p className="text-[15px] text-[var(--color-text-primary)]">{EMAIL}</p>
                    </li>
                    <li>
                      <p className="text-[11px] font-bold uppercase tracking-widest text-[var(--color-text-secondary)] mb-1">
                        Address
                      </p>
                      <p className="text-[15px] text-[var(--color-text-primary)]">{ADDRESS}</p>
                    </li>
                    <li>
                      <p className="text-[11px] font-bold uppercase tracking-widest text-[var(--color-text-secondary)] mb-1">
                        Hours
                      </p>
                      <p className="text-[15px] text-[var(--color-text-primary)]">{CONTACT_HOURS}</p>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
