"use client";
import { motion } from "framer-motion";
import { RefCode } from "@/components/ui/RefCode";
import { TESTIMONIALS, TESTIMONIALS_REF } from "@/content/site";

/**
 * Renders NOTHING if TESTIMONIALS is empty. This is intentional — the template
 * ships honest by default (no fake reviews). The customer fills the array in
 * after launch, after which this section appears.
 *
 * Per the auto_honest_diag DNA: three glass cards, oversized serif quote glyph,
 * italic body, uppercase mono author + city below a thin top border.
 */
export function Testimonials() {
  if (!TESTIMONIALS.length) return null;

  return (
    <section id="testimonials" className="relative py-20 sm:py-28 border-t border-white/5">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-12 max-w-2xl">
          <RefCode accent>// {TESTIMONIALS_REF}</RefCode>
          <h2 className="mt-3 stencil text-5xl sm:text-6xl">WORD OF MOUTH</h2>
        </div>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {TESTIMONIALS.map((t, i) => (
            <motion.figure
              key={`${t.author}-${i}`}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="glass-card flex flex-col gap-4 p-7"
            >
              <span className="font-display text-6xl leading-none text-primary/60" aria-hidden="true">
                &ldquo;
              </span>
              <blockquote className="italic text-base text-body">{t.quote}</blockquote>
              <figcaption className="mt-auto border-t border-white/10 pt-4 font-mono text-[10px] uppercase tracking-[0.14em] text-fg/80">
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
