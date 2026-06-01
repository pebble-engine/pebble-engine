"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactReservation() {
  return (
    <section className="bg-stone-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-14">
          <p className="text-amber-700 text-sm uppercase tracking-widest font-sans mb-3" data-pebble-id="pb-cb4c27">
            Come find us
          </p>
          <h2 className="text-stone-900 font-serif text-4xl md:text-5xl leading-tight max-w-xl" data-pebble-id="pb-6eeba2">
            <RevealWords>Stop in, or drop us a line — we're easy to reach.</RevealWords>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16">

          {/* Left — reservation / contact form */}
          <div>
            <p className="text-stone-900/65 font-sans text-lg leading-relaxed mb-10" data-pebble-id="pb-74f370">
              Questions about a bean, a subscription, or a wholesale order? Send us a message and we'll get back to you within one business day. Walk-ins are always welcome during café hours.
            </p>

            <form
              action="/api/forms/ember-and-oak-roasters"
              method="POST"
              className="space-y-6"
            >
              <div>
                <label
                  htmlFor="res-name"
                  className="block text-stone-900 font-sans text-xs font-semibold mb-2 uppercase tracking-widest" data-pebble-id="pb-2e534e">
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
                  className="block text-stone-900 font-sans text-xs font-semibold mb-2 uppercase tracking-widest" data-pebble-id="pb-90dda3">
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
                  className="block text-stone-900 font-sans text-xs font-semibold mb-2 uppercase tracking-widest" data-pebble-id="pb-269d74">
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
                className="bg-amber-700 text-stone-50 px-8 py-4 rounded-full font-sans font-semibold hover:scale-105 hover:opacity-95 transition-transform duration-200 w-full md:w-auto" data-pebble-id="pb-1ef657">
                Request a table
              </button>
            </form>
          </div>

          {/* Right — address, hours, contact details */}
          <div className="md:pt-16 space-y-10">
            <div>
              <h3 className="text-stone-900 font-sans text-xs font-semibold uppercase tracking-widest mb-3" data-pebble-id="pb-fec802">
                Find us
              </h3>
              <p className="text-stone-900/65 font-sans text-lg leading-relaxed" data-pebble-id="pb-29dc8f">
                412 Maple Street, Portland, OR 97209 — Kerns neighborhood
              </p>
            </div>

            <div>
              <h3 className="text-stone-900 font-sans text-xs font-semibold uppercase tracking-widest mb-3" data-pebble-id="pb-af92b2">
                Hours
              </h3>
              <p className="text-stone-900/65 font-sans text-lg leading-relaxed whitespace-pre-line" data-pebble-id="pb-11adc5">
                Café open Tuesday – Saturday, 7am – 2pm. Roasting days: Tuesday, Thursday, Saturday — come early for the smell.
              </p>
            </div>

            <div>
              <h3 className="text-stone-900 font-sans text-xs font-semibold uppercase tracking-widest mb-3" data-pebble-id="pb-408ce5">
                Get in touch
              </h3>
              <p className="text-stone-900/65 font-sans text-lg" data-pebble-id="pb-dedb2f">
                <a href="tel:(503) 555-0174" className="hover:text-amber-700 transition" data-pebble-id="pb-cf96b1">
                  (503) 555-0174
                </a>
              </p>
              <p className="text-stone-900/65 font-sans text-lg mt-2" data-pebble-id="pb-9f6a79">
                <a href="mailto:hello@emberandoakroasters.com" className="hover:text-amber-700 transition" data-pebble-id="pb-56810d">
                  hello@emberandoakroasters.com
                </a>
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
