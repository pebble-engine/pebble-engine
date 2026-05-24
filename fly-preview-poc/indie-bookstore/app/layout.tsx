import { Inter, EB_Garamond, Geist_Mono } from "next/font/google";
import type { Metadata } from "next";
import { Footer } from "@/components/layout/Footer";
import { Navbar } from "@/components/layout/Navbar";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  variable: "--font-inter",
  display: "swap",
});

const garamond = EB_Garamond({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-display",
  display: "swap",
  style: ["normal", "italic"],
});

const geist = Geist_Mono({
  subsets: ["latin"],
  weight: ["400"],
  variable: "--font-mono",
  display: "swap",
});

export const viewport = {
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  title: "Indie Bookstore",
  description: "Curated collections, community events, and a cozy reading space in the heart of Portland.",
  openGraph: {
    title: "Indie Bookstore",
    description: "Curated collections, community events, and a cozy reading space in the heart of Portland.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Indie Bookstore",
    description: "Curated collections, community events, and a cozy reading space in the heart of Portland.",
  },
};

const ld = {
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Indie Bookstore",
  "description": "Curated collections, community events, and a cozy reading space in the heart of Portland.",
  "telephone": "[BUSINESS PHONE]",
  "email": "[EMAIL]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[ADDRESS]",
    "addressLocality": "Portland",
    "addressRegion": "OR",
    "addressCountry": "US"
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${garamond.variable} ${geist.variable}`}>
      <body className={`${inter.className} antialiased bg-[var(--color-bg)] text-[var(--color-text-primary)]`}>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(ld) }}
        />
        <Navbar />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}