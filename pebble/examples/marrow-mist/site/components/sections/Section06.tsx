"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactAppointment() {
  return (
    <section className="bg-stone-50 py-32 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-5 font-light" data-pebble-id="pb-1e1b3e">
            We hold space for you.
          </p>
          <h2 className="text-stone-700 text-5xl md:text-6xl font-light leading-tight max-w-xl tracking-tight" data-pebble-id="pb-33ec1f">
            <RevealWords>When you're ready, we'll be here.</RevealWords>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16">

          {/* Left — form */}
          <div>
            <p className="text-stone-500 text-lg font-light leading-relaxed mb-10" data-pebble-id="pb-e72419">
              Send us a note and we'll confirm your booking within one business day. Let us know if it's a first visit, a special occasion, or if there's anything about the treatment you'd like us to know in advance.
            </p>

            <form
              action="/api/forms/marrow-and-mist"
              method="POST"
              className="space-y-6"
            >
              <div>
                <label
                  htmlFor="appt-name"
                  className="block text-stone-500 text-xs font-light mb-2 uppercase tracking-[0.15em]" data-pebble-id="pb-280336">
                  Your name
                </label>
                <input
                  id="appt-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Jane Smith"
                  className="w-full bg-transparent text-stone-700 placeholder-stone-300 border-b border-stone-300 py-3 text-base font-light focus:outline-none focus:border-amber-600 transition-colors duration-200"
                />
              </div>

              <div>
                <label
                  htmlFor="appt-email"
                  className="block text-stone-500 text-xs font-light mb-2 uppercase tracking-[0.15em]" data-pebble-id="pb-8f38fb">
                  Email address
                </label>
                <input
                  id="appt-email"
                  type="email"
                  name="email"
                  required
                  placeholder="jane@example.com"
                  className="w-full bg-transparent text-stone-700 placeholder-stone-300 border-b border-stone-300 py-3 text-base font-light focus:outline-none focus:border-amber-600 transition-colors duration-200"
                />
              </div>

              <div>
                <label
                  htmlFor="appt-message"
                  className="block text-stone-500 text-xs font-light mb-2 uppercase tracking-[0.15em]" data-pebble-id="pb-412661">
                  Message
                </label>
                <textarea
                  id="appt-message"
                  name="message"
                  required
                  rows={4}
                  placeholder="What would you like to experience?"
                  className="w-full bg-transparent text-stone-700 placeholder-stone-300 border-b border-stone-300 py-3 text-base font-light focus:outline-none focus:border-amber-600 transition-colors duration-200 resize-none"
                />
              </div>

              <div className="pt-4">
                <button
                  type="submit"
                  className="inline-block border border-stone-700 text-stone-700 px-10 py-4 rounded-full text-xs uppercase tracking-[0.2em] font-light hover:border-amber-600 hover:text-amber-600 transition-colors duration-300" data-pebble-id="pb-ca5bf7">
                  Send request
                </button>
              </div>
            </form>
          </div>

          {/* Right — address, hours, contact */}
          <div className="md:pt-4 space-y-10">
            <div>
              <h3 className="text-stone-400 text-xs font-light uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-5d7a36">
                Find us
              </h3>
              <p className="text-stone-600 text-lg font-light leading-relaxed" data-pebble-id="pb-d65ffe">
                14 Alderwood Lane, just off Merchant Street, Millhaven
              </p>
            </div>

            <div>
              <h3 className="text-stone-400 text-xs font-light uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-4c12e6">
                Hours
              </h3>
              <p className="text-stone-600 text-lg font-light leading-relaxed whitespace-pre-line" data-pebble-id="pb-dbb76f">
                Tuesday – Friday, 10am – 7pm
Saturday, 9am – 6pm
Sunday, 10am – 4pm
Closed Monday
              </p>
            </div>

            <div>
              <h3 className="text-stone-400 text-xs font-light uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-9eb950">
                Get in touch
              </h3>
              <p className="text-stone-600 text-lg font-light" data-pebble-id="pb-eb9bc8">
                <a href="tel:(503) 882-4170" className="hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-64dabc">
                  (503) 882-4170
                </a>
              </p>
              <p className="text-stone-600 text-lg font-light mt-2" data-pebble-id="pb-a84b70">
                <a href="mailto:hello@marrowandmist.com" className="hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-c30f26">
                  hello@marrowandmist.com
                </a>
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
