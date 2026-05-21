import * as React from "react";
import { ContactForm } from "@/components/forms/ContactForm";
import { ScriptText } from "@/components/ui/ScriptText";
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
 * Contact — split-pane editorial contact section.
 * Left: address/hours/phone. Right: glass-card form.
 */
export function Contact() {
  return (
    <section
      aria-labelledby="contact-heading"
      className="bg-surface-container-low"
    >
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 md:gap-16 items-start">
          <div className="lg:col-span-5">
            <p className="text-label mb-3">{CONTACT_EYEBROW}</p>
            <h2 id="contact-heading" className="text-headline italic mb-2">
              {CONTACT_HEADLINE}
            </h2>
            <ScriptText className="text-3xl md:text-4xl block mb-6">
              we read every note
            </ScriptText>
            <p className="text-body-lg mb-10">{CONTACT_INTRO}</p>

            <dl className="space-y-6 text-sm">
              <div>
                <dt className="text-label mb-1">Visit</dt>
                <dd className="text-on-surface leading-relaxed">
                  {ADDRESS_LINE_1}
                  <br />
                  {ADDRESS_LINE_2}
                </dd>
              </div>
              <div>
                <dt className="text-label mb-1">Hours</dt>
                <dd className="text-on-surface">{HOURS}</dd>
              </div>
              <div>
                <dt className="text-label mb-1">Reach us</dt>
                <dd className="text-on-surface">
                  <a href={`mailto:${EMAIL}`} className="hover:text-primary transition-colors block">
                    {EMAIL}
                  </a>
                  <a href={`tel:${PHONE}`} className="hover:text-primary transition-colors block">
                    {PHONE}
                  </a>
                </dd>
              </div>
            </dl>
          </div>

          <div className="lg:col-span-7">
            <div className="glass-card-strong rounded-3xl p-8 md:p-10 vapor-shadow">
              <ContactForm />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
