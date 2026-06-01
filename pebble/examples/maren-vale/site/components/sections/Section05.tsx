"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactAppointment() {
  return (
    <section className="bg-stone-50 py-32 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-5 font-light" data-pebble-id="pb-80b2d1">
            Begin a commission.
          </p>
          <h2 className="text-stone-700 text-5xl md:text-6xl font-light leading-tight max-w-xl tracking-tight" data-pebble-id="pb-1bfe79">
            <RevealWords>Every piece starts with a single conversation.</RevealWords>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16">

          {/* Left — form */}
          <div>
            <p className="text-stone-500 text-lg font-light leading-relaxed mb-10" data-pebble-id="pb-65cc19">
              Tell me a little about what you have in mind — the occasion, a feeling, a material you love. I read every message personally and respond within two business days.
            </p>

            <form
              action="/api/forms/maren-and-vale"
              method="POST"
              className="space-y-6"
            >
              <div>
                <label
                  htmlFor="appt-name"
                  className="block text-stone-500 text-xs font-light mb-2 uppercase tracking-[0.15em]" data-pebble-id="pb-1260d7">
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
                  className="block text-stone-500 text-xs font-light mb-2 uppercase tracking-[0.15em]" data-pebble-id="pb-6b282e">
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
                  className="block text-stone-500 text-xs font-light mb-2 uppercase tracking-[0.15em]" data-pebble-id="pb-c06095">
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
                  className="inline-block border border-stone-700 text-stone-700 px-10 py-4 rounded-full text-xs uppercase tracking-[0.2em] font-light hover:border-amber-600 hover:text-amber-600 transition-colors duration-300" data-pebble-id="pb-b1b910">
                  Send request
                </button>
              </div>
            </form>
          </div>

          {/* Right — address, hours, contact */}
          <div className="md:pt-4 space-y-10">
            <div>
              <h3 className="text-stone-400 text-xs font-light uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-d890ee">
                Find us
              </h3>
              <p className="text-stone-600 text-lg font-light leading-relaxed" data-pebble-id="pb-e2c798">
                Studio by appointment — Portland, Oregon
              </p>
            </div>

            <div>
              <h3 className="text-stone-400 text-xs font-light uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-4033c0">
                Hours
              </h3>
              <p className="text-stone-600 text-lg font-light leading-relaxed whitespace-pre-line" data-pebble-id="pb-a6328b">
                Tuesday – Saturday, 10am – 5pm. Evening appointments available on request.
              </p>
            </div>

            <div>
              <h3 className="text-stone-400 text-xs font-light uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-0b9677">
                Get in touch
              </h3>
              <p className="text-stone-600 text-lg font-light" data-pebble-id="pb-0bef1f">
                <a href="tel:(503) 214-0876" className="hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-275917">
                  (503) 214-0876
                </a>
              </p>
              <p className="text-stone-600 text-lg font-light mt-2" data-pebble-id="pb-a61451">
                <a href="mailto:hello@marenandvale.com" className="hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-2d41b1">
                  hello@marenandvale.com
                </a>
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
