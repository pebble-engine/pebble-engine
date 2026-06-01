"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactReservation() {
  return (
    <section className="bg-stone-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-14">
          <p className="text-amber-800 text-sm uppercase tracking-widest font-sans mb-3" data-pebble-id="pb-a5b288">
            Reservations
          </p>
          <h2 className="text-stone-900 font-serif text-4xl md:text-5xl leading-tight max-w-xl" data-pebble-id="pb-a3c611">
            <RevealWords>The table is ready when you are.</RevealWords>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16">

          {/* Left — reservation / contact form */}
          <div>
            <p className="text-stone-900/65 font-sans text-lg leading-relaxed mb-10" data-pebble-id="pb-a12f75">
              Send us a note and we'll confirm within one business day. Walk-ins welcome when space allows — call ahead if you'd like to be sure we have a spot. We're a small room, so booking ahead is always a good idea.
            </p>

            <form
              action="/api/forms/maple-and-furrow-contact"
              method="POST"
              className="space-y-6"
            >
              <div>
                <label
                  htmlFor="res-name"
                  className="block text-stone-900 font-sans text-xs font-semibold mb-2 uppercase tracking-widest" data-pebble-id="pb-31ef0b">
                  Name
                </label>
                <input
                  id="res-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Your name"
                  className="w-full bg-stone-900/5 text-stone-900 placeholder-stone-900/30 border border-stone-900/15 rounded-2xl px-5 py-4 font-sans text-base focus:outline-none focus:ring-2 focus:ring-amber-800/40 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="res-email"
                  className="block text-stone-900 font-sans text-xs font-semibold mb-2 uppercase tracking-widest" data-pebble-id="pb-063c27">
                  Email
                </label>
                <input
                  id="res-email"
                  type="email"
                  name="email"
                  required
                  placeholder="you@example.com"
                  className="w-full bg-stone-900/5 text-stone-900 placeholder-stone-900/30 border border-stone-900/15 rounded-2xl px-5 py-4 font-sans text-base focus:outline-none focus:ring-2 focus:ring-amber-800/40 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="res-message"
                  className="block text-stone-900 font-sans text-xs font-semibold mb-2 uppercase tracking-widest" data-pebble-id="pb-030e9e">
                  Message or party size
                </label>
                <textarea
                  id="res-message"
                  name="message"
                  required
                  rows={4}
                  placeholder="Party of two, Friday evening, any dietary notes…"
                  className="w-full bg-stone-900/5 text-stone-900 placeholder-stone-900/30 border border-stone-900/15 rounded-2xl px-5 py-4 font-sans text-base focus:outline-none focus:ring-2 focus:ring-amber-800/40 transition resize-none"
                />
              </div>

              <button
                type="submit"
                className="bg-amber-800 text-stone-50 px-8 py-4 rounded-full font-sans font-semibold hover:scale-105 hover:opacity-95 transition-transform duration-200 w-full md:w-auto" data-pebble-id="pb-6e8530">
                Request a table
              </button>
            </form>
          </div>

          {/* Right — address, hours, contact details */}
          <div className="md:pt-16 space-y-10">
            <div>
              <h3 className="text-stone-900 font-sans text-xs font-semibold uppercase tracking-widest mb-3" data-pebble-id="pb-4b7b02">
                Find us
              </h3>
              <p className="text-stone-900/65 font-sans text-lg leading-relaxed" data-pebble-id="pb-1ebf7a">
                42 Millbrook Turnpike, Rhinebeck, NY 12572
              </p>
            </div>

            <div>
              <h3 className="text-stone-900 font-sans text-xs font-semibold uppercase tracking-widest mb-3" data-pebble-id="pb-af5a21">
                Hours
              </h3>
              <p className="text-stone-900/65 font-sans text-lg leading-relaxed whitespace-pre-line" data-pebble-id="pb-3e9fa4">
                Dinner: Wed – Sun, 5pm – 10pm
Lunch: Sat – Sun, 11:30am – 2:30pm
Closed Monday & Tuesday
              </p>
            </div>

            <div>
              <h3 className="text-stone-900 font-sans text-xs font-semibold uppercase tracking-widest mb-3" data-pebble-id="pb-ab90b5">
                Get in touch
              </h3>
              <p className="text-stone-900/65 font-sans text-lg" data-pebble-id="pb-2e74ce">
                <a href="tel:(845) 555-0183" className="hover:text-amber-800 transition" data-pebble-id="pb-e2a822">
                  (845) 555-0183
                </a>
              </p>
              <p className="text-stone-900/65 font-sans text-lg mt-2" data-pebble-id="pb-df7527">
                <a href="mailto:hello@mapleandfurrow.com" className="hover:text-amber-800 transition" data-pebble-id="pb-f0061a">
                  hello@mapleandfurrow.com
                </a>
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
