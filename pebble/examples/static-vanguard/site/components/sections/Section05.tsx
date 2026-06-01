"use client";

import RevealWords from "@/components/motion/RevealWords";

export default function ContactCompactBold() {
  return (
    <section className="bg-zinc-900 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-14">
          <p className="text-lime-400 text-xs font-black uppercase tracking-[0.3em] mb-4" data-pebble-id="pb-11e74d">
            PARTNER WITH US
          </p>
          <h2 className="text-zinc-50 text-6xl md:text-8xl font-black uppercase leading-none max-w-3xl" data-pebble-id="pb-9f1653">
            <RevealWords>LET'S MAKE SOME NOISE.</RevealWords>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">

          {/* Left — form */}
          <div>
            <p className="text-zinc-50/60 text-base leading-relaxed mb-8" data-pebble-id="pb-ab3999">
              Whether you're a brand looking for your next play or a player wanting to try out — drop us a message. We reply within 24 hours. No bots. No run-around.
            </p>

            <form
              action="/api/forms/static-vanguard-contact"
              method="POST"
              className="space-y-4"
            >
              <div>
                <label
                  htmlFor="cb-name"
                  className="block text-zinc-50 text-xs font-black uppercase tracking-[0.2em] mb-2" data-pebble-id="pb-fa9d9c">
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
                  className="block text-zinc-50 text-xs font-black uppercase tracking-[0.2em] mb-2" data-pebble-id="pb-052ba9">
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
                  className="block text-zinc-50 text-xs font-black uppercase tracking-[0.2em] mb-2" data-pebble-id="pb-759fe8">
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
                className="bg-lime-400 text-zinc-900 px-10 py-4 rounded-md font-black uppercase tracking-widest text-sm hover:scale-105 hover:bg-zinc-50 transition-all duration-150 w-full md:w-auto" data-pebble-id="pb-4c01f2">
                Send it
              </button>
            </form>
          </div>

          {/* Right — contact details, bold and sparse */}
          <div className="space-y-10 md:pt-28">
            <div>
              <h3 className="text-zinc-50 text-xs font-black uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-f75761">
                Location
              </h3>
              <p className="text-zinc-50/60 text-base leading-relaxed" data-pebble-id="pb-a2b07d">
                Online-first org — based in Los Angeles, CA
              </p>
            </div>

            <div>
              <h3 className="text-zinc-50 text-xs font-black uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-b584c7">
                Hours
              </h3>
              <p className="text-zinc-50/60 text-base leading-relaxed whitespace-pre-line" data-pebble-id="pb-26f041">
                Mon–Fri, 10am–8pm PT. Match nights: always live.
              </p>
            </div>

            <div>
              <h3 className="text-zinc-50 text-xs font-black uppercase tracking-[0.2em] mb-3" data-pebble-id="pb-9b5c53">
                Contact
              </h3>
              <p className="text-zinc-50/60 text-base" data-pebble-id="pb-16093c">
                <a href="tel:+1 (213) 555-0194" className="hover:text-lime-400 transition font-bold" data-pebble-id="pb-18465a">
                  +1 (213) 555-0194
                </a>
              </p>
              <p className="text-zinc-50/60 text-base mt-1" data-pebble-id="pb-603e40">
                <a href="mailto:partners@staticvanguard.gg" className="hover:text-lime-400 transition" data-pebble-id="pb-20b35c">
                  partners@staticvanguard.gg
                </a>
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
