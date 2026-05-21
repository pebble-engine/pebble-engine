import * as React from "react";
import { ContactForm } from "@/components/forms/ContactForm";
import {
  CONTACT_EYEBROW,
  CONTACT_HEADLINE,
  CONTACT_INTRO,
  ADDRESS_LINE_1,
  ADDRESS_LINE_2,
  EMAIL,
  PHONE,
  HOURS,
} from "@/content/site";

/**
 * Contact — split-pane section. Left: address/hours/email. Right: dark card
 * with the booking inquiry form.
 */
export function Contact() {
  return (
    <section
      aria-labelledby="contact-heading"
      className="bg-ink-bg"
    >
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 md:gap-16 items-start">
          <div className="lg:col-span-5">
            <p className="text-eyebrow mb-4">{CONTACT_EYEBROW}</p>
            <h2 id="contact-heading" className="text-headline mb-6">
              {CONTACT_HEADLINE}
            </h2>
            <p className="text-body-lg mb-10">{CONTACT_INTRO}</p>

            <dl className="space-y-6 text-sm">
              <div>
                <dt className="text-label mb-2">Visit</dt>
                <dd className="text-ink-fg leading-relaxed">
                  {ADDRESS_LINE_1}
                  <br />
                  {ADDRESS_LINE_2}
                </dd>
              </div>
              <div>
                <dt className="text-label mb-2">Hours</dt>
                <dd className="text-ink-fg">{HOURS}</dd>
              </div>
              <div>
                <dt className="text-label mb-2">Reach us</dt>
                <dd className="text-ink-fg">
                  <a
                    href={`mailto:${EMAIL}`}
                    className="hover:text-ink-primary transition-colors block"
                  >
                    {EMAIL}
                  </a>
                  <a
                    href={`tel:${PHONE}`}
                    className="hover:text-ink-primary transition-colors block"
                  >
                    {PHONE}
                  </a>
                </dd>
              </div>
            </dl>
          </div>

          <div className="lg:col-span-7">
            <div className="border border-ink-border bg-ink-card p-8 md:p-10">
              <ContactForm />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
