"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactAppointment() {
  return (
    <section className="bg-stone-50 py-32 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-5 font-light" data-pebble-id="pb-e35b1e">
            Come in and sit down.
          </p>
          <h2 className="text-stone-700 text-5xl md:text-6xl font-light leading-tight max-w-xl tracking-tight" data-pebble-id="pb-8bcaf3">
            <RevealWords>Book a visit at Marigold Lane.</RevealWords>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16">

          {/* Left — form */}
          <div>
            <p className="text-stone-500 text-lg font-light leading-relaxed mb-10" data-pebble-id="pb-19ad85">
              Send us a note with your name, what you're thinking, and when works for you. We'll get back to you within one business day to confirm your appointment.
            </p>

            <form
              action="/api/forms/marigold-lane"
              method="POST"
              className="space-y-6"
            >
              <div>
                <label
                  htmlFor="appt-name"
                  className="block text-stone-500 text-xs font-light mb-2 uppercase tracking-[0.15em]" data-pebble-id="pb-64a01f">
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
                  className="block text-stone-500 text-xs font-light mb-2 uppercase tracking-[0.15em]" data-pebble-id="pb-1737ee">
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
                  className="block text-stone-500 text-xs font-light mb-2 uppercase tracking-[0.15em]" data-pebble-id="pb-116062">
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
                  className="inline-block border border-stone-700 text-stone-700 px-10 py-4 rounded-full text-xs uppercase tracking-[0.2em] font-light hover:border-amber-600 hover:text-amber-600 transition-colors duration-300" data-pebble-id="pb-678b29">
                  Send request
                </button>
              </div>
            </form>
          </div>

          {/* Right — address, hours, contact */}
          <div className="md:pt-4 space-y-10">
            <div>
              <h3 className="text-stone-400 text-xs font-light uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-12d503">
                Find us
              </h3>
              <p className="text-stone-600 text-lg font-light leading-relaxed" data-pebble-id="pb-9be8be">
                Marigold Lane Salon · East Side
              </p>
            </div>

            <div>
              <h3 className="text-stone-400 text-xs font-light uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-bc563c">
                Hours
              </h3>
              <p className="text-stone-600 text-lg font-light leading-relaxed whitespace-pre-line" data-pebble-id="pb-de024e">
                Tuesday – Friday, 10am – 7pm · Saturday, 9am – 5pm · Closed Sunday & Monday
              </p>
            </div>

            <div>
              <h3 className="text-stone-400 text-xs font-light uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-90a937">
                Get in touch
              </h3>
              <p className="text-stone-600 text-lg font-light" data-pebble-id="pb-2ddb74">
                <a href="tel:(503) 555-0182" className="hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-657c89">
                  (503) 555-0182
                </a>
              </p>
              <p className="text-stone-600 text-lg font-light mt-2" data-pebble-id="pb-d6d160">
                <a href="mailto:hello@marigoldlanesalon.com" className="hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-d9e95e">
                  hello@marigoldlanesalon.com
                </a>
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
