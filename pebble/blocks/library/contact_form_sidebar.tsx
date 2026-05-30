export default function ContactForm() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-14">
          <p className="text-{{accent}} text-sm uppercase tracking-widest mb-3">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-5xl md:text-6xl font-bold leading-tight max-w-xl">
            {{headline}}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16">

          {/* Left column — contact form */}
          <div>
            <p className="text-{{fg}}/70 text-xl leading-relaxed mb-10">
              {{form_intro}}
            </p>

            <form
              action="/api/forms/{{form_slug}}"
              method="POST"
              className="space-y-6"
            >
              <div>
                <label
                  htmlFor="contact-name"
                  className="block text-{{fg}} text-sm font-medium mb-2 uppercase tracking-wide"
                >
                  Your name
                </label>
                <input
                  id="contact-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Jane Smith"
                  className="w-full bg-{{fg}}/5 text-{{fg}} placeholder-{{fg}}/30 border border-{{fg}}/15 rounded-2xl px-5 py-4 text-base focus:outline-none focus:ring-2 focus:ring-{{accent}}/40 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="contact-email"
                  className="block text-{{fg}} text-sm font-medium mb-2 uppercase tracking-wide"
                >
                  Email address
                </label>
                <input
                  id="contact-email"
                  type="email"
                  name="email"
                  required
                  placeholder="jane@example.com"
                  className="w-full bg-{{fg}}/5 text-{{fg}} placeholder-{{fg}}/30 border border-{{fg}}/15 rounded-2xl px-5 py-4 text-base focus:outline-none focus:ring-2 focus:ring-{{accent}}/40 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="contact-message"
                  className="block text-{{fg}} text-sm font-medium mb-2 uppercase tracking-wide"
                >
                  Message
                </label>
                <textarea
                  id="contact-message"
                  name="message"
                  required
                  rows={5}
                  placeholder="Tell us what you have in mind…"
                  className="w-full bg-{{fg}}/5 text-{{fg}} placeholder-{{fg}}/30 border border-{{fg}}/15 rounded-2xl px-5 py-4 text-base focus:outline-none focus:ring-2 focus:ring-{{accent}}/40 transition resize-none"
                />
              </div>

              <button
                type="submit"
                className="bg-{{accent}} text-{{bg}} px-8 py-4 rounded-full font-semibold hover:opacity-90 transition w-full md:w-auto"
              >
                Send message
              </button>
            </form>
          </div>

          {/* Right column — address, hours, phone */}
          <div className="md:pt-20 space-y-10">
            <div>
              <h3 className="text-{{fg}} text-sm font-semibold uppercase tracking-widest mb-3">
                Find us
              </h3>
              <p className="text-{{fg}}/70 text-xl leading-relaxed">
                {{address}}
              </p>
            </div>

            <div>
              <h3 className="text-{{fg}} text-sm font-semibold uppercase tracking-widest mb-3">
                Hours
              </h3>
              <p className="text-{{fg}}/70 text-xl leading-relaxed whitespace-pre-line">
                {{hours_text}}
              </p>
            </div>

            <div>
              <h3 className="text-{{fg}} text-sm font-semibold uppercase tracking-widest mb-3">
                Get in touch
              </h3>
              <p className="text-{{fg}}/70 text-xl">
                <a
                  href="tel:{{phone}}"
                  className="hover:text-{{accent}} transition"
                >
                  {{phone}}
                </a>
              </p>
              <p className="text-{{fg}}/70 text-xl mt-2">
                <a
                  href="mailto:{{email}}"
                  className="hover:text-{{accent}} transition"
                >
                  {{email}}
                </a>
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
