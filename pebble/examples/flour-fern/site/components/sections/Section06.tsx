"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactReservation() {
  return (
    <section className="bg-stone-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-14">
          <p className="text-amber-700 text-sm uppercase tracking-widest font-sans mb-3" data-pebble-id="pb-8b1f0e">
            Come find us
          </p>
          <h2 className="text-stone-900 font-serif text-4xl md:text-5xl leading-tight max-w-xl" data-pebble-id="pb-f4482c">
            <RevealWords>The loaves are out early. So are we.</RevealWords>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16">

          {/* Left — reservation / contact form */}
          <div>
            <p className="text-stone-900/65 font-sans text-lg leading-relaxed mb-10" data-pebble-id="pb-648dfd">
              Want to reserve a loaf for the week, ask about wholesale, or just say hello? Send us a note and we'll reply within one business day. Walk-ins always welcome — just come early.
            </p>

            <form
              action="/api/forms/flour-and-fern-contact"
              method="POST"
              className="space-y-6"
            >
              <div>
                <label
                  htmlFor="res-name"
                  className="block text-stone-900 font-sans text-xs font-semibold mb-2 uppercase tracking-widest" data-pebble-id="pb-5a0c28">
                  Name
                </label>
                <input
                  id="res-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Your name"
                  className="w-full bg-stone-900/5 text-stone-900 placeholder-stone-900/30 border border-stone-900/15 rounded-2xl px-5 py-4 font-sans text-base focus:outline-none focus:ring-2 focus:ring-amber-700/40 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="res-email"
                  className="block text-stone-900 font-sans text-xs font-semibold mb-2 uppercase tracking-widest" data-pebble-id="pb-a79026">
                  Email
                </label>
                <input
                  id="res-email"
                  type="email"
                  name="email"
                  required
                  placeholder="you@example.com"
                  className="w-full bg-stone-900/5 text-stone-900 placeholder-stone-900/30 border border-stone-900/15 rounded-2xl px-5 py-4 font-sans text-base focus:outline-none focus:ring-2 focus:ring-amber-700/40 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="res-message"
                  className="block text-stone-900 font-sans text-xs font-semibold mb-2 uppercase tracking-widest" data-pebble-id="pb-214bb1">
                  Message or party size
                </label>
                <textarea
                  id="res-message"
                  name="message"
                  required
                  rows={4}
                  placeholder="Party of two, Friday evening, any dietary notes…"
                  className="w-full bg-stone-900/5 text-stone-900 placeholder-stone-900/30 border border-stone-900/15 rounded-2xl px-5 py-4 font-sans text-base focus:outline-none focus:ring-2 focus:ring-amber-700/40 transition resize-none"
                />
              </div>

              <button
                type="submit"
                className="bg-amber-700 text-stone-50 px-8 py-4 rounded-full font-sans font-semibold hover:scale-105 hover:opacity-95 transition-transform duration-200 w-full md:w-auto" data-pebble-id="pb-10eaf9">
                Request a table
              </button>
            </form>
          </div>

          {/* Right — address, hours, contact details */}
          <div className="md:pt-16 space-y-10">
            <div>
              <h3 className="text-stone-900 font-sans text-xs font-semibold uppercase tracking-widest mb-3" data-pebble-id="pb-10db9b">
                Find us
              </h3>
              <p className="text-stone-900/65 font-sans text-lg leading-relaxed" data-pebble-id="pb-3295d8">
                Corner of Fern Ave & Riverside Dr, Riverside neighborhood
              </p>
            </div>

            <div>
              <h3 className="text-stone-900 font-sans text-xs font-semibold uppercase tracking-widest mb-3" data-pebble-id="pb-b8586f">
                Hours
              </h3>
              <p className="text-stone-900/65 font-sans text-lg leading-relaxed whitespace-pre-line" data-pebble-id="pb-27de72">
                Wednesday – Friday: 7am – noon (or until sold out)
Saturday – Sunday: 6:30am – noon (or until sold out)
Monday – Tuesday: Closed
              </p>
            </div>

            <div>
              <h3 className="text-stone-900 font-sans text-xs font-semibold uppercase tracking-widest mb-3" data-pebble-id="pb-5aaa6b">
                Get in touch
              </h3>
              <p className="text-stone-900/65 font-sans text-lg" data-pebble-id="pb-84f02e">
                <a href="tel:(503) 741-0892" className="hover:text-amber-700 transition" data-pebble-id="pb-d68bdc">
                  (503) 741-0892
                </a>
              </p>
              <p className="text-stone-900/65 font-sans text-lg mt-2" data-pebble-id="pb-d83868">
                <a href="mailto:hello@flourandfern.com" className="hover:text-amber-700 transition" data-pebble-id="pb-df07bd">
                  hello@flourandfern.com
                </a>
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
