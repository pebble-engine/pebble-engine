"use client";
import RevealWords from "@/components/motion/RevealWords";

export default function ContactSplitClean() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-start">

          {/* Left — info panel */}
          <div>
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5">
              {{eyebrow}}
            </p>
            <h2 className="text-{{fg}} text-4xl md:text-5xl font-semibold leading-tight tracking-tight max-w-sm mb-8">
              <RevealWords>{{headline}}</RevealWords>
            </h2>
            <p className="text-slate-500 text-base leading-relaxed mb-10 max-w-xs">
              {{form_intro}}
            </p>

            <div className="space-y-8">
              <div>
                <p className="text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em] mb-2">
                  Address
                </p>
                <p className="text-slate-500 text-base leading-relaxed">
                  {{address}}
                </p>
              </div>
              <div>
                <p className="text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em] mb-2">
                  Office hours
                </p>
                <p className="text-slate-500 text-base leading-relaxed whitespace-pre-line">
                  {{hours_text}}
                </p>
              </div>
              <div>
                <p className="text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em] mb-2">
                  Contact
                </p>
                <p className="text-slate-500 text-base">
                  <a href="tel:{{phone}}" className="hover:text-sky-600 transition">
                    {{phone}}
                  </a>
                </p>
                <p className="text-slate-500 text-base mt-1">
                  <a href="mailto:{{email}}" className="hover:text-sky-600 transition">
                    {{email}}
                  </a>
                </p>
              </div>
            </div>
          </div>

          {/* Right — form */}
          <div className="bg-slate-50 border border-slate-200 rounded-md p-8">
            <form
              action="/api/forms/{{form_slug}}"
              method="POST"
              className="space-y-5"
            >
              <div>
                <label
                  htmlFor="clean-name"
                  className="block text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em] mb-2"
                >
                  Your name
                </label>
                <input
                  id="clean-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Jane Smith"
                  className="w-full bg-white text-{{fg}} placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-sky-600/30 focus:border-sky-600 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="clean-email"
                  className="block text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em] mb-2"
                >
                  Email address
                </label>
                <input
                  id="clean-email"
                  type="email"
                  name="email"
                  required
                  placeholder="jane@example.com"
                  className="w-full bg-white text-{{fg}} placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-sky-600/30 focus:border-sky-600 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="clean-phone"
                  className="block text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em] mb-2"
                >
                  Phone <span className="text-slate-400 normal-case font-normal">(optional)</span>
                </label>
                <input
                  id="clean-phone"
                  type="tel"
                  name="phone"
                  placeholder="(212) 555-0100"
                  className="w-full bg-white text-{{fg}} placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-sky-600/30 focus:border-sky-600 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="clean-message"
                  className="block text-{{fg}} text-xs font-semibold uppercase tracking-[0.15em] mb-2"
                >
                  How can we help?
                </label>
                <textarea
                  id="clean-message"
                  name="message"
                  required
                  rows={4}
                  placeholder="Briefly describe what you need…"
                  className="w-full bg-white text-{{fg}} placeholder-slate-300 border border-slate-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-sky-600/30 focus:border-sky-600 transition resize-none"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-sky-600 text-white px-6 py-3 rounded-md font-medium text-sm hover:bg-sky-700 transition tracking-wide"
              >
                Send message
              </button>
            </form>
          </div>

        </div>
      </div>
    </section>
  );
}
