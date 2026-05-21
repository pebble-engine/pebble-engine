import * as React from "react";
import { ContactForm } from "@/components/forms/ContactForm";
import { SectionDivider } from "@/components/ui/SectionDivider";
import {
  CONTACT_PILL,
  CONTACT_HEADLINE_LINE_1,
  CONTACT_HEADLINE_LINE_2,
  CONTACT_INTRO,
  ADDRESS_LINE_1,
  ADDRESS_LINE_2,
  EMAIL,
  PHONE,
  HOURS,
} from "@/content/site";

/**
 * Contact — centered "Confidential inquiries" pill border, gigantic
 * 2-line headline, intro line, then a 2-col form grid with a full-width
 * textarea and full-width vermilion "INITIATE INQUIRY" CTA.
 */
export function Contact() {
  return (
    <section
      aria-labelledby="contact-heading"
      className="bg-bg"
    >
      <div className="page-container">
        <SectionDivider index="04" label="Contact" />
      </div>

      <div className="page-container pb-section-mobile md:pb-section-desktop">
        <div className="max-w-3xl mx-auto text-center mb-12 md:mb-16">
          {/* Pill border */}
          <span className="inline-flex items-center px-4 py-2 border border-border text-eyebrow cinematic-radius mb-8">
            {CONTACT_PILL}
          </span>
          <h2 id="contact-heading" className="text-display mb-6">
            {CONTACT_HEADLINE_LINE_1}
            <br />
            <span className="text-accent">{CONTACT_HEADLINE_LINE_2}</span>
          </h2>
          <p className="text-body-lg max-w-2xl mx-auto">{CONTACT_INTRO}</p>
        </div>

        <div className="max-w-3xl mx-auto">
          <ContactForm />
        </div>

        {/* Quiet contact details strip beneath the form */}
        <dl className="max-w-3xl mx-auto mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 pt-10 border-t border-border">
          <div>
            <dt className="text-label mb-3">Visit</dt>
            <dd className="text-fg leading-relaxed text-sm not-italic">
              {ADDRESS_LINE_1}
              <br />
              {ADDRESS_LINE_2}
            </dd>
          </div>
          <div>
            <dt className="text-label mb-3">Hours</dt>
            <dd className="text-fg text-sm">{HOURS}</dd>
          </div>
          <div>
            <dt className="text-label mb-3">Reach us</dt>
            <dd className="text-fg text-sm">
              <a href={`mailto:${EMAIL}`} className="hover:text-accent transition-colors block">
                {EMAIL}
              </a>
              <a href={`tel:${PHONE}`} className="hover:text-accent transition-colors block">
                {PHONE}
              </a>
            </dd>
          </div>
        </dl>
      </div>
    </section>
  );
}
