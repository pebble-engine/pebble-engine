import { Inter } from "next/font/google";
import { Hero } from "@/components/sections/Hero";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], weight: ["300","400","500","600"], variable: "--font-inter" });

const ld = {
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Heron Plumbing",
};

export const viewport = { width: "device-width", initialScale: 1 };

export const metadata = {
  title: "Heron Plumbing",
  openGraph: { title: "Heron Plumbing", type: "website" },
  twitter: { card: "summary_large_image" },
};

export default function L({children}: any) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="preload" as="image" href="/images/hero-poster.jpg" />
      </head>
      <body className={inter.className}>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(ld) }}
        />
        <Hero />
        <footer>(212) 234-9876</footer>
        {children}
      </body>
    </html>
  );
}
