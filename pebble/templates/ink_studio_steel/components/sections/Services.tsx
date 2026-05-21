"use client";

import * as React from "react";
import { motion, useReducedMotion } from "framer-motion";
import {
  SERVICES,
  SERVICES_EYEBROW,
  SERVICES_HEADLINE,
} from "@/content/site";

/**
 * Services — three-column block listing the studio's core offerings.
 * Numeric eyebrow (01/02/03), blackletter title, body copy. The columns
 * sit on the elevated card background to create a visual shelf within
 * the dark page.
 */
export function Services() {
  const reduce = useReducedMotion();

  return (
    <section
      aria-labelledby="services-heading"
      className="bg-ink-secondary border-y border-ink-border"
    >
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="mb-12 md:mb-16 max-w-2xl">
          <p className="text-eyebrow mb-4">{SERVICES_EYEBROW}</p>
          <h2 id="services-heading" className="text-headline">
            {SERVICES_HEADLINE}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 md:gap-12">
          {SERVICES.map((service, i) => (
            <motion.div
              key={service.id}
              initial={{ opacity: 0, y: reduce ? 0 : 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.7, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
              className="flex flex-col gap-4 border border-ink-border bg-ink-card p-8 md:p-10 hover:border-ink-primary/60 transition-colors duration-500"
            >
              <span className="text-eyebrow text-ink-primary">
                0{i + 1}
              </span>
              <h3 className="font-display text-3xl md:text-4xl text-ink-fg leading-tight">
                {service.name}
              </h3>
              <p className="text-body-lg">{service.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
