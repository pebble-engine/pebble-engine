import type { Metadata } from "next";
import { JetBrains_Mono, Cormorant, Plus_Jakarta_Sans, Cinzel } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { AuthProvider } from "@/components/auth-provider";
import { CommandPalette } from "@/components/command-palette";

// Display font — Cormorant (ultra-refined luxury serif).
// Used for all display.* and heading.* roles. The thin strokes at 96px
// are genuinely breathtaking; weights 300–700 give full range from
// whisper-light editorial to bold statement.
const cormorant = Cormorant({
  variable: "--font-cormorant",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  style: ["normal", "italic"],
});

// Logo / wordmark font — Cinzel (Roman-inscription luxury serif).
// Used ONLY for the rotating Pebble wordmark in the nav + footer.
// Roman proportions, high-contrast strokes, openly luxurious. Distinct
// from Cormorant so the logo has its own identity apart from headings.
const cinzel = Cinzel({
  variable: "--font-cinzel",
  subsets: ["latin"],
  weight: ["400", "600"],
});

// Body font — Plus Jakarta Sans (geometric humanist sans).
// Used for all body.*, label, caption, eyebrow, mono-adjacent narration.
// Widely adopted by premium SaaS (Vercel, Loom, Linear-adjacent tools).
// Excellent legibility at 11–16px; slightly warmer than Inter.
const plusJakartaSans = Plus_Jakarta_Sans({
  variable: "--font-plus-jakarta-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  weight: ["400"],
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
      className={`${cormorant.variable} ${cinzel.variable} ${plusJakartaSans.variable} ${jetbrainsMono.variable} h-full antialiased`}
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
