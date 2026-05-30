export default function ContactReservation() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-14">
          <p className="text-{{accent}} text-sm uppercase tracking-widest font-sans mb-3">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} font-serif text-4xl md:text-5xl leading-tight max-w-xl">
            {{headline}}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16">

          {/* Left — reservation / contact form */}
          <div>
            <p className="text-{{fg}}/65 font-sans text-lg leading-relaxed mb-10">
              {{form_intro}}
            </p>

            <form
              action="/api/forms/{{form_slug}}"
              method="POST"
              className="space-y-6"
            >
              <div>
                <label
                  htmlFor="res-name"
                  className="block text-{{fg}} font-sans text-xs font-semibold mb-2 uppercase tracking-widest"
                >
                  Name
                </label>
                <input
                  id="res-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Your name"
                  className="w-full bg-{{fg}}/5 text-{{fg}} placeholder-{{fg}}/30 border border-{{fg}}/15 rounded-2xl px-5 py-4 font-sans text-base focus:outline-none focus:ring-2 focus:ring-{{accent}}/40 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="res-email"
                  className="block text-{{fg}} font-sans text-xs font-semibold mb-2 uppercase tracking-widest"
                >
                  Email
                </label>
                <input
                  id="res-email"
                  type="email"
                  name="email"
                  required
                  placeholder="you@example.com"
                  className="w-full bg-{{fg}}/5 text-{{fg}} placeholder-{{fg}}/30 border border-{{fg}}/15 rounded-2xl px-5 py-4 font-sans text-base focus:outline-none focus:ring-2 focus:ring-{{accent}}/40 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="res-message"
                  className="block text-{{fg}} font-sans text-xs font-semibold mb-2 uppercase tracking-widest"
                >
                  Message or party size
                </label>
                <textarea
                  id="res-message"
                  name="message"
                  required
                  rows={4}
                  placeholder="Party of two, Friday evening, any dietary notes…"
                  className="w-full bg-{{fg}}/5 text-{{fg}} placeholder-{{fg}}/30 border border-{{fg}}/15 rounded-2xl px-5 py-4 font-sans text-base focus:outline-none focus:ring-2 focus:ring-{{accent}}/40 transition resize-none"
                />
              </div>

              <button
                type="submit"
                className="bg-{{accent}} text-{{accent_fg}} px-8 py-4 rounded-full font-sans font-semibold hover:scale-105 hover:opacity-95 transition-transform duration-200 w-full md:w-auto"
              >
                Request a table
              </button>
            </form>
          </div>

          {/* Right — address, hours, contact details */}
          <div className="md:pt-16 space-y-10">
            <div>
              <h3 className="text-{{fg}} font-sans text-xs font-semibold uppercase tracking-widest mb-3">
                Find us
              </h3>
              <p className="text-{{fg}}/65 font-sans text-lg leading-relaxed">
                {{address}}
              </p>
            </div>

            <div>
              <h3 className="text-{{fg}} font-sans text-xs font-semibold uppercase tracking-widest mb-3">
                Hours
              </h3>
              <p className="text-{{fg}}/65 font-sans text-lg leading-relaxed whitespace-pre-line">
                {{hours_text}}
              </p>
            </div>

            <div>
              <h3 className="text-{{fg}} font-sans text-xs font-semibold uppercase tracking-widest mb-3">
                Get in touch
              </h3>
              <p className="text-{{fg}}/65 font-sans text-lg">
                <a href="tel:{{phone}}" className="hover:text-{{accent}} transition">
                  {{phone}}
                </a>
              </p>
              <p className="text-{{fg}}/65 font-sans text-lg mt-2">
                <a href="mailto:{{email}}" className="hover:text-{{accent}} transition">
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
