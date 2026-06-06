"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactQuoteTrade() {
  return (
    <section id="contact" className="bg-stone-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-16 items-start">

          {/* Left — contact info panel */}
          <div>
            <h2 className="text-stone-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight max-w-sm mb-6" data-pebble-id="pb-8f633e">
              <RevealWords>Request Your Free In-Home Estimate</RevealWords>
            </h2>
            <p className="text-slate-600 text-base leading-relaxed mb-10 max-w-xs" data-pebble-id="pb-6ccfc3">
              Tell us about your project and we'll get back to you within one business day to schedule a no-obligation consultation.
            </p>

            <div className="space-y-8">

              {/* Phone — tap-to-call */}
              <div>
                <p className="text-stone-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-15625a">
                  Phone
                </p>
                <a
                  href="tel:(208) 555-0187"
                  className="text-stone-900 hover:text-amber-700 transition focus-visible:ring-2 focus-visible:ring-amber-700/50 outline-none min-h-[44px] inline-flex items-center gap-2 text-base" data-pebble-id="pb-c48b26">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.6 1.18h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.73a16 16 0 0 0 5.63 5.63l1.62-1.62a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 14.92z" />
                  </svg>
                  (208) 555-0187
                </a>
              </div>

              {/* Email */}
              <div>
                <p className="text-stone-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-6544cf">
                  Email
                </p>
                <a
                  href="mailto:hello@ridgelinebuildersboise.com"
                  className="text-stone-900 hover:text-amber-700 transition focus-visible:ring-2 focus-visible:ring-amber-700/50 outline-none min-h-[44px] inline-flex items-center gap-2 text-base" data-pebble-id="pb-04eb96">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                    <polyline points="22,6 12,13 2,6" />
                  </svg>
                  hello@ridgelinebuildersboise.com
                </a>
              </div>

              {/* Address */}
              <div>
                <p className="text-stone-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-6d94b1">
                  Address
                </p>
                <p className="text-slate-600 text-base leading-relaxed flex items-start gap-2" data-pebble-id="pb-690123">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="mt-0.5 shrink-0"
                    aria-hidden="true"
                  >
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                    <circle cx="12" cy="10" r="3" />
                  </svg>
                  Serving Boise and the Treasure Valley, ID
                </p>
              </div>

            </div>
          </div>

          {/* Right — quote form */}
          <div className="bg-stone-50 border border-slate-200 rounded-md p-6 md:p-8">
            <form
              action="/api/forms/ridgeline-builders-estimate"
              method="POST"
              className="space-y-5"
            >

              {/* Name */}
              <div>
                <label
                  htmlFor="quote-name"
                  className="block text-stone-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-cf3b04">
                  Your name
                </label>
                <input
                  id="quote-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Jane Smith"
                  className="w-full min-h-[44px] bg-white text-stone-900 placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-amber-700/30 focus:border-amber-700 transition"
                />
              </div>

              {/* Phone */}
              <div>
                <label
                  htmlFor="quote-phone"
                  className="block text-stone-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-d703b9">
                  Phone
                </label>
                <input
                  id="quote-phone"
                  type="tel"
                  inputMode="tel"
                  name="phone"
                  required
                  placeholder="(212) 555-0100"
                  className="w-full min-h-[44px] bg-white text-stone-900 placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-amber-700/30 focus:border-amber-700 transition"
                />
              </div>

              {/* Service select */}
              <div>
                <label
                  htmlFor="quote-service"
                  className="block text-stone-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-9dc41c">
                  Service needed
                </label>
                <select
                  id="quote-service"
                  name="service"
                  required
                  className="w-full min-h-[44px] bg-white text-stone-900 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-amber-700/30 focus:border-amber-700 transition"
                >
                  <option value="">Select a service…</option>
                  
                  <option value="Whole-Home Remodel">Whole-Home Remodel</option>
                  
                  <option value="Room Addition">Room Addition</option>
                  
                  <option value="Kitchen Renovation">Kitchen Renovation</option>
                  
                  <option value="Bathroom Upgrade">Bathroom Upgrade</option>
                  
                  <option value="Custom Deck & Outdoor Living">Custom Deck & Outdoor Living</option>
                  
                  <option value="Other / Not Sure Yet">Other / Not Sure Yet</option>
                  
                </select>
              </div>

              {/* Message */}
              <div>
                <label
                  htmlFor="quote-message"
                  className="block text-stone-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-81da73">
                  Tell us about the job
                </label>
                <textarea
                  id="quote-message"
                  name="message"
                  rows={4}
                  placeholder="Describe the work you need done…"
                  className="w-full bg-white text-stone-900 placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-amber-700/30 focus:border-amber-700 transition resize-none"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-amber-700 text-stone-50 px-6 py-3 rounded-md font-medium text-sm hover:opacity-90 transition tracking-wide min-h-[44px] focus-visible:ring-2 focus-visible:ring-amber-700/50 outline-none" data-pebble-id="pb-8c4190">
                Request my free quote
              </button>

            </form>
          </div>

        </div>
      </div>
    </section>
  );
}
