import type { Metadata } from "next";
import { Inter, Fraunces, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  variable: "--font-inter",
  display: "swap",
});

const fraunces = Fraunces({
  subsets: ["latin"],
  weight: ["400"],
  style: ["italic"],
  variable: "--font-fraunces",
  display: "swap",
});

const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-plex-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Pebble — Beautiful websites, made easy",
  description:
    "Pebble makes building a beautiful website feel easy. Answer 8 questions and turn an idea into a real, working site. Built for people, not coders.",
  metadataBase: new URL("https://getpebble.net"),
  openGraph: {
    title: "Pebble — Beautiful websites, made easy",
    description: "Answer 8 questions. Get a beautiful website. Own every line of code.",
    url: "https://getpebble.net",
    siteName: "Pebble",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Pebble — Beautiful websites, made easy",
    description: "Answer 8 questions. Get a beautiful website. Own every line of code.",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${fraunces.variable} ${plexMono.variable}`}
    >
      <body className={`${inter.className} antialiased`}>
        {children}
      </body>
    </html>
  );
}
