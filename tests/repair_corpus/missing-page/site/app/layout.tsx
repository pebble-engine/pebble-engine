import { Inter } from "next/font/google";
import { Hero } from "@/components/sections/Hero";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], weight: ["300","400","500","600"], variable: "--font-inter" });

export default function L({children}: any) {
  return (
    <html lang="en" className={inter.variable}>
      <body className={inter.className}>
        <Hero />
        <footer>(212) 234-9876</footer>
        {children}
      </body>
    </html>
  );
}
