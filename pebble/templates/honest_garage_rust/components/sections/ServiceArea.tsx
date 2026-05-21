"use client";
import { motion } from "framer-motion";
import { RefCode } from "@/components/ui/RefCode";
import { SERVICE_AREA_HEADING, SERVICE_AREAS } from "@/content/site";

/**
 * Town list with a rust border-left-2 accent bar on each item per the DNA's
 * section_flow.service_area spec.
 */
export function ServiceArea() {
  if (!SERVICE_AREAS.length) return null;

  return (
    <section className="relative py-20 sm:py-28 border-t border-white/5">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-10 max-w-2xl">
          <RefCode accent>// AREA-MAP-001</RefCode>
          <h2 className="mt-3 stencil text-5xl sm:text-6xl">{SERVICE_AREA_HEADING}</h2>
        </div>

        <ul className="grid grid-cols-2 gap-x-8 gap-y-3 sm:grid-cols-3 lg:grid-cols-4">
          {SERVICE_AREAS.map((area, i) => (
            <motion.li
              key={area}
              initial={{ opacity: 0, x: -8 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.4, delay: i * 0.04, ease: "easeOut" }}
              className="border-l-2 border-primary pl-3 font-mono text-sm uppercase tracking-[0.12em] text-fg/90"
            >
              {area}
            </motion.li>
          ))}
        </ul>
      </div>
    </section>
  );
}
