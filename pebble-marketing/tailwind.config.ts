import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        editorial: ["var(--font-fraunces)", "Fraunces", "Georgia", "serif"],
        mono: ["var(--font-plex-mono)", "IBM Plex Mono", "ui-monospace", "monospace"],
      },
      colors: {
        // Brand book palette — see BRAND_BOOK.md
        // Updated 2026-05-14: Spark promoted to primary action, Earth added.
        sand:  "#FAF8F3",  // primary background (light, warm paper)
        stone: "#2C2C2A",  // primary ink (dark warm gray, never pure black)
        spark: "#C8A96E",  // PRIMARY ACTION (warm amber, "go" energy)
        river: "#5E7A6E",  // success / supporting (sage green)
        earth: "#C57E5A",  // warm highlight (terracotta, decorative only)
        mist:  "#E8E2D5",  // borders, dividers (light warm gray)
      },
      fontSize: {
        // Brand book typography: minimum 18px body for older readers
        base: ["18px", { lineHeight: "1.6" }],   // body default
        lg:   ["20px", { lineHeight: "1.55" }],  // body emphasis
        xl:   ["22px", { lineHeight: "1.5" }],   // sub-headline / lead
      },
      borderRadius: {
        // Brand book pattern #1: rounded everything (pebble metaphor)
        button: "8px",
        input:  "8px",
        card:   "12px",
      },
      spacing: {
        // Brand book pattern #3: generous section gaps
        section:        "5rem",   // 80px
        "section-mobile": "3.5rem", // 56px
      },
    },
  },
  plugins: [],
};

export default config;
