"use client";
import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { RefCode } from "@/components/ui/RefCode";
import { ImgRefTag } from "@/components/ui/ImgRefTag";
import { SERVICES } from "@/content/site";

/**
 * Service directory — alternating two-column image/text blocks per the DNA's
 * section_flow.services spec. Each block:
 *   - SVC-XXX // SVC-NAME ref code header
 *   - stencil-hollow heading
 *   - body paragraph + 'See details' link
 *   - photo with a warm-amber IMG-REF-XXXXX corner tag
 *   - slides from opposite sides on scroll-into-view
 */
export function Services() {
  if (!SERVICES.length) return null;

  return (
    <section id="services" className="relative py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        {/* Section header */}
        <div className="mb-16 max-w-2xl">
          <RefCode accent>// SVC-DIR-001</RefCode>
          <h2 className="mt-3 stencil text-5xl sm:text-6xl">WHAT WE FIX</h2>
          <p className="mt-4 text-base text-muted">
            Every service starts with a real diagnosis. Written estimate before any work
            begins.
          </p>
        </div>

        <div className="space-y-20 sm:space-y-28">
          {SERVICES.map((service, i) => {
            const flipped = i % 2 === 1;
            return (
              <div
                key={service.id}
                id={service.id}
                className={
                  flipped
                    ? "grid gap-10 lg:grid-cols-2 lg:items-center"
                    : "grid gap-10 lg:grid-cols-2 lg:items-center"
                }
              >
                {/* Text column */}
                <motion.div
                  initial={{ opacity: 0, x: flipped ? 48 : -48 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: "-80px" }}
                  transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                  className={flipped ? "lg:order-2" : ""}
                >
                  <RefCode accent>
                    {service.ref} // {service.name}
                  </RefCode>
                  <h3 className="mt-3 stencil text-4xl sm:text-5xl">{service.name}</h3>
                  <p className="mt-2 font-mono text-xs uppercase tracking-[0.12em] text-primary">
                    {service.short}
                  </p>
                  <p className="mt-5 text-base text-body">{service.description}</p>
                  <Link
                    href="/contact"
                    className="mt-6 inline-flex items-center gap-2 font-mono text-xs font-bold uppercase tracking-[0.12em] text-primary hover:text-fg transition-colors"
                  >
                    Request estimate <ArrowIcon />
                  </Link>
                </motion.div>

                {/* Image column */}
                <motion.div
                  initial={{ opacity: 0, x: flipped ? -48 : 48 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: "-80px" }}
                  transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                  className={
                    flipped
                      ? "lg:order-1 relative aspect-[4/3] overflow-hidden border border-white/10 group"
                      : "relative aspect-[4/3] overflow-hidden border border-white/10 group"
                  }
                >
                  <Image
                    src={service.image}
                    alt=""
                    fill
                    sizes="(min-width: 1024px) 50vw, 100vw"
                    className="object-cover transition-all duration-700 group-hover:scale-105"
                    style={{ filter: "grayscale(0.6) contrast(1.1)" }}
                  />
                  <ImgRefTag code={service.imageRef} />
                </motion.div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function ArrowIcon() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M5 12h14M13 5l7 7-7 7" />
    </svg>
  );
}
