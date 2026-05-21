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
        // Hudson Valley sage-bronze palette — light editorial luxury.
        // bg cream, fg deep forest-charcoal, accent warm bronze (CTAs),
        // primary deep sage (brand mark), secondary mid sage (supporting).
        bg: "#FAF8F2",
        fg: "#1F2421",
        accent: {
          DEFAULT: "#9B7B47",
          hover: "#8A6C3D",
        },
        primary: {
          DEFAULT: "#4A5840",
          hover: "#3A4632",
        },
        secondary: "#6E7A60",
        surface: "#EFEDE4",
        muted: "#6E7A60",
        border: "#E0DDD3",
      },
      fontFamily: {
        display: ["var(--font-unbounded)", "serif", "system-ui", "sans-serif"],
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
