import type { Metadata } from "next";
import { Cormorant_Infant, Great_Vibes } from "next/font/google";
import { SITE_TITLE, SITE_DESCRIPTION } from "@/content/site";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import "./globals.css";

const cormorant = Cormorant_Infant({
  subsets: ["latin"],
  variable: "--font-bodoni",
  display: "swap",
  weight: ["300", "400", "500", "600", "700"],
});

const cormorantBody = Cormorant_Infant({
  subsets: ["latin"],
  variable: "--font-manrope",
  display: "swap",
  weight: ["300", "400", "500"],
});

const greatVibes = Great_Vibes({
  subsets: ["latin"],
  variable: "--font-pinyon",
  display: "swap",
  weight: ["400"],
});

export const metadata: Metadata = {
  title: SITE_TITLE,
  description: SITE_DESCRIPTION,
  metadataBase: new URL("https://example.com"),
  openGraph: {
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    type: "website",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${cormorant.variable} ${cormorantBody.variable} ${greatVibes.variable}`}
    >
      <body className="min-h-screen flex flex-col bg-surface">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
