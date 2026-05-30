export default function ContactFriendlyPlayful() {
  return (
    <section className="bg-purple-100 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-14">
          <p className="inline-flex items-center gap-2 bg-pink-500 text-white text-sm font-bold px-5 py-2 rounded-full mb-6 tracking-wide">
            {{eyebrow}}
          </p>
          <h2 className="text-purple-900 text-5xl md:text-6xl font-extrabold leading-tight max-w-xl">
            {{headline}}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16">

          {/* Left — form */}
          <div className="bg-white rounded-[2rem] p-10 shadow-lg ring-2 ring-pink-100">
            <p className="text-purple-900/70 text-xl leading-relaxed mb-8">
              {{form_intro}}
            </p>

            <form
              action="/api/forms/{{form_slug}}"
              method="POST"
              className="space-y-6"
            >
              <div>
                <label
                  htmlFor="playful-contact-name"
                  className="block text-purple-900 text-sm font-extrabold mb-2 uppercase tracking-wide"
                >
                  Your name
                </label>
                <input
                  id="playful-contact-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Alex"
                  className="w-full bg-pink-50 text-purple-900 placeholder-purple-300 border-2 border-pink-200 rounded-2xl px-5 py-4 text-base focus:outline-none focus:ring-2 focus:ring-pink-400 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="playful-contact-email"
                  className="block text-purple-900 text-sm font-extrabold mb-2 uppercase tracking-wide"
                >
                  Email address
                </label>
                <input
                  id="playful-contact-email"
                  type="email"
                  name="email"
                  required
                  placeholder="alex@example.com"
                  className="w-full bg-pink-50 text-purple-900 placeholder-purple-300 border-2 border-pink-200 rounded-2xl px-5 py-4 text-base focus:outline-none focus:ring-2 focus:ring-pink-400 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="playful-contact-message"
                  className="block text-purple-900 text-sm font-extrabold mb-2 uppercase tracking-wide"
                >
                  Message
                </label>
                <textarea
                  id="playful-contact-message"
                  name="message"
                  required
                  rows={5}
                  placeholder="What's on your mind?"
                  className="w-full bg-pink-50 text-purple-900 placeholder-purple-300 border-2 border-pink-200 rounded-2xl px-5 py-4 text-base focus:outline-none focus:ring-2 focus:ring-pink-400 transition resize-none"
                />
              </div>

              <button
                type="submit"
                className="bg-pink-500 text-white px-10 py-5 rounded-full font-extrabold shadow hover:scale-110 hover:rotate-1 hover:shadow-pink-300 transition-all duration-200 w-full md:w-auto"
              >
                Send it!
              </button>
            </form>
          </div>

          {/* Right — info */}
          <div className="md:pt-4 space-y-10">
            <div>
              <h3 className="text-purple-900 text-sm font-extrabold uppercase tracking-widest mb-3 flex items-center gap-2">
                Find us
              </h3>
              <p className="text-purple-900/70 text-xl leading-relaxed">
                {{address}}
              </p>
            </div>

            <div>
              <h3 className="text-purple-900 text-sm font-extrabold uppercase tracking-widest mb-3">
                Hours
              </h3>
              <p className="text-purple-900/70 text-xl leading-relaxed whitespace-pre-line">
                {{hours_text}}
              </p>
            </div>

            <div>
              <h3 className="text-purple-900 text-sm font-extrabold uppercase tracking-widest mb-3">
                Get in touch
              </h3>
              <p className="text-purple-900/70 text-xl">
                <a
                  href="tel:{{phone}}"
                  className="hover:text-pink-500 transition font-semibold"
                >
                  {{phone}}
                </a>
              </p>
              <p className="text-purple-900/70 text-xl mt-2">
                <a
                  href="mailto:{{email}}"
                  className="hover:text-pink-500 transition font-semibold"
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
