import * as React from "react";
import { ContactForm } from "@/components/forms/ContactForm";
import { EyebrowChip } from "@/components/ui/EyebrowChip";
import {
  CONTACT_EYEBROW,
  CONTACT_HEADLINE,
  CONTACT_INTRO,
  ADDRESS_LINE_1,
  ADDRESS_LINE_2,
  EMAIL,
  PHONE,
  HOURS_LINES,
} from "@/content/site";

/**
 * Contact — DNA's two_column_info_card_form.
 * Left: liquid-glass info card with Visit / Hours / Reach blocks.
 * Right: surface card with name/email/message form + gradient submit.
 */
export function Contact() {
  return (
    <section
      aria-labelledby="contact-heading"
      className="bg-cream"
    >
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="mb-12 md:mb-16 max-w-2xl">
          <EyebrowChip className="mb-4">{CONTACT_EYEBROW}</EyebrowChip>
          <h2 id="contact-heading" className="text-headline mb-4">
            {CONTACT_HEADLINE}
          </h2>
          <p className="text-body-lg">{CONTACT_INTRO}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 md:gap-10 items-start">
          {/* Info card */}
          <aside className="lg:col-span-5">
            <div className="liquid-glass rounded-4xl p-8 md:p-10 warm-shadow">
              <dl className="space-y-7">
                <div>
                  <dt className="text-label mb-2">Visit</dt>
                  <dd className="text-ink leading-relaxed">
                    {ADDRESS_LINE_1}
                    <br />
                    {ADDRESS_LINE_2}
                  </dd>
                </div>
                <div>
                  <dt className="text-label mb-2">Hours</dt>
                  <dd className="text-ink">
                    <ul className="space-y-1.5">
                      {HOURS_LINES.map((row) => (
                        <li
                          key={row.label}
                          className="flex justify-between text-sm gap-4"
                        >
                          <span className="font-medium">{row.label}</span>
                          <span className="text-ink-soft">{row.value}</span>
                        </li>
                      ))}
                    </ul>
                  </dd>
                </div>
                <div>
                  <dt className="text-label mb-2">Reach us</dt>
                  <dd className="text-ink">
                    <a
                      href={`mailto:${EMAIL}`}
                      className="block hover:text-crust transition-colors"
                    >
                      {EMAIL}
                    </a>
                    <a
                      href={`tel:${PHONE}`}
                      className="block hover:text-crust transition-colors"
                    >
                      {PHONE}
                    </a>
                  </dd>
                </div>
              </dl>
            </div>
          </aside>

          {/* Form card */}
          <div className="lg:col-span-7">
            <div className="rounded-4xl bg-surface p-8 md:p-10 warm-shadow">
              <ContactForm />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
