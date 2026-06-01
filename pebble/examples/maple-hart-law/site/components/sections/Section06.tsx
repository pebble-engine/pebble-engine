"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactSplitClean() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-start">

          {/* Left — info panel */}
          <div>
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-2f870a">
              Get in touch
            </p>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight max-w-sm mb-8" data-pebble-id="pb-346c7b">
              <RevealWords>Start with a free 30-minute call</RevealWords>
            </h2>
            <p className="text-slate-500 text-base leading-relaxed mb-10 max-w-xs" data-pebble-id="pb-569366">
              Fill out the form and Dana will follow up within one business day to schedule your free plain English call. No obligation, no pressure — just honest answers.
            </p>

            <div className="space-y-8">
              <div>
                <p className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-169bda">
                  Address
                </p>
                <p className="text-slate-500 text-base leading-relaxed" data-pebble-id="pb-36eec3">
                  184 Church Street, Suite 3, Burlington, VT 05401
                </p>
              </div>
              <div>
                <p className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-3453f0">
                  Office hours
                </p>
                <p className="text-slate-500 text-base leading-relaxed whitespace-pre-line" data-pebble-id="pb-774cd8">
                  Mon–Fri, 9am–5pm. Evening calls available by arrangement.
                </p>
              </div>
              <div>
                <p className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-089aa3">
                  Contact
                </p>
                <p className="text-slate-500 text-base" data-pebble-id="pb-6ee915">
                  <a href="tel:(802) 555-0147" className="hover:text-sky-600 transition" data-pebble-id="pb-1ac531">
                    (802) 555-0147
                  </a>
                </p>
                <p className="text-slate-500 text-base mt-1" data-pebble-id="pb-2bd742">
                  <a href="mailto:hello@mapleandhart.law" className="hover:text-sky-600 transition" data-pebble-id="pb-dca0e5">
                    hello@mapleandhart.law
                  </a>
                </p>
              </div>
            </div>
          </div>

          {/* Right — form */}
          <div className="bg-slate-50 border border-slate-200 rounded-md p-8">
            <form
              action="/api/forms/maple-hart-law"
              method="POST"
              className="space-y-5"
            >
              <div>
                <label
                  htmlFor="clean-name"
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-d80c8b">
                  Your name
                </label>
                <input
                  id="clean-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Jane Smith"
                  className="w-full bg-white text-slate-900 placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-sky-600/30 focus:border-sky-600 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="clean-email"
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-93d503">
                  Email address
                </label>
                <input
                  id="clean-email"
                  type="email"
                  name="email"
                  required
                  placeholder="jane@example.com"
                  className="w-full bg-white text-slate-900 placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-sky-600/30 focus:border-sky-600 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="clean-phone"
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-1b1f4d">
                  Phone <span className="text-slate-400 normal-case font-normal" data-pebble-id="pb-548d68">(optional)</span>
                </label>
                <input
                  id="clean-phone"
                  type="tel"
                  name="phone"
                  placeholder="(212) 555-0100"
                  className="w-full bg-white text-slate-900 placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-sky-600/30 focus:border-sky-600 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="clean-message"
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-baf93e">
                  How can we help?
                </label>
                <textarea
                  id="clean-message"
                  name="message"
                  required
                  rows={4}
                  placeholder="Briefly describe what you need…"
                  className="w-full bg-white text-slate-900 placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-sky-600/30 focus:border-sky-600 transition resize-none"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-sky-600 text-white px-6 py-3 rounded-md font-medium text-sm hover:bg-sky-700 transition tracking-wide" data-pebble-id="pb-40d289">
                Send message
              </button>
            </form>
          </div>

        </div>
      </div>
    </section>
  );
}
