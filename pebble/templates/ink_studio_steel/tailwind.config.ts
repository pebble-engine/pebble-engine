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
        // tattoo_studio DNA palette — COLD INDUSTRIAL STEEL variant:
        // deep cool-charcoal bg + warm bone fg + brushed steel grey +
        // muted aged-brass spark. Cold counterpart to oxblood.
        ink: {
          bg: "#0E1014",
          fg: "#E8E6E0",
          primary: "#A8B0BD",
          secondary: "#16181D",
          accent: "#C0B47A",
          muted: "#6E727A",
          border: "#2A2D33",
          elevated: "#1C1F25",
          card: "#13161B",
          "gold-light": "#C5CBD4",
          "gold-dark": "#5C6068",
          "blood-light": "#D4C68A",
          "text-secondary": "#A8ABB2",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        body: ["var(--font-mono)", "monospace"],
        accent: ["var(--font-mono)", "monospace"],
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
          "0 0 24px rgba(168, 176, 189, 0.32), 0 0 60px rgba(168, 176, 189, 0.16)",
        "gold-strong":
          "0 0 32px rgba(168, 176, 189, 0.46), 0 0 96px rgba(168, 176, 189, 0.24)",
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
          "0%, 100%": { textShadow: "0 0 18px rgba(168, 176, 189, 0.4), 0 0 36px rgba(192, 180, 122, 0.18)" },
          "50%": { textShadow: "0 0 26px rgba(168, 176, 189, 0.55), 0 0 52px rgba(192, 180, 122, 0.28)" },
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
