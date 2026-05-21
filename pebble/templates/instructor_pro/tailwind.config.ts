import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./content/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-dm-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-outfit)", "var(--font-dm-sans)", "system-ui", "sans-serif"],
      },
      colors: {
        bg: "hsl(var(--bg) / <alpha-value>)",
        fg: "hsl(var(--fg) / <alpha-value>)",
        primary: "hsl(var(--primary) / <alpha-value>)",
        secondary: "hsl(var(--secondary) / <alpha-value>)",
        accent: "hsl(var(--accent) / <alpha-value>)",
        "accent-warm": "hsl(var(--accent-warm) / <alpha-value>)",
        muted: "hsl(var(--muted) / <alpha-value>)",
        card: "hsl(var(--card) / <alpha-value>)",
        border: "hsl(var(--border) / <alpha-value>)",
        ring: "hsl(var(--ring) / <alpha-value>)",
      },
      keyframes: {
        "shimmer-band": {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(200%)" },
        },
        "pulse-dot": {
          "0%, 100%": { opacity: "1", transform: "scale(1)" },
          "50%": { opacity: "0.55", transform: "scale(1.25)" },
        },
        "fade-up": {
          from: { opacity: "0", transform: "translateY(16px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "subtle-glow": {
          "0%, 100%": { boxShadow: "0 0 0 0 hsl(var(--accent-warm) / 0)" },
          "50%": { boxShadow: "0 0 36px 4px hsl(var(--accent-warm) / 0.18)" },
        },
      },
      animation: {
        "shimmer-band": "shimmer-band 3s linear infinite",
        "pulse-dot": "pulse-dot 1.8s ease-in-out infinite",
        "fade-up": "fade-up 0.8s ease-out both",
        "subtle-glow": "subtle-glow 4.5s ease-in-out infinite",
      },
      letterSpacing: {
        "headline": "-0.02em",
        "wide-15": "0.15em",
        "wide-12": "0.12em",
      },
    },
  },
  plugins: [],
};
export default config;
