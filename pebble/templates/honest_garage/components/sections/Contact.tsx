import { ContactForm } from "@/components/forms/ContactForm";
import { RefCode } from "@/components/ui/RefCode";
import {
  EMAIL,
  ADDRESS,
  HOURS,
  PHONE,
  PHONE_DISPLAY,
} from "@/content/site";

/**
 * Two-column form-left / contact-info-right per the DNA's section_flow.contact
 * spec. The DNA mentions a grayscale-filtered Google Maps iframe — we omit it
 * by default because every customer needs a custom embed code; the right
 * column instead surfaces address + hours + phone + email in mono.
 */
export function Contact() {
  return (
    <section id="contact" className="relative py-20 sm:py-28 border-t border-white/5">
      <div className="mx-auto max-w-6xl px-6">
        <div className="grid gap-12 lg:grid-cols-5">
          {/* Form column */}
          <div className="lg:col-span-3 space-y-7">
            <div>
              <RefCode accent>// INQ-FORM-001</RefCode>
              <h2 className="mt-3 stencil text-5xl sm:text-6xl">GET AN ESTIMATE</h2>
              <p className="mt-3 text-base text-muted">
                Tell us what's going on. Written estimate within one business day. No
                obligation, no upsell.
              </p>
            </div>

            <div className="border border-white/10 bg-card/40 p-6 sm:p-8">
              <ContactForm />
            </div>
          </div>

          {/* Info column */}
          <div className="lg:col-span-2 space-y-7">
            <div>
              <RefCode accent>// SHOP-INFO-001</RefCode>
              <h3 className="mt-3 stencil-filled text-2xl">SHOP DETAILS</h3>
            </div>

            <ul className="space-y-5">
              <ContactRow label="PHONE">
                <a
                  href={`tel:${PHONE.replace(/[^+\d]/g, "")}`}
                  className="font-mono text-base text-fg/90 hover:text-primary transition-colors"
                >
                  {PHONE_DISPLAY}
                </a>
              </ContactRow>
              <ContactRow label="EMAIL">
                <a
                  href={`mailto:${EMAIL}`}
                  className="font-mono text-sm text-fg/90 hover:text-primary transition-colors break-all"
                >
                  {EMAIL}
                </a>
              </ContactRow>
              <ContactRow label="ADDRESS">
                <span className="font-mono text-sm uppercase tracking-[0.06em] text-fg/90">
                  {ADDRESS}
                </span>
              </ContactRow>
              <ContactRow label="HOURS">
                <span className="font-mono text-xs uppercase tracking-[0.06em] text-fg/90">
                  {HOURS}
                </span>
              </ContactRow>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

function ContactRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <li className="border-l-2 border-primary pl-4">
      <RefCode>{label}</RefCode>
      <div className="mt-1">{children}</div>
    </li>
  );
}
