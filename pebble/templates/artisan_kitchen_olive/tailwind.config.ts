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
        // bakery_warm DNA palette — olive variant: Mediterranean trattoria (butter cream + deep olive + honey + terracotta)
        cream: {
          DEFAULT: "#F7F2E8", // warm butter cream
          alt: "#EFE8D6",
        },
        ink: {
          DEFAULT: "#2A2D1F", // deep olive-charcoal
          soft: "#5C6048",
        },
        crust: {
          DEFAULT: "#4F5D2F", // primary — deep olive green
          soft: "#7A8E4A",   // secondary — sage olive
        },
        herb: {
          DEFAULT: "#A03A28", // tertiary — terracotta / tomato-red CTA accent
        },
        honey: {
          DEFAULT: "#C8943C", // accent — warm honey (warm-anchor preserved)
        },
        muted: {
          DEFAULT: "#8C8770",
        },
        edge: {
          DEFAULT: "#D9D2BD",
        },
        surface: {
          DEFAULT: "#FFFFFF",
        },
      },
      fontFamily: {
        display: ["var(--font-fraunces)", "Georgia", "serif"],
        body: ["var(--font-inter)", "Georgia", "serif"],
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
          "0 4px 16px rgba(79, 93, 47, 0.08), 0 16px 40px rgba(42, 45, 31, 0.06)",
        "warm-strong":
          "0 8px 24px rgba(79, 93, 47, 0.14), 0 28px 64px rgba(42, 45, 31, 0.10)",
        glass:
          "0 4px 24px rgba(42, 45, 31, 0.06), inset 0 0 0 1px rgba(255, 255, 255, 0.55)",
        cta:
          "0 6px 18px rgba(79, 93, 47, 0.28), 0 18px 40px rgba(79, 93, 47, 0.18)",
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
