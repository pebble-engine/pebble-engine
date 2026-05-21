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
        // Material Design 3 surface tokens — beauty_ethereal palette (aubergine variant)
        // Champagne ivory surfaces over deep aubergine ink; warm champagne gold as CTA tertiary.
        surface: {
          DEFAULT: "#FAF7F2",
          dim: "#EBE5DA",
          variant: "#F2EDE3",
          "container-lowest": "#FFFFFF",
          "container-low": "#F6F2EA",
          container: "#F0EBE0",
          "container-high": "#E8E1D3",
          "container-highest": "#DED5C4",
        },
        primary: {
          DEFAULT: "#4A1A4D",
          container: "#7A3D7F",
        },
        secondary: {
          DEFAULT: "#7A3D7F",
        },
        tertiary: {
          DEFAULT: "#B8924A",
          container: "#E6D2A8",
        },
        "on-surface": {
          DEFAULT: "#1B0F1F",
          variant: "#4A3B4F",
        },
        outline: {
          DEFAULT: "#8A7E92",
          variant: "#D4CFC8",
        },
      },
      fontFamily: {
        display: ["var(--font-bodoni)", "Georgia", "serif"],
        body: ["var(--font-manrope)", "system-ui", "sans-serif"],
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
          "0 8px 24px rgba(74, 26, 77, 0.10), 0 24px 64px rgba(74, 26, 77, 0.14), 0 64px 120px rgba(74, 26, 77, 0.12)",
        "vapor-strong":
          "0 12px 32px rgba(74, 26, 77, 0.14), 0 32px 80px rgba(74, 26, 77, 0.20), 0 80px 160px rgba(74, 26, 77, 0.16)",
        glass: "0 4px 32px rgba(27, 15, 31, 0.08), inset 0 0 0 1px rgba(255, 255, 255, 0.5)",
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
