"use client";
import RevealWords from "@/components/motion/RevealWords";

export default function ContactCompactBold() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-14">
          <p className="text-{{accent}} text-xs font-black uppercase tracking-[0.3em] mb-4">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-6xl md:text-8xl font-black uppercase leading-none max-w-3xl">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">

          {/* Left — form */}
          <div>
            <p className="text-{{fg}}/60 text-base leading-relaxed mb-8">
              {{form_intro}}
            </p>

            <form
              action="/api/forms/{{form_slug}}"
              method="POST"
              className="space-y-4"
            >
              <div>
                <label
                  htmlFor="cb-name"
                  className="block text-{{fg}} text-xs font-black uppercase tracking-[0.2em] mb-2"
                >
                  Name
                </label>
                <input
                  id="cb-name"
                  type="text"
                  name="name"
                  required
                  placeholder="Your name"
                  className="w-full bg-{{fg}}/5 text-{{fg}} placeholder-{{fg}}/20 border border-{{fg}}/20 rounded-md px-5 py-4 text-base focus:outline-none focus:ring-2 focus:ring-{{accent}} transition"
                />
              </div>

              <div>
                <label
                  htmlFor="cb-email"
                  className="block text-{{fg}} text-xs font-black uppercase tracking-[0.2em] mb-2"
                >
                  Email
                </label>
                <input
                  id="cb-email"
                  type="email"
                  name="email"
                  required
                  placeholder="your@email.com"
                  className="w-full bg-{{fg}}/5 text-{{fg}} placeholder-{{fg}}/20 border border-{{fg}}/20 rounded-md px-5 py-4 text-base focus:outline-none focus:ring-2 focus:ring-{{accent}} transition"
                />
              </div>

              <div>
                <label
                  htmlFor="cb-message"
                  className="block text-{{fg}} text-xs font-black uppercase tracking-[0.2em] mb-2"
                >
                  Message
                </label>
                <textarea
                  id="cb-message"
                  name="message"
                  required
                  rows={4}
                  placeholder="What do you need?"
                  className="w-full bg-{{fg}}/5 text-{{fg}} placeholder-{{fg}}/20 border border-{{fg}}/20 rounded-md px-5 py-4 text-base focus:outline-none focus:ring-2 focus:ring-{{accent}} transition resize-none"
                />
              </div>

              <button
                type="submit"
                className="bg-{{accent}} text-{{bg}} px-10 py-4 rounded-md font-black uppercase tracking-widest text-sm hover:scale-105 hover:bg-{{fg}} transition-all duration-150 w-full md:w-auto"
              >
                Send it
              </button>
            </form>
          </div>

          {/* Right — contact details, bold and sparse */}
          <div className="space-y-10 md:pt-28">
            <div>
              <h3 className="text-{{fg}} text-xs font-black uppercase tracking-[0.2em] mb-3">
                Location
              </h3>
              <p className="text-{{fg}}/60 text-base leading-relaxed">
                {{address}}
              </p>
            </div>

            <div>
              <h3 className="text-{{fg}} text-xs font-black uppercase tracking-[0.2em] mb-3">
                Hours
              </h3>
              <p className="text-{{fg}}/60 text-base leading-relaxed whitespace-pre-line">
                {{hours_text}}
              </p>
            </div>

            <div>
              <h3 className="text-{{fg}} text-xs font-black uppercase tracking-[0.2em] mb-3">
                Contact
              </h3>
              <p className="text-{{fg}}/60 text-base">
                <a href="tel:{{phone}}" className="hover:text-{{accent}} transition font-bold">
                  {{phone}}
                </a>
              </p>
              <p className="text-{{fg}}/60 text-base mt-1">
                <a href="mailto:{{email}}" className="hover:text-{{accent}} transition">
                  {{email}}
                </a>
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
