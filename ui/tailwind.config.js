/** @type {import('tailwindcss').Config} */
// Mirror of the inline `tailwind.config = {...}` block that used to live in
// ui/index.html when the page ran on the Tailwind CDN. Now that we ship a
// pre-built ui/style.css, this is the single source of truth for the theme.
//
// To regenerate ui/style.css after editing this file or the HTML:
//   cd ui && npm run build
module.exports = {
  content: ["./index.html"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "primary-fixed":     "#E5E5E5",
        "primary-fixed-dim": "#A3A3A3",
        "primary":           "#F5F5F5",
        "primary-container": "#737373",
        "on-primary":        "#0A0A0A",
        "on-primary-fixed":  "#0A0A0A",
        "secondary":         "#D4D4D4",
        "tertiary":          "#BFBFBF",
        "error":             "#ff6b6b",
        "background":        "#080808",
        "surface":           "#080808",
        "surface-dim":       "#080808",
        "surface-container-lowest": "#050505",
        "surface-container-low":    "#121212",
        "surface-container":        "#1A1A1A",
        "surface-container-high":   "#222222",
        "surface-container-highest":"#2A2A2A",
        "surface-bright":    "#333333",
        "surface-variant":   "#2A2A2A",
        "on-surface":        "#EDEDED",
        "on-surface-variant":"#A3A3A3",
        "outline":           "#6B6B6B",
        "outline-variant":   "#2E2E2E",
      },
      borderRadius: { DEFAULT: "0.25rem", lg: "0.5rem", xl: "0.75rem", full: "9999px" },
      spacing: {
        "max-width": "720px",
        "stack-sm":  "12px",
        "stack-md":  "24px",
        "stack-lg":  "48px",
        "stack-xl":  "80px",
        "gutter":    "24px",
      },
      fontFamily: {
        display: ["Unbounded", "sans-serif"],
        body:    ["Geist", "ui-sans-serif", "system-ui", "sans-serif"],
        mono:    ["Geist Mono", "ui-monospace", "monospace"],
      },
      fontSize: {
        "display-xl":        ["64px", { lineHeight: "72px", letterSpacing: "-0.02em", fontWeight: "600" }],
        "display-xl-mobile": ["40px", { lineHeight: "48px", letterSpacing: "-0.01em", fontWeight: "600" }],
        "headline-lg":       ["32px", { lineHeight: "40px", fontWeight: "600" }],
        "body-lg":           ["18px", { lineHeight: "28px", fontWeight: "400" }],
        "body-md":           ["16px", { lineHeight: "24px", fontWeight: "400" }],
        "label-mono":        ["12px", { lineHeight: "16px", letterSpacing: "0.05em", fontWeight: "500" }],
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/container-queries"),
  ],
};
