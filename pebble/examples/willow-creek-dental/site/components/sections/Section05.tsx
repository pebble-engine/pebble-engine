"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactSplitClean() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-start">

          {/* Left — info panel */}
          <div>
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-f745b7">
              Request an appointment
            </p>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight max-w-sm mb-8" data-pebble-id="pb-75826e">
              <RevealWords>Schedule a visit — we'll find a time that works for you</RevealWords>
            </h2>
            <p className="text-slate-500 text-base leading-relaxed mb-10 max-w-xs" data-pebble-id="pb-448b8f">
              Fill out the form and we'll follow up within one business day to confirm your appointment. New patients are always welcome. No referral needed.
            </p>

            <div className="space-y-8">
              <div>
                <p className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-b8c211">
                  Address
                </p>
                <p className="text-slate-500 text-base leading-relaxed" data-pebble-id="pb-701264">
                  214 Willow Creek Road, Suite 101, Maplewood, NJ 07040
                </p>
              </div>
              <div>
                <p className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-e9dde7">
                  Office hours
                </p>
                <p className="text-slate-500 text-base leading-relaxed whitespace-pre-line" data-pebble-id="pb-923b57">
                  Monday – Thursday, 8am – 5pm
Friday, 8am – 2pm
Saturday by appointment
                </p>
              </div>
              <div>
                <p className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-04039e">
                  Contact
                </p>
                <p className="text-slate-500 text-base" data-pebble-id="pb-afc214">
                  <a href="tel:(973) 555-0184" className="hover:text-sky-600 transition" data-pebble-id="pb-efb87e">
                    (973) 555-0184
                  </a>
                </p>
                <p className="text-slate-500 text-base mt-1" data-pebble-id="pb-7a984f">
                  <a href="mailto:hello@willowcreekdental.com" className="hover:text-sky-600 transition" data-pebble-id="pb-0c363f">
                    hello@willowcreekdental.com
                  </a>
                </p>
              </div>
            </div>
          </div>

          {/* Right — form */}
          <div className="bg-slate-50 border border-slate-200 rounded-md p-8">
            <form
              action="/api/forms/willow-creek-dental"
              method="POST"
              className="space-y-5"
            >
              <div>
                <label
                  htmlFor="clean-name"
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-f36901">
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
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-97cd75">
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
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-98e677">
                  Phone <span className="text-slate-400 normal-case font-normal" data-pebble-id="pb-a9eb7c">(optional)</span>
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
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-6b5bc0">
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
                className="w-full bg-sky-600 text-white px-6 py-3 rounded-md font-medium text-sm hover:bg-sky-700 transition tracking-wide" data-pebble-id="pb-fde54c">
                Send message
              </button>
            </form>
          </div>

        </div>
      </div>
    </section>
  );
}
