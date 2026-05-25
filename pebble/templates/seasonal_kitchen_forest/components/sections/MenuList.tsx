"use client";

import { useState } from "react";
import { MENU_SECTIONS } from "@/content/site";

type Filter = "all" | "v" | "gf" | "df";

const FILTERS: Array<{ value: Filter; label: string }> = [
  { value: "all", label: "All" },
  { value: "v",   label: "Vegan" },
  { value: "gf",  label: "Gluten-Free" },
  { value: "df",  label: "Dairy-Free" },
];

export function MenuList() {
  const [filter, setFilter] = useState<Filter>("all");

  return (
    <>
      <div className="max-w-4xl mx-auto mb-12 flex flex-wrap gap-3 justify-center">
        {FILTERS.map((f) => (
          <button
            key={f.value}
            type="button"
            onClick={() => setFilter(f.value)}
            className={`px-5 py-2 border rounded-full text-sm font-medium transition-colors ${
              filter === f.value
                ? "bg-burgundy text-bone border-burgundy"
                : "bg-bone text-charcoal border-charcoal/20 hover:border-burgundy"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="max-w-4xl mx-auto space-y-6 pb-24">
        {MENU_SECTIONS.map((section) => (
          <section key={section.title} className="border-t border-charcoal/20 py-2">
            <details className="group" open>
              <summary className="w-full flex items-center justify-between py-6 text-left font-[family-name:var(--font-display)] text-2xl tracking-wide cursor-pointer select-none">
                <span>{section.title}</span>
                <span className="transition-transform duration-300 group-open:rotate-45 text-2xl">+</span>
              </summary>
              <div className="space-y-5 pb-4">
                {section.items
                  .filter((item) => filter === "all" || item.tags.includes(filter))
                  .map((item, i) => (
                    <div key={i} className="flex justify-between items-start border-b border-charcoal/5 pb-2 pt-2">
                      <div>
                        <h3 className="font-medium">{item.name}</h3>
                        <p className="text-sm text-charcoal/60 mt-1">{item.description}</p>
                        {item.tags.length > 0 && (
                          <span className="text-xs text-warmgold uppercase tracking-wider mt-1 block">
                            {item.tags.map((t) => t).join(" · ")}
                          </span>
                        )}
                      </div>
                      <span className="font-[family-name:var(--font-display)] whitespace-nowrap ml-4">
                        {item.price}
                      </span>
                    </div>
                  ))}
                {section.items.filter((item) => filter === "all" || item.tags.includes(filter)).length === 0 && (
                  <p className="text-charcoal/50 italic py-4">No items match that filter in this course.</p>
                )}
              </div>
            </details>
          </section>
        ))}
      </div>
    </>
  );
}
