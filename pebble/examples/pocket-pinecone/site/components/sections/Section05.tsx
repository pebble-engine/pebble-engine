"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactFriendlyPlayful() {
  return (
    <section className="bg-purple-100 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-14">
          <p className="inline-flex items-center gap-2 bg-pink-500 text-white text-sm font-bold px-5 py-2 rounded-full mb-6 tracking-wide" data-pebble-id="pb-cb1573">
            👋 Say hello!
          </p>
          <h2 className="text-purple-900 text-5xl md:text-6xl font-extrabold leading-tight max-w-xl" data-pebble-id="pb-645ba3">
            <RevealWords>We'd love to see you — or answer your burning toy questions</RevealWords>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16">

          {/* Left — form */}
          <div className="bg-white rounded-[2rem] p-10 shadow-lg ring-2 ring-pink-100">
            <p className="text-purple-900/70 text-xl leading-relaxed mb-8" data-pebble-id="pb-09903d">
              Whether you need a gift idea, want to know what's new in the cubbies, or just want to chat about toys, drop us a message. A real human (us!) will write back within one business day.
            </p>

            <form
              action="/api/forms/pocket-and-pinecone"
              method="POST"
              className="space-y-6"
            >
              <div>
                <label
                  htmlFor="playful-contact-name"
                  className="block text-purple-900 text-sm font-extrabold mb-2 uppercase tracking-wide" data-pebble-id="pb-d87597">
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
                  className="block text-purple-900 text-sm font-extrabold mb-2 uppercase tracking-wide" data-pebble-id="pb-ce0081">
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
                  className="block text-purple-900 text-sm font-extrabold mb-2 uppercase tracking-wide" data-pebble-id="pb-f3c3ac">
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
                className="bg-pink-500 text-white px-10 py-5 rounded-full font-extrabold shadow hover:scale-110 hover:rotate-1 hover:shadow-pink-300 transition-all duration-200 w-full md:w-auto" data-pebble-id="pb-15fa83">
                Send it!
              </button>
            </form>
          </div>

          {/* Right — info */}
          <div className="md:pt-4 space-y-10">
            <div>
              <h3 className="text-purple-900 text-sm font-extrabold uppercase tracking-widest mb-3 flex items-center gap-2" data-pebble-id="pb-25fc08">
                Find us
              </h3>
              <p className="text-purple-900/70 text-xl leading-relaxed" data-pebble-id="pb-f74004">
                114 Elm Corner, Millbrook, NY 12545
              </p>
            </div>

            <div>
              <h3 className="text-purple-900 text-sm font-extrabold uppercase tracking-widest mb-3" data-pebble-id="pb-321106">
                Hours
              </h3>
              <p className="text-purple-900/70 text-xl leading-relaxed whitespace-pre-line" data-pebble-id="pb-0cb735">
                Tuesday – Friday: 10am – 6pm
Saturday: 10am – 5pm
Sunday: 11am – 4pm
Closed Mondays
              </p>
            </div>

            <div>
              <h3 className="text-purple-900 text-sm font-extrabold uppercase tracking-widest mb-3" data-pebble-id="pb-5db334">
                Get in touch
              </h3>
              <p className="text-purple-900/70 text-xl" data-pebble-id="pb-79fc47">
                <a
                  href="tel:(845) 555-0173"
                  className="hover:text-pink-500 transition font-semibold" data-pebble-id="pb-6707f5">
                  (845) 555-0173
                </a>
              </p>
              <p className="text-purple-900/70 text-xl mt-2" data-pebble-id="pb-574297">
                <a
                  href="mailto:hello@pocketandpinecone.com"
                  className="hover:text-pink-500 transition font-semibold" data-pebble-id="pb-45c0b2">
                  hello@pocketandpinecone.com
                </a>
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
