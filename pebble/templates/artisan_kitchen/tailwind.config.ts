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
        // bakery_warm DNA palette — tactile Y2K warm-cream
        cream: {
          DEFAULT: "#FDF6EC",
          alt: "#FFF4E6",
        },
        ink: {
          DEFAULT: "#1A1A1A",
          soft: "#6B5B4F",
        },
        crust: {
          DEFAULT: "#E8590C", // primary — warm vermilion/burnt orange
          soft: "#FF6B35",
        },
        herb: {
          DEFAULT: "#4A6741", // secondary — sage / pickled-bay
        },
        honey: {
          DEFAULT: "#C77D4A", // accent — toasted mustard
        },
        muted: {
          DEFAULT: "#9B8A7D",
        },
        edge: {
          DEFAULT: "#E8DDD0",
        },
        surface: {
          DEFAULT: "#FFFFFF",
        },
      },
      fontFamily: {
        display: ["var(--font-fraunces)", "Georgia", "serif"],
        body: ["var(--font-inter)", "system-ui", "sans-serif"],
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
      borderRadius: {
        "4xl": "2rem",
      },
      boxShadow: {
        warm:
          "0 4px 16px rgba(232, 89, 12, 0.08), 0 16px 40px rgba(26, 26, 26, 0.06)",
        "warm-strong":
          "0 8px 24px rgba(232, 89, 12, 0.14), 0 28px 64px rgba(26, 26, 26, 0.10)",
        glass:
          "0 4px 24px rgba(26, 26, 26, 0.06), inset 0 0 0 1px rgba(255, 255, 255, 0.55)",
        cta:
          "0 6px 18px rgba(232, 89, 12, 0.28), 0 18px 40px rgba(232, 89, 12, 0.18)",
      },
      backdropBlur: {
        glass: "16px",
        "glass-strong": "20px",
      },
      animation: {
        "fade-in": "fadeIn 0.8s ease-out forwards",
        "fade-in-up": "fadeInUp 0.8s ease-out forwards",
        "blob-bounce": "blobBounce 4s ease-in-out infinite",
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
        blobBounce: {
          "0%, 100%": { transform: "translate(0, 0) scale(1)" },
          "50%": { transform: "translate(0, -12px) scale(1.02)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
