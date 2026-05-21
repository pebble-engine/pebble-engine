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
        // tattoo_studio DNA palette — WARM GOTHIC variant:
        // oxblood-charcoal bg + warm parchment fg + deep oxblood + warmed gold.
        ink: {
          bg: "#1A0E0E",
          fg: "#F3E9D7",
          primary: "#B8924A",
          secondary: "#241313",
          accent: "#8B1A1A",
          muted: "#7A6358",
          border: "#3D2020",
          elevated: "#2A1616",
          card: "#1F1010",
          "gold-light": "#C9A85F",
          "gold-dark": "#967438",
          "blood-light": "#A82424",
          "text-secondary": "#C5B5A0",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        body: ["var(--font-body)", "Georgia", "serif"],
      },
      spacing: {
        "page-mobile": "20px",
        "page-desktop": "80px",
        "section-mobile": "72px",
        "section-desktop": "128px",
      },
      maxWidth: {
        page: "1440px",
      },
      boxShadow: {
        gold:
          "0 0 24px rgba(184, 146, 74, 0.35), 0 0 60px rgba(184, 146, 74, 0.18)",
        "gold-strong":
          "0 0 32px rgba(184, 146, 74, 0.5), 0 0 96px rgba(184, 146, 74, 0.28)",
        deep: "0 24px 64px rgba(0, 0, 0, 0.6), 0 64px 120px rgba(0, 0, 0, 0.5)",
      },
      animation: {
        "fade-in": "fadeIn 0.8s ease-out forwards",
        "fade-in-up": "fadeInUp 0.8s ease-out forwards",
        "gold-pulse": "goldPulse 4s ease-in-out infinite",
        "grain-shift": "grainShift 8s steps(10) infinite",
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
        goldPulse: {
          "0%, 100%": { textShadow: "0 0 20px rgba(184, 146, 74, 0.45), 0 0 40px rgba(184, 146, 74, 0.25)" },
          "50%": { textShadow: "0 0 28px rgba(184, 146, 74, 0.6), 0 0 56px rgba(184, 146, 74, 0.35)" },
        },
        grainShift: {
          "0%, 100%": { transform: "translate(0, 0)" },
          "10%": { transform: "translate(-5%, -10%)" },
          "20%": { transform: "translate(-15%, 5%)" },
          "30%": { transform: "translate(7%, -25%)" },
          "40%": { transform: "translate(-5%, 25%)" },
          "50%": { transform: "translate(-15%, 10%)" },
          "60%": { transform: "translate(15%, 0)" },
          "70%": { transform: "translate(0, 15%)" },
          "80%": { transform: "translate(3%, 35%)" },
          "90%": { transform: "translate(-10%, 10%)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
