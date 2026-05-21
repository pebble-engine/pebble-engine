import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./content/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Cinematic IMAX vermilion-slab palette — 6 tokens only.
        bg: "#0A0A0A",
        fg: "#FFFFFF",
        accent: {
          DEFAULT: "#FF3A1F",
          hover: "#E02E16",
        },
        surface: "#141414",
        muted: "#A0A0A0",
        border: "#2A2A2A",
      },
      fontFamily: {
        display: ["var(--font-unbounded)", "Impact", "system-ui", "sans-serif"],
        body: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      spacing: {
        "page-mobile": "20px",
        "page-desktop": "80px",
        "section-mobile": "80px",
        "section-desktop": "140px",
      },
      maxWidth: {
        page: "1440px",
      },
      borderRadius: {
        // Signature 2px micro-rounding — the cinematic-radius slab edge.
        cinematic: "2px",
      },
      letterSpacing: {
        cinematic: "0.3em",
        wider: "0.18em",
        widest: "0.32em",
      },
      animation: {
        "fade-in": "fadeIn 0.8s ease-out forwards",
        "fade-in-up": "fadeInUp 0.8s ease-out forwards",
      },
      keyframes: {
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        fadeInUp: {
          from: { opacity: "0", transform: "translateY(24px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
