import type { Metadata } from "next";
import { UnifrakturCook, Source_Sans_3, Bebas_Neue } from "next/font/google";
import { SITE_TITLE, SITE_DESCRIPTION } from "@/content/site";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { GrainOverlay } from "@/components/ui/GrainOverlay";
import "./globals.css";

const unifraktur = UnifrakturCook({
  subsets: ["latin"],
  variable: "--font-unifraktur",
  display: "swap",
  weight: ["700"],
});

const sourceSans = Source_Sans_3({
  subsets: ["latin"],
  variable: "--font-source",
  display: "swap",
  weight: ["300", "400", "500", "600", "700"],
});

const bebas = Bebas_Neue({
  subsets: ["latin"],
  variable: "--font-bebas",
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
      className={`${unifraktur.variable} ${sourceSans.variable} ${bebas.variable}`}
    >
      <body className="min-h-screen flex flex-col bg-ink-bg text-ink-fg">
        <GrainOverlay />
        <Navbar />
        <main className="flex-1 relative z-[2]">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
