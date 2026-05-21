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
        // Material Design 3 surface tokens — beauty_ethereal palette
        surface: {
          DEFAULT: "#e8fdfe",
          dim: "#c9dedf",
          variant: "#d2e6e7",
          "container-lowest": "#ffffff",
          "container-low": "#e3f8f8",
          container: "#ddf2f3",
          "container-high": "#d7eced",
          "container-highest": "#d1e6e7",
        },
        primary: {
          DEFAULT: "#3c6569",
          container: "#a7d2d6",
        },
        secondary: {
          DEFAULT: "#5d5f5f",
        },
        tertiary: {
          DEFAULT: "#94483f",
          container: "#ffb9b0",
        },
        "on-surface": {
          DEFAULT: "#0b1e1f",
          variant: "#404849",
        },
        outline: {
          DEFAULT: "#717879",
          variant: "#c0c8c8",
        },
      },
      fontFamily: {
        display: ["var(--font-bodoni)", "Georgia", "serif"],
        body: ["var(--font-manrope)", "system-ui", "sans-serif"],
        script: ["var(--font-pinyon)", "cursive"],
      },
      spacing: {
        "page-mobile": "20px",
        "page-desktop": "80px",
        "section-mobile": "64px",
        "section-desktop": "120px",
      },
      maxWidth: {
        page: "1440px",
      },
      boxShadow: {
        vapor:
          "0 8px 24px rgba(60, 101, 105, 0.08), 0 24px 64px rgba(60, 101, 105, 0.12), 0 64px 120px rgba(60, 101, 105, 0.10)",
        "vapor-strong":
          "0 12px 32px rgba(60, 101, 105, 0.12), 0 32px 80px rgba(60, 101, 105, 0.18), 0 80px 160px rgba(60, 101, 105, 0.14)",
        glass: "0 4px 32px rgba(11, 30, 31, 0.06), inset 0 0 0 1px rgba(255, 255, 255, 0.5)",
      },
      backdropBlur: {
        glass: "16px",
        "glass-strong": "20px",
      },
      animation: {
        "fade-in": "fadeIn 0.8s ease-out forwards",
        "fade-in-up": "fadeInUp 0.8s ease-out forwards",
        float: "float 6s ease-in-out infinite",
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
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-8px)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
