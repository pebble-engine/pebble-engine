"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactInquiryEditorial() {
  return (
    <section className="bg-neutral-50 py-28 px-8">
      <div className="container mx-auto max-w-4xl">

        {/* Header */}
        <div className="mb-16 border-b border-neutral-900/10 pb-10">
          <p className="text-neutral-100 text-xs uppercase tracking-widest mb-4 font-sans" data-pebble-id="pb-f40866">
            Inquiries
          </p>
          <h2 className="font-serif text-neutral-900 text-4xl md:text-5xl leading-tight max-w-lg" data-pebble-id="pb-cee579">
            <RevealWords>Every project begins with a conversation.</RevealWords>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-16">

          {/* Form — spans 7 of 12 */}
          <div className="md:col-span-7">
            <p className="text-neutral-900/55 text-sm leading-relaxed mb-10 font-sans max-w-sm" data-pebble-id="pb-ff4db3">
              We take on a small number of projects each year. If you have a site and a sense of what you're after, we'd like to hear from you. We respond within two business days.
            </p>

            <form
              action="/api/forms/field-and-frame"
              method="POST"
              className="space-y-8"
            >
              <div>
                <label
                  htmlFor="ci-name"
                  className="block text-neutral-900/50 text-xs uppercase tracking-widest mb-3 font-sans" data-pebble-id="pb-b8839a">
                  Name
                </label>
                <input
                  id="ci-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Your name"
                  className="w-full bg-transparent text-neutral-900 placeholder-neutral-900/25 border-b border-neutral-900/20 py-3 text-base font-sans focus:outline-none focus:border-neutral-900/60 transition-colors"
                />
              </div>

              <div>
                <label
                  htmlFor="ci-email"
                  className="block text-neutral-900/50 text-xs uppercase tracking-widest mb-3 font-sans" data-pebble-id="pb-8aee43">
                  Email
                </label>
                <input
                  id="ci-email"
                  type="email"
                  name="email"
                  required
                  placeholder="your@email.com"
                  className="w-full bg-transparent text-neutral-900 placeholder-neutral-900/25 border-b border-neutral-900/20 py-3 text-base font-sans focus:outline-none focus:border-neutral-900/60 transition-colors"
                />
              </div>

              <div>
                <label
                  htmlFor="ci-message"
                  className="block text-neutral-900/50 text-xs uppercase tracking-widest mb-3 font-sans" data-pebble-id="pb-95163b">
                  Message
                </label>
                <textarea
                  id="ci-message"
                  name="message"
                  required
                  rows={5}
                  placeholder="Tell me about your project."
                  className="w-full bg-transparent text-neutral-900 placeholder-neutral-900/25 border-b border-neutral-900/20 py-3 text-base font-sans focus:outline-none focus:border-neutral-900/60 transition-colors resize-none"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  className="text-neutral-900 text-sm font-sans tracking-wide border-b border-neutral-900/40 pb-px hover:border-neutral-900 transition-colors bg-transparent" data-pebble-id="pb-82cdda">
                  Send inquiry →
                </button>
              </div>
            </form>
          </div>

          {/* Contact details — spans 5 of 12 */}
          <div className="md:col-span-5 md:pt-24 space-y-10">
            <div>
              <h3 className="text-neutral-900/40 text-xs uppercase tracking-widest mb-3 font-sans" data-pebble-id="pb-423248">
                Studio
              </h3>
              <p className="text-neutral-900/65 text-sm leading-relaxed font-sans" data-pebble-id="pb-3f1bdf">
                Stone Ridge, New York 12484
              </p>
            </div>

            <div>
              <h3 className="text-neutral-900/40 text-xs uppercase tracking-widest mb-3 font-sans" data-pebble-id="pb-70c743">
                Hours
              </h3>
              <p className="text-neutral-900/65 text-sm leading-relaxed font-sans whitespace-pre-line" data-pebble-id="pb-0c1dd2">
                Studio hours: Monday – Friday, 9am – 5pm
              </p>
            </div>

            <div>
              <h3 className="text-neutral-900/40 text-xs uppercase tracking-widest mb-3 font-sans" data-pebble-id="pb-44bb8b">
                Contact
              </h3>
              <a
                href="tel:(845) 555-0192"
                className="text-neutral-900/65 text-sm font-sans block hover:text-neutral-900 transition-colors" data-pebble-id="pb-3b275c">
                (845) 555-0192
              </a>
              <a
                href="mailto:hello@fieldandframe.studio"
                className="text-neutral-900/65 text-sm font-sans block mt-1 hover:text-neutral-900 transition-colors" data-pebble-id="pb-753415">
                hello@fieldandframe.studio
              </a>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
