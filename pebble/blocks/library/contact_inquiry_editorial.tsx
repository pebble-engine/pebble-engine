"use client";
import RevealWords from "@/components/motion/RevealWords";

export default function ContactInquiryEditorial() {
  return (
    <section className="bg-{{bg}} py-28 px-8">
      <div className="container mx-auto max-w-4xl">

        {/* Header */}
        <div className="mb-16 border-b border-{{fg}}/10 pb-10">
          <p className="text-{{muted}} text-xs uppercase tracking-widest mb-4 font-sans">
            {{eyebrow}}
          </p>
          <h2 className="font-serif text-{{fg}} text-4xl md:text-5xl leading-tight max-w-lg">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-16">

          {/* Form — spans 7 of 12 */}
          <div className="md:col-span-7">
            <p className="text-{{fg}}/55 text-sm leading-relaxed mb-10 font-sans max-w-sm">
              {{form_intro}}
            </p>

            <form
              action="/api/forms/{{form_slug}}"
              method="POST"
              className="space-y-8"
            >
              <div>
                <label
                  htmlFor="ci-name"
                  className="block text-{{fg}}/50 text-xs uppercase tracking-widest mb-3 font-sans"
                >
                  Name
                </label>
                <input
                  id="ci-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Your name"
                  className="w-full bg-transparent text-{{fg}} placeholder-{{fg}}/25 border-b border-{{fg}}/20 py-3 text-base font-sans focus:outline-none focus:border-{{fg}}/60 transition-colors"
                />
              </div>

              <div>
                <label
                  htmlFor="ci-email"
                  className="block text-{{fg}}/50 text-xs uppercase tracking-widest mb-3 font-sans"
                >
                  Email
                </label>
                <input
                  id="ci-email"
                  type="email"
                  name="email"
                  required
                  placeholder="your@email.com"
                  className="w-full bg-transparent text-{{fg}} placeholder-{{fg}}/25 border-b border-{{fg}}/20 py-3 text-base font-sans focus:outline-none focus:border-{{fg}}/60 transition-colors"
                />
              </div>

              <div>
                <label
                  htmlFor="ci-message"
                  className="block text-{{fg}}/50 text-xs uppercase tracking-widest mb-3 font-sans"
                >
                  Message
                </label>
                <textarea
                  id="ci-message"
                  name="message"
                  required
                  rows={5}
                  placeholder="Tell me about your project."
                  className="w-full bg-transparent text-{{fg}} placeholder-{{fg}}/25 border-b border-{{fg}}/20 py-3 text-base font-sans focus:outline-none focus:border-{{fg}}/60 transition-colors resize-none"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  className="text-{{fg}} text-sm font-sans tracking-wide border-b border-{{fg}}/40 pb-px hover:border-{{fg}} transition-colors bg-transparent"
                >
                  Send inquiry →
                </button>
              </div>
            </form>
          </div>

          {/* Contact details — spans 5 of 12 */}
          <div className="md:col-span-5 md:pt-24 space-y-10">
            <div>
              <h3 className="text-{{fg}}/40 text-xs uppercase tracking-widest mb-3 font-sans">
                Studio
              </h3>
              <p className="text-{{fg}}/65 text-sm leading-relaxed font-sans">
                {{address}}
              </p>
            </div>

            <div>
              <h3 className="text-{{fg}}/40 text-xs uppercase tracking-widest mb-3 font-sans">
                Hours
              </h3>
              <p className="text-{{fg}}/65 text-sm leading-relaxed font-sans whitespace-pre-line">
                {{hours_text}}
              </p>
            </div>

            <div>
              <h3 className="text-{{fg}}/40 text-xs uppercase tracking-widest mb-3 font-sans">
                Contact
              </h3>
              <a
                href="tel:{{phone}}"
                className="text-{{fg}}/65 text-sm font-sans block hover:text-{{fg}} transition-colors"
              >
                {{phone}}
              </a>
              <a
                href="mailto:{{email}}"
                className="text-{{fg}}/65 text-sm font-sans block mt-1 hover:text-{{fg}} transition-colors"
              >
                {{email}}
              </a>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
