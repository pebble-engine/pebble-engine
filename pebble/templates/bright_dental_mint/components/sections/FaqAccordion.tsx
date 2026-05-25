"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { FAQS } from "@/content/site";

export function FaqAccordion() {
  const [openIdx, setOpenIdx] = useState<number>(0);
  const reduce = useReducedMotion();

  return (
    <div className="max-w-3xl mx-auto pb-24 space-y-4">
      {FAQS.map((faq, i) => {
        const isOpen = openIdx === i;
        return (
          <div
            key={faq.q}
            className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm"
          >
            <button
              type="button"
              onClick={() => setOpenIdx(isOpen ? -1 : i)}
              className="w-full font-[family-name:var(--font-display)] text-xl font-bold text-navy pr-2 flex items-center justify-between cursor-pointer text-left"
              aria-expanded={isOpen}
            >
              <span>{faq.q}</span>
              <span
                className={`w-6 h-6 text-mint text-2xl leading-none transition-transform duration-300 ${
                  isOpen ? "rotate-45" : ""
                }`}
                aria-hidden="true"
              >
                +
              </span>
            </button>
            <AnimatePresence initial={false}>
              {isOpen && (
                <motion.div
                  initial={reduce ? false : { height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={reduce ? { opacity: 0 } : { height: 0, opacity: 0 }}
                  transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                  className="overflow-hidden"
                >
                  <p className="text-slate-600 leading-relaxed pt-4">{faq.a}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
}
