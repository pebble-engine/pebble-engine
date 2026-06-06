"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactQuoteTrade() {
  return (
    <section id="contact" className="bg-slate-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-16 items-start">

          {/* Left — contact info panel */}
          <div>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight max-w-sm mb-6" data-pebble-id="pb-eacfb0">
              <RevealWords>Get Your Free Estimate Today</RevealWords>
            </h2>
            <p className="text-slate-600 text-base leading-relaxed mb-10 max-w-xs" data-pebble-id="pb-3fecf0">
              Fill out the form and we'll get back to you fast — usually the same day. Written estimates always included.
            </p>

            <div className="space-y-8">

              {/* Phone — tap-to-call */}
              <div>
                <p className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-7d1af4">
                  Phone
                </p>
                <a
                  href="tel:(816) 555-0190"
                  className="text-slate-900 hover:text-sky-700 transition focus-visible:ring-2 focus-visible:ring-sky-700/50 outline-none min-h-[44px] inline-flex items-center gap-2 text-base" data-pebble-id="pb-c6b5c7">
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
                  (816) 555-0190
                </a>
              </div>

              {/* Email */}
              <div>
                <p className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-128699">
                  Email
                </p>
                <a
                  href="mailto:info@summitridgeroofing.com"
                  className="text-slate-900 hover:text-sky-700 transition focus-visible:ring-2 focus-visible:ring-sky-700/50 outline-none min-h-[44px] inline-flex items-center gap-2 text-base" data-pebble-id="pb-a01081">
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
                  info@summitridgeroofing.com
                </a>
              </div>

              {/* Address */}
              <div>
                <p className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-61aa92">
                  Address
                </p>
                <p className="text-slate-600 text-base leading-relaxed flex items-start gap-2" data-pebble-id="pb-b81112">
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
                  Serving Kansas City, MO and surrounding areas
                </p>
              </div>

            </div>
          </div>

          {/* Right — quote form */}
          <div className="bg-slate-50 border border-slate-200 rounded-md p-6 md:p-8">
            <form
              action="/api/forms/summit-ridge-roofing-contact"
              method="POST"
              className="space-y-5"
            >

              {/* Name */}
              <div>
                <label
                  htmlFor="quote-name"
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-9484b4">
                  Your name
                </label>
                <input
                  id="quote-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Jane Smith"
                  className="w-full min-h-[44px] bg-white text-slate-900 placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-sky-700/30 focus:border-sky-700 transition"
                />
              </div>

              {/* Phone */}
              <div>
                <label
                  htmlFor="quote-phone"
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-e1b8a0">
                  Phone
                </label>
                <input
                  id="quote-phone"
                  type="tel"
                  inputMode="tel"
                  name="phone"
                  required
                  placeholder="(212) 555-0100"
                  className="w-full min-h-[44px] bg-white text-slate-900 placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-sky-700/30 focus:border-sky-700 transition"
                />
              </div>

              {/* Service select */}
              <div>
                <label
                  htmlFor="quote-service"
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-4e29f2">
                  Service needed
                </label>
                <select
                  id="quote-service"
                  name="service"
                  required
                  className="w-full min-h-[44px] bg-white text-slate-900 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-sky-700/30 focus:border-sky-700 transition"
                >
                  <option value="">Select a service…</option>
                  
                  <option value="Full Roof Replacement">Full Roof Replacement</option>
                  
                  <option value="Storm Damage Repair">Storm Damage Repair</option>
                  
                  <option value="Insurance Claim Assistance">Insurance Claim Assistance</option>
                  
                  <option value="Residential Inspection">Residential Inspection</option>
                  
                  <option value="Gutter Installation">Gutter Installation</option>
                  
                  <option value="Gutter Cleaning">Gutter Cleaning</option>
                  
                  <option value="Not Sure — Need an Inspection">Not Sure — Need an Inspection</option>
                  
                </select>
              </div>

              {/* Message */}
              <div>
                <label
                  htmlFor="quote-message"
                  className="block text-slate-900 text-xs font-semibold uppercase tracking-[0.15em] mb-2" data-pebble-id="pb-1c77c5">
                  Tell us about the job
                </label>
                <textarea
                  id="quote-message"
                  name="message"
                  rows={4}
                  placeholder="Describe the work you need done…"
                  className="w-full bg-white text-slate-900 placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-sky-700/30 focus:border-sky-700 transition resize-none"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-sky-700 text-slate-50 px-6 py-3 rounded-md font-medium text-sm hover:opacity-90 transition tracking-wide min-h-[44px] focus-visible:ring-2 focus-visible:ring-sky-700/50 outline-none" data-pebble-id="pb-0eab93">
                Request my free quote
              </button>

            </form>
          </div>

        </div>
      </div>
    </section>
  );
}
