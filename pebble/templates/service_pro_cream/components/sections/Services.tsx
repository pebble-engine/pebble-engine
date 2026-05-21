"use client";
import { motion } from "framer-motion";
import { ServiceCard } from "@/components/ui/ServiceCard";
import { SERVICES } from "@/content/site";

export function Services() {
  if (!SERVICES.length) return null;

  return (
    <section id="services" className="relative py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            What we do
          </p>
          <h2 className="mt-3 font-display text-4xl font-bold tracking-tight text-fg sm:text-5xl">
            Services built for <span className="gradient-text">every property</span>
          </h2>
          <p className="mt-4 text-base text-muted">
            Pick the program that matches your needs. Every job starts with a free inspection.
          </p>
        </div>

        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {SERVICES.map((service, i) => (
            <motion.div
              key={service.id}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, delay: i * 0.06, ease: "easeOut" }}
            >
              <ServiceCard service={service} />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
