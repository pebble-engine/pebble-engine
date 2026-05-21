"use client";

import * as React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { CategoryCard } from "@/components/ui/CategoryCard";
import { ScriptText } from "@/components/ui/ScriptText";
import {
  PRODUCT_CATEGORIES,
  CATEGORIES_EYEBROW,
  CATEGORIES_HEADLINE,
  CATEGORIES_SCRIPT_ACCENT,
} from "@/content/site";

/**
 * CategoryGrid — 2x2 grid of square category tiles. Each tile is a stylized
 * CategoryCard with imagery + italic Bodoni name + tracked "Shop now ->" label.
 */
export function CategoryGrid() {
  const reduce = useReducedMotion();

  return (
    <section
      aria-labelledby="categories-heading"
      className="bg-surface"
    >
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="mb-12 md:mb-16 flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div className="max-w-2xl">
            <p className="text-label mb-3">{CATEGORIES_EYEBROW}</p>
            <h2 id="categories-heading" className="text-headline italic">
              {CATEGORIES_HEADLINE}
            </h2>
            <ScriptText className="text-3xl md:text-4xl block mt-2">
              {CATEGORIES_SCRIPT_ACCENT}
            </ScriptText>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 md:gap-6">
          {PRODUCT_CATEGORIES.map((cat, i) => (
            <motion.div
              key={cat.id}
              initial={{ opacity: 0, y: reduce ? 0 : 32 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.8, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] }}
            >
              <CategoryCard
                name={cat.name}
                description={cat.description}
                imageUrl={cat.image_url}
                href={cat.href}
              />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
