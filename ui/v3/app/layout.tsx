import type { Metadata } from "next";
import { Inter, Literata, JetBrains_Mono, Instrument_Sans, Instrument_Serif } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { AuthProvider } from "@/components/auth-provider";
import { CommandPalette } from "@/components/command-palette";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
});

const literata = Literata({
  variable: "--font-literata",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  weight: ["400"],
});

const instrumentSans = Instrument_Sans({
  variable: "--font-instrument-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const instrumentSerif = Instrument_Serif({
  variable: "--font-instrument-serif",
  subsets: ["latin"],
  weight: ["400"],
  style: ["normal", "italic"],
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_BASE_URL ?? "https://pebbleapp.ai"),
  title: "Pebble",
  description: "Pebble — build a website you understand.",
};

// Inline script applies the user's stored theme before the page paints,
// so a dark-mode user doesn't see a flash of light theme on load.
//
// 2026-05-19 second pass: app DEFAULTS to DARK and the dark theme is now
// pure neutral (true black background, white text, neutral grays). The
// landing hero, the workspace, and the marketing body share one mono
// identity. Light mode still exists for accessibility / user preference
// but is no longer the auto default.
const THEME_INIT_SCRIPT = `
(function() {
  try {
    var stored = localStorage.getItem('pebble.theme');
    var theme = stored === 'dark' || stored === 'light' ? stored : 'dark';
    if (theme === 'dark') document.documentElement.classList.add('dark');
  } catch (e) {
    document.documentElement.classList.add('dark');
  }
})();
`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${literata.variable} ${jetbrainsMono.variable} ${instrumentSans.variable} ${instrumentSerif.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <AuthProvider>
          {children}
          <CommandPalette />
        </AuthProvider>
        {process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN && (
          <Script
            defer
            data-domain={process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN}
            src="https://plausible.io/js/script.js"
          />
        )}
      </body>
    </html>
  );
}
