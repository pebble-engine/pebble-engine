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
        // Yacht-club navy + antique-brass palette — 6 tokens only.
        // Deep marine navy ground, warm ivory foreground, brass action color.
        bg: "#0A1726",
        fg: "#F5F1E8",
        accent: {
          DEFAULT: "#B8924A",
          hover: "#9E7A3A",
        },
        surface: "#1E3A5F",
        muted: "#7A8B9D",
        border: "#1A2A40",
      },
      fontFamily: {
        display: ["var(--font-unbounded)", "serif", "system-ui"],
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
