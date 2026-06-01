"use client";
import RevealWords from "@/components/motion/RevealWords";

export default function ContactQuoteTrade() {
  return (
    <section id="contact" className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-16 items-start">

          {/* Left — contact info panel */}
          <div>
            <h2 className="text-{{fg}} text-4xl md:text-5xl font-semibold leading-tight tracking-tight max-w-sm mb-6">
              <RevealWords>{{headline}}</RevealWords>
            </h2>
            <p className="text-slate-600 text-base leading-relaxed mb-10 max-w-xs">
              {{subheadline}}
            </p>

            <div className="space-y-8">

              {/* Phone — tap-to-call */}
              <div>
                <p className="text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em] mb-2">
                  Phone
                </p>
                <a
                  href="tel:{{phone}}"
                  className="text-{{fg}} hover:text-{{accent}} transition focus-visible:ring-2 focus-visible:ring-{{accent}}/50 outline-none min-h-[44px] inline-flex items-center gap-2 text-base"
                >
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
                  {{phone}}
                </a>
              </div>

              {/* Email */}
              <div>
                <p className="text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em] mb-2">
                  Email
                </p>
                <a
                  href="mailto:{{email}}"
                  className="text-{{fg}} hover:text-{{accent}} transition focus-visible:ring-2 focus-visible:ring-{{accent}}/50 outline-none min-h-[44px] inline-flex items-center gap-2 text-base"
                >
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
                  {{email}}
                </a>
              </div>

              {/* Address */}
              <div>
                <p className="text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em] mb-2">
                  Address
                </p>
                <p className="text-slate-600 text-base leading-relaxed flex items-start gap-2">
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
                  {{address}}
                </p>
              </div>

            </div>
          </div>

          {/* Right — quote form */}
          <div className="bg-{{bg}} border border-slate-200 rounded-md p-6 md:p-8">
            <form
              action="/api/forms/{{form_slug}}"
              method="POST"
              className="space-y-5"
            >

              {/* Name */}
              <div>
                <label
                  htmlFor="quote-name"
                  className="block text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em] mb-2"
                >
                  Your name
                </label>
                <input
                  id="quote-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Jane Smith"
                  className="w-full min-h-[44px] bg-white text-{{fg}} placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-{{accent}}/30 focus:border-{{accent}} transition"
                />
              </div>

              {/* Phone */}
              <div>
                <label
                  htmlFor="quote-phone"
                  className="block text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em] mb-2"
                >
                  Phone
                </label>
                <input
                  id="quote-phone"
                  type="tel"
                  inputMode="tel"
                  name="phone"
                  required
                  placeholder="(212) 555-0100"
                  className="w-full min-h-[44px] bg-white text-{{fg}} placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-{{accent}}/30 focus:border-{{accent}} transition"
                />
              </div>

              {/* Service select */}
              <div>
                <label
                  htmlFor="quote-service"
                  className="block text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em] mb-2"
                >
                  Service needed
                </label>
                <select
                  id="quote-service"
                  name="service"
                  required
                  className="w-full min-h-[44px] bg-white text-{{fg}} border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-{{accent}}/30 focus:border-{{accent}} transition"
                >
                  <option value="">Select a service…</option>
                  {/* {{service_options_list_start}} */}
                  <option value="{{service_options[]}}">{{service_options[]}}</option>
                  {/* {{service_options_list_end}} */}
                </select>
              </div>

              {/* Message */}
              <div>
                <label
                  htmlFor="quote-message"
                  className="block text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em] mb-2"
                >
                  Tell us about the job
                </label>
                <textarea
                  id="quote-message"
                  name="message"
                  rows={4}
                  placeholder="Describe the work you need done…"
                  className="w-full bg-white text-{{fg}} placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-{{accent}}/30 focus:border-{{accent}} transition resize-none"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-{{accent}} text-{{accent_fg}} px-6 py-3 rounded-md font-medium text-sm hover:opacity-90 transition tracking-wide min-h-[44px] focus-visible:ring-2 focus-visible:ring-{{accent}}/50 outline-none"
              >
                Request my free quote
              </button>

            </form>
          </div>

        </div>
      </div>
    </section>
  );
}
