"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactSplitClean() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-start">

          {/* Left — info panel */}
          <div>
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-d5808b">
              Get in touch
            </p>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight max-w-sm mb-8" data-pebble-id="pb-c8ce1d">
              <RevealWords>Schedule your free 20-minute Shoebox Review.</RevealWords>
            </h2>
            <p className="text-slate-500 text-base leading-relaxed mb-10 max-w-xs" data-pebble-id="pb-1ec947">
              Fill out the form and we'll get back to you within one business day to set up your free review. No commitment, no sales pitch — just a straight assessment of where you stand.
            </p>

            <div className="space-y-8">
              <div>
                <p className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-2ad81a">
                  Address
                </p>
                <p className="text-slate-500 text-base leading-relaxed" data-pebble-id="pb-35ce80">
                  412 Maple Street, Suite 3, Millbrook, OH 44101
                </p>
              </div>
              <div>
                <p className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-8f84b4">
                  Office hours
                </p>
                <p className="text-slate-500 text-base leading-relaxed whitespace-pre-line" data-pebble-id="pb-4e62eb">
                  Monday – Friday, 9am – 5pm
Evening appointments available by request
                </p>
              </div>
              <div>
                <p className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-2b6b24">
                  Contact
                </p>
                <p className="text-slate-500 text-base" data-pebble-id="pb-724d42">
                  <a href="tel:(330) 555-0182" className="hover:text-sky-600 transition" data-pebble-id="pb-401937">
                    (330) 555-0182
                  </a>
                </p>
                <p className="text-slate-500 text-base mt-1" data-pebble-id="pb-00fba3">
                  <a href="mailto:hello@mapleandledger.com" className="hover:text-sky-600 transition" data-pebble-id="pb-107b70">
                    hello@mapleandledger.com
                  </a>
                </p>
              </div>
            </div>
          </div>

          {/* Right — form */}
          <div className="bg-slate-50 border border-slate-200 rounded-md p-8">
            <form
              action="/api/forms/maple-and-ledger-contact"
              method="POST"
              className="space-y-5"
            >
              <div>
                <label
                  htmlFor="clean-name"
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-bf8f5c">
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
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-fbd50a">
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
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-9791f9">
                  Phone <span className="text-slate-400 normal-case font-normal" data-pebble-id="pb-8ffb42">(optional)</span>
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
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-7a9568">
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
                className="w-full bg-sky-600 text-white px-6 py-3 rounded-md font-medium text-sm hover:bg-sky-700 transition tracking-wide" data-pebble-id="pb-c0d46f">
                Send message
              </button>
            </form>
          </div>

        </div>
      </div>
    </section>
  );
}
