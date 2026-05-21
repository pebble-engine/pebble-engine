"use client";

import * as React from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { EyebrowChip } from "@/components/ui/EyebrowChip";
import { MenuCard } from "@/components/ui/MenuCard";
import { cn } from "@/lib/cn";
import {
  MENU_CATEGORIES,
  MENU_EYEBROW,
  MENU_HEADLINE,
  MENU_INTRO,
  MENU_ITEMS,
} from "@/content/site";

type Props = {
  /** When true, every item renders without the filter strip. Used on /menu. */
  showAllNoFilter?: boolean;
};

/**
 * Menu — DNA's filterable_masonry_columns adapted for the cafe bar.
 * Chip filters (All / Espresso / Brew / Bakery / Breakfast) drive a CSS columns
 * masonry. Each tile is a MenuCard with photo, name, description, price.
 * Returns null if MENU_ITEMS is empty (anti-slop).
 */
export function Menu({ showAllNoFilter = false }: Props) {
  const reduce = useReducedMotion();
  const [active, setActive] = React.useState<string>("All");

  if (MENU_ITEMS.length === 0) {
    return null;
  }

  const filtered =
    showAllNoFilter || active === "All"
      ? MENU_ITEMS
      : MENU_ITEMS.filter((item) => item.category === active);

  return (
    <section
      aria-labelledby="menu-heading"
      className="bg-cream-alt"
    >
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="mb-10 md:mb-14 max-w-2xl">
          <EyebrowChip className="mb-4">{MENU_EYEBROW}</EyebrowChip>
          <h2 id="menu-heading" className="text-headline mb-4">
            {MENU_HEADLINE}
          </h2>
          <p className="text-body-lg">{MENU_INTRO}</p>
        </div>

        {/* Filter chips */}
        {!showAllNoFilter && (
          <div
            role="tablist"
            aria-label="Menu filter"
            className="mb-10 md:mb-12 flex flex-wrap gap-2"
          >
            {MENU_CATEGORIES.map((cat) => {
              const isActive = cat === active;
              return (
                <button
                  key={cat}
                  role="tab"
                  aria-selected={isActive}
                  onClick={() => setActive(cat)}
                  className={cn(
                    "inline-flex items-center rounded-full px-5 py-2 text-sm transition-all duration-200",
                    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-crust focus-visible:ring-offset-2 focus-visible:ring-offset-cream-alt",
                    isActive
                      ? "bg-ink text-cream"
                      : "bg-surface text-ink hover:bg-cream",
                  )}
                >
                  {cat}
                </button>
              );
            })}
          </div>
        )}

        {/* Masonry */}
        <div className="columns-menu">
          <AnimatePresence mode="popLayout">
            {filtered.map((item, i) => (
              <motion.div
                key={item.id}
                layout
                initial={{ opacity: 0, scale: reduce ? 1 : 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: reduce ? 1 : 0.95 }}
                transition={{
                  duration: 0.5,
                  delay: Math.min(i * 0.04, 0.3),
                  ease: [0.16, 1, 0.3, 1],
                }}
              >
                <MenuCard
                  name={item.name}
                  description={item.description}
                  price={item.price}
                  category={item.category}
                  imageUrl={item.image_url}
                />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}
