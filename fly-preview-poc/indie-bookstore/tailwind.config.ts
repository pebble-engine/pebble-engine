import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "EB Garamond", "serif"],
        mono: ["var(--font-mono)", "Geist Mono", "monospace"],
      },
      maxWidth: {
        "prose": "680px",
      }
    },
  },
  plugins: [],
};
export default config;