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
        // Material Design 3 surface tokens — beauty_ethereal palette (rose variant)
        surface: {
          DEFAULT: "#fdf2f8",
          dim: "#f4d5e3",
          variant: "#f8dde9",
          "container-lowest": "#ffffff",
          "container-low": "#fde7f1",
          container: "#fbdde9",
          "container-high": "#f9d2e2",
          "container-highest": "#f6c8db",
        },
        primary: {
          DEFAULT: "#ec4899",
          container: "#fbcfe8",
        },
        secondary: {
          DEFAULT: "#f9a8d4",
        },
        tertiary: {
          DEFAULT: "#8b5cf6",
          container: "#ddd6fe",
        },
        "on-surface": {
          DEFAULT: "#831843",
          variant: "#9d2f5a",
        },
        outline: {
          DEFAULT: "#c97aa0",
          variant: "#fbcfe8",
        },
      },
      fontFamily: {
        display: ["var(--font-bodoni)", "Georgia", "serif"],
        body: ["var(--font-manrope)", "system-ui", "sans-serif"],
        script: ["var(--font-pinyon)", "script"],
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
          "0 8px 24px rgba(236, 72, 153, 0.08), 0 24px 64px rgba(236, 72, 153, 0.12), 0 64px 120px rgba(236, 72, 153, 0.10)",
        "vapor-strong":
          "0 12px 32px rgba(236, 72, 153, 0.12), 0 32px 80px rgba(236, 72, 153, 0.18), 0 80px 160px rgba(236, 72, 153, 0.14)",
        glass: "0 4px 32px rgba(131, 24, 67, 0.06), inset 0 0 0 1px rgba(255, 255, 255, 0.5)",
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
