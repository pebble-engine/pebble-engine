"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactInquiryEditorial() {
  return (
    <section className="bg-neutral-50 py-28 px-8">
      <div className="container mx-auto max-w-4xl">

        {/* Header */}
        <div className="mb-16 border-b border-neutral-900/10 pb-10">
          <p className="text-neutral-200 text-xs uppercase tracking-widest mb-4 font-sans" data-pebble-id="pb-47b57c">
            Inquiries
          </p>
          <h2 className="font-serif text-neutral-900 text-4xl md:text-5xl leading-tight max-w-lg" data-pebble-id="pb-c87878">
            <RevealWords>Every wedding begins with a conversation.</RevealWords>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-16">

          {/* Form — spans 7 of 12 */}
          <div className="md:col-span-7">
            <p className="text-neutral-900/55 text-sm leading-relaxed mb-10 font-sans max-w-sm" data-pebble-id="pb-aac157">
              Tell me your date, where you're getting married, and a little about what you're after. I respond within two days and book a limited number of weddings each year.
            </p>

            <form
              action="/api/forms/linen-and-light"
              method="POST"
              className="space-y-8"
            >
              <div>
                <label
                  htmlFor="ci-name"
                  className="block text-neutral-900/50 text-xs uppercase tracking-widest mb-3 font-sans" data-pebble-id="pb-707cfc">
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
                  className="block text-neutral-900/50 text-xs uppercase tracking-widest mb-3 font-sans" data-pebble-id="pb-1e4954">
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
                  className="block text-neutral-900/50 text-xs uppercase tracking-widest mb-3 font-sans" data-pebble-id="pb-dde0b2">
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
                  className="text-neutral-900 text-sm font-sans tracking-wide border-b border-neutral-900/40 pb-px hover:border-neutral-900 transition-colors bg-transparent" data-pebble-id="pb-6c6b78">
                  Send inquiry →
                </button>
              </div>
            </form>
          </div>

          {/* Contact details — spans 5 of 12 */}
          <div className="md:col-span-5 md:pt-24 space-y-10">
            <div>
              <h3 className="text-neutral-900/40 text-xs uppercase tracking-widest mb-3 font-sans" data-pebble-id="pb-cd2f09">
                Studio
              </h3>
              <p className="text-neutral-900/65 text-sm leading-relaxed font-sans" data-pebble-id="pb-fcce73">
                Portland, Oregon
              </p>
            </div>

            <div>
              <h3 className="text-neutral-900/40 text-xs uppercase tracking-widest mb-3 font-sans" data-pebble-id="pb-0c988a">
                Hours
              </h3>
              <p className="text-neutral-900/65 text-sm leading-relaxed font-sans whitespace-pre-line" data-pebble-id="pb-c9e75d">
                Available for weddings in Oregon and Northern California.
              </p>
            </div>

            <div>
              <h3 className="text-neutral-900/40 text-xs uppercase tracking-widest mb-3 font-sans" data-pebble-id="pb-93216d">
                Contact
              </h3>
              <a
                href="tel:"
                className="text-neutral-900/65 text-sm font-sans block hover:text-neutral-900 transition-colors" data-pebble-id="pb-f3ac97">
                
              </a>
              <a
                href="mailto:nora@linenandlight.com"
                className="text-neutral-900/65 text-sm font-sans block mt-1 hover:text-neutral-900 transition-colors" data-pebble-id="pb-6a50ee">
                nora@linenandlight.com
              </a>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
