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
        sand:  "#FAF8F3",  // primary background (light)
        stone: "#2C2C2A",  // primary ink (dark warm gray)
        river: "#5E7A6E",  // primary accent (sage green)
        spark: "#C8A96E",  // secondary accent (warm amber)
        mist:  "#E8E2D5",  // borders, dividers (light warm gray)
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
