"use client";
import { motion } from "framer-motion";
import { TESTIMONIALS } from "@/content/site";

/**
 * Renders NOTHING if TESTIMONIALS is empty — by design.
 * The template ships honest by default (no fake reviews).
 * The customer fills the array after launch, then this section appears.
 */
export function Testimonials() {
  if (!TESTIMONIALS.length) return null;

  return (
    <section id="testimonials" className="relative py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-bold uppercase tracking-wide-15 text-accent">
            Student Reviews
          </p>
          <h2 className="mt-3 font-display text-4xl font-black uppercase tracking-headline text-fg sm:text-5xl">
            What They <span className="text-gold-gradient">Say</span>
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
              className="glass flex flex-col gap-4 rounded-2xl p-6"
            >
              <span className="flex" aria-hidden="true">
                {Array.from({ length: 5 }).map((_, n) => (
                  <svg key={n} width="14" height="14" viewBox="0 0 24 24" fill="#FBBF24">
                    <path d="M12 2 14.85 8.78 22 9.27l-5.47 4.73L18.18 21 12 17.27 5.82 21l1.65-6.99L2 9.27l7.15-.49L12 2z" />
                  </svg>
                ))}
              </span>
              <blockquote className="text-sm text-body leading-relaxed">
                &ldquo;{t.quote}&rdquo;
              </blockquote>
              <figcaption className="mt-auto text-xs font-bold uppercase tracking-wide-15 text-subtle">
                {t.author}
                {t.course ? ` · ${t.course}` : ""}
              </figcaption>
            </motion.figure>
          ))}
        </div>
      </div>
    </section>
  );
}
