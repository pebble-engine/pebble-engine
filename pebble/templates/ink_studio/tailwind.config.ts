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
        // tattoo_studio DNA palette — pitch-black + deep-gold + oxblood
        ink: {
          bg: "#0A0A0A",
          fg: "#F5F5F0",
          primary: "#C9A84C",
          secondary: "#141414",
          accent: "#8B0000",
          muted: "#6B6B6B",
          border: "#2A2A2A",
          elevated: "#1C1C1C",
          card: "#111111",
          "gold-light": "#D4B96A",
          "gold-dark": "#A88A3D",
          "blood-light": "#A01010",
          "text-secondary": "#A3A3A3",
        },
      },
      fontFamily: {
        display: ["var(--font-unifraktur)", "Georgia", "serif"],
        body: ["var(--font-source)", "system-ui", "sans-serif"],
        accent: ["var(--font-bebas)", "Impact", "sans-serif"],
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
          "0 0 24px rgba(201, 168, 76, 0.35), 0 0 60px rgba(201, 168, 76, 0.18)",
        "gold-strong":
          "0 0 32px rgba(201, 168, 76, 0.5), 0 0 96px rgba(201, 168, 76, 0.28)",
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
          "0%, 100%": { textShadow: "0 0 20px rgba(201, 168, 76, 0.45), 0 0 40px rgba(201, 168, 76, 0.25)" },
          "50%": { textShadow: "0 0 28px rgba(201, 168, 76, 0.6), 0 0 56px rgba(201, 168, 76, 0.35)" },
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
