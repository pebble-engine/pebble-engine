"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { Reveal } from "@/components/ui/Reveal";
import { FAQ_HEADLINE, FAQ_SUBLINE, FAQ_ITEMS } from "@/content/site";

export function FAQList() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section className="py-20 md:py-28 max-w-3xl mx-auto px-6">
      <Reveal>
        <header className="mb-12">
          <h1 className="font-[family-name:var(--font-display)] text-3xl md:text-5xl uppercase tracking-tight">
            {FAQ_HEADLINE}
          </h1>
          <p className="mt-4 text-base md:text-lg text-[var(--color-text-secondary)] leading-relaxed">
            {FAQ_SUBLINE}
          </p>
        </header>
      </Reveal>

      <div className="divide-y divide-[var(--color-border)]">
        {FAQ_ITEMS.map((item, i) => {
          const isOpen = openIndex === i;
          return (
            <Reveal key={item.q} delay={i * 0.06}>
              <button
                type="button"
                onClick={() => setOpenIndex(isOpen ? null : i)}
                className="w-full flex items-center justify-between gap-4 py-6 text-left hover:text-[var(--color-accent)] transition-colors"
                aria-expanded={isOpen}
              >
                <span className="font-semibold text-lg">{item.q}</span>
                <ChevronDown
                  className={`w-5 h-5 shrink-0 transition-transform ${isOpen ? "rotate-180" : ""}`}
                  aria-hidden
                />
              </button>
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                    className="overflow-hidden"
                  >
                    <p className="pb-6 text-base text-[var(--color-text-secondary)] leading-relaxed max-w-prose">
                      {item.a}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </Reveal>
          );
        })}
      </div>
    </section>
  );
}
