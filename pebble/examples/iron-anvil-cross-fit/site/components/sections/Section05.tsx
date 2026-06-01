"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactCompactBold() {
  return (
    <section className="bg-zinc-900 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-14">
          <p className="text-lime-400 text-xs font-black uppercase tracking-[0.3em] mb-4" data-pebble-id="pb-43bdfb">
            READY TO START
          </p>
          <h2 className="text-zinc-50 text-6xl md:text-8xl font-black uppercase leading-none max-w-3xl" data-pebble-id="pb-ee4a82">
            <RevealWords>MAKE YOUR MOVE.</RevealWords>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">

          {/* Left — form */}
          <div>
            <p className="text-zinc-50/60 text-base leading-relaxed mb-8" data-pebble-id="pb-ef3dd5">
              Send us a message and we'll get back to you within 24 hours. No spam, no pressure — just a straight answer about getting you started.
            </p>

            <form
              action="/api/forms/iron-anvil-crossfit"
              method="POST"
              className="space-y-4"
            >
              <div>
                <label
                  htmlFor="cb-name"
                  className="block text-zinc-50 text-xs font-black uppercase tracking-[0.2em] mb-2" data-pebble-id="pb-b76bd1">
                  Name
                </label>
                <input
                  id="cb-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Your name"
                  className="w-full bg-zinc-50/5 text-zinc-50 placeholder-zinc-50/20 border border-zinc-50/20 rounded-md px-5 py-4 text-base focus:outline-none focus:ring-2 focus:ring-lime-400 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="cb-email"
                  className="block text-zinc-50 text-xs font-black uppercase tracking-[0.2em] mb-2" data-pebble-id="pb-1baabb">
                  Email
                </label>
                <input
                  id="cb-email"
                  type="email"
                  name="email"
                  required
                  placeholder="your@email.com"
                  className="w-full bg-zinc-50/5 text-zinc-50 placeholder-zinc-50/20 border border-zinc-50/20 rounded-md px-5 py-4 text-base focus:outline-none focus:ring-2 focus:ring-lime-400 transition"
                />
              </div>

              <div>
                <label
                  htmlFor="cb-message"
                  className="block text-zinc-50 text-xs font-black uppercase tracking-[0.2em] mb-2" data-pebble-id="pb-27df43">
                  Message
                </label>
                <textarea
                  id="cb-message"
                  name="message"
                  required
                  rows={4}
                  placeholder="What do you need?"
                  className="w-full bg-zinc-50/5 text-zinc-50 placeholder-zinc-50/20 border border-zinc-50/20 rounded-md px-5 py-4 text-base focus:outline-none focus:ring-2 focus:ring-lime-400 transition resize-none"
                />
              </div>

              <button
                type="submit"
                className="bg-lime-400 text-zinc-900 px-10 py-4 rounded-md font-black uppercase tracking-widest text-sm hover:scale-105 hover:bg-zinc-50 transition-all duration-150 w-full md:w-auto" data-pebble-id="pb-8d4f8e">
                Send it
              </button>
            </form>
          </div>

          {/* Right — contact details, bold and sparse */}
          <div className="space-y-10 md:pt-28">
            <div>
              <h3 className="text-zinc-50 text-xs font-black uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-ee0788">
                Location
              </h3>
              <p className="text-zinc-50/60 text-base leading-relaxed" data-pebble-id="pb-8b554b">
                412 Eastgate Blvd, East Side District
              </p>
            </div>

            <div>
              <h3 className="text-zinc-50 text-xs font-black uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-fb5227">
                Hours
              </h3>
              <p className="text-zinc-50/60 text-base leading-relaxed whitespace-pre-line" data-pebble-id="pb-66c632">
                Mon–Fri 5:30am–8pm | Sat 7am–12pm | Sun 8am–11am
              </p>
            </div>

            <div>
              <h3 className="text-zinc-50 text-xs font-black uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-750dfd">
                Contact
              </h3>
              <p className="text-zinc-50/60 text-base" data-pebble-id="pb-49870c">
                <a href="tel:(555) 874-2600" className="hover:text-lime-400 transition font-bold" data-pebble-id="pb-b12fd4">
                  (555) 874-2600
                </a>
              </p>
              <p className="text-zinc-50/60 text-base mt-1" data-pebble-id="pb-1c6a79">
                <a href="mailto:hello@ironanvilcrossfit.com" className="hover:text-lime-400 transition" data-pebble-id="pb-0d4a56">
                  hello@ironanvilcrossfit.com
                </a>
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
