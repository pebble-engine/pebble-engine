"use client";
import { motion } from "framer-motion";
import { TESTIMONIALS } from "@/content/site";

/**
 * Renders NOTHING if TESTIMONIALS is empty. This is intentional — the template
 * ships honest by default (no fake reviews). The customer fills the array in
 * after launch, after which this section appears.
 */
export function Testimonials() {
  if (!TESTIMONIALS.length) return null;

  return (
    <section id="testimonials" className="relative py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            From our customers
          </p>
          <h2 className="mt-3 font-display text-4xl font-bold tracking-tight text-fg sm:text-5xl">
            What they say
          </h2>
        </div>

        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {TESTIMONIALS.map((t, i) => (
            <motion.figure
              key={`${t.author}-${i}`}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, delay: i * 0.06 }}
              className="glass-card flex flex-col gap-4 rounded-2xl p-6"
            >
              <span className="flex" aria-hidden="true">
                {Array.from({ length: 5 }).map((_, n) => (
                  <svg key={n} width="14" height="14" viewBox="0 0 24 24" fill="#fbbf24">
                    <path d="M12 2 14.85 8.78 22 9.27l-5.47 4.73L18.18 21 12 17.27 5.82 21l1.65-6.99L2 9.27l7.15-.49L12 2z" />
                  </svg>
                ))}
              </span>
              <blockquote className="text-sm text-body">&ldquo;{t.quote}&rdquo;</blockquote>
              <figcaption className="mt-auto text-xs uppercase tracking-widest text-subtle">
                {t.author}
                {t.location ? ` · ${t.location}` : ""}
              </figcaption>
            </motion.figure>
          ))}
        </div>
      </div>
    </section>
  );
}
