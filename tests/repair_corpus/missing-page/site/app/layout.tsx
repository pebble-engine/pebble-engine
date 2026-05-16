import { Inter } from "next/font/google";
import { Hero } from "@/components/sections/Hero";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], weight: ["300","400","500","600"], variable: "--font-inter" });

const ld = {
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Heron Plumbing",
};

export default function L({children}: any) {
  return (
    <html lang="en" className={inter.variable}>
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
