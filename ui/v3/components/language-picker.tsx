"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Globe, Check, ChevronDown } from "lucide-react";
import { type } from "@/lib/type";
import { getBrief, patchBrief } from "@/lib/state";

/**
 * Language picker — sits inline near the questionnaire's notes field.
 *
 * Default behaviour is *no* explicit pick: the engine auto-detects the
 * target language from the brief's free-text fields and stamps the
 * canonical BCP 47 code into ``_language`` server-side. This picker
 * exists for the edge case where auto-detect would guess wrong (e.g.
 * "I want a Spanish version of an English brief") OR the user simply
 * wants a definitive promise about what they'll get.
 *
 * The component keeps a local copy of the choice (defaults to whatever
 * brief._language already says, OR "auto") and writes to the brief on
 * every pick. Choosing "Auto" clears the override so the server takes
 * over.
 */

type LanguageOption = {
  code:        string;   // BCP 47 code; "auto" is a special sentinel
  english:     string;   // Display name in English (for searchability)
  native:      string;   // What the user actually sees
};

// Mirrors pebble/language.py LANGUAGES. Kept in TS source rather than
// fetched at runtime — the list is small and stable enough that a
// network round-trip on every /intake load would be more annoying than
// the maintenance cost. When adding a language: update both files +
// confirm the engine actually generates copy in that language well.
const OPTIONS: LanguageOption[] = [
  { code: "auto", english: "Auto-detect",        native: "Auto-detect from your description" },
  { code: "en",   english: "English",            native: "English" },
  { code: "es",   english: "Spanish",            native: "Español" },
  { code: "fr",   english: "French",             native: "Français" },
  { code: "de",   english: "German",             native: "Deutsch" },
  { code: "it",   english: "Italian",            native: "Italiano" },
  { code: "pt",   english: "Portuguese",         native: "Português" },
  { code: "nl",   english: "Dutch",              native: "Nederlands" },
  { code: "pl",   english: "Polish",             native: "Polski" },
  { code: "sv",   english: "Swedish",            native: "Svenska" },
  { code: "tr",   english: "Turkish",            native: "Türkçe" },
  { code: "id",   english: "Indonesian",         native: "Bahasa Indonesia" },
  { code: "vi",   english: "Vietnamese",         native: "Tiếng Việt" },
  { code: "ja",   english: "Japanese",           native: "日本語" },
  { code: "ko",   english: "Korean",             native: "한국어" },
  { code: "zh",   english: "Chinese (Simplified)", native: "中文" },
  { code: "ar",   english: "Arabic",             native: "العربية" },
  { code: "he",   english: "Hebrew",             native: "עברית" },
  { code: "ru",   english: "Russian",            native: "Русский" },
  { code: "uk",   english: "Ukrainian",          native: "Українська" },
  { code: "hi",   english: "Hindi",              native: "हिन्दी" },
];

export function LanguagePicker() {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<string>("auto");
  const ref = useRef<HTMLDivElement>(null);

  // Hydrate from the brief once on mount.
  useEffect(() => {
    const brief = getBrief();
    const existing = (brief._language as string) || "auto";
    setSelected(OPTIONS.some((o) => o.code === existing) ? existing : "auto");
  }, []);

  // Click-outside-to-close — keep the menu unobtrusive.
  useEffect(() => {
    if (!open) return;
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    window.addEventListener("click", onClick);
    return () => window.removeEventListener("click", onClick);
  }, [open]);

  const current = OPTIONS.find((o) => o.code === selected) || OPTIONS[0];

  function choose(code: string) {
    setSelected(code);
    setOpen(false);
    if (code === "auto") {
      // Clear the override so the server's auto-detect takes the wheel.
      patchBrief({ _language: "" });
    } else {
      patchBrief({ _language: code });
    }
  }

  return (
    <div ref={ref} className={`mt-6 flex items-center justify-center gap-2 ${type.caption}`}>
      <Globe className="w-3.5 h-3.5" aria-hidden />
      <span>Site language:</span>
      <div className="relative">
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            setOpen((v) => !v);
          }}
          className="inline-flex items-center gap-1 text-foreground font-semibold hover:bg-accent rounded-md px-2 py-1 transition-colors"
          aria-haspopup="listbox"
          aria-expanded={open}
        >
          {current.native}
          <ChevronDown className={`w-3.5 h-3.5 transition-transform ${open ? "rotate-180" : ""}`} aria-hidden />
        </button>
        <AnimatePresence>
          {open && (
            <motion.ul
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.15 }}
              role="listbox"
              aria-label="Site language"
              className="absolute z-30 right-0 mt-1 w-64 max-h-80 overflow-y-auto bg-card border border-border rounded-xl shadow-lg py-1"
            >
              {OPTIONS.map((opt) => {
                const isCurrent = opt.code === selected;
                return (
                  <li key={opt.code} role="option" aria-selected={isCurrent}>
                    <button
                      type="button"
                      onClick={() => choose(opt.code)}
                      className={`w-full flex items-center justify-between gap-2 px-3 py-2 text-left text-sm transition-colors ${
                        isCurrent ? "bg-secondary/10 text-foreground" : "hover:bg-accent text-foreground"
                      }`}
                    >
                      <span className="flex flex-col">
                        <span className="font-semibold">{opt.native}</span>
                        {opt.english !== opt.native && (
                          <span className="text-[10px] text-muted-foreground">{opt.english}</span>
                        )}
                      </span>
                      {isCurrent && <Check className="w-3.5 h-3.5 text-secondary flex-shrink-0" aria-hidden />}
                    </button>
                  </li>
                );
              })}
            </motion.ul>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
