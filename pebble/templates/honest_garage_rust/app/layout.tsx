import type { Metadata } from "next";
import { Source_Sans_3, Bebas_Neue, JetBrains_Mono } from "next/font/google";
import { SITE_TITLE, SITE_DESCRIPTION, PHONE, ADDRESS } from "@/content/site";
import "./globals.css";

const sourceSans3 = Source_Sans_3({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-source-sans-3",
  display: "swap",
});

// Bebas Neue is the bold condensed display face. Single weight (400) per Google Fonts spec.
const bebasneue = Bebas_Neue({
  subsets: ["latin"],
  weight: ["400"],
  variable: "--font-bebas-neue",
  display: "swap",
});

// JetBrains Mono is the parts-catalog ref-code voice.
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#1A1714",
};

export const metadata: Metadata = {
  title: `${SITE_TITLE} — ${SITE_DESCRIPTION}`,
  description: SITE_DESCRIPTION,
  openGraph: {
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const ld = {
    "@context": "https://schema.org",
    "@type": "AutoRepair",
    name: SITE_TITLE,
    description: SITE_DESCRIPTION,
    telephone: PHONE,
    address: {
      "@type": "PostalAddress",
      streetAddress: ADDRESS,
      addressCountry: "US",
    },
  };

  return (
    <html
      lang="en"
      className={`${sourceSans3.variable} ${bebasneue.variable} ${jetbrainsMono.variable}`}
    >
      <body className={`${sourceSans3.className} antialiased`}>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(ld) }}
        />
        {/* The load-bearing hazard stripe. Sits above the nav on every page. */}
        <div className="hazard-stripe" aria-hidden="true" />
        {children}
      </body>
    </html>
  );
}
